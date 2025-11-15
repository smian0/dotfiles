#!/usr/bin/env python3
"""Test the graph visualization with sample data"""

from streamlit_agraph import agraph, Node, Edge, Config

# Create sample nodes (entities)
nodes = [
    Node(id="1", label="Iran", size=400, color="#FFA807", title="<b>Iran</b><br>Country in Middle East"),
    Node(id="2", label="Tehran", size=400, color="#FFA807", title="<b>Tehran</b><br>Capital of Iran"),
    Node(id="3", label="Israel", size=400, color="#FFA807", title="<b>Israel</b><br>Country in Middle East"),
    Node(id="4", label="Middle East", size=400, color="#FFA807", title="<b>Middle East</b><br>Geographic region"),
    Node(id="5", label="Biden", size=400, color="#FB7E81", title="<b>Biden</b><br>US President"),
]

# Create sample edges (relationships)
edges = [
    Edge(source="1", target="2", label="capital", type="CURVE_SMOOTH"),
    Edge(source="1", target="4", label="located_in", type="CURVE_SMOOTH"),
    Edge(source="3", target="4", label="located_in", type="CURVE_SMOOTH"),
]

# Configure
config = Config(
    width=800,
    height=600,
    directed=True,
    physics=True,
    nodeHighlightBehavior=True,
    highlightColor="#F7A7A6",
)

print("✅ streamlit-agraph imported successfully")
print(f"📊 Created {len(nodes)} nodes and {len(edges)} edges")
print("\n🌐 Graph configuration:")
print(f"   • Width: {config.width}px")
print(f"   • Height: {config.height}px")
print(f"   • Physics: {config.physics}")
print(f"   • Directed: {config.directed}")
print("\n✅ Visualization ready - will render in Streamlit app")
