# Claude Code 2.0.0 Settings.json Changes

This document tracks the new and updated configuration options in the `settings.json` file for Claude Code 2.0.0.

## New Configuration Options

### API and Authentication Settings
- `apiKeyHelper`: Custom script to generate an authentication value
- `forceLoginMethod`: Restrict login to either `claudeai` or `console`
- `forceLoginOrgUUID`: Auto-select organization during login
- `awsAuthRefresh`: Custom script for AWS authentication
- `awsCredentialExport`: Script that outputs JSON with AWS credentials

### Privacy and Collaboration Settings
- `includeCoAuthoredBy`: Include `co-authored-by Claude` in commits (default: `true`)
- `cleanupPeriodDays`: Retention period for chat transcripts (default: 30 days)

### Hooks and Automation Settings
- `disableAllHooks`: Disable all hooks entirely
- `disableAllRules`: Disable all rules (new in 2.0.0)

### MCP Server Settings
- `enableAllProjectMcpServers`: Auto-approve all MCP servers in `.mcp.json`
- `enabledMcpjsonServers`: List of specific MCP servers to approve
- `disabledMcpjsonServers`: List of specific MCP servers to reject

### Model and Performance Settings
- `model`: Override default model selection
- `permissions`: Control tool access with allow/deny rules

### Environment Settings
- `env`: Set environment variables for sessions

## Example settings.json structure:
```json
{
  "apiKeyHelper": "custom-auth-script.sh",
  "cleanupPeriodDays": 15,
  "includeCoAuthoredBy": false,
  "disableAllHooks": false,
  "forceLoginMethod": "claudeai",
  "forceLoginOrgUUID": "your-org-uuid",
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["server1", "server2"],
  "disabledMcpjsonServers": ["problematic-server"],
  "model": "claude-3-5-sonnet",
  "permissions": {
    "allow": ["Read", "Write", "Bash"],
    "deny": ["WebSearch"]
  },
  "env": {
    "NODE_ENV": "development"
  }
}
```

## Notable Changes from Previous Versions

1. **Enhanced Security Controls**: New options like `forceLoginMethod` and `forceLoginOrgUUID` provide more granular control over authentication
2. **Improved Privacy Options**: `includeCoAuthoredBy` and `cleanupPeriodDays` give users more control over their data
3. **Better MCP Integration**: New server approval options allow for more secure MCP server management
4. **Flexible Authentication**: Support for custom authentication scripts with `apiKeyHelper`, `awsAuthRefresh`, and `awsCredentialExport`

## How to Use These Settings

1. **Global Settings**: Place in `~/.claude/settings.json` to apply to all projects
2. **Project Settings**: Place in `.claude/settings.json` within your project directory
3. **Local Overrides**: Place in `.claude/settings.local.json` for personal overrides (git-ignored)

Settings follow this precedence: 
Enterprise managed policies → Command line → Local project → Shared project → User settings

## Version History

- **2.0.0**: Initial release with all the above settings
- _Previous versions did not have these specific configuration options_

This document will be updated as new settings are added or existing ones are modified in future versions.