# Pattern Templates Reference

Complete collection of common VTREE patterns with detailed examples.

## 1. Linear Pipeline

**Use for:** Sequential data processing, ETL workflows, transformation chains

```
[1]     Data Pipeline [📥 raw_data] → [📤 insights → (2)]
[1.1]   ├─ Clean [📥 raw ← (1)] → [🔄 cleaned → (1.2)]
[1.2]   ├─ Transform [📥 cleaned ← (1.1)] → [🔄 normalized → (1.3)]
[1.3]   └─ **Analyze** [📥 normalized ← (1.2)] → [📊 insights → (1)]
[2]     Storage [💾 insights ← (1)] → [✅ saved]
```

**Key characteristics:**
- Each step feeds into the next
- Clear data transformation flow
- Single path through the system
- Bold critical analysis step

## 2. Parallel Processing (Fan-out/Fan-in)

**Use for:** Distributed processing, parallel task execution, aggregation patterns

```
[1]     Request Router [📥 request] → [🎯 distribute → (2.1,2.2,2.3)]
[2.1]   ├─ **Service_A** [📥 task ← (1)] → [⚡ result_a → (3)]
[2.2]   ├─ Service_B [📥 task ← (1)] → [⚡ result_b → (3)]
[2.3]   └─ *Service_C* [⏳ task ← (1)] → [📤 result_c → (3)]
[3]     Aggregator [📥 results ← (2.1)+(2.2)+(2.3)] → [📤 combined]
```

**Key characteristics:**
- Single input fans out to multiple processors
- Parallel execution (note Service_C is async)
- Fan-in aggregation with multi-source input `← (2.1)+(2.2)+(2.3)`
- Service_A is critical path (bold)

## 3. Error Handling Flow

**Use for:** Resilient systems, retry logic, error recovery patterns

```
[1]     API Operation [📥 input] → [✅ success → (2) | ❌ error → (3)]
[2]     **Success_Path** [📥 data ← (1)] → [🔄 process → (4)]
[3]     Error_Handler [📥 error ← (1)] → [🔧 handle → (3.1,3.2)]
[3.1]   ├─ Retry_Logic [📥 context ← (3)] → [🔄 retry → (1)]
[3.2]   └─ Error_Log [📥 error ← (3)] → [💾 logged → (4)]
[4]     Response [📥 result ← (2)+(3.2)] → [📤 final]
```

**Key characteristics:**
- Conditional branching with `|` notation
- Retry loop back to source `→ (1)`
- Multiple error handling paths
- Final response aggregates both success and error paths
- Success path is critical (bold)

## 4. Async Operations

**Use for:** External API calls, background jobs, concurrent async tasks

```
[1]     Main_Process [📥 start] → [⚡ initiate → (2)]
[2]     *Fetch_Data* [⏳ await ← (1)] → [🌐 api_calls → (2.1,2.2)]
[2.1]   ├─ *Primary_API* [⏳ request ← (2)] → [📤 data_1 → (3)]
[2.2]   └─ *Backup_API* [⏳ request ← (2)] → [📤 data_2 → (3)]
[3]     Process_Results [📥 data ← (2.1)+(2.2)] → [⚡ computed → (4)]
[4]     Cache_Update [💾 results ← (3)] → [✅ cached → (5)]
[5]     Return [📥 final ← (4)] → [📤 response]
```

**Key characteristics:**
- All async nodes use italics
- Async indicator emoji ⏳
- External API calls 🌐
- Primary and backup API pattern
- Aggregation of async results

## 5. Multiagent System

**Use for:** AI agent orchestration, collaborative workflows, complex multi-role systems

```
[1]     **Orchestrator** [📥 user_request] → [🎯 distribute → (2.1,2.2,2.3)]
[2.1]   ├─ Research_Agent [📥 query ← (1)] → [📊 analysis → (3.1)]
[2.1.1] │  ├─ *Web_Search* [🌐 keywords ← (2.1)] → [📤 results → (2.1.2)]
[2.1.2] │  └─ Analyze [📊 raw ← (2.1.1)] → [🧠 insights → (2.1)]
[2.2]   ├─ Code_Agent [📥 spec ← (1)] → [💻 code → (3.2)]
[2.2.1] │  ├─ Plan [📥 requirements ← (2.2)] → [🏗️ design → (2.2.2)]
[2.2.2] │  └─ **Implement** [📥 design ← (2.2.1)] → [⚡ code → (2.2)]
[2.3]   └─ QA_Agent [📥 context ← (1)] → [✅ validated → (3.3)]
[3]     Aggregator [📥 inputs ← (2.1)+(2.2)+(2.3)] → [🔗 combined → (4)]
[3.1]   ├─ Merge_Data [📥 data ← (2.1)] → [📤 merged → (3)]
[3.2]   ├─ Merge_Code [📥 code ← (2.2)] → [📤 merged → (3)]
[3.3]   └─ Merge_QA [📥 validation ← (2.3)] → [📤 merged → (3)]
[4]     **Response** [📤 final ← (3)] → [🚀 delivered]
```

**Key characteristics:**
- Three-level hierarchy showing agent delegation
- Each agent has internal workflow
- External web search is async (italics)
- Critical paths: Orchestrator, Implement, Response (bold)
- Multi-agent aggregation pattern
- AI decision indicators 🧠

## 6. State Machine

**Use for:** State transitions, workflow states, lifecycle management

```
[1]     State_Machine [📥 event] → [🎯 transition → (2,3,4)]
[2]     Idle_State [📥 start ← (1)] → [⚡ activate → (3)]
[3]     **Active_State** [📥 work ← (2)] → [✅ complete → (4) | ❌ error → (5)]
[4]     Success_State [📥 result ← (3)] → [🚀 finalize → (6)]
[5]     Error_State [📥 error ← (3)] → [🔧 recover → (2,6)]
[6]     Final_State [📥 outcome ← (4)+(5)] → [📤 END]
```

**Key characteristics:**
- State machine transitions clearly shown
- Conditional state transitions
- Error recovery loop back to Idle `→ (2,6)`
- Active state is critical (bold)
- Terminal state with `→ END`
- Multiple paths converge at final state

## Pattern Selection Guide

| Your System Has... | Use Pattern |
|-------------------|-------------|
| Sequential steps, data transformation | **Linear Pipeline** |
| Parallel tasks, aggregation | **Parallel Processing** |
| Retry logic, error recovery | **Error Handling** |
| External APIs, concurrent calls | **Async Operations** |
| Multiple AI agents, delegation | **Multiagent System** |
| State transitions, lifecycle | **State Machine** |

## Combining Patterns

Many real systems combine multiple patterns:

**Example: Async + Error Handling**
```
[1]   API_Call [📥 request] → [🌐 external] → [✅ success → (2) | ❌ error → (3)]
[2]   Success [📥 data ← (1)] → [📤 result]
[3]   Error [❌ failed ← (1)] → [🔧 retry → (1) | 💾 log → (4)]
```

**Example: Multiagent + Parallel**
```
[1]     Orchestrator [📥 task] → [🎯 distribute → (2.1,2.2)]
[2.1]   ├─ Agent_A [📥 subtask ← (1)] → [🧠 result_a → (3)]
[2.2]   └─ Agent_B [📥 subtask ← (1)] → [🧠 result_b → (3)]
[3]     Combine [📥 results ← (2.1)+(2.2)] → [📤 final]
```

## Advanced Notation

**Recursive loops:**
```
[1] Processor [📥 input] → [🔄 process → (SELF) | ✅ done → (2)]
```

**Multi-target conditional:**
```
[1] Router [📥 request] → [🎯 route → (2) | (3) | (4)]
```

**Complex aggregation:**
```
[1] Aggregator [📥 data ← (A.1)+(A.2)+(B.1)+(B.2)] → [📤 combined]
```
