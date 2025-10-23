---
name: vtree
description: Generate enhanced ASCII tree diagrams for hierarchical systems with data flow, node references, and semantic indicators. Use when user asks to diagram, visualize, or show structure of workflows, architectures, processes, or hierarchies.
---

# VTREE - Visual Tree Diagrams

Generate enhanced ASCII tree diagrams with explicit data flow tracking, node references, and semantic indicators for any hierarchical system.

## When to Use

Trigger this skill when the user requests:
- "diagram this", "visualize the structure", "show the workflow"
- "tree view", "hierarchy", "architecture diagram"
- "data flow", "process map", "system structure"

Works for: software systems, business processes, decision trees, data pipelines, multiagent systems, microservices, state machines, error handling flows.

## Core Format

```
[ID]    Node_Name [📥 input ← (source)] → [📤 output → (target)]
├─ Sub_Node [emoji operation] → [result → (next)]
└─ *Optional_Node* [⏳ async] → [result → (target)]
```

### Key Elements

1. **Node IDs**: `[1]`, `[2.1]`, `[3.2.1]` - Hierarchical identifiers
2. **Data Flow**:
   - `← (node_id)` = Input from node
   - `→ (node_id)` = Output to node
   - `← (A)+(B)+(C)` = Multi-source input
   - `→ (A,B,C)` = Multi-target output
3. **Emojis**: Semantic indicators (see references/emoji-semantics.md)
4. **Styling**:
   - Normal = Required, synchronous, internal
   - *Italics* = Optional, async, external
   - **Bold** = Critical path, essential

## Generation Process

### 1. Understand the System
Ask clarifying questions if needed:
- What are the main components/nodes?
- What's the data/control flow?
- Are there async operations?
- What are critical paths?

### 2. Assign Node IDs
Use hierarchical numbering:
- Top-level: `[1]`, `[2]`, `[3]`
- Second-level: `[1.1]`, `[1.2]`, `[2.1]`
- Third-level: `[1.1.1]`, `[1.1.2]`

### 3. Choose Pattern Template
Select from common patterns (see references/pattern-templates.md):
- Linear Pipeline (sequential processing)
- Parallel Processing (fan-out/fan-in)
- Error Handling (conditional branching)
- Async Operations (external APIs)
- Multiagent System (coordinated agents)
- State Machine (state transitions)

### 4. Apply Semantic Indicators

**Choose emojis based on primary operation**:
- 📥/📤 for input/output
- 🔄 for transforms
- ⚡ for execution
- 🧠 for AI/decisions
- ⏳ for async
- ✅/❌ for success/error
- 🔐 for auth/security
- 💾 for storage

Full emoji reference: references/emoji-semantics.md

**Apply text styling**:
- *Italics*: async operations, external APIs, optional steps
- **Bold**: critical paths, essential operations
- Normal: standard operations

### 5. Connect with Explicit Flow

Show data flow explicitly:
```
[1]   Source [📥 input] → [📤 data → (2)]
[2]   Process [📥 data ← (1)] → [🔄 result → (3)]
[3]   Store [💾 result ← (2)] → [✅ saved]
```

### 6. Format for Readability

- Use `├─` `│` `└─` for tree structure
- 3-7 spaces per indentation level
- Keep lines under 120 characters
- Align similar elements vertically

## Output Structure

Provide:
1. **Brief overview** (1-2 sentences about the system)
2. **ASCII diagram** with node IDs, emojis, and flow
3. **Key explanations** (highlight critical paths or complex flows)
4. **Note**: "Enhanced for terminal display with semantic indicators"

## Examples

See references/pattern-templates.md for complete examples of:
- Linear Pipeline
- Parallel Processing (Fan-out/Fan-in)
- Error Handling Flow
- Async Operations
- Multiagent System
- State Machine

## Quick Reference

| Symbol | Meaning |
|--------|---------|
| `[1.2.3]` | Hierarchical node ID |
| `← (id)` | Input from node |
| `→ (id)` | Output to node |
| `← (A)+(B)` | Multiple inputs |
| `→ (A,B)` | Multiple outputs |
| `→ (A) \| → (B)` | Conditional branch |
| *italic* | Optional/async/external |
| **bold** | Critical/essential |

## Progressive Disclosure

Load these references as needed:
- **emoji-semantics.md** - Complete emoji vocabulary
- **pattern-templates.md** - 6 detailed template examples
- **usage-rules.md** - Detailed structural and flow rules
