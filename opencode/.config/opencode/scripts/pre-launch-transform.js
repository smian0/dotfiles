#!/usr/bin/env node

/**
 * Pre-Launch Agent & Command Transformer
 * 
 * Transforms Claude agents and commands to OpenCode format before OpenCode starts.
 * This solves the timing issue where OpenCode validates files
 * before plugins can patch the filesystem.
 * 
 * Usage:
 *   node pre-launch-transform.js
 */

import { readFile, writeFile, mkdir, stat } from 'fs/promises';
import { join, dirname, basename } from 'path';
import { fileURLToPath } from 'url';
import { existsSync, readdirSync } from 'fs';
import { homedir } from 'os';
import { transformAgent } from '../plugin-util/agent-transformer-core.js';
import { transformCommand } from '../plugin-util/command-transformer-core.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const LOG_PREFIX = '[Pre-Launch Transform]';

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
 * Transform a single agent file if needed
 */
async function transformAgentFile(sourcePath, targetPath) {
  try {
    // Check if transformation is needed
    if (existsSync(targetPath)) {
      const needsUpdate = await isSourceNewer(sourcePath, targetPath);
      if (!needsUpdate) {
        console.log(`${LOG_PREFIX} Skipping agent ${basename(sourcePath)} (target is up-to-date)`);
        return false;
      }
    }
    
    console.log(`${LOG_PREFIX} Transforming agent ${basename(sourcePath)}...`);
    
    // Read source Claude agent
    const claudeContent = await readFile(sourcePath, 'utf8');
    
    // Check if it's actually a Claude agent (has tools field or missing model)
    if (!claudeContent.includes('---') || 
        (claudeContent.includes('model:') && !claudeContent.includes('tools:'))) {
      console.log(`${LOG_PREFIX} Skipping agent ${basename(sourcePath)} (already OpenCode format)`);
      return false;
    }
    
    // Transform to OpenCode format
    const transformedContent = transformAgent(claudeContent, {
      returnOriginalOnError: true,
      enableLogging: false  // Quiet for startup
    });
    
    // Ensure target directory exists
    const targetDir = dirname(targetPath);
    if (!existsSync(targetDir)) {
      await mkdir(targetDir, { recursive: true });
    }
    
    // Write transformed content
    await writeFile(targetPath, transformedContent, 'utf8');
    console.log(`${LOG_PREFIX} ✅ Transformed agent ${basename(sourcePath)}`);
    
    return true;
    
  } catch (error) {
    console.error(`${LOG_PREFIX} ❌ Error transforming agent ${basename(sourcePath)}:`, error.message);
    return false;
  }
}

/**
 * Transform a single command file if needed
 */
async function transformCommandFile(sourcePath, targetPath) {
  try {
    // Check if transformation is needed
    if (existsSync(targetPath)) {
      const needsUpdate = await isSourceNewer(sourcePath, targetPath);
      if (!needsUpdate) {
        console.log(`${LOG_PREFIX} Skipping command ${basename(sourcePath)} (target is up-to-date)`);
        return false;
      }
    }
    
    console.log(`${LOG_PREFIX} Transforming command ${basename(sourcePath)}...`);
    
    // Read source Claude command
    const claudeContent = await readFile(sourcePath, 'utf8');
    
    // Check if it's actually a Claude command (has allowed-tools field)
    if (!claudeContent.includes('---') || 
        (!claudeContent.includes('allowed-tools:') && claudeContent.includes('agent:'))) {
      console.log(`${LOG_PREFIX} Skipping command ${basename(sourcePath)} (already OpenCode format)`);
      return false;
    }
    
    // Transform to OpenCode format
    const transformedContent = transformCommand(claudeContent, {
      returnOriginalOnError: true,
      enableLogging: false  // Quiet for startup
    });
    
    // Ensure target directory exists
    const targetDir = dirname(targetPath);
    if (!existsSync(targetDir)) {
      await mkdir(targetDir, { recursive: true });
    }
    
    // Write transformed content
    await writeFile(targetPath, transformedContent, 'utf8');
    console.log(`${LOG_PREFIX} ✅ Transformed command ${basename(sourcePath)}`);
    
    return true;
    
  } catch (error) {
    console.error(`${LOG_PREFIX} ❌ Error transforming command ${basename(sourcePath)}:`, error.message);
    return false;
  }
}

/**
 * Find all agent files in a directory
 */
function findAgentFiles(dir) {
  if (!existsSync(dir)) {
    return [];
  }
  
  try {
    return readdirSync(dir)
      .filter(file => file.endsWith('.md'))
      .map(file => join(dir, file));
  } catch (error) {
    console.error(`${LOG_PREFIX} Error reading agent directory ${dir}:`, error.message);
    return [];
  }
}

/**
 * Find all command files in a directory
 */
function findCommandFiles(dir) {
  if (!existsSync(dir)) {
    return [];
  }
  
  try {
    return readdirSync(dir)
      .filter(file => file.endsWith('.md'))
      .map(file => join(dir, file));
  } catch (error) {
    console.error(`${LOG_PREFIX} Error reading command directory ${dir}:`, error.message);
    return [];
  }
}

/**
 * Get target OpenCode agent path for a Claude agent
 */
function getAgentTargetPath(claudeAgentPath, isGlobal = false) {
  const filename = basename(claudeAgentPath);
  
  if (isGlobal) {
    // Global agents go to ~/.config/opencode/agent/
    return join(homedir(), '.config/opencode/agent', filename);
  } else {
    // Project agents - determine project root from Claude path
    // Path like: /project/root/.claude/agents/file.md -> /project/root/.opencode/agent/file.md
    const projectRoot = dirname(dirname(claudeAgentPath)); // Go up from .claude/agents to project root
    return join(projectRoot, '.opencode/agent', filename);
  }
}

/**
 * Get target OpenCode command path for a Claude command
 */
function getCommandTargetPath(claudeCommandPath, isGlobal = false) {
  const filename = basename(claudeCommandPath);
  
  if (isGlobal) {
    // Global commands go to ~/.config/opencode/command/
    return join(homedir(), '.config/opencode/command', filename);
  } else {
    // Project commands - determine project root from Claude path
    // Path like: /project/root/.claude/commands/file.md -> /project/root/.opencode/command/file.md
    const projectRoot = dirname(dirname(dirname(claudeCommandPath))); // Go up from .claude/commands to project root
    return join(projectRoot, '.opencode/command', filename);
  }
}

/**
 * Main transformation function for both agents and commands
 */
async function transformAll() {
  console.log(`${LOG_PREFIX} Starting pre-launch transformation...`);
  
  let totalTransformed = 0;
  let totalChecked = 0;
  
  // === AGENTS ===
  console.log(`${LOG_PREFIX} === TRANSFORMING AGENTS ===`);
  
  // 1. Transform global Claude agents
  const globalClaudeAgentsDir = join(homedir(), 'dotfiles/claude/.claude/agents');
  const globalAgents = findAgentFiles(globalClaudeAgentsDir);
  
  if (globalAgents.length > 0) {
    console.log(`${LOG_PREFIX} Checking ${globalAgents.length} global agents...`);
    
    for (const claudeAgentPath of globalAgents) {
      const targetPath = getAgentTargetPath(claudeAgentPath, true);
      const transformed = await transformAgentFile(claudeAgentPath, targetPath);
      if (transformed) totalTransformed++;
      totalChecked++;
    }
  }
  
  // 2. Transform project-local Claude agents (if we're in a project)
  const currentDir = process.cwd();
  const projectClaudeAgentsDir = join(currentDir, '.claude/agents');
  const projectAgents = findAgentFiles(projectClaudeAgentsDir);
  
  if (projectAgents.length > 0) {
    console.log(`${LOG_PREFIX} Checking ${projectAgents.length} project agents...`);
    
    for (const claudeAgentPath of projectAgents) {
      const targetPath = getAgentTargetPath(claudeAgentPath, false);
      const transformed = await transformAgentFile(claudeAgentPath, targetPath);
      if (transformed) totalTransformed++;
      totalChecked++;
    }
  }
  
  // === COMMANDS ===
  console.log(`${LOG_PREFIX} === TRANSFORMING COMMANDS ===`);
  
  // 3. Transform global Claude commands
  const globalClaudeCommandsDir = join(homedir(), 'dotfiles/claude/.claude/commands');
  const globalCommands = findCommandFiles(globalClaudeCommandsDir);
  
  if (globalCommands.length > 0) {
    console.log(`${LOG_PREFIX} Checking ${globalCommands.length} global commands...`);
    
    for (const claudeCommandPath of globalCommands) {
      const targetPath = getCommandTargetPath(claudeCommandPath, true);
      const transformed = await transformCommandFile(claudeCommandPath, targetPath);
      if (transformed) totalTransformed++;
      totalChecked++;
    }
  }
  
  // 4. Transform project-local Claude commands (if we're in a project)
  const projectClaudeCommandsDir = join(currentDir, '.claude/commands');
  const projectCommands = findCommandFiles(projectClaudeCommandsDir);
  
  if (projectCommands.length > 0) {
    console.log(`${LOG_PREFIX} Checking ${projectCommands.length} project commands...`);
    
    for (const claudeCommandPath of projectCommands) {
      const targetPath = getCommandTargetPath(claudeCommandPath, false);
      const transformed = await transformCommandFile(claudeCommandPath, targetPath);
      if (transformed) totalTransformed++;
      totalChecked++;
    }
  }
  
  // Summary
  if (totalChecked === 0) {
    console.log(`${LOG_PREFIX} No Claude files found to transform`);
  } else {
    console.log(`${LOG_PREFIX} Checked ${totalChecked} files, transformed ${totalTransformed}`);
  }
  
  console.log(`${LOG_PREFIX} Pre-launch transformation complete ✅`);
  return totalTransformed;
}

// Export for testing
export { transformAll, transformAgentFile, transformCommandFile };

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  transformAll().catch(error => {
    console.error(`${LOG_PREFIX} Fatal error:`, error);
    process.exit(1);
  });
}