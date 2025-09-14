# Claude Code Configuration Reference

This document contains commonly tweaked Claude Code environment variables and configuration options based on community discussions and official documentation (2025).

## Current Configuration Status

✅ **Already Configured:**
- `BASH_DEFAULT_TIMEOUT_MS`: "300000" (5 minutes)
- `BASH_MAX_TIMEOUT_MS`: "1200000" (20 minutes)

## Environment Variables Reference

### Core Output & Performance Settings

```json
"env": {
  "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "16384",        // Max output tokens (8192-32000)
  "BASH_MAX_OUTPUT_LENGTH": "20000",               // Max bash output chars before truncation
  "BASH_DEFAULT_TIMEOUT_MS": "300000",             // Default bash timeout (5 minutes) ✅
  "BASH_MAX_TIMEOUT_MS": "1200000"                 // Max bash timeout (20 minutes) ✅
}
```

### API & Authentication Settings

```json
"env": {
  "CLAUDE_CODE_API_KEY_HELPER_TTL_MS": "600000",   // API key refresh interval (10 minutes)
  "MCP_TIMEOUT": "30000",                          // MCP server startup timeout (30 seconds)
  "ANTHROPIC_API_KEY": "your-api-key-here"         // Direct API key (not recommended)
}
```

### Privacy & Telemetry Settings

```json
"env": {
  "DISABLE_TELEMETRY": "true",                     // Opt out of usage tracking
  "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "true"  // Disable telemetry, updates, etc.
}
```

### Network Settings

```json
"env": {
  "HTTP_PROXY": "http://proxy.example.com:8080",   // Network proxy settings
  "HTTPS_PROXY": "https://proxy.example.com:8080"
}
```

## Common Configuration Profiles

### High-Performance Setup
For users working with large codebases or long-running tasks:

```json
"env": {
  "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "32000",
  "BASH_MAX_OUTPUT_LENGTH": "50000",
  "BASH_DEFAULT_TIMEOUT_MS": "1800000",           // 30 minutes
  "BASH_MAX_TIMEOUT_MS": "7200000",               // 120 minutes
  "MCP_TIMEOUT": "60000"                          // 60 seconds
}
```

### Privacy-Focused Setup
For users who prefer minimal data collection:

```json
"env": {
  "DISABLE_TELEMETRY": "true",
  "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "true",
  "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "16384",
  "BASH_MAX_OUTPUT_LENGTH": "30000"
}
```

### Balanced Setup (Recommended)
Good middle ground for most users:

```json
"env": {
  "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "16384",
  "BASH_MAX_OUTPUT_LENGTH": "20000",
  "BASH_DEFAULT_TIMEOUT_MS": "300000",            // 5 minutes (current)
  "BASH_MAX_TIMEOUT_MS": "1200000",               // 20 minutes (current)
  "CLAUDE_CODE_API_KEY_HELPER_TTL_MS": "600000",
  "MCP_TIMEOUT": "30000"
}
```

## Configuration Guidelines

### Timeout Values
- **2-5 minutes**: Good for general development
- **30+ minutes**: Better for CI/CD, large builds, or data processing
- **120+ minutes**: For very long-running tasks (use sparingly)

### Output Token Limits
- **8192**: Conservative, faster responses
- **16384**: Good balance (recommended)
- **32000**: Maximum for most models (check model limits)

### Output Length Limits
- **20000**: Default, good for most cases
- **50000+**: For viewing large files or command outputs
- **100000+**: Only if you frequently need to see very large outputs

## Known Issues & Workarounds

### CLAUDE_CODE_MAX_OUTPUT_TOKENS Bug
- **Issue**: Some versions incorrectly enforce 32k limit for all models
- **Workaround**: Use values ≤32000 even for models that support more
- **Status**: Reported in GitHub issues #4510, #4255

### MCP Timeout Issues
- **Issue**: MCP servers may timeout during startup
- **Solution**: Increase `MCP_TIMEOUT` to 30000-60000ms
- **Status**: GitHub issue #424

### Bash Timeout Not Working
- **Issue**: Environment variables not taking effect
- **Solution**: Full Claude Code restart required
- **Verification**: Test with `sleep` command longer than old timeout

## Configuration File Locations

### User-Level (Global)
```
~/.claude/settings.json
```

### Project-Level (Shared)
```
.claude/settings.json
```

### Project-Level (Personal)
```
.claude/settings.local.json
```

## Testing Your Configuration

### Test Timeout Settings
```bash
# Test 3-minute timeout (should work with current 5-minute setting)
sleep 180 && echo "Timeout test passed"
```

### Test Output Length
```bash
# Generate large output to test BASH_MAX_OUTPUT_LENGTH
seq 1 1000
```

### Validate JSON Syntax
```bash
jq . ~/.claude/settings.json
```

## Community Recommendations

Based on 2025 GitHub discussions and user reports:

1. **Most users set timeouts to 15-30 minutes** for development work
2. **16384 tokens** is the sweet spot for output limits
3. **Privacy settings** are increasingly popular
4. **MCP_TIMEOUT** is essential if using browser automation or other MCP servers
5. **Full restart required** for all environment variable changes

## Additional Resources

- [Official Claude Code Settings Documentation](https://docs.anthropic.com/en/docs/claude-code/settings)
- [GitHub Issue #5615: Complete Timeout Configuration Guide](https://github.com/anthropics/claude-code/issues/5615)
- [Community Configuration Examples](https://claudelog.com/configuration/)

---

*Last Updated: September 2025*
*Current Status: Timeout settings configured and tested ✅*