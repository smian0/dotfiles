/**
 * OpenCode Plugin: Agent Transformer
 * Dynamically transforms Claude agent files to OpenCode format on-the-fly
 */

import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { basename, join, dirname } from 'path';
import { homedir } from 'os';
import { transformAgent } from '../plugin-util/agent-transformer-core.js';

// CRITICAL: Patch filesystem immediately when module loads
// This must happen before OpenCode tries to read agent files
console.log('[Agent Transformer] Patching filesystem at module load time');
patchFileSystemGlobally();

// Tool name mapping from Claude to OpenCode format
const TOOL_MAPPING = {
  'Glob': 'glob',
  'Grep': 'grep', 
  'LS': 'ls',
  'Read': 'view',
  'Write': 'write',
  'Edit': 'edit',
  'MultiEdit': 'edit',
  'Task': 'agent',
  'Agent': 'agent',
  'Bash': 'bash',
  'WebFetch': 'fetch',
  'TodoWrite': 'todo',
  'WebSearch': 'websearch',
  'Search': 'search'
};

// Transformation functions imported from shared module

/**
 * Check if path is requesting an OpenCode agent
 */
function isOpenCodeAgentPath(filePath) {
  return filePath && (
    filePath.includes('.opencode/agent/') ||
    filePath.includes('/.opencode/agent/') ||
    filePath.endsWith('.opencode/agent')
  );
}

/**
 * Get corresponding Claude agent path with smart fallback
 * Checks project-local first, then global ~/.claude
 */
function getClaudeAgentPath(opencodePath, directory) {
  const filename = basename(opencodePath);
  const projectRoot = dirname(directory); // Go up one level from .opencode to project root
  
  // First try project-local (takes precedence)
  const projectPath = join(projectRoot, '.claude/agents', filename);
  if (existsSync(projectPath)) {
    return projectPath;
  }
  
  // Fall back to global ~/.claude
  const globalPath = join(homedir(), '.claude/agents', filename);
  if (existsSync(globalPath)) {
    return globalPath;
  }
  
  // Return project path anyway for error handling
  return projectPath;
}

/**
 * Override Node.js fs functions globally to intercept agent file reads
 * This MUST happen at module load time, before OpenCode reads agent files
 */
function patchFileSystemGlobally() {
  const fs = require('fs');
  const fsPromises = require('fs/promises');
  
  // Store original functions
  if (!global._originalReadFileSync) {
    global._originalReadFileSync = fs.readFileSync;
    global._originalReadFile = fsPromises.readFile;
    
    // Patch synchronous readFileSync
    fs.readFileSync = function(path, options) {
      // Debug: Log ALL file reads to see what OpenCode is accessing
      if (typeof path === 'string' && path.endsWith('.md')) {
        console.log(`[Agent Transformer] DEBUG readFileSync: ${path}`);
      }
      
      // Check if this is an agent file read (both opencode/agent/ and claude/agents/ paths)
      if (typeof path === 'string' && 
          (path.includes('/agent/') || path.includes('/.claude/agents/')) && 
          path.endsWith('.md')) {
        console.log(`[Agent Transformer] Intercepting readFileSync: ${path}`);
        
        try {
          // Read the original file
          const content = global._originalReadFileSync.call(this, path, options);
          const contentStr = content.toString();
          
          // Check if it's a Claude agent (missing model field)
          if (contentStr.includes('---') && !contentStr.includes('model:')) {
            console.log(`[Agent Transformer] Transforming Claude agent: ${path}`);
            const transformed = transformAgent(contentStr, { 
              returnOriginalOnError: true, 
              enableLogging: true, 
              logPrefix: '[Agent Transformer]' 
            });
            return options && options.encoding ? transformed : Buffer.from(transformed);
          }
          
          return content;
        } catch (error) {
          console.error(`[Agent Transformer] Error transforming ${path}:`, error);
          return global._originalReadFileSync.call(this, path, options);
        }
      }
      
      return global._originalReadFileSync.call(this, path, options);
    };
    
    // Patch asynchronous readFile
    fsPromises.readFile = async function(path, options) {
      // Check if this is an agent file read (both opencode/agent/ and claude/agents/ paths)
      if (typeof path === 'string' && 
          (path.includes('/agent/') || path.includes('/.claude/agents/')) && 
          path.endsWith('.md')) {
        console.log(`[Agent Transformer] Intercepting readFile: ${path}`);
        
        try {
          // Read the original file
          const content = await global._originalReadFile.call(this, path, options);
          const contentStr = content.toString();
          
          // Check if it's a Claude agent (missing model field)
          if (contentStr.includes('---') && !contentStr.includes('model:')) {
            console.log(`[Agent Transformer] Transforming Claude agent: ${path}`);
            const transformed = transformAgent(contentStr, { 
              returnOriginalOnError: true, 
              enableLogging: true, 
              logPrefix: '[Agent Transformer]' 
            });
            return options && options.encoding ? transformed : Buffer.from(transformed);
          }
          
          return content;
        } catch (error) {
          console.error(`[Agent Transformer] Error transforming ${path}:`, error);
          return global._originalReadFile.call(this, path, options);
        }
      }
      
      return global._originalReadFile.call(this, path, options);
    };
    
    console.log('[Agent Transformer] File system patched globally (sync + async)');
  } else {
    console.log('[Agent Transformer] File system already patched');
  }
}

/**
 * Plugin export - Handles agent transformation
 */
export const AgentTransformer = async ({ directory }) => {
  console.log('[Agent Transformer] Plugin initializing');
  console.log(`[Agent Transformer] Working directory: ${directory}`);
  
  // Filesystem is already patched at module load time
  
  // Detect and log agents from both global and project .claude directories
  const { readdirSync } = await import('fs');
  const projectRoot = dirname(directory); // Go up one level from .opencode to project root
  const agents = new Map(); // Use Map to handle duplicates with precedence
  
  // Check global ~/.claude/agents first
  try {
    const globalAgentsPath = join(homedir(), '.claude/agents');
    const globalAgents = readdirSync(globalAgentsPath).filter(file => file.endsWith('.md'));
    globalAgents.forEach(agent => agents.set(agent, 'global'));
    console.log(`[Agent Transformer] Global agents detected: ${globalAgents.join(', ')}`);
  } catch (error) {
    console.log(`[Agent Transformer] No global agents found: ${error.message}`);
  }
  
  // Check project-local .claude/agents (these override global)
  try {
    const projectAgentsPath = join(projectRoot, '.claude/agents');
    const projectAgents = readdirSync(projectAgentsPath).filter(file => file.endsWith('.md'));
    projectAgents.forEach(agent => agents.set(agent, 'project')); // Overrides global
    console.log(`[Agent Transformer] Project agents detected: ${projectAgents.join(', ')}`);
  } catch (error) {
    console.log(`[Agent Transformer] No project agents found: ${error.message}`);
  }
  
  // Summary of all available agents
  const allAgents = Array.from(agents.entries());
  if (allAgents.length > 0) {
    const summary = allAgents.map(([name, source]) => `${name}(${source})`).join(', ');
    console.log(`[Agent Transformer] Total agents available: ${summary}`);
  } else {
    console.log(`[Agent Transformer] No Claude agents found in any location`);
  }
  
  return {
    /**
     * Hook into tool execution to transform agent files on-the-fly
     */
    "tool.execute.before": async (input, output) => {
      try {
        // Debug: Log all tool calls to see what OpenCode is using
        console.log(`[Agent Transformer] Tool call: ${input.tool} with args:`, JSON.stringify(output.args, null, 2));
        
        // Intercept view/read tool calls for agent files
        if (input.tool === 'view' && output.args?.filePath && isOpenCodeAgentPath(output.args.filePath)) {
          const opencodePath = output.args.filePath;
          const claudePath = getClaudeAgentPath(opencodePath, directory);
          
          console.log(`[Agent Transformer] Intercepting ${input.tool} tool: ${opencodePath}`);
          console.log(`[Agent Transformer] Redirecting to: ${claudePath}`);
          
          try {
            const claudeContent = await readFile(claudePath, 'utf8');
            const transformedContent = transformAgent(claudeContent, { 
              returnOriginalOnError: true, 
              enableLogging: true, 
              logPrefix: '[Agent Transformer]' 
            });
            
            // Modify args to return transformed content
            output.args = {
              ...output.args,
              filePath: claudePath,
              _transformedContent: transformedContent
            };
            
            console.log(`[Agent Transformer] Successfully intercepted and transformed`);
            
          } catch (readError) {
            console.error(`[Agent Transformer] Could not read Claude agent: ${claudePath}`, readError);
          }
        }
        
      } catch (error) {
        console.error('[Agent Transformer] Plugin error:', error);
      }
      
      // Return undefined to let default behavior continue
      return undefined;
    }
  };
};