# Claude Agent SDK Workflow Debug Tree Analysis

## Overview
Analysis of the enhanced workflow tree visualizer to identify captured data vs missing data for workflow debugging.

## ✅ Data Successfully Captured

### 1. Tool Execution Metadata
- **Tool Name**: Captured via `tool_name` field (e.g., "TodoWrite", "Task", "WebSearch")
- **Tool ID**: Unique identifier for each tool invocation (e.g., "toolu_0143osakVUjpgWy5YB3ugHjr")
- **Timestamp**: Execution start time with millisecond precision (e.g., "18:01:08.042")
- **Duration**: Execution time in seconds (e.g., "0.076s")

### 2. Complete Input Data Structure
Successfully captures ALL input data passed to each tool:
```json
{
  "session_id": "...",
  "transcript_path": "...",
  "cwd": "...",
  "permission_mode": "acceptEdits",
  "hook_event_name": "PreToolUse",
  "tool_name": "TodoWrite",
  "tool_input": {
    "todos": [
      {
        "content": "Research Python programming language comprehensively",
        "status": "in_progress",
        "activeForm": "Researching Python programming language comprehensively"
      }
    ]
  }
}
```

**Key strengths:**
- Complete `tool_input` object with all parameters
- Session and environment context (session_id, cwd, transcript_path)
- Permission mode and hook event metadata

### 3. Context Data
Captures the context dictionary passed to hooks:
```json
{
  "signal": null
}
```

**Available context keys:**
- `signal` - Signal for cancellation/interruption

### 4. Output Data Structure
Captures complete tool response data:
```json
{
  "tool_response": {
    "oldTodos": [],
    "newTodos": [...]
  }
}
```

### 5. Visual Presentation
- **Syntax Highlighting**: JSON with monokai color scheme
- **Tree Structure**: Hierarchical display of tool calls
- **Metrics Table**: Aggregated statistics per tool type

---

## ❌ Data NOT Captured (Potential Gaps)

### 1. **Sub-Agent Delegation Tracking**
**Issue**: When using `Task` tool to delegate to sub-agents, we don't see:
- Which sub-agent was invoked (e.g., @technical-analyst, @business-analyst)
- Sub-agent execution tree (nested tool calls within sub-agent)
- Sub-agent return values/outputs

**Example Missing Data**:
```
Task Tool Input:
  - subagent_type: "general-purpose"
  - prompt: "Research Python..."

MISSING:
  - Sub-agent's internal tool calls (WebSearch, Read, etc.)
  - Sub-agent's intermediate results
  - Sub-agent's final response text
```

**Impact**: Cannot trace workflow execution through delegation boundaries.

### 2. **Agent-to-Agent Communication**
**Issue**: No visibility into:
- Messages passed between parent and sub-agents
- Return values from delegated tasks
- How sub-agent outputs are used in parent agent

**Example**:
```
Parent Agent -> Task(delegate to @technical-analyst)
  -> @technical-analyst executes...
    -> [BLACK BOX - no visibility]
  <- Returns result
Parent Agent continues with result
```

### 3. **Tool Call Results/Outputs**
**Issue**: While we capture `tool_response` in output_data, we don't capture:
- The actual text/data returned by tools in a human-readable format
- Large responses are truncated in logs but not made accessible in visualizer
- No way to see the "content" that was generated

**Example with Task tool**:
```
Captured:
  - tool_name: "Task"
  - tool_input: {...}

MISSING:
  - The actual text response from the sub-agent
  - Any files created/modified during delegation
  - Error messages or failures
```

### 4. **Multi-Turn Interactions**
**Issue**: Cannot see:
- Back-and-forth exchanges in agent conversations
- User prompts that triggered specific tool calls
- Assistant responses between tool calls

**Example**:
```
User: "Research Python vs JavaScript"
Assistant: "I'll research both..." [NOT LOGGED]
  -> Tool: TodoWrite
  -> Tool: Task (Python research)
    -> [Sub-agent work - NOT VISIBLE]
  -> Tool: Task (JavaScript research)
    -> [Sub-agent work - NOT VISIBLE]
Assistant: "Here's the comparison..." [NOT LOGGED]
```

### 5. **Workflow State Transitions**
**Issue**: No visibility into:
- Why specific tools were called (decision logic)
- State of the workflow between tool calls
- Variables or context maintained across tool calls
- Control flow decisions

### 6. **Error Handling & Failures**
**Issue**: Limited information about:
- Failed tool calls (no PostToolUse hook fired)
- Exception details
- Retry attempts
- Fallback strategies

### 7. **Parallel Execution**
**Issue**: Cannot determine:
- Which tool calls ran in parallel vs sequential
- Parallel execution timing/overlaps
- Dependencies between parallel tasks
- Race conditions or synchronization

**Example**:
```
Expected visualization for parallel workflow:
├── Task(technical-analyst) -----> [running simultaneously]
└── Task(business-analyst)  -----> [running simultaneously]

Current: Shows them sequentially with no indication of parallelism
```

### 8. **Resource Usage**
**Missing metrics**:
- Token consumption per tool/agent
- API costs
- Memory usage
- Network requests

### 9. **Causality & Dependencies**
**Issue**: Cannot see:
- Why a specific tool was called
- What triggered the decision to use this tool
- Input data provenance (where did these values come from?)
- Output data consumers (what uses this tool's result?)

---

## 🔍 Specific Limitations Discovered

### Problem 1: "unknown" Tool Names
Many tool calls show `tool_name: "unknown"` instead of the actual tool name.

**Root Cause**: The `context.get('tool_name')` in PreToolUse hook may not have the correct tool name populated.

**Solution**: Need to extract tool name from `tool_input` or use a different context field.

### Problem 2: No Nested Tree for Sub-Agents
When the main workflow calls a sub-agent via `Task` tool:
- Main workflow logs show: `Task` tool call with prompt
- Sub-agent execution is completely invisible
- Cannot see sub-agent's internal tool calls

**Impact**: Debugging multi-agent workflows is difficult.

**Solution**: Need sub-agent hooks or transcript parsing to reconstruct nested execution.

### Problem 3: Large Output Truncation
Output data can be very large (especially for web searches, file reads).
- Current: Logs are truncated to 1000 chars
- Visualizer: Shows truncated data with no way to expand

**Solution**:
- Add option to save full outputs to separate files
- Add "expand" option in visualizer to show full data

---

## 📊 Comparison with Agno Workflow Debugger

| Feature | Our Implementation | Agno | Gap |
|---------|-------------------|------|-----|
| Tool input data | ✅ Complete | ✅ | None |
| Tool output data | ⚠️ Truncated | ✅ | Output expansion |
| Context/state | ⚠️ Limited | ✅ | State tracking |
| Sub-agent visibility | ❌ None | ✅ | Nested execution |
| Timing/metrics | ✅ Basic | ✅ Advanced | Resource metrics |
| Parallel execution | ❌ Not shown | ✅ | Concurrency viz |
| Error handling | ⚠️ Partial | ✅ | Error details |
| Causality graph | ❌ None | ✅ | Dependencies |

---

## 💡 Recommendations for Improvement

### Priority 1: Sub-Agent Visibility
**Goal**: See nested tool calls within delegated sub-agents

**Approach**:
1. Parse transcript files to reconstruct sub-agent execution
2. Add nested tree nodes for sub-agent tool calls
3. Show parent → child delegation with visual indentation

### Priority 2: Tool Name Resolution
**Goal**: Always show correct tool name (not "unknown")

**Approach**:
1. Extract tool name from tool_use_id or input_data
2. Add fallback logic in hook to resolve tool name

### Priority 3: Output Data Expansion
**Goal**: Make full output data accessible

**Approach**:
1. Save full output to separate JSON files
2. Add "show full output" option in visualizer
3. Smart truncation with expandable sections

### Priority 4: Parallel Execution Visualization
**Goal**: Show which tasks ran concurrently

**Approach**:
1. Track tool call start/end times
2. Detect overlapping time ranges
3. Visualize with timeline or Gantt chart

### Priority 5: Workflow State Tracking
**Goal**: Show state/variables between tool calls

**Approach**:
1. Add custom state logging in workflows
2. Capture state snapshots in hooks
3. Display state changes in tree

---

## 🎯 Next Steps

1. **Fix "unknown" tool name** - Immediate fix for better readability
2. **Add sub-agent transcript parsing** - Enable nested visualization
3. **Implement output expansion** - Allow viewing full tool responses
4. **Add parallel execution detection** - Show timing overlaps
5. **Create workflow state hooks** - Track variables/state across tool calls

---

## Example: Ideal Enhanced Visualization

```
🌳 Parallel Research Workflow
├── 1. 🔧 TodoWrite @ 18:01:08.042 ⏱️ 0.076s
│   ├── 📥 INPUT: {"todos": [...]}
│   ├── 📤 OUTPUT: {"newTodos": [...]}
│   └── 📊 State: todos=[3 pending]
│
├── 2. 🔧 Task (delegate to @technical-analyst) @ 18:01:12.652 ⏱️ 45.3s [PARALLEL]
│   ├── 📥 INPUT: {"prompt": "Research technical aspects...", "subagent_type": "technical-analyst"}
│   ├── 🤖 Sub-Agent Execution (@technical-analyst):
│   │   ├── 1. WebSearch("Python performance benchmarks") ⏱️ 2.1s
│   │   │   └── 📤 Found 10 results
│   │   ├── 2. WebFetch("python.org/performance") ⏱️ 1.8s
│   │   │   └── 📤 Extracted 2500 words
│   │   ├── 3. TodoWrite (mark research complete) ⏱️ 0.05s
│   │   └── 4. Response: "Technical analysis: ..." (1200 words)
│   └── 📤 OUTPUT: {"text": "Technical analysis...", "sources": [...]}
│
├── 3. 🔧 Task (delegate to @business-analyst) @ 18:01:12.789 ⏱️ 42.1s [PARALLEL]
│   ├── 📥 INPUT: {"prompt": "Research business aspects...", "subagent_type": "business-analyst"}
│   ├── 🤖 Sub-Agent Execution (@business-analyst):
│   │   ├── 1. WebSearch("Python market share") ⏱️ 1.9s
│   │   ├── 2. WebSearch("Python enterprise adoption") ⏱️ 2.3s
│   │   ├── 3. TodoWrite (mark research complete) ⏱️ 0.04s
│   │   └── 4. Response: "Business analysis: ..." (1100 words)
│   └── 📤 OUTPUT: {"text": "Business analysis...", "sources": [...]}
│
└── 4. 🔧 Write (synthesis report) @ 18:01:58.156 ⏱️ 0.12s
    ├── 📥 INPUT: {"file_path": "report.md", "content": "..."}
    ├── 📤 OUTPUT: {"success": true}
    └── 📊 State: report_generated=true

⏱️ Total Time: 45.5s (2 parallel tasks saved ~42s)
📊 Tool Calls: 9 total (2 parent + 7 nested)
💰 Token Usage: 15,234 tokens (~$0.23)
```

This would provide complete visibility into multi-agent workflow execution.
