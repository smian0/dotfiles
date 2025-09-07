# VTree Visualization Format

This document defines the formatting rules for ASCII tree visualization in Claude Code responses.

## Simplified Format

Use this format for quick understanding of hierarchical structures:

### Core Structure
- **Node IDs**: [1], [2], [2.1] for reference tracking
- **Connections**: Use ├─ └─ for tree structure  
- **Data Flow**: → (node_id) for outputs, ← (node_id) for inputs
- **Multiple outputs**: → (A,B,C) for distribution to multiple nodes

### Visual Indicators
- **Minimal emojis**: 📥 input, 📤 output only
- **Clear component names** describing function
- **Simple connections** showing data flow

### Spacing
- **3-5 spaces** per indentation level
- **Keep lines concise** and readable

### Example Template
```
[1]  Main_Component [📥 input] → (2.1,2.2)
[2]  ├─ Sub_Component_A → (3)
     └─ Sub_Component_B → (3)
[3]  Output_Handler [📤 result]
```

### End Note
Add after simplified diagrams: "Simplified vtree for quick understanding"

## Comprehensive Format (*vtree)

Use this format when user types `*vtree` for detailed system analysis:

### Core Structure
- **Node IDs**: [1], [1.1], [1.2.1] for explicit reference tracking
- **Connections**: Use ├─ │ └─ for tree structure
- **Data Flow**: → (node_id) for outputs, ← (node_id) for inputs
- **Multiple I/O**: ← (A)+(B) for combined inputs, → (A,B) for split outputs

### Advanced Notation
- **Conditional Logic**: if(condition) → (success) else → (error)
- **Parallel Processing**: → (1.1||1.2||1.3) for concurrent execution
- **Error Handlers**: [1.1.E] suffix for error handling nodes

### Visual Indicators
- **Priority**: 🔴 Critical/P0, 🟡 Important/P1, 🟢 Normal/P2
- **Status**: ⚡ Active/Fast, ⏸️ Paused/Waiting, 🐌 Slow/Bottleneck
- **Operations**: 📥 input, 📤 output, 🔄 process, 📊 analyze, 💾 store, 🌐 external
- **Security**: 🔒 Secure, 🛡️ Protected, [Auth: level]

### Organization
- **System Grouping**: # =========== LAYER NAME ===========
- **Infrastructure**: [@deployment-target, resources]
- **Comments**: # Inline explanatory comments
- **Performance**: [2.3ms, 99.9% uptime] metrics

### Text Styling
- ***italics*** for optional/async/external elements
- ***bold*** for critical paths and main processes
- **Normal text** for standard required operations

### Spacing
- **3-7 spaces** per indentation level for readability
- **Keep under 120 characters** per line when possible

### Example Template
```
# =========== FRONTEND LAYER ===========
[1]     🌐 **Load_Balancer** [@nginx-ingress] → [🎯 → (1.1||1.2||1.3)]
[1.1]   ├─ Web_Server_1 [⚡ 1.2ms, 99.9% uptime] → [📤 → (2)]
[1.2]   ├─ Web_Server_2 [⚡ 1.4ms, 99.8% uptime] → [📤 → (2)]
[1.3]   └─ *Web_Server_3* [🐌 5.2ms, 95% uptime] → [📤 → (2)]

# =========== API LAYER ===========
[2]     🔒 **API_Gateway** [Auth: oauth2] → [if(authenticated) → (3) else → (2.E)]
[2.E]   └─ ❌ Auth_Failure → [📤 401_error]

# =========== DATA LAYER ===========
[3]     💾 **Database_Cluster** [@kubernetes-prod, CPU: 16 cores] → [📤 data]
```

### End Note
Add after comprehensive diagrams: "Comprehensive vtree optimized for terminal display with advanced semantic indicators"

## Usage Guidelines

### When to Use Simplified
- Quick workflow overviews
- Basic component relationships
- Simple process flows
- Educational explanations

### When to Use Comprehensive (*vtree)
- Complex system architectures
- Performance analysis
- Security assessments
- Production system documentation
- Infrastructure planning

### Content Types Suitable for VTree
- **Workflows**: Multi-step processes, pipelines
- **Architecture**: System components, microservices
- **Decision Trees**: Branching logic, conditions
- **File Structure**: Directory hierarchies, project organization
- **Data Flow**: Processing pipelines, transformations
- **Multi-Agent Systems**: Coordinated processes, orchestration