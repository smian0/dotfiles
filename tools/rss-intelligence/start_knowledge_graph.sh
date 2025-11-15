#!/bin/bash
# Launch the Knowledge Graph Explorer

echo "🧠 Starting Knowledge Graph Explorer..."
echo ""
echo "Make sure the Graphiti MCP server is running:"
echo "  docker-compose up -d"
echo ""

streamlit run knowledge_graph.py --server.port 8507
