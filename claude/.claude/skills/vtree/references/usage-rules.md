# Usage Rules Reference

Detailed rules for creating well-formed VTREE diagrams.

## Structural Rules

### Tree Connection Characters

Use ASCII box-drawing characters for tree structure:

```
├─  Branch continues (more siblings below)
│   Vertical line (continuation)
└─  Last branch (no more siblings)
```

**Examples:**
```
[1]   Root
├─ First_Child     # More siblings below
├─ Second_Child    # More siblings below
└─ Last_Child      # No more siblings
```

**Multi-level:**
```
[1]     Root
[1.1]   ├─ Parent
[1.1.1] │  ├─ Child_A
[1.1.2] │  └─ Child_B
[1.2]   └─ Parent_B
```

### Indentation Standards

**Use 3-7 spaces per indentation level** for readability:

```
# Good: 4 spaces per level
[1]    Root
[1.1]  ├─ Child
[1.2]  └─ Child

# Also good: 7 spaces for complex diagrams
[1]       Root
[1.1]     ├─ Child
[1.1.1]   │  └─ Grandchild
```

**Consistency is key**: Pick one spacing and stick with it throughout the diagram.

### Node ID Hierarchical Numbering

Node IDs follow hierarchical structure:

```
[1]       Top-level node 1
[1.1]     First child of 1
[1.1.1]   First child of 1.1
[1.1.2]   Second child of 1.1
[1.2]     Second child of 1
[2]       Top-level node 2
[2.1]     First child of 2
```

**Rules:**
- Start at `[1]` for first top-level node
- Increment for siblings: `[1]`, `[2]`, `[3]`
- Add level for children: `[1.1]`, `[1.2]`, `[1.3]`
- Continue for deeper levels: `[1.1.1]`, `[1.1.2]`

### Line Length

**Keep lines under 120 characters when possible** for terminal compatibility.

If a line is too long, break it:

```
# Too long:
[1] Very_Long_Operation [📥 extremely_long_input_parameter_name ← (upstream)] → [📤 equally_long_output_parameter → (downstream)]

# Better:
[1] Very_Long_Operation [📥 long_input ← (upstream)]
    → [📤 long_output → (downstream)]
```

## Semantic Rules

### Emoji Selection

**Choose emojis based on the primary operation type:**

1. **What does this node DO?** → Select operation emoji
2. **What's the state?** → Add state emoji if needed
3. **Is it special?** → Consider security/async indicators

**Priority order:**
1. State indicators (✅/❌/⏳) for status-critical nodes
2. Operation type (🔄/⚡/🧠) for processing nodes
3. Input/output (📥/📤) for data flow nodes
4. Special concerns (🔐/🌐/💾) for security/external/storage

### Text Styling Application

Apply markdown-style formatting within node names:

**Normal text** = Required, synchronous, internal operations
```
[1] Standard_Process [⚡ execute] → [📤 result]
```

***Italics*** = Optional, async, external, or abstract elements
```
[1] *Optional_Step* [⏳ await] → [📤 result]
[2] *External_API* [🌐 fetch] → [📤 data]
```

**Bold** = Critical path or high-priority operations
```
[1] **Critical_Auth** [🔐 validate] → [✅ token]
```

~~Strikethrough~~ = Deprecated or to-be-removed nodes
```
[1] ~~Legacy_Handler~~ [⚡ old_way] → [📤 deprecated]
```

### When to Apply Styling

**Use italics for:**
- Async operations that don't block the main flow
- External API calls or third-party services
- Optional steps in a workflow
- Abstract interfaces or contracts

**Use bold for:**
- Critical path operations (must succeed for system to work)
- Main processing steps in a pipeline
- Essential security or validation steps
- Primary entry/exit points

**Use normal text for:**
- Standard synchronous operations
- Internal processing
- Regular workflow steps
- Non-critical operations

## Flow Rules

### Explicit Connection Notation

**All connections must be explicit** using node ID references.

**Basic flow:**
```
[1] Source → [📤 data → (2)]      # Sends to node 2
[2] Target [📥 data ← (1)]         # Receives from node 1
```

### Multiple Input Notation

Use `+` to combine multiple inputs:

```
[3] Combiner [📥 data ← (1)+(2)] → [📤 merged]
```

**Multi-line for readability:**
```
[5] Aggregator [📥 inputs ← (2.1)+(2.2)+(2.3)+(2.4)]
    → [📤 combined → (6)]
```

### Multiple Output Notation

Use commas to show multiple outputs:

```
[1] Router [📥 input] → [🎯 route → (2,3,4)]
```

**Means:** Node 1 sends output to nodes 2, 3, and 4 simultaneously.

### Conditional Flow Notation

Use pipe `|` for conditional branching:

```
[1] Validator [📥 input] → [✅ valid → (2) | ❌ invalid → (3)]
```

**Complex conditionals:**
```
[1] Router [📥 request]
    → [🎯 type_a → (2.1) | type_b → (2.2) | type_c → (2.3)]
```

### Special Flow Patterns

**Recursive/Retry loops** - use `→ (SELF)`:
```
[1] Retry_Handler [📥 task]
    → [✅ success → (2) | ❌ retry → (SELF)]
```

**Terminal outputs** - use `→ (END)`:
```
[5] Final_Step [📥 result] → [🚀 deployed → (END)]
```

**Broadcast/All** - use `→ (ALL)`:
```
[1] Notifier [📥 event] → [📡 broadcast → (ALL)]
```

## Alignment and Visual Clarity

### Vertical Alignment

Align similar elements for readability:

```
# Good alignment
[1]     Router        [📥 request]       → [🎯 route → (2.1,2.2)]
[2.1]   ├─ Service_A  [📥 task ← (1)]    → [⚡ result_a → (3)]
[2.2]   └─ Service_B  [📥 task ← (1)]    → [⚡ result_b → (3)]
[3]     Aggregator    [📥 data ← (2.1)+(2.2)] → [📤 combined]

# Poor alignment (harder to read)
[1] Router [📥 request] → [🎯 route → (2.1,2.2)]
[2.1] ├─ Service_A [📥 task ← (1)] → [⚡ result_a → (3)]
[2.2] └─ Service_B [📥 task ← (1)] → [⚡ result_b → (3)]
[3] Aggregator [📥 data ← (2.1)+(2.2)] → [📤 combined]
```

### Grouping Related Nodes

Use blank lines to separate logical groups:

```
[1]   Entry_Point [📥 start] → [⚡ begin → (2)]

[2]   Process_Group [📥 data ← (1)] → [🔄 process → (3)]
[2.1] ├─ Step_A [🔄 transform]
[2.2] └─ Step_B [🔄 transform]

[3]   Output [📥 result ← (2)] → [📤 final]
```

## Common Patterns

### Standard Input/Output Pattern
```
[1] Node_Name [📥 input_param ← (source)] → [📤 output_param → (target)]
```

### Multi-Step Processing
```
[1] Node [📥 input] → [🔄 step1] → [🔄 step2] → [📤 output → (2)]
```

### Conditional with Error Handling
```
[1] Operation [📥 input]
    → [✅ success → (2) | ❌ error → (3)]
[2] Success_Path [📥 data ← (1)] → [📤 result]
[3] Error_Handler [📥 error ← (1)] → [🔧 fix → (1,4)]
```

### Parallel Fan-out/Fan-in
```
[1]   Distributor [📥 work] → [🎯 distribute → (2.1,2.2,2.3)]
[2.1] ├─ Worker_A [📥 task ← (1)] → [⚡ result_a → (3)]
[2.2] ├─ Worker_B [📥 task ← (1)] → [⚡ result_b → (3)]
[2.3] └─ Worker_C [📥 task ← (1)] → [⚡ result_c → (3)]
[3]   Aggregator [📥 results ← (2.1)+(2.2)+(2.3)] → [📤 combined]
```

## Validation Checklist

Before finalizing a diagram, check:

- [ ] All node IDs are unique and hierarchical
- [ ] All connections use explicit node ID references
- [ ] Tree structure uses correct ASCII characters
- [ ] Indentation is consistent
- [ ] Line length is under 120 characters
- [ ] Emojis match operation types
- [ ] Async operations use italics
- [ ] Critical paths use bold
- [ ] All inputs reference their sources with `← (id)`
- [ ] All outputs reference their targets with `→ (id)`
- [ ] Multi-source inputs use `+` notation
- [ ] Multi-target outputs use `,` notation
- [ ] Conditional flows use `|` notation
- [ ] Similar elements are vertically aligned
- [ ] Related nodes are grouped with spacing
