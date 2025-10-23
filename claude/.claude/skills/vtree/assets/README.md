# VTREE Templates

Quick-start templates for common diagram patterns. Copy and customize for your needs.

## Available Templates

### template-basic.md
Simple hierarchical structure with parent-child relationships. Best for:
- Organizational charts
- Simple process flows
- Basic system architecture
- File/folder structures

### template-api-workflow.md
Complete API request/response flow with authentication and error handling. Best for:
- RESTful APIs
- GraphQL resolvers
- Webhook handlers
- Microservice endpoints

## Usage

1. **Choose a template** that matches your use case
2. **Copy the diagram** from the template
3. **Customize node names** and IDs
4. **Update emojis** to match your operations
5. **Adjust connections** (`← (id)` and `→ (id)`)
6. **Add/remove nodes** as needed

## Quick Customization Tips

### Change Operation Type
Replace emojis based on what the node does:
- Processing: 🔄 (transform), ⚡ (execute), 📊 (analyze)
- State: ✅ (success), ❌ (error), ⏳ (async)
- Security: 🔐 (auth), 🛡️ (validate)
- Storage: 💾 (persist), 🌐 (external API)

### Add Async Operations
Make any node async by:
1. Add *italics* to node name
2. Add ⏳ emoji
3. Mark as async operation

```
[1] *Async_Call* [⏳ await] → [📤 result]
```

### Mark Critical Paths
Bold critical operations:
```
[1] **Critical_Step** [⚡ must_work] → [📤 result]
```

### Add Error Handling
Use conditional branching:
```
[1] Operation [📥 input] → [✅ ok → (2) | ❌ error → (3)]
```

## Need More Examples?

See `references/pattern-templates.md` for comprehensive patterns:
- Linear Pipeline
- Parallel Processing
- Error Handling Flow
- Async Operations
- Multiagent System
- State Machine
