# Basic VTREE Template

Use this template as a starting point for simple hierarchical diagrams.

```
[1]     Root_Node [📥 input] → [📤 output → (2)]
[1.1]   ├─ Child_A [⚡ process] → [📤 result_a → (1)]
[1.2]   └─ Child_B [⚡ process] → [📤 result_b → (1)]
[2]     Next_Node [📥 data ← (1)] → [📤 final]
```

## Quick Customization

1. **Replace node names**: `Root_Node`, `Child_A`, etc.
2. **Update node IDs**: Maintain hierarchical numbering
3. **Choose emojis**: Match to your operation types
4. **Set connections**: Update `← (id)` and `→ (id)` references

## Common Modifications

### Add more children
```
[1]     Root_Node [📥 input] → [📤 output → (2)]
[1.1]   ├─ Child_A [⚡ process] → [📤 result_a → (1)]
[1.2]   ├─ Child_B [⚡ process] → [📤 result_b → (1)]
[1.3]   └─ Child_C [⚡ process] → [📤 result_c → (1)]
```

### Add deeper hierarchy
```
[1]       Root_Node [📥 input] → [📤 output → (2)]
[1.1]     ├─ Parent_A [⚡ process] → [📤 result_a → (1)]
[1.1.1]   │  ├─ Child_A1 [🔄 transform] → [📤 data → (1.1)]
[1.1.2]   │  └─ Child_A2 [🔄 transform] → [📤 data → (1.1)]
[1.2]     └─ Parent_B [⚡ process] → [📤 result_b → (1)]
```

### Make nodes async or optional
```
[1]     Root_Node [📥 input] → [📤 output → (2)]
[1.1]   ├─ *Async_Child* [⏳ await] → [📤 result_a → (1)]
[1.2]   └─ *Optional_Step* [⚡ maybe] → [📤 result_b → (1)]
```

### Mark critical paths
```
[1]     Root_Node [📥 input] → [📤 output → (2)]
[1.1]   ├─ **Critical_Step** [⚡ must_succeed] → [📤 result_a → (1)]
[1.2]   └─ Helper_Step [⚡ process] → [📤 result_b → (1)]
```
