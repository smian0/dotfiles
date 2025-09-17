/**
 * Shared Command Transformation Logic
 * 
 * Core transformation functions used by pre-launch script and runtime plugin.
 * Ensures consistent behavior across all transformation contexts.
 */

/**
 * Parse YAML frontmatter for commands
 */
export function parseCommandYAML(yamlStr) {
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
        result[key] = value.replace(/^["']|["']$/g, ''); // Remove quotes
      }
    }
  }
  return result;
}

/**
 * Tool name mapping from Claude to OpenCode format
 */
export const CLAUDE_TO_OPENCODE_TOOLS = {
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
  'Agent': 'agent',
  'Notebook': 'notebook',
  'Jupyter': 'jupyter'
};

/**
 * Transform Claude command frontmatter to OpenCode format
 */
export function transformCommandFrontmatter(claudeFM) {
  const opencodeFM = {};
  
  // Transform description - prefer title, fallback to description, then generate
  if (claudeFM.title) {
    opencodeFM.description = claudeFM.title;
  } else if (claudeFM.description) {
    opencodeFM.description = claudeFM.description;
  } else {
    opencodeFM.description = "Auto-converted Claude command";
  }
  
  // Remove quotes from description if present
  opencodeFM.description = opencodeFM.description.replace(/^["']|["']$/g, '');
  
  // Map tools to OpenCode agent (simplified approach)
  opencodeFM.agent = 'build'; // Default agent for commands
  
  // Transform allowed-tools if present (for documentation purposes)
  if (claudeFM['allowed-tools']) {
    const mappedTools = claudeFM['allowed-tools'].map(tool => 
      CLAUDE_TO_OPENCODE_TOOLS[tool] || tool.toLowerCase()
    );
    // Store as comment in description if needed
    opencodeFM.description += ` (uses: ${mappedTools.join(', ')})`;
  }
  
  // Preserve other relevant fields
  if (claudeFM.category) {
    opencodeFM.category = claudeFM.category;
  }
  
  if (claudeFM.author) {
    opencodeFM.author = claudeFM.author;
  }
  
  if (claudeFM.version) {
    opencodeFM.version = claudeFM.version;
  }
  
  return opencodeFM;
}

/**
 * Transform command body content
 */
export function transformCommandBody(body) {
  return body
    // Update directory references
    .replace(/\.claude\//g, '.opencode/')
    .replace(/~\/\.claude\//g, '~/.opencode/')
    
    // Update tool references
    .replace(/Task tool/g, 'agent tool')
    .replace(/Claude Code/g, 'OpenCode')
    .replace(/claude code/g, 'opencode')
    
    // Update command references
    .replace(/\$CLAUDE_/g, '$OPENCODE_')
    .replace(/claude\s+run/g, 'opencode run')
    .replace(/oc\s+run/g, 'opencode run') // Normalize to opencode
    
    // Update configuration references
    .replace(/CLAUDE\.md/g, 'OPENCODE.md')
    .replace(/\.claude_/g, '.opencode_');
}

/**
 * Build OpenCode YAML frontmatter string
 */
export function buildOpenCodeYAML(opencodeFM) {
  let yaml = '';
  
  // Required fields first
  if (opencodeFM.description) {
    yaml += `description: "${opencodeFM.description}"\n`;
  }
  
  if (opencodeFM.agent) {
    yaml += `agent: ${opencodeFM.agent}\n`;
  }
  
  // Optional fields
  if (opencodeFM.category) {
    yaml += `category: ${opencodeFM.category}\n`;
  }
  
  if (opencodeFM.author) {
    yaml += `author: ${opencodeFM.author}\n`;
  }
  
  if (opencodeFM.version) {
    yaml += `version: ${opencodeFM.version}\n`;
  }
  
  return yaml;
}

/**
 * Check if content is already in OpenCode format
 */
export function isOpenCodeFormat(content) {
  if (!content.includes('---')) {
    return false; // No frontmatter
  }
  
  const parts = content.split('---');
  if (parts.length < 3) {
    return false; // Invalid frontmatter
  }
  
  const frontmatter = parts[1];
  
  // Check for OpenCode characteristics (has agent or description, no allowed-tools)
  return (
    (frontmatter.includes('agent:') || frontmatter.includes('description:')) &&
    !frontmatter.includes('allowed-tools:') &&
    !frontmatter.includes('tools:')
  );
}

/**
 * Transform complete Claude command to OpenCode format
 */
export function transformCommand(content, options = {}) {
  const {
    returnOriginalOnError = true,
    enableLogging = true
  } = options;
  
  try {
    // Check if already OpenCode format
    if (isOpenCodeFormat(content)) {
      if (enableLogging) {
        console.log('[Command Transformer] Already OpenCode format, skipping transformation');
      }
      return content;
    }
    
    // Split frontmatter and body
    const parts = content.split('---');
    if (parts.length < 3) {
      if (enableLogging) {
        console.warn('[Command Transformer] Invalid command format - missing frontmatter');
      }
      return returnOriginalOnError ? content : null;
    }
    
    const frontmatterStr = parts[1];
    const body = parts.slice(2).join('---');
    
    // Parse Claude frontmatter
    const claudeFM = parseCommandYAML(frontmatterStr);
    
    // Transform to OpenCode format
    const opencodeFM = transformCommandFrontmatter(claudeFM);
    const transformedBody = transformCommandBody(body);
    
    // Build result
    const openCodeYAML = buildOpenCodeYAML(opencodeFM);
    const result = `---\n${openCodeYAML}---${transformedBody}`;
    
    if (enableLogging) {
      console.log('[Command Transformer] ✅ Successfully transformed command');
    }
    
    return result;
    
  } catch (error) {
    if (enableLogging) {
      console.error('[Command Transformer] ❌ Transform error:', error.message);
    }
    return returnOriginalOnError ? content : null;
  }
}

/**
 * Validate transformed command
 */
export function validateTransformedCommand(content) {
  try {
    if (!content.includes('---')) {
      return { valid: false, error: 'Missing frontmatter delimiters' };
    }
    
    const parts = content.split('---');
    if (parts.length < 3) {
      return { valid: false, error: 'Invalid frontmatter structure' };
    }
    
    const frontmatter = parts[1];
    
    // Check required fields
    if (!frontmatter.includes('description:')) {
      return { valid: false, error: 'Missing required description field' };
    }
    
    if (!frontmatter.includes('agent:')) {
      return { valid: false, error: 'Missing required agent field' };
    }
    
    // Check for Claude-specific fields (shouldn't be present)
    if (frontmatter.includes('allowed-tools:') || frontmatter.includes('tools:')) {
      return { valid: false, error: 'Contains Claude-specific fields' };
    }
    
    return { valid: true };
    
  } catch (error) {
    return { valid: false, error: error.message };
  }
}

/**
 * Get sample transformation for testing
 */
export function getSampleClaudeCommand() {
  return `---
title: "Test Command"
description: "A sample Claude command for testing"
allowed-tools: Read, Write, Bash, Grep
category: testing
---

This is a test command that uses Claude Code tools.

Use the Task tool to run complex operations.
Check .claude/ directory for configurations.
Run with: claude run "/test-command"
`;
}

/**
 * Get expected OpenCode output for sample
 */
export function getSampleOpenCodeCommand() {
  return `---
description: "Test Command"
agent: build
category: testing
---

This is a test command that uses OpenCode tools.

Use the agent tool to run complex operations.
Check .opencode/ directory for configurations.
Run with: opencode run "/test-command"
`;
}