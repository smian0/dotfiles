#!/usr/bin/env python3
"""RSS Intelligence - Multi-page Streamlit App

Home page with navigation to:
- Audit Dashboard (workflow runs, step inspector, newsletters)
- Knowledge Graph Explorer (entity search and relationships)
"""

import streamlit as st

st.set_page_config(
    page_title="RSS Intelligence",
    page_icon="📰",
    layout="wide",
)

st.title("📰 RSS Intelligence System")

st.markdown("""
Welcome to the RSS Intelligence System - a Graphiti-enhanced multi-agent newsletter workflow.

## Available Pages

Use the sidebar to navigate between pages:

### 📊 Audit Dashboard
Monitor workflow runs, inspect steps, and view generated newsletters.
- Recent workflow runs with status
- Detailed run inspection
- Step-by-step execution viewer
- Newsletter previews

### 🧠 Knowledge Graph Explorer
Explore the temporal knowledge graph built from RSS news articles.
- Search for entities (people, organizations, locations, events)
- Discover relationships between entities
- Temporal analysis of news events
- Interactive entity exploration

## System Architecture

```
RSS Sources → Agno Workflow → Content Analysis → Newsletter Generation
                    ↓
              Graphiti Ingestion → Knowledge Graph (FalkorDB)
                    ↓
              Entity Extraction → Relationship Mapping
```

## Quick Stats
""")

# Try to get some basic stats
try:
    from audit_dashboard import get_inspector
    inspector = get_inspector()
    runs = inspector.get_recent_runs(limit=100)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Runs", len(runs))
    with col2:
        successful = len([r for r in runs if r.get('status') == 'success'])
        st.metric("Successful Runs", successful)
    with col3:
        failed = len([r for r in runs if r.get('status') != 'success'])
        st.metric("Failed Runs", failed)
except:
    st.info("💡 Start exploring using the sidebar navigation")

st.divider()

st.markdown("""
## Getting Started

1. **View Workflow Runs**: Click "📊 Audit Dashboard" in the sidebar
2. **Explore Knowledge**: Click "🧠 Knowledge Graph" in the sidebar

## About

Powered by:
- **Agno**: Multi-agent workflow orchestration
- **Graphiti**: Temporal knowledge graph framework
- **FalkorDB**: Redis-based graph database
- **Streamlit**: Interactive web interface
- **Ollama**: Local LLM inference

Built with ❤️ for intelligent news analysis
""")
