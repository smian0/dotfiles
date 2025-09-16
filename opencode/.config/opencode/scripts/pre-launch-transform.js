#!/usr/bin/env node

/**
 * Pre-Launch Agent Transformer
 * 
 * Transforms Claude agents to OpenCode format before OpenCode starts.
 * This solves the timing issue where OpenCode validates agent files
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
        console.log(`${LOG_PREFIX} Skipping ${basename(sourcePath)} (target is up-to-date)`);
        return false;
      }
    }
    
    console.log(`${LOG_PREFIX} Transforming ${basename(sourcePath)}...`);
    
    // Read source Claude agent
    const claudeContent = await readFile(sourcePath, 'utf8');
    
    // Check if it's actually a Claude agent (has tools field or missing model)
    if (!claudeContent.includes('---') || 
        (claudeContent.includes('model:') && !claudeContent.includes('tools:'))) {
      console.log(`${LOG_PREFIX} Skipping ${basename(sourcePath)} (already OpenCode format)`);
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
    console.log(`${LOG_PREFIX} ✅ Transformed ${basename(sourcePath)}`);
    
    return true;
    
  } catch (error) {
    console.error(`${LOG_PREFIX} ❌ Error transforming ${basename(sourcePath)}:`, error.message);
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
    console.error(`${LOG_PREFIX} Error reading directory ${dir}:`, error.message);
    return [];
  }
}

/**
 * Get target OpenCode agent path for a Claude agent
 */
function getTargetPath(claudeAgentPath, isGlobal = false) {
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
 * Main transformation function
 */
async function transformAgents() {
  console.log(`${LOG_PREFIX} Starting pre-launch agent transformation...`);
  
  let transformedCount = 0;
  let totalChecked = 0;
  
  // 1. Transform global Claude agents
  const globalClaudeDir = join(homedir(), 'dotfiles/claude/.claude/agents');
  const globalAgents = findAgentFiles(globalClaudeDir);
  
  if (globalAgents.length > 0) {
    console.log(`${LOG_PREFIX} Checking ${globalAgents.length} global agents...`);
    
    for (const claudeAgentPath of globalAgents) {
      const targetPath = getTargetPath(claudeAgentPath, true);
      const transformed = await transformAgentFile(claudeAgentPath, targetPath);
      if (transformed) transformedCount++;
      totalChecked++;
    }
  }
  
  // 2. Transform project-local Claude agents (if we're in a project)
  const currentDir = process.cwd();
  const projectClaudeDir = join(currentDir, '.claude/agents');
  const projectAgents = findAgentFiles(projectClaudeDir);
  
  if (projectAgents.length > 0) {
    console.log(`${LOG_PREFIX} Checking ${projectAgents.length} project agents...`);
    
    for (const claudeAgentPath of projectAgents) {
      const targetPath = getTargetPath(claudeAgentPath, false);
      const transformed = await transformAgentFile(claudeAgentPath, targetPath);
      if (transformed) transformedCount++;
      totalChecked++;
    }
  }
  
  // Summary
  if (totalChecked === 0) {
    console.log(`${LOG_PREFIX} No Claude agents found to transform`);
  } else {
    console.log(`${LOG_PREFIX} Checked ${totalChecked} agents, transformed ${transformedCount}`);
  }
  
  console.log(`${LOG_PREFIX} Pre-launch transformation complete ✅`);
  return transformedCount;
}

// Export for testing
export { transformAgents };

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  transformAgents().catch(error => {
    console.error(`${LOG_PREFIX} Fatal error:`, error);
    process.exit(1);
  });
}