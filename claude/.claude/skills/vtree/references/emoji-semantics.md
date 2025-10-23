# Emoji Semantics Reference

Complete vocabulary of emojis for VTREE diagrams, organized by category.

## Input/Output Flow

| Emoji | Meaning | Usage |
|-------|---------|-------|
| 📥 | Receive/Input data | Node receives data from another source |
| 📤 | Send/Output data | Node sends data to another target |
| 🎯 | Target/Route/Direct | Routing or directing to specific destination |
| 🔗 | Chain/Link/Connect | Connecting or linking components |

**Examples:**
```
[1] API_Handler [📥 request] → [📤 response → (2)]
[2] Router [🎯 route ← (1)] → [🔗 connect → (3)]
```

## Processing Operations

| Emoji | Meaning | Usage |
|-------|---------|-------|
| 🔄 | Transform/Process/Convert | Data transformation or processing |
| ⚡ | Execute/Active/Run | Execution or active processing |
| 📊 | Analyze/Compute/Calculate | Analysis or computation |
| 💻 | Code/Implementation/Build | Code generation or building |
| 🧠 | Intelligence/Decision/AI | AI operations or decision-making |

**Examples:**
```
[1] Transformer [🔄 convert] → [📤 output]
[2] Executor [⚡ run] → [✅ done]
[3] Analyzer [📊 compute] → [📤 results]
[4] AI_Agent [🧠 decide] → [🎯 action]
```

## State Indicators

| Emoji | Meaning | Usage |
|-------|---------|-------|
| ⏳ | Pending/Async/Waiting | Asynchronous or waiting operations |
| ✅ | Success/Valid/Complete | Successful completion |
| ❌ | Error/Failed/Invalid | Error or failure state |
| 🔧 | Fix/Handle/Repair | Error handling or fixing |
| ⚠️ | Warning/Caution/Review | Warning or needs review |

**Examples:**
```
[1] *Async_Task* [⏳ waiting] → [✅ done → (2) | ❌ failed → (3)]
[2] Success_Handler [✅ result ← (1)]
[3] Error_Handler [❌ error ← (1)] → [🔧 fix → (1)]
[4] Validator [⚠️ check] → [✅ ok | ❌ invalid]
```

## Security & Data

| Emoji | Meaning | Usage |
|-------|---------|-------|
| 🔐 | Auth/Secure/Encrypt | Authentication or encryption |
| 🛡️ | Protect/Validate/Guard | Protection or validation |
| 💾 | Store/Persist/Save | Storage or persistence |
| 🌐 | External/Network/API | External services or APIs |
| 🚀 | Deploy/Finalize/Launch | Deployment or finalization |

**Examples:**
```
[1] Auth_Service [🔐 authenticate] → [✅ token → (2)]
[2] Validator [🛡️ validate ← (1)] → [✅ safe → (3)]
[3] Database [💾 save] → [✅ stored]
[4] *External_API* [🌐 fetch] → [📤 data]
[5] Deployer [🚀 launch] → [✅ live]
```

## Resource & Infrastructure

| Emoji | Meaning | Usage |
|-------|---------|-------|
| 💰 | Cost/Payment/Transaction | Financial or payment operations |
| 🏗️ | Build/Construct/Setup | Building or construction |
| 📡 | Communication/Broadcast | Communication or broadcasting |
| ⚙️ | Configure/Settings/Tune | Configuration or settings |

**Examples:**
```
[1] Payment_Gateway [💰 charge] → [✅ paid → (2)]
[2] Builder [🏗️ construct] → [📤 artifact]
[3] Broadcaster [📡 notify] → [📤 message → (all)]
[4] Config_Manager [⚙️ setup] → [✅ configured]
```

## Combination Patterns

### Multi-Operation Nodes
Combine emojis to show sequential operations within a node:

```
[1] API_Handler [📥 input] → [🔐 auth] → [🛡️ validate] → [📤 safe_data → (2)]
```

### Conditional States
Use state emojis to show branching:

```
[1] Processor [📥 data] → [✅ success → (2) | ❌ error → (3)]
```

### Async External Calls
Combine async and external indicators:

```
[1] *External_Service* [🌐 api_call] → [⏳ waiting] → [📤 result]
```

## Selection Guide

**Choose emojis based on primary operation:**

1. **Input/Output dominates?** → 📥/📤
2. **Transformation/processing?** → 🔄/⚡
3. **Decision/intelligence?** → 🧠
4. **State change?** → ✅/❌/⏳
5. **Security concern?** → 🔐/🛡️
6. **Storage operation?** → 💾
7. **External call?** → 🌐
8. **Final deployment?** → 🚀

**When in doubt:**
- Use 📥/📤 for clear input/output
- Use ⚡ for general execution
- Use 🔄 for transformations
