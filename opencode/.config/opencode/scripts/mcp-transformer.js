#!/usr/bin/env node

/**
 * MCP Configuration Transformer
 * 
 * Transforms Claude MCP configurations (.mcp.json) to OpenCode format.
 * Can be run manually or as part of automated processes.
 * 
 * Usage:
 *   node mcp-transformer.js [options]
 *   
 * Options:
 *   --source PATH       Source Claude .mcp.json file (default: ~/dotfiles/claude/.claude/.mcp.json)
 *   --target PATH       Target OpenCode config file (default: current opencode.json)
 *   --metadata PATH     Output metadata file (default: .mcp-metadata.json in target dir)
 *   --dry-run          Show what would be changed without writing files
 *   --verbose          Enable verbose output
 *   --overwrite        Overwrite existing MCP servers (default: merge)
 *   --help             Show this help message
 */

import { readFile, writeFile, stat } from 'fs/promises';
import { join, dirname, basename, resolve } from 'path';
import { fileURLToPath } from 'url';
import { existsSync } from 'fs';
import { homedir } from 'os';
import { transformMcp } from '../plugin-util/mcp-transformer-core.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const LOG_PREFIX = '[MCP Transformer]';

// Default paths
const DEFAULT_SOURCE = join(homedir(), 'dotfiles/claude/.claude/.mcp.json');
const DEFAULT_TARGET = join(dirname(__dirname), 'opencode.json');

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = {
    source: DEFAULT_SOURCE,
    target: DEFAULT_TARGET,
    metadata: null, // Will be set based on target directory
    dryRun: false,
    verbose: false,
    overwrite: false,
    help: false
  };

  const argv = process.argv.slice(2);
  
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    
    switch (arg) {
      case '--source':
        args.source = argv[++i];
        break;
      case '--target':
        args.target = argv[++i];
        break;
      case '--metadata':
        args.metadata = argv[++i];
        break;
      case '--dry-run':
        args.dryRun = true;
        break;
      case '--verbose':
        args.verbose = true;
        break;
      case '--overwrite':
        args.overwrite = true;
        break;
      case '--help':
        args.help = true;
        break;
      default:
        console.error(`${LOG_PREFIX} Unknown argument: ${arg}`);
        process.exit(1);
    }
  }
  
  // Set default metadata path if not specified
  if (!args.metadata) {
    args.metadata = join(dirname(args.target), '.mcp-metadata.json');
  }
  
  return args;
}

/**
 * Show help message
 */
function showHelp() {
  console.log(`
MCP Configuration Transformer

Transforms Claude MCP configurations to OpenCode format.

Usage:
  node mcp-transformer.js [options]

Options:
  --source PATH       Source Claude .mcp.json file 
                     (default: ~/dotfiles/claude/.claude/.mcp.json)
  --target PATH       Target OpenCode config file 
                     (default: ./opencode.json)
  --metadata PATH     Output metadata file 
                     (default: .mcp-metadata.json in target dir)
  --dry-run          Show what would be changed without writing files
  --verbose          Enable verbose output
  --overwrite        Overwrite existing MCP servers (default: merge)
  --help             Show this help message

Examples:
  node mcp-transformer.js                           # Use defaults
  node mcp-transformer.js --verbose                 # With verbose output
  node mcp-transformer.js --dry-run                 # Preview changes
  node mcp-transformer.js --source /path/to/.mcp.json --target /path/to/opencode.json

The transformer will:
1. Read Claude MCP configuration from source file
2. Transform server configurations to OpenCode format
3. Merge with existing OpenCode configuration (preserving other settings)
4. Generate tool permissions for MCP servers
5. Save metadata about original descriptions/purposes
`);
}

/**
 * Get file modification time
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
    throw new Error(`Failed to load ${filePath}: ${error.message}`);
  }
}

/**
 * Save JSON file safely
 */
async function saveJsonFile(filePath, data, dryRun = false) {
  const content = JSON.stringify(data, null, 2);
  
  if (dryRun) {
    console.log(`${LOG_PREFIX} [DRY RUN] Would write to ${filePath}:`);
    console.log('--- Start of file ---');
    console.log(content);
    console.log('--- End of file ---');
    return;
  }
  
  try {
    await writeFile(filePath, content, 'utf8');
    console.log(`${LOG_PREFIX} ✅ Saved: ${filePath}`);
  } catch (error) {
    throw new Error(`Failed to save ${filePath}: ${error.message}`);
  }
}

/**
 * Main transformation function
 */
async function transformMcpConfigs(args) {
  const { source, target, metadata, dryRun, verbose, overwrite } = args;
  
  console.log(`${LOG_PREFIX} Starting MCP configuration transformation`);
  if (verbose) {
    console.log(`${LOG_PREFIX} Source: ${source}`);
    console.log(`${LOG_PREFIX} Target: ${target}`);
    console.log(`${LOG_PREFIX} Metadata: ${metadata}`);
    console.log(`${LOG_PREFIX} Dry run: ${dryRun}`);
    console.log(`${LOG_PREFIX} Overwrite: ${overwrite}`);
  }
  
  // Check if transformation is needed (unless dry run or overwrite)
  if (!dryRun && !overwrite && existsSync(target)) {
    const needsUpdate = await isSourceNewer(source, target);
    if (!needsUpdate) {
      console.log(`${LOG_PREFIX} Target is up-to-date, skipping transformation`);
      return;
    }
  }
  
  // Load source Claude MCP configuration
  console.log(`${LOG_PREFIX} Loading Claude MCP configuration...`);
  const claudeMcpConfig = await loadJsonFile(source, true);
  
  if (verbose) {
    const serverCount = Object.keys(claudeMcpConfig.mcpServers || {}).length;
    console.log(`${LOG_PREFIX} Found ${serverCount} MCP servers in source`);
  }
  
  // Load existing OpenCode configuration (if exists)
  console.log(`${LOG_PREFIX} Loading existing OpenCode configuration...`);
  const existingConfig = await loadJsonFile(target, false) || {};
  
  if (verbose && existingConfig) {
    const existingMcpCount = Object.keys(existingConfig.mcp || {}).length;
    const existingToolsCount = Object.keys(existingConfig.tools || {}).length;
    console.log(`${LOG_PREFIX} Existing config has ${existingMcpCount} MCP servers, ${existingToolsCount} tool permissions`);
  }
  
  // Transform the configuration
  console.log(`${LOG_PREFIX} Transforming MCP configuration...`);
  const transformResult = transformMcp(claudeMcpConfig, existingConfig, {
    enableLogging: verbose,
    validateInput: true,
    generateMetadata: true,
    overwriteExisting: overwrite
  });
  
  if (!transformResult.success) {
    console.error(`${LOG_PREFIX} ❌ Transformation failed:`);
    if (transformResult.validation) {
      transformResult.validation.errors.forEach(error => {
        console.error(`${LOG_PREFIX}   Error: ${error}`);
      });
      transformResult.validation.warnings.forEach(warning => {
        console.warn(`${LOG_PREFIX}   Warning: ${warning}`);
      });
    }
    if (transformResult.error) {
      console.error(`${LOG_PREFIX}   ${transformResult.error}`);
    }
    process.exit(1);
  }
  
  // Show transformation summary
  console.log(`${LOG_PREFIX} ✅ Transformation completed successfully`);
  console.log(`${LOG_PREFIX} Transformed servers: ${transformResult.transformedServers.join(', ')}`);
  console.log(`${LOG_PREFIX} Added tool permissions: ${transformResult.addedTools.length}`);
  
  if (transformResult.validation.warnings.length > 0) {
    console.log(`${LOG_PREFIX} Warnings:`);
    transformResult.validation.warnings.forEach(warning => {
      console.warn(`${LOG_PREFIX}   ${warning}`);
    });
  }
  
  // Save the transformed configuration
  await saveJsonFile(target, transformResult.config, dryRun);
  
  // Save metadata if generated
  if (transformResult.metadata && Object.keys(transformResult.metadata.servers).length > 0) {
    await saveJsonFile(metadata, transformResult.metadata, dryRun);
    console.log(`${LOG_PREFIX} ✅ Saved metadata for ${Object.keys(transformResult.metadata.servers).length} servers`);
  }
  
  if (!dryRun) {
    console.log(`${LOG_PREFIX} 🎉 MCP configuration transformation complete!`);
    console.log(`${LOG_PREFIX} Next steps:`);
    console.log(`${LOG_PREFIX}   1. Review the updated configuration in ${basename(target)}`);
    console.log(`${LOG_PREFIX}   2. Restart OpenCode to load the new MCP servers`);
    if (transformResult.metadata) {
      console.log(`${LOG_PREFIX}   3. Check ${basename(metadata)} for server descriptions`);
    }
  }
}

/**
 * Main entry point
 */
async function main() {
  try {
    const args = parseArgs();
    
    if (args.help) {
      showHelp();
      process.exit(0);
    }
    
    // Resolve relative paths
    args.source = resolve(args.source);
    args.target = resolve(args.target);
    args.metadata = resolve(args.metadata);
    
    await transformMcpConfigs(args);
    
  } catch (error) {
    console.error(`${LOG_PREFIX} ❌ Fatal error: ${error.message}`);
    if (process.argv.includes('--verbose')) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Export for testing
export { transformMcpConfigs, parseArgs, main };

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}