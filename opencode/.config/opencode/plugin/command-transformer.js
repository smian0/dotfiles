/**
 * OpenCode Plugin: Command Transformer  
 * Dynamically transforms Claude command files to OpenCode format on-the-fly
 */

import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { basename, join, dirname } from 'path';
import { homedir } from 'os';

// Tool name mapping from Claude to OpenCode format
const TOOL_MAPPING = {
  'Task': 'agent',
  'Read': 'view', 
  'Edit': 'edit',
  'MultiEdit': 'edit',
  'Write': 'write',
  'LS': 'ls',
  'Grep': 'grep',
  'Glob': 'glob',
  'Bash': 'bash',
  'WebFetch': 'fetch',
  'TodoWrite': 'todo',
  'WebSearch': 'websearch',
  'Search': 'search',
  'Agent': 'agent'
};

/**
 * Parse YAML frontmatter for commands
 */
function parseCommandYAML(yamlStr) {
  const result = {};
  const lines = yamlStr.trim().split('\n');
  
  for (const line of lines) {
    const colonIndex = line.indexOf(':');
    if (colonIndex > 0) {
      const key = line.substring(0, colonIndex).trim();
      const value = line.substring(colonIndex + 1).trim();
      
      if (key === 'allowed-tools') {
        // Parse comma-separated tools
        result[key] = value.split(',').map(t => t.trim());
      } else {
        result[key] = value;
      }
    }
  }
  return result;
}

/**
 * Transform Claude command to OpenCode format
 */
function transformCommand(content) {
  try {
    const parts = content.split('---');
    if (parts.length < 3) {
      console.warn('[Command Transformer] Invalid command file format, missing frontmatter');
      return content;
    }
    
    const frontmatterStr = parts[1];
    const body = parts.slice(2).join('---');
    
    const claudeFM = parseCommandYAML(frontmatterStr);
    
    // Transform allowed-tools
    if (claudeFM['allowed-tools']) {
      claudeFM['allowed-tools'] = claudeFM['allowed-tools'].map(tool => 
        TOOL_MAPPING[tool] || tool.toLowerCase()
      );
    }
    
    // Transform body content
    const transformedBody = body
      .replace(/\.claude\//g, '.opencode/')
      .replace(/Task tool/g, 'agent tool')
      .replace(/Claude Code/g, 'OpenCode');
    
    // Build YAML frontmatter
    let yaml = '';
    for (const [key, value] of Object.entries(claudeFM)) {
      if (Array.isArray(value)) {
        yaml += `${key}: ${value.join(', ')}\n`;
      } else {
        yaml += `${key}: ${value}\n`;
      }
    }
    
    const result = `---\n${yaml}---${transformedBody}`;
    
    console.log(`[Command Transformer] Transformed command`);
    return result;
    
  } catch (error) {
    console.error('[Command Transformer] Transform error:', error);
    return content; // Return original on error
  }
}

/**
 * Check if path is requesting an OpenCode command
 */
function isOpenCodeCommandPath(filePath) {
  return filePath && (
    filePath.includes('.opencode/command/') ||
    filePath.includes('/.opencode/command/') ||
    filePath.endsWith('.opencode/command')
  );
}

/**
 * Get corresponding Claude command path with smart fallback
 * Checks project-local first, then global ~/.claude
 */
function getClaudeCommandPath(opencodePath, directory) {
  // Extract relative path from .opencode/command/
  const relativePath = opencodePath.replace(/.*\.opencode\/command\//, '');
  const projectRoot = dirname(directory); // Go up one level from .opencode to project root
  
  // First try project-local (takes precedence)
  const projectPath = join(projectRoot, '.claude/commands', relativePath);
  if (existsSync(projectPath)) {
    return projectPath;
  }
  
  // Fall back to global ~/.claude
  const globalPath = join(homedir(), '.claude/commands', relativePath);
  if (existsSync(globalPath)) {
    return globalPath;
  }
  
  // Return project path anyway for error handling
  return projectPath;
}

/**
 * Plugin export - Handles command transformation
 */
export const CommandTransformer = async ({ project, client, $, directory, worktree }) => {
  console.log('[Command Transformer] Plugin initializing');
  console.log(`[Command Transformer] Working directory: ${directory}`);
  
  // Detect and log commands from both global and project .claude directories
  const { readdirSync } = await import('fs');
  const projectRoot = dirname(directory); // Go up one level from .opencode to project root
  const commands = new Map(); // Use Map to handle duplicates with precedence
  
  // Check global ~/.claude/commands first
  try {
    const globalCommandsPath = join(homedir(), '.claude/commands');
    const globalCommands = readdirSync(globalCommandsPath, { recursive: true }).filter(file => file.endsWith('.md'));
    globalCommands.forEach(cmd => commands.set(cmd, 'global'));
    console.log(`[Command Transformer] Global commands detected: ${globalCommands.join(', ')}`);
  } catch (error) {
    console.log(`[Command Transformer] No global commands found: ${error.message}`);
  }
  
  // Check project-local .claude/commands (these override global)
  try {
    const projectCommandsPath = join(projectRoot, '.claude/commands');
    const projectCommands = readdirSync(projectCommandsPath, { recursive: true }).filter(file => file.endsWith('.md'));
    projectCommands.forEach(cmd => commands.set(cmd, 'project')); // Overrides global
    console.log(`[Command Transformer] Project commands detected: ${projectCommands.join(', ')}`);
  } catch (error) {
    console.log(`[Command Transformer] No project commands found: ${error.message}`);
  }
  
  // Summary of all available commands
  const allCommands = Array.from(commands.entries());
  if (allCommands.length > 0) {
    const summary = allCommands.map(([name, source]) => `${name}(${source})`).join(', ');
    console.log(`[Command Transformer] Total commands available: ${summary}`);
  } else {
    console.log(`[Command Transformer] No Claude commands found in any location`);
  }
  
  return {
    /**
     * Hook into tool execution to transform command files on-the-fly  
     */
    "tool.execute.before": async (input, output) => {
      try {
        // Intercept view/read tool calls for command files
        if (input.tool === 'view' && output.args?.filePath && isOpenCodeCommandPath(output.args.filePath)) {
          const opencodePath = output.args.filePath;
          const claudePath = getClaudeCommandPath(opencodePath, directory);
          
          console.log(`[Command Transformer] Intercepting ${input.tool} tool: ${opencodePath}`);
          console.log(`[Command Transformer] Redirecting to: ${claudePath}`);
          
          try {
            const claudeContent = await readFile(claudePath, 'utf8');
            const transformedContent = transformCommand(claudeContent);
            
            // Modify args to return transformed content
            output.args = {
              ...output.args,
              filePath: claudePath,
              _transformedContent: transformedContent
            };
            
            console.log(`[Command Transformer] Successfully intercepted and transformed`);
            
          } catch (readError) {
            console.error(`[Command Transformer] Could not read Claude command: ${claudePath}`, readError);
          }
        }
        
      } catch (error) {
        console.error('[Command Transformer] Plugin error:', error);
      }
      
      // Return undefined to let default behavior continue
      return undefined;
    }
  };
};