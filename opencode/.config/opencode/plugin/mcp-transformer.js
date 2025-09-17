/**
 * OpenCode Plugin: MCP Transformer  
 * 
 * Provides live monitoring and transformation of Claude MCP configurations.
 * Integrates with OpenCode's plugin system to automatically detect changes
 * and transform MCP server configurations on-the-fly.
 */

import { readFile, writeFile, watch } from 'fs/promises';
import { existsSync } from 'fs';
import { basename, join, dirname } from 'path';
import { homedir } from 'os';
import { transformMcp } from '../plugin-util/mcp-transformer-core.js';
import { checkMcpStatus } from '../scripts/pre-launch-mcp.js';

/**
 * Check if a file path is an MCP configuration file
 */
function isMcpConfigPath(filePath) {
  return filePath && (
    filePath.endsWith('.mcp.json') ||
    filePath.includes('/.mcp.json') ||
    filePath.includes('\\.mcp.json')
  );
}

/**
 * Get corresponding OpenCode config path for a Claude MCP path
 */
function getOpenCodeConfigPath(claudeMcpPath, directory) {
  // For global config
  if (claudeMcpPath.includes(homedir())) {
    return join(dirname(directory), 'opencode.json');
  }
  
  // For project config
  const projectRoot = dirname(dirname(claudeMcpPath)); // Go up from .claude/.mcp.json
  return join(projectRoot, '.opencode.json');
}

/**
 * Load JSON file safely
 */
async function loadJsonFile(filePath) {
  try {
    if (!existsSync(filePath)) {
      return null;
    }
    const content = await readFile(filePath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    console.error(`[MCP Transformer] Failed to load ${filePath}: ${error.message}`);
    return null;
  }
}

/**
 * Save JSON file safely
 */
async function saveJsonFile(filePath, data) {
  try {
    const content = JSON.stringify(data, null, 2);
    await writeFile(filePath, content, 'utf8');
    return true;
  } catch (error) {
    console.error(`[MCP Transformer] Failed to save ${filePath}: ${error.message}`);
    return false;
  }
}

/**
 * Transform a Claude MCP config to OpenCode format
 */
async function transformMcpConfig(claudeMcpPath, openCodeConfigPath) {
  try {
    console.log(`[MCP Transformer] Transforming ${basename(claudeMcpPath)} → ${basename(openCodeConfigPath)}`);
    
    // Load source and target configurations
    const claudeMcpConfig = await loadJsonFile(claudeMcpPath);
    if (!claudeMcpConfig) {
      console.error(`[MCP Transformer] Failed to load Claude MCP config: ${claudeMcpPath}`);
      return false;
    }
    
    const existingConfig = await loadJsonFile(openCodeConfigPath) || {};
    
    // Transform the configuration
    const transformResult = transformMcp(claudeMcpConfig, existingConfig, {
      enableLogging: false, // Plugin mode - quiet logging
      validateInput: true,
      generateMetadata: false, // Skip metadata in plugin mode
      overwriteExisting: false // Merge mode
    });
    
    if (!transformResult.success) {
      console.error(`[MCP Transformer] Transformation failed:`, transformResult.error);
      return false;
    }
    
    // Save the updated configuration
    const saved = await saveJsonFile(openCodeConfigPath, transformResult.config);
    if (saved) {
      console.log(`[MCP Transformer] ✅ Updated ${transformResult.transformedServers.length} MCP servers`);
      return true;
    }
    
    return false;
    
  } catch (error) {
    console.error(`[MCP Transformer] Error during transformation: ${error.message}`);
    return false;
  }
}

/**
 * Plugin export - Handles MCP transformation and monitoring
 */
export const McpTransformer = async ({ project, client, $, directory, worktree }) => {
  console.log('[MCP Transformer] Plugin initializing');
  console.log(`[MCP Transformer] Working directory: ${directory}`);
  
  // Check initial MCP status
  try {
    const status = await checkMcpStatus();
    
    if (status.global.claudeExists) {
      console.log(`[MCP Transformer] Global Claude MCP config detected`);
      if (status.global.needsUpdate) {
        console.log(`[MCP Transformer] Global MCP config needs update`);
      }
    }
    
    if (status.project.claudeExists) {
      console.log(`[MCP Transformer] Project Claude MCP config detected`);
      if (status.project.needsUpdate) {
        console.log(`[MCP Transformer] Project MCP config needs update`);
      }
    }
    
    if (!status.global.claudeExists && !status.project.claudeExists) {
      console.log(`[MCP Transformer] No Claude MCP configurations found`);
    }
    
  } catch (error) {
    console.log(`[MCP Transformer] Could not check MCP status: ${error.message}`);
  }
  
  return {
    /**
     * Hook into tool execution to transform MCP files on-the-fly
     */
    "tool.execute.before": async (input, output) => {
      try {
        // Intercept file operations on MCP config files
        if ((input.tool === 'read' || input.tool === 'view') && 
            output.args?.filePath && 
            isMcpConfigPath(output.args.filePath)) {
          
          const claudeMcpPath = output.args.filePath;
          const openCodeConfigPath = getOpenCodeConfigPath(claudeMcpPath, directory);
          
          console.log(`[MCP Transformer] MCP config file accessed: ${basename(claudeMcpPath)}`);
          
          // Check if we need to transform to OpenCode format
          if (existsSync(claudeMcpPath) && !existsSync(openCodeConfigPath)) {
            console.log(`[MCP Transformer] OpenCode config missing, triggering transformation`);
            await transformMcpConfig(claudeMcpPath, openCodeConfigPath);
          }
        }
        
        // Intercept writes to MCP config files
        if ((input.tool === 'write' || input.tool === 'edit') && 
            output.args?.filePath && 
            isMcpConfigPath(output.args.filePath)) {
          
          console.log(`[MCP Transformer] MCP config write detected: ${basename(output.args.filePath)}`);
          
          // Note: We'll handle the transformation after the write in a setTimeout
          // since we can't easily hook into post-write events
          const claudeMcpPath = output.args.filePath;
          const openCodeConfigPath = getOpenCodeConfigPath(claudeMcpPath, directory);
          
          setTimeout(async () => {
            try {
              console.log(`[MCP Transformer] Post-write transformation for ${basename(claudeMcpPath)}`);
              await transformMcpConfig(claudeMcpPath, openCodeConfigPath);
            } catch (error) {
              console.error(`[MCP Transformer] Post-write transformation failed: ${error.message}`);
            }
          }, 1000); // Wait 1 second for write to complete
        }
        
      } catch (error) {
        console.error('[MCP Transformer] Error in tool.execute.before hook:', error.message);
        // Don't throw - let the original tool continue
      }
    },
    
    /**
     * Initialize file watching for MCP configurations (if supported)
     */
    "session.start": async () => {
      try {
        // Watch global Claude MCP config
        const globalClaudeMcpPath = join(homedir(), 'dotfiles/claude/.claude/.mcp.json');
        if (existsSync(globalClaudeMcpPath)) {
          console.log(`[MCP Transformer] Setting up watcher for global MCP config`);
          
          // Note: File watching in OpenCode plugins may have limitations
          // This is a best-effort attempt
          try {
            const watcher = watch(globalClaudeMcpPath);
            (async () => {
              for await (const event of watcher) {
                if (event.eventType === 'change') {
                  console.log(`[MCP Transformer] Global MCP config changed, transforming...`);
                  const openCodeConfigPath = join(dirname(directory), 'opencode.json');
                  await transformMcpConfig(globalClaudeMcpPath, openCodeConfigPath);
                }
              }
            })().catch(error => {
              console.log(`[MCP Transformer] File watcher error (expected): ${error.message}`);
            });
          } catch (watchError) {
            console.log(`[MCP Transformer] File watching not available: ${watchError.message}`);
          }
        }
        
        // Watch project MCP config if it exists
        const projectClaudeMcpPath = join(directory, '.claude/.mcp.json');
        if (existsSync(projectClaudeMcpPath)) {
          console.log(`[MCP Transformer] Project MCP config detected`);
          // Similar watching logic could be added here
        }
        
      } catch (error) {
        console.log(`[MCP Transformer] Session start handler error: ${error.message}`);
      }
    }
  };
};

// Export the plugin
export default McpTransformer;