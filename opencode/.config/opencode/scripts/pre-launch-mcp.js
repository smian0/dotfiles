#!/usr/bin/env node

/**
 * Pre-Launch MCP Transformer
 * 
 * Automatically transforms Claude MCP configurations during OpenCode startup.
 * This runs as part of the pre-launch transformation system to ensure
 * MCP servers are available when OpenCode starts.
 * 
 * Usage:
 *   node pre-launch-mcp.js
 */

import { readFile, writeFile, stat } from 'fs/promises';
import { join, dirname, basename } from 'path';
import { fileURLToPath } from 'url';
import { existsSync } from 'fs';
import { homedir } from 'os';
import { transformMcp } from '../plugin-util/mcp-transformer-core.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const LOG_PREFIX = '[Pre-Launch MCP]';

/**
 * Get modification time of a file
 */
async function getModTime(filePath) {
  try {
    const stats = await stat(filePath);
    return stats.mtime;
  } catch {
    return new Date(0); // Return epoch if file doesn't exist
  }
}

/**
 * Check if source is newer than target
 */
async function isSourceNewer(sourcePath, targetPath) {
  const sourceTime = await getModTime(sourcePath);
  const targetTime = await getModTime(targetPath);
  return sourceTime > targetTime;
}

/**
 * Load JSON file safely
 */
async function loadJsonFile(filePath, required = true) {
  try {
    if (!existsSync(filePath)) {
      if (required) {
        throw new Error(`File not found: ${filePath}`);
      }
      return null;
    }
    
    const content = await readFile(filePath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    if (required) {
      throw new Error(`Failed to load ${filePath}: ${error.message}`);
    }
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
    throw new Error(`Failed to save ${filePath}: ${error.message}`);
  }
}

/**
 * Transform MCP configuration if needed
 */
async function transformMcpIfNeeded(sourcePath, targetPath, metadataPath = null) {
  try {
    // Check if source file exists
    if (!existsSync(sourcePath)) {
      console.log(`${LOG_PREFIX} No Claude MCP config found at ${sourcePath}, skipping`);
      return false;
    }
    
    // Check if transformation is needed
    if (existsSync(targetPath)) {
      const needsUpdate = await isSourceNewer(sourcePath, targetPath);
      if (!needsUpdate) {
        console.log(`${LOG_PREFIX} MCP config is up-to-date (${basename(sourcePath)} → ${basename(targetPath)})`);
        return false;
      }
    }
    
    console.log(`${LOG_PREFIX} Transforming MCP config: ${basename(sourcePath)} → ${basename(targetPath)}`);
    
    // Load source Claude MCP configuration
    const claudeMcpConfig = await loadJsonFile(sourcePath, true);
    
    // Load existing OpenCode configuration (if exists)
    const existingConfig = await loadJsonFile(targetPath, false) || {};
    
    // Transform the configuration
    const transformResult = transformMcp(claudeMcpConfig, existingConfig, {
      enableLogging: false, // Quiet for startup
      validateInput: true,
      generateMetadata: true,
      overwriteExisting: false // Merge mode for startup
    });
    
    if (!transformResult.success) {
      console.error(`${LOG_PREFIX} ❌ MCP transformation failed:`);
      if (transformResult.validation?.errors) {
        transformResult.validation.errors.forEach(error => {
          console.error(`${LOG_PREFIX}   ${error}`);
        });
      }
      if (transformResult.error) {
        console.error(`${LOG_PREFIX}   ${transformResult.error}`);
      }
      return false;
    }
    
    // Save the transformed configuration
    await saveJsonFile(targetPath, transformResult.config);
    
    // Save metadata if generated and path provided
    if (metadataPath && transformResult.metadata && 
        Object.keys(transformResult.metadata.servers).length > 0) {
      await saveJsonFile(metadataPath, transformResult.metadata);
    }
    
    console.log(`${LOG_PREFIX} ✅ Transformed ${transformResult.transformedServers.length} MCP servers`);
    return true;
    
  } catch (error) {
    console.error(`${LOG_PREFIX} ❌ Error transforming MCP config: ${error.message}`);
    return false;
  }
}

/**
 * Main transformation function for both global and project MCP configs
 */
async function transformAllMcpConfigs() {
  console.log(`${LOG_PREFIX} Starting pre-launch MCP transformation...`);
  
  let totalTransformed = 0;
  
  // 1. Transform global Claude MCP config to OpenCode
  const globalClaudeMcpPath = join(homedir(), 'dotfiles/claude/.claude/.mcp.json');
  const globalOpenCodeConfigPath = join(dirname(__dirname), 'opencode.json');
  const globalMetadataPath = join(dirname(__dirname), '.mcp-metadata.json');
  
  const globalTransformed = await transformMcpIfNeeded(
    globalClaudeMcpPath,
    globalOpenCodeConfigPath,
    globalMetadataPath
  );
  if (globalTransformed) totalTransformed++;
  
  // 2. Check for project-local Claude MCP config (if we're in a project)
  const currentDir = process.cwd();
  const projectClaudeMcpPath = join(currentDir, '.claude/.mcp.json');
  const projectOpenCodeConfigPath = join(currentDir, '.opencode.json');
  const projectMetadataPath = join(currentDir, '.mcp-metadata.json');
  
  if (existsSync(projectClaudeMcpPath)) {
    const projectTransformed = await transformMcpIfNeeded(
      projectClaudeMcpPath,
      projectOpenCodeConfigPath,
      projectMetadataPath
    );
    if (projectTransformed) totalTransformed++;
  }
  
  // Summary
  if (totalTransformed === 0) {
    console.log(`${LOG_PREFIX} No MCP transformations needed`);
  } else {
    console.log(`${LOG_PREFIX} Completed ${totalTransformed} MCP transformation(s)`);
  }
  
  console.log(`${LOG_PREFIX} Pre-launch MCP transformation complete ✅`);
  return totalTransformed;
}

/**
 * Check MCP configuration status (for diagnostics)
 */
async function checkMcpStatus() {
  const status = {
    global: {
      claudeExists: false,
      opencodeExists: false,
      needsUpdate: false
    },
    project: {
      claudeExists: false,
      opencodeExists: false,
      needsUpdate: false
    }
  };
  
  // Check global config
  const globalClaudeMcpPath = join(homedir(), 'dotfiles/claude/.claude/.mcp.json');
  const globalOpenCodeConfigPath = join(dirname(__dirname), 'opencode.json');
  
  status.global.claudeExists = existsSync(globalClaudeMcpPath);
  status.global.opencodeExists = existsSync(globalOpenCodeConfigPath);
  
  if (status.global.claudeExists && status.global.opencodeExists) {
    status.global.needsUpdate = await isSourceNewer(globalClaudeMcpPath, globalOpenCodeConfigPath);
  }
  
  // Check project config
  const currentDir = process.cwd();
  const projectClaudeMcpPath = join(currentDir, '.claude/.mcp.json');
  const projectOpenCodeConfigPath = join(currentDir, '.opencode.json');
  
  status.project.claudeExists = existsSync(projectClaudeMcpPath);
  status.project.opencodeExists = existsSync(projectOpenCodeConfigPath);
  
  if (status.project.claudeExists && status.project.opencodeExists) {
    status.project.needsUpdate = await isSourceNewer(projectClaudeMcpPath, projectOpenCodeConfigPath);
  }
  
  return status;
}

// Export for testing and integration
export {
  transformAllMcpConfigs,
  transformMcpIfNeeded,
  checkMcpStatus
};

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  transformAllMcpConfigs().catch(error => {
    console.error(`${LOG_PREFIX} Fatal error:`, error.message);
    process.exit(1);
  });
}