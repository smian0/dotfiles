# OpenCode Automatic Rate Limit Fallback System

## Overview

Research and implementation plan for automatically detecting rate limits in OpenCode and falling back to alternative models without manual intervention.

## Research Summary

### OpenCode Plugin System

OpenCode supports a plugin system that allows hooking into various events:

- **`tool.execute.before`** - Runs before any tool is executed, can intercept and modify behavior
- **`tool.execute.after`** - Runs after tool execution (limited error handling capabilities)
- **Plugin Structure**: JavaScript modules that export hook functions

### Rate Limit Detection Patterns

From Anthropic/Claude API documentation and OpenCode issues:

1. **Error Patterns to Detect**:
   - `{"type": "rate_limit_error", "message": "..."}`
   - `{"type": "overloaded_error", "message": "Overloaded"}`
   - HTTP 429 status codes
   - `Retry-After` headers indicating wait time

2. **Exponential Backoff Strategy**:
   - Start with 1 second delay
   - Double wait time: 1s → 2s → 4s → 8s
   - Add jitter to avoid synchronized retries
   - Honor `Retry-After` headers when available

### Current OpenCode Limitations

- No built-in automatic retry for rate limits
- Manual agent switching required: `oc run --agent claude-fallback "prompt"`
- Plugin hooks don't currently support tool execution error handling
- Limited error handling hooks (feature request exists for `OnToolError`)

## Implementation Approaches

### Approach 1: Plugin-Based Hook System

**File**: `~/.config/opencode/plugin/rate-limit-fallback.js`

**Strategy**:
- Hook into `tool.execute.before` to intercept commands
- Parse OpenCode logs for rate limit errors
- Maintain session state for retry logic
- Automatically switch to fallback agents

**Limitations**:
- Current plugin system doesn't provide robust error handling hooks
- Would need to monitor log files or output streams

### Approach 2: Wrapper Script with Log Monitoring

**File**: `/Users/smian/dotfiles/bin/oc-smart`

**Strategy**:
- Wrap the `oc` command with bash script
- Monitor OpenCode output/logs for rate limit patterns
- Automatically retry with fallback agent on detection
- Preserve original command arguments and context

**Benefits**:
- Works with current OpenCode version
- No dependency on plugin system limitations
- Can implement full retry logic with exponential backoff

### Approach 3: Pre-Launch Transform Enhancement

**File**: `/Users/smian/dotfiles/opencode/.config/opencode/scripts/rate-limit-monitor.js`

**Strategy**:
- Enhance existing pre-launch transform system
- Add runtime monitoring capabilities
- Integrate with the existing plugin infrastructure

## Current Configuration

### Model Mappings

Primary models and their fallback alternatives:

```json
{
  "claude-primary": "github-copilot/claude-sonnet-4",
  "claude-fallback": "zhipuai/glm-4.5",
  "gpt-oss-120": "ollamat/gpt-oss:120b",
  "qwen3-coder": "ollamat/qwen3-coder:480b",
  "small_model": "ollamat/gpt-oss:120b"
}
```

### Fallback Chain Strategy

1. **Primary**: `github-copilot/claude-sonnet-4`
   - **Fallback**: `zhipuai/glm-4.5`
   - **Reason**: GLM 4.5 via ZhipuAI has different rate limits

2. **Alternative Chain**: Local models for unlimited usage
   - `ollamat/gpt-oss:120b` → `ollamat/qwen3-coder:480b`

## Implementation Plan

### Phase 1: Wrapper Script Approach

1. **Create `oc-smart` wrapper script**:
   - Parse `oc` command arguments
   - Execute with primary agent
   - Monitor output for rate limit patterns
   - Retry with fallback agent on detection

2. **Add rate limit detection patterns**:
   - Parse JSON error responses
   - Detect HTTP 429 status codes
   - Extract `Retry-After` header values

3. **Implement exponential backoff**:
   - Track retry attempts
   - Calculate backoff delays
   - Add jitter to prevent synchronized retries

### Phase 2: Integration with Existing System

1. **Update `oc` script**:
   - Modify `/Users/smian/dotfiles/bin/oc` to use smart wrapper
   - Preserve all existing functionality
   - Add fallback configuration

2. **Create configuration file**:
   - Define primary → fallback model mappings
   - Set retry limits and backoff parameters
   - Allow per-model configuration

### Phase 3: Plugin Enhancement (Future)

When OpenCode adds better error handling hooks:

1. **Migrate to plugin system**
2. **Add real-time monitoring**
3. **Integrate with OpenCode's internal retry mechanisms**

## Configuration Schema

```json
{
  "rateLimit": {
    "maxRetries": 3,
    "baseDelay": 1000,
    "maxDelay": 30000,
    "jitterRange": 0.1,
    "fallbackChain": {
      "github-copilot/claude-sonnet-4": "zhipuai/glm-4.5",
      "ollamat/gpt-oss:120b": "ollamat/qwen3-coder:480b"
    },
    "errorPatterns": [
      "rate_limit_error",
      "overloaded_error",
      "429"
    ]
  }
}
```

## Files to Create/Modify

1. **New Files**:
   - `/Users/smian/dotfiles/bin/oc-smart` - Wrapper script
   - `/Users/smian/dotfiles/opencode/.config/opencode/rate-limit-config.json` - Configuration
   - `~/.config/opencode/plugin/rate-limit-fallback.js` - Future plugin

2. **Modified Files**:
   - `/Users/smian/dotfiles/bin/oc` - Update to use smart wrapper
   - `/Users/smian/dotfiles/opencode/.config/opencode/opencode.json` - Add plugin config

## Benefits

1. **Automatic Recovery**: No manual intervention needed when rate limits hit
2. **Transparent Operation**: Existing workflows continue to work
3. **Configurable**: Easy to adjust retry logic and fallback chains
4. **Cost Optimization**: Automatically use cheaper models when primary is unavailable
5. **Improved Reliability**: Reduces failed operations due to rate limits

## Future Enhancements

1. **Model Load Balancing**: Distribute requests across multiple API keys/providers
2. **Predictive Fallback**: Switch before hitting rate limits based on usage patterns
3. **Context Preservation**: Maintain conversation context across model switches
4. **Performance Monitoring**: Track fallback success rates and response times

## References

- [OpenCode Plugin Documentation](https://opencode.ai/docs/plugins/)
- [Anthropic Rate Limits](https://docs.claude.com/en/api/rate-limits)
- [OpenCode GitHub Issues - Rate Limit Handling](https://github.com/sst/opencode/issues/833)
- [Current OpenCode Configuration](/Users/smian/dotfiles/opencode/.config/opencode/opencode.json)

---

**Status**: Research Complete - Ready for Implementation
**Priority**: Medium
**Estimated Implementation Time**: 2-4 hours
**Dependencies**: None (uses existing infrastructure)