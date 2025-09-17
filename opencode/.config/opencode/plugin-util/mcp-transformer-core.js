/**
 * Shared MCP Transformation Logic
 * 
 * Core transformation functions for converting Claude MCP configurations
 * to OpenCode format. Ensures consistent behavior across all transformation contexts.
 */

/**
 * Transform a single Claude MCP server configuration to OpenCode format
 * @param {string} serverName - The name/key of the MCP server
 * @param {Object} claudeConfig - Claude MCP server configuration
 * @returns {Object} OpenCode MCP server configuration
 */
export function transformMcpServer(serverName, claudeConfig) {
  const openCodeConfig = {};
  
  // Handle command transformation: merge command + args into single array
  if (claudeConfig.command) {
    const command = [claudeConfig.command];
    if (claudeConfig.args && Array.isArray(claudeConfig.args)) {
      command.push(...claudeConfig.args);
    }
    openCodeConfig.command = command;
  }
  
  // Map type field
  if (claudeConfig.type) {
    // Map Claude types to OpenCode types
    switch (claudeConfig.type) {
      case 'stdio':
        openCodeConfig.type = 'local';
        break;
      case 'http':
      case 'remote':
        openCodeConfig.type = 'remote';
        // If there's a URL, add it
        if (claudeConfig.url) {
          openCodeConfig.url = claudeConfig.url;
        }
        break;
      default:
        openCodeConfig.type = 'local'; // Default fallback
    }
  } else {
    openCodeConfig.type = 'local'; // Default
  }
  
  // Always enable by default
  openCodeConfig.enabled = true;
  
  // Handle environment variables if present
  if (claudeConfig.env && Object.keys(claudeConfig.env).length > 0) {
    openCodeConfig.env = claudeConfig.env;
  }
  
  return openCodeConfig;
}

/**
 * Generate tool permissions for an MCP server
 * @param {string} serverName - The name/key of the MCP server
 * @returns {string} Tool permission pattern
 */
export function generateMcpToolPermission(serverName) {
  // Sanitize server name for tool permission (replace special chars with underscores)
  const sanitizedName = serverName.replace(/[^a-zA-Z0-9_]/g, '_');
  return `mcp__${sanitizedName}__*`;
}

/**
 * Transform complete Claude MCP configuration to OpenCode format
 * @param {Object} claudeMcpConfig - Full Claude .mcp.json content
 * @param {Object} options - Transformation options
 * @returns {Object} Object with 'mcp' and 'tools' sections for OpenCode
 */
export function transformMcpConfig(claudeMcpConfig, options = {}) {
  const {
    enableLogging = true,
    preserveDisabled = false,
    generateTools = true
  } = options;
  
  const result = {
    mcp: {},
    tools: {}
  };
  
  // Extract mcpServers from Claude config
  const mcpServers = claudeMcpConfig.mcpServers || {};
  
  if (enableLogging) {
    console.log(`[MCP Transformer] Processing ${Object.keys(mcpServers).length} MCP servers`);
  }
  
  // Transform each server
  for (const [serverName, serverConfig] of Object.entries(mcpServers)) {
    try {
      // Transform server configuration
      const transformedServer = transformMcpServer(serverName, serverConfig);
      result.mcp[serverName] = transformedServer;
      
      // Generate tool permissions if requested
      if (generateTools) {
        const toolPattern = generateMcpToolPermission(serverName);
        result.tools[toolPattern] = true;
      }
      
      if (enableLogging) {
        console.log(`[MCP Transformer] ✅ Transformed server: ${serverName}`);
      }
      
    } catch (error) {
      if (enableLogging) {
        console.error(`[MCP Transformer] ❌ Error transforming server ${serverName}:`, error.message);
      }
      
      // Continue with other servers even if one fails
      continue;
    }
  }
  
  return result;
}

/**
 * Merge transformed MCP config with existing OpenCode configuration
 * @param {Object} existingConfig - Current OpenCode configuration
 * @param {Object} transformedMcp - Transformed MCP configuration from transformMcpConfig
 * @param {Object} options - Merge options
 * @returns {Object} Merged OpenCode configuration
 */
export function mergeMcpConfig(existingConfig, transformedMcp, options = {}) {
  const {
    overwriteExisting = true,
    preserveExistingTools = true,
    enableLogging = true
  } = options;
  
  // Deep clone existing config to avoid mutations
  const merged = JSON.parse(JSON.stringify(existingConfig));
  
  // Ensure mcp and tools sections exist
  if (!merged.mcp) merged.mcp = {};
  if (!merged.tools) merged.tools = {};
  
  // Merge MCP servers
  for (const [serverName, serverConfig] of Object.entries(transformedMcp.mcp)) {
    if (merged.mcp[serverName] && !overwriteExisting) {
      if (enableLogging) {
        console.log(`[MCP Transformer] Skipping existing server: ${serverName}`);
      }
      continue;
    }
    
    merged.mcp[serverName] = serverConfig;
    if (enableLogging) {
      console.log(`[MCP Transformer] Added/updated server: ${serverName}`);
    }
  }
  
  // Merge tool permissions
  for (const [toolPattern, enabled] of Object.entries(transformedMcp.tools)) {
    if (merged.tools[toolPattern] !== undefined && preserveExistingTools) {
      if (enableLogging) {
        console.log(`[MCP Transformer] Preserving existing tool setting: ${toolPattern}`);
      }
      continue;
    }
    
    merged.tools[toolPattern] = enabled;
    if (enableLogging) {
      console.log(`[MCP Transformer] Added tool permission: ${toolPattern}`);
    }
  }
  
  return merged;
}

/**
 * Create metadata file content from Claude MCP configuration
 * This preserves description, purpose, scope fields that OpenCode doesn't use
 * @param {Object} claudeMcpConfig - Full Claude .mcp.json content
 * @returns {Object} Metadata object
 */
export function extractMcpMetadata(claudeMcpConfig) {
  const metadata = {
    generatedAt: new Date().toISOString(),
    sourceFormat: 'claude',
    servers: {}
  };
  
  const mcpServers = claudeMcpConfig.mcpServers || {};
  
  for (const [serverName, serverConfig] of Object.entries(mcpServers)) {
    const serverMetadata = {};
    
    // Extract metadata fields
    if (serverConfig.description) serverMetadata.description = serverConfig.description;
    if (serverConfig.purpose) serverMetadata.purpose = serverConfig.purpose;
    if (serverConfig.scope) serverMetadata.scope = serverConfig.scope;
    
    // Only add if there's actual metadata
    if (Object.keys(serverMetadata).length > 0) {
      metadata.servers[serverName] = serverMetadata;
    }
  }
  
  return metadata;
}

/**
 * Validate Claude MCP configuration
 * @param {Object} claudeMcpConfig - Claude MCP configuration to validate
 * @returns {Object} Validation result with success boolean and errors array
 */
export function validateClaudeMcpConfig(claudeMcpConfig) {
  const result = {
    success: true,
    errors: [],
    warnings: []
  };
  
  if (!claudeMcpConfig || typeof claudeMcpConfig !== 'object') {
    result.success = false;
    result.errors.push('Invalid MCP configuration: not an object');
    return result;
  }
  
  if (!claudeMcpConfig.mcpServers) {
    result.warnings.push('No mcpServers section found');
    return result;
  }
  
  const mcpServers = claudeMcpConfig.mcpServers;
  
  for (const [serverName, serverConfig] of Object.entries(mcpServers)) {
    if (!serverConfig.command) {
      result.errors.push(`Server ${serverName}: missing required 'command' field`);
      result.success = false;
    }
    
    if (serverConfig.type && !['stdio', 'http', 'remote'].includes(serverConfig.type)) {
      result.warnings.push(`Server ${serverName}: unknown type '${serverConfig.type}'`);
    }
    
    if (serverConfig.args && !Array.isArray(serverConfig.args)) {
      result.warnings.push(`Server ${serverName}: 'args' should be an array`);
    }
  }
  
  return result;
}

/**
 * Main transformation function that handles the complete process
 * @param {Object} claudeMcpConfig - Full Claude .mcp.json content
 * @param {Object} existingOpenCodeConfig - Current OpenCode configuration (optional)
 * @param {Object} options - Transformation options
 * @returns {Object} Complete result with config, metadata, and validation
 */
export function transformMcp(claudeMcpConfig, existingOpenCodeConfig = {}, options = {}) {
  const {
    enableLogging = true,
    validateInput = true,
    generateMetadata = true,
    ...transformOptions
  } = options;
  
  // Validate input if requested
  let validation = { success: true, errors: [], warnings: [] };
  if (validateInput) {
    validation = validateClaudeMcpConfig(claudeMcpConfig);
    if (!validation.success) {
      if (enableLogging) {
        console.error('[MCP Transformer] Validation failed:', validation.errors);
      }
      return { success: false, validation, config: null, metadata: null };
    }
  }
  
  try {
    // Transform the configuration
    const transformedMcp = transformMcpConfig(claudeMcpConfig, transformOptions);
    
    // Merge with existing configuration
    const mergedConfig = mergeMcpConfig(existingOpenCodeConfig, transformedMcp, transformOptions);
    
    // Generate metadata if requested
    let metadata = null;
    if (generateMetadata) {
      metadata = extractMcpMetadata(claudeMcpConfig);
    }
    
    return {
      success: true,
      validation,
      config: mergedConfig,
      metadata,
      transformedServers: Object.keys(transformedMcp.mcp),
      addedTools: Object.keys(transformedMcp.tools)
    };
    
  } catch (error) {
    if (enableLogging) {
      console.error('[MCP Transformer] Transformation failed:', error.message);
    }
    
    return {
      success: false,
      error: error.message,
      validation,
      config: null,
      metadata: null
    };
  }
}