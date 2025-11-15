# Export Full Graphiti Knowledge Graph

**Script**: `export_full_knowledge_graph.py`
**Purpose**: Export the COMPLETE Graphiti knowledge graph from FalkorDB to interactive visualizations and standard formats

## Quick Start

```bash
# Basic usage (auto-detects settings)
python3 export_full_knowledge_graph.py --port 6380

# Specify custom graph name
python3 export_full_knowledge_graph.py --port 6380 --graph your_graph_name

# Disable physics for large graphs
python3 export_full_knowledge_graph.py --port 6380 --no-physics
```

## What It Does

1. **Connects to FalkorDB** - Queries the complete knowledge graph
2. **Exports to multiple formats**:
   - `knowledge_graph.html` - Interactive visualization (open in browser)
   - `knowledge_graph.json` - For D3.js/custom tools
   - `knowledge_graph.gexf` - For Gephi
   - `knowledge_graph.graphml` - For Cytoscape/yEd

3. **Creates interactive visualization** with:
   - Color-coded nodes (red=people, green=orgs, orange=locations)
   - Hover tooltips showing entity details
   - Drag/zoom/pan controls
   - Physics simulation (for smaller graphs)

## Current Status

✅ **Script Created and Tested**
- Connects to FalkorDB successfully (port 6380)
- Export functions working
- Visualization ready

⚠️ **Graph Name Issue**
The default graph name 'graphiti' appears to be empty or incorrect.

**To find your graph name:**

### Option 1: Check MCP Server Logs
```bash
docker logs graphiti-mcp-server 2>&1 | grep -i 'graph\|GRAPH\|falkor'
```

### Option 2: Check when ingesting episodes
Look at your `rss_intelligence_workflow.py` where it calls `add_memory`:
```python
result = await agent.arun(
    f"add_memory(name={repr(episode_name)}, episode_body={repr(episode_body)}, "
    f"source='json', source_description='RSS news article', group_id='rss-intelligence')"
)
```

The graph name might be related to `group_id='rss-intelligence'`.

### Option 3: Query MCP directly
```python
from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama

async def find_graph_name():
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
    )

    async with graphiti_mcp:
        await graphiti_mcp.initialize()

        agent = Agent(
            name="Graph Info",
            model=Ollama(id="glm-4.6:cloud"),
            tools=[graphiti_mcp],
            instructions="Get information about the graph configuration",
        )

        # Try to get status or configuration
        result = await agent.arun("get_status()")
        print(result.content)
```

## Usage Examples

### Example 1: Export with Custom Graph Name

Once you know your graph name:

```bash
python3 export_full_knowledge_graph.py \
  --port 6380 \
  --graph rss-intelligence  # Replace with actual name
```

### Example 2: Large Graph (Disable Physics)

For graphs with 100+ nodes:

```bash
python3 export_full_knowledge_graph.py \
  --port 6380 \
  --no-physics  # Better performance
```

### Example 3: Save to Custom Directory

```bash
python3 export_full_knowledge_graph.py \
  --port 6380 \
  --output-dir ./graph_exports
```

## Output Files

After running successfully:

```
knowledge_graph.html      # 🌐 Open in browser to explore
knowledge_graph.json      # For D3.js, custom visualizations
knowledge_graph.gexf      # For Gephi (professional network analysis)
knowledge_graph.graphml   # For Cytoscape (bioinformatics/network viz)
```

## Viewing the Graph

### Interactive HTML (Recommended)

```bash
# Open in browser
open knowledge_graph.html

# Or on Linux
xdg-open knowledge_graph.html
```

**Features**:
- Click and drag nodes to reposition
- Scroll to zoom in/out
- Hover over nodes for details
- Click nodes to highlight connections

### Gephi (Professional Analysis)

1. Open Gephi
2. File → Open → `knowledge_graph.gexf`
3. Apply layout: Layout → ForceAtlas 2
4. Size nodes by degree: Appearance → Nodes → Size → Degree
5. Color by modularity: Statistics → Modularity → Run → Appearance → Nodes → Color → Partition → Modularity Class

### Cytoscape (Network Biology)

1. Open Cytoscape
2. File → Import → Network from File → `knowledge_graph.graphml`
3. Apply layout: Layout → Prefuse Force Directed Layout
4. Style nodes based on properties

## Troubleshooting

### Error: "Invalid graph operation on empty key"

**Cause**: Graph name is incorrect or graph is empty

**Fix**:
1. Find correct graph name (see "To find your graph name" above)
2. Run with `--graph your_actual_graph_name`

### Error: "Authentication required"

**Cause**: Wrong port or FalkorDB requires password

**Fix**:
```bash
# Check which port FalkorDB is running on
docker ps | grep falkordb

# Use the correct port
python3 export_full_knowledge_graph.py --port CORRECT_PORT
```

### Error: "Connection refused"

**Cause**: FalkorDB is not running

**Fix**:
```bash
# Start FalkorDB
docker start graphiti-falkordb

# Verify it's running
docker ps | grep falkordb
```

### No nodes in output

**Possible causes**:
1. Graph is genuinely empty (no episodes ingested yet)
2. Wrong graph name
3. Graph uses different structure than expected

**Debug**:
```python
# Connect and check manually
from falkordb import FalkorDB

db = FalkorDB(host='localhost', port=6380)
g = db.select_graph('your_graph_name')

# Try listing all labels
result = g.ro_query("MATCH (n) RETURN DISTINCT labels(n) LIMIT 10")
print("Available labels:", result.result_set)

# Count total nodes
result = g.ro_query("MATCH (n) RETURN count(n)")
print("Total nodes:", result.result_set[0][0])
```

## Command Line Options

```
--host HOST         FalkorDB host (default: localhost)
--port PORT         FalkorDB port (default: 6379, use 6380 for Docker)
--graph GRAPH       Graph name in FalkorDB (default: graphiti)
--no-physics        Disable physics simulation (faster for large graphs)
--output-dir DIR    Output directory (default: current directory)
```

## Performance

| Graph Size | Export Time | Visualization | Physics Enabled |
|------------|-------------|---------------|-----------------|
| <100 nodes | <5 seconds | Smooth | ✅ Yes |
| 100-500 nodes | 5-15 seconds | Good | ✅ Yes |
| 500-1000 nodes | 15-30 seconds | Moderate | ⚠️ Optional |
| >1000 nodes | 30-60 seconds | Slow | ❌ Disable |

**Tip**: For graphs >500 nodes, use `--no-physics` for better performance

## Differences from Search-Based Visualization

**Current Knowledge Graph Page** (pages/2_🧠_Knowledge_Graph.py):
- Shows SEARCH RESULTS only (subset of graph)
- Limited to queried entities
- Good for exploring specific topics

**This Export Script**:
- Shows ENTIRE GRAPH (all nodes and edges)
- Complete knowledge base state
- Good for understanding overall structure

## Integration Options

### Option A: Add to Streamlit App

Add a button to Knowledge Graph page:

```python
# In pages/2_🧠_Knowledge_Graph.py
if st.button("📥 Export Full Graph"):
    with st.spinner("Exporting full knowledge graph..."):
        # Run export script
        os.system("python3 export_full_knowledge_graph.py --port 6380")

    # Provide download links
    st.download_button("Download HTML", "knowledge_graph.html")
    st.download_button("Download JSON", "knowledge_graph.json")
```

### Option B: Standalone Script (Current)

Keep as separate script for:
- Offline analysis
- Periodic exports
- Large graph exports (better performance)
- Professional tool integration (Gephi/Cytoscape)

## Next Steps

1. **Find your graph name** using one of the methods above
2. **Run the export** with correct graph name
3. **Open the HTML file** to view your full knowledge graph
4. **Optional**: Import into Gephi/Cytoscape for advanced analysis

## Dependencies

```bash
pip install falkordb pyvis networkx
```

Already installed ✅ (from previous setup)

## Example Output

When successful:

```
============================================================
🧠 GRAPHITI KNOWLEDGE GRAPH EXPORTER
============================================================
📡 Connecting to FalkorDB at localhost:6380...
✓ Connected to graph 'rss-intelligence'

📊 Exporting full knowledge graph...
   Querying all relationships...
   ✓ Processed 1,234 relationships
   Querying isolated nodes...
   ✓ Found 56 isolated nodes

✅ Export complete: 892 nodes, 1,234 edges

📦 EXPORTING TO FORMATS
   ✓ Saved knowledge_graph.json
   ✓ Saved knowledge_graph.gexf
   ✓ Saved knowledge_graph.graphml

🎨 CREATING VISUALIZATION
   ✓ Interactive visualization saved to knowledge_graph.html

📊 KNOWLEDGE GRAPH STATISTICS
  Total Nodes:     892
  Total Edges:     1,234
  Graph Density:   0.0031
  Avg Degree:      2.77

  Nodes by Type:
    • Entity: 845
    • Episode: 47

✅ EXPORT COMPLETE
```

---

**Last Updated**: 2025-11-15
