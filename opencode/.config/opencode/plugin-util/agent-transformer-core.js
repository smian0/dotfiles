/**
 * Shared Agent Transformation Logic
 * 
 * Core transformation functions used by the plugin and test scripts.
 * Ensures consistent behavior across all transformation contexts.
 */

/**
 * Parse YAML frontmatter into object
 */
export function parseYAML(yamlStr) {
  const result = {};
  const lines = yamlStr.trim().split('\n');
  
  for (const line of lines) {
    if (line.includes(':')) {
      const [key, ...valueParts] = line.split(':');
      const value = valueParts.join(':').trim();
      
      // Skip tools field entirely - OpenCode handles tools differently
      if (key.trim() === 'tools') {
        continue;
      }
      
      result[key.trim()] = value;
    }
  }
  
  return result;
}

/**
 * Transform Claude frontmatter to OpenCode format
 */
export function transformFrontmatter(claudeFM) {
  // Extract clean description from first sentence, removing examples and markup
  let cleanDescription = 'Transformed agent';
  if (claudeFM.description) {
    cleanDescription = claudeFM.description
      .split('\n')[0]                           // Take first line
      .split('.')[0] + '.'                     // Take first sentence
      .replace(/<[^>]*>/g, '')                 // Remove HTML/XML tags
      .replace(/\s+/g, ' ')                    // Normalize whitespace
      .trim();
    
    // Fallback if description becomes too short
    if (cleanDescription.length < 20) {
      cleanDescription = claudeFM.name ? `${claudeFM.name} agent for specialized tasks` : 'Transformed agent';
    }
  }
  
  return {
    description: cleanDescription,
    mode: claudeFM.mode || 'all',
    model: 'zhipuai/glm-4.5'  // Use default OpenCode model
  };
}

/**
 * Convert object back to YAML string
 */
export function stringifyYAML(obj) {
  let result = '';
  
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'object' && !Array.isArray(value)) {
      result += `${key}:\n`;
      for (const [subKey, subValue] of Object.entries(value)) {
        result += `  ${subKey}: ${subValue}\n`;
      }
    } else if (Array.isArray(value)) {
      result += `${key}: [${value.join(', ')}]\n`;
    } else {
      result += `${key}: ${value}\n`;
    }
  }
  
  return result;
}

/**
 * Transform complete agent file from Claude to OpenCode format
 * @param {string} content - The agent file content to transform
 * @param {object} options - Transformation options
 * @param {boolean} options.returnOriginalOnError - Return original content on error instead of throwing
 * @param {boolean} options.enableLogging - Enable console logging
 * @param {string} options.logPrefix - Prefix for log messages
 */
export function transformAgent(content, options = {}) {
  const { returnOriginalOnError = false, enableLogging = false, logPrefix = '[Agent Transformer]' } = options;
  
  try {
    // Split frontmatter and body
    const parts = content.split('---');
    if (parts.length < 3) {
      const message = 'Invalid agent file format, missing frontmatter';
      if (enableLogging) {
        console.warn(`${logPrefix} ${message}`);
      }
      if (returnOriginalOnError) {
        return content;
      }
      throw new Error(message);
    }
    
    const frontmatterStr = parts[1];
    const body = parts.slice(2).join('---');
    
    // Parse and transform frontmatter
    const claudeFM = parseYAML(frontmatterStr);
    const opencodeFM = transformFrontmatter(claudeFM);
    
    // Transform body content
    const transformedBody = body
      .replace(/\.claude\//g, '.opencode/')
      .replace(/Task tool/g, 'agent tool')
      .replace(/Claude Code/g, 'OpenCode');
    
    // Reconstruct file
    const result = `---\n${stringifyYAML(opencodeFM)}---${transformedBody}`;
    
    if (enableLogging) {
      console.log(`${logPrefix} Transformed ${claudeFM.name || 'unknown'} agent`);
    }
    
    return result;
    
  } catch (error) {
    if (enableLogging) {
      console.error(`${logPrefix} Transform error:`, error);
    }
    if (returnOriginalOnError) {
      return content;
    }
    throw new Error(`Transform error: ${error.message}`);
  }
}