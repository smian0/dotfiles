# OpenCode ACP Analysis

## Summary

After investigating the opencode-acp adapter, I've determined that **ACP (Agent Client Protocol) is incompatible with Claude Code's MCP (Model Context Protocol)** architecture. While both use JSON-RPC over stdio, they serve fundamentally different purposes and cannot be bridged without significant custom development.

## Key Findings

### Protocol Differences

| Aspect | ACP (Agent Client Protocol) | MCP (Model Context Protocol) |
|--------|----------------------------|------------------------------|
| **Purpose** | Real-time editor-agent streaming | Tool/resource integration |
| **Pattern** | Long-running bidirectional streaming | Request/response with timeout |
| **Use Case** | Editor assistants (Zed, VS Code) | External tools and data sources |
| **Timeout** | No timeout (streaming) | 10-30 seconds typical |
| **State** | Persistent session per project | Stateless tool calls |

### Why opencode-acp Doesn't Work

1. **Protocol Mismatch**: ACP speaks a different JSON-RPC dialect than MCP
   - ACP: Session management, streaming updates, editor commands
   - MCP: Tool definitions, resource access, prompts

2. **Execution Model**: OpenCode via ACP expects:
   - Long-running server per project
   - Streaming text and reasoning updates
   - File/shell operations via permissions
   - Cancel/abort support

3. **Claude Code MCP Model**: Claude Code expects:
   - Stateless tool invocations
   - Quick request/response (< 30 seconds)
   - Synchronous results
   - No streaming updates

### OpenCode Performance Constraints

Testing revealed OpenCode's inherent performance characteristics:

- **First run**: 40-120 seconds (includes model loading, context building)
- **With `-T` flag**: 40-60 seconds (skips sync, still slow)
- **Persistent server**: `oc serve` exists but `oc run` doesn't connect to it
- **Session model**: Each `oc run` creates a new isolated session

## Attempted Solutions

### 1. ❌ Direct MCP Server (Failed)
**Approach**: Create FastMCP server wrapping `oc run`

**Result**: Timeout errors
```
MCP error -32001: Request timed out
```

**Why it failed**: OpenCode's 40+ second execution exceeds MCP's 10-30 second timeout

### 2. ❌ opencode-acp Adapter (Not Applicable)
**Approach**: Use opencode-acp adapter as MCP server

**Result**: Protocol incompatibility
- ACP adapter speaks ACP (agent streaming protocol)
- Claude Code speaks MCP (tool integration protocol)
- No way to bridge without major development

### 3. ✅ Agent-Based Delegation (Current Solution)
**Approach**: `@opencode-delegate` agent using direct `oc run` commands

**Result**: Works reliably, but slow
```bash
oc run -T --model "github-copilot/claude-sonnet-4" "task description"
```

**Pros**:
- ✅ Clean isolation between Claude Code and OpenCode contexts
- ✅ Reliable execution (no protocol issues)
- ✅ Full OpenCode capabilities available
- ✅ Well-documented patterns

**Cons**:
- ❌ 40-60 second execution time per task
- ❌ No streaming updates (user sees nothing until complete)
- ❌ No way to accelerate via persistent server

## Architecture Comparison

### ACP in Zed Editor
```
Zed UI ←→ opencode-acp ←→ OpenCode Server ←→ MCP Servers
         (ACP/stdio)       (HTTP/SSE)           (MCP/HTTP)
```

- Zed keeps opencode-acp running persistently
- opencode-acp spawns per-session OpenCode servers
- File/shell operations proxy back to Zed via ACP
- Streaming updates flow through SSE → ACP → Zed

### Current Claude Code Setup
```
Claude Code ←→ @opencode-delegate ←→ oc run (new session each time)
            (conversation)          (bash/stdio)
```

- Each delegation creates new OpenCode session
- No persistent connection
- Results returned after full completion
- Context isolation maintained

## Recommendations

### Best Approach: Continue Using @opencode-delegate Agent

The current agent-based approach is the most pragmatic solution:

1. **Works reliably** within Claude Code's architecture
2. **Maintains clean context isolation** (OpenCode doesn't see Claude history)
3. **Fully documented** with patterns and error handling
4. **No protocol bridging complexity**

### When to Use OpenCode Delegation

✅ **Good use cases**:
- Complex research requiring web search
- Alternative code generation approaches
- Tasks benefiting from fresh context
- Parallel processing of independent tasks
- Using OpenCode's specialized MCP servers

❌ **Poor use cases**:
- Quick queries (not worth 40-60 second wait)
- Tasks requiring conversation history
- Real-time iterative development
- Anything time-sensitive

### Performance Expectations

Users should understand:
- **Each OpenCode delegation takes 40-60 seconds minimum**
- This is inherent to OpenCode's design, not a configuration issue
- The `-T` flag helps but doesn't eliminate the delay
- No way to speed this up without OpenCode architecture changes

## Future Possibilities

If Anthropic/OpenCode adds:
1. **MCP-native mode**: OpenCode exposing tools via MCP protocol
2. **Persistent server with instant sessions**: `oc run` connecting to `oc serve`
3. **Streaming MCP support**: MCP protocol extension for streaming
4. **Session reuse**: Warm sessions for faster repeated calls

Then faster integration would become possible. Until then, the agent-based approach remains optimal.

## References

- opencode-acp: https://github.com/josephschmitt/opencode-acp
- Agent implementation: `claude/.claude/agents/opencode-delegate.md`
- Quick reference: `docs/OPENCODE_DELEGATE_QUICK.md`
- Full documentation: `docs/OPENCODE_AS_SUBAGENT.md`

---
**Last Updated**: 2025-10-23
**Conclusion**: ACP approach not viable; continue with `@opencode-delegate` agent
