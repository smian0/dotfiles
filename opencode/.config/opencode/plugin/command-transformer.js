/**
 * OpenCode Plugin: Command Transformer  
 * Dynamically transforms Claude command files to OpenCode format on-the-fly
 * Uses shared transformation logic for consistency with pre-launch script
 */

import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { basename, join, dirname } from 'path';
import { homedir } from 'os';
import { transformCommand } from '../plugin-util/command-transformer-core.js';

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
  const globalPath = join(homedir(), 'dotfiles/claude/.claude/commands', relativePath);
  if (existsSync(globalPath)) {
    return globalPath;
  }
  
  // Return project path anyway for error handling
  return projectPath;
}

/**
 * Plugin export - Handles command transformation using shared core logic
 */
export const CommandTransformer = async ({ project, client, $, directory, worktree }) => {
  console.log('[Command Transformer] Plugin initializing with shared core logic');
  console.log(`[Command Transformer] Working directory: ${directory}`);
  
  // Detect and log commands from both global and project .claude directories
  const { readdirSync } = await import('fs');
  const projectRoot = directory; // The directory parameter IS the project root
  const commands = new Map(); // Use Map to handle duplicates with precedence
  
  // Check global commands first
  try {
    const globalCommandsPath = join(homedir(), 'dotfiles/claude/.claude/commands');
    const globalCommands = readdirSync(globalCommandsPath, { recursive: true }).filter(file => file.endsWith('.md'));
    globalCommands.forEach(cmd => commands.set(cmd, 'global'));
    console.log(`[Command Transformer] Global commands detected: ${globalCommands.join(', ')}`);
  } catch (error) {
    console.log(`[Command Transformer] No global commands found: ${error.message}`);
  }
  
  // Check project-local commands (these override global)
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
            
            // Use shared transformation logic
            const transformedContent = transformCommand(claudeContent, {
              returnOriginalOnError: true,
              enableLogging: true
            });
            
            // Modify args to return transformed content
            output.args = {
              ...output.args,
              filePath: claudePath,
              _transformedContent: transformedContent
            };
            
            console.log(`[Command Transformer] Successfully intercepted and transformed using shared core`);
            
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