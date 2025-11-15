#!/usr/bin/env python3
"""Knowledge Graph Explorer - Standalone Streamlit App

Interactive exploration of the Graphiti knowledge graph built from RSS news articles.
Search for entities (people, organizations, locations, events) and discover their relationships.
"""

import streamlit as st
import json
import asyncio
from datetime import datetime
from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama
from streamlit_agraph import agraph, Node, Edge, Config


def format_timestamp(ts: str) -> str:
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return ts


def search_entities_cached(query: str, max_nodes: int = 20):
    """Search Graphiti knowledge graph for entities.

    Uses sync wrapper pattern with isolated event loop - idiomatic Streamlit async handling.
    """
    async def _async_search():
        graphiti_mcp = MCPTools(
            url="http://localhost:8000/mcp/",
            transport="streamable-http",
            timeout_seconds=60,
        )

        async with graphiti_mcp:
            await graphiti_mcp.initialize()

            agent = Agent(
                name="Entity Search",
                model=Ollama(id="glm-4.6:cloud"),
                tools=[graphiti_mcp],
                instructions="Execute the search_nodes tool and return the raw JSON result.",
                markdown=False,
            )

            result = await agent.arun(
                f"search_nodes(query='{query}', group_ids=['rss-intelligence'], max_nodes={max_nodes})"
            )

            return parse_graphiti_response(result.content)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async_search())
    finally:
        loop.close()


def search_facts_cached(query: str, center_node_uuid: str = None, max_facts: int = 10):
    """Search Graphiti knowledge graph for relationship facts.

    Uses sync wrapper pattern with isolated event loop - idiomatic Streamlit async handling.
    """
    async def _async_search():
        graphiti_mcp = MCPTools(
            url="http://localhost:8000/mcp/",
            transport="streamable-http",
            timeout_seconds=60,
        )

        async with graphiti_mcp:
            await graphiti_mcp.initialize()

            agent = Agent(
                name="Facts Search",
                model=Ollama(id="glm-4.6:cloud"),
                tools=[graphiti_mcp],
                instructions="Execute the search_memory_facts tool and return the raw JSON result.",
                markdown=False,
            )

            if center_node_uuid:
                result = await agent.arun(
                    f"search_memory_facts(query='{query}', group_ids=['rss-intelligence'], "
                    f"center_node_uuid='{center_node_uuid}', max_facts={max_facts})"
                )
            else:
                result = await agent.arun(
                    f"search_memory_facts(query='{query}', group_ids=['rss-intelligence'], max_facts={max_facts})"
                )

            return parse_graphiti_response(result.content)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async_search())
    finally:
        loop.close()


def parse_graphiti_response(content: str):
    """Parse agent response to extract JSON results.

    Agent responses may include text before/after JSON - extract the JSON portion.
    Handles common LLM JSON generation issues like trailing commas and control characters.
    """
    import re

    try:
        # First try direct JSON parse
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Extract JSON from mixed text
    try:
        json_match = re.search(r'\{.*\}|\[.*\]', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()

            # Fix common LLM JSON issues
            # 1. Remove trailing commas before closing braces/brackets
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

            # 2. Fix missing opening quotes before property names
            # Pattern: find lines like: { uuid" or , uuid"
            json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*")', r'\1"\2', json_str)

            # 3. Remove invalid control characters (except allowed whitespace)
            # Keep: \n \r \t (newline, carriage return, tab)
            # Remove: other control chars like \x00-\x1F except \t \n \r
            json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', json_str)

            # 4. Fix unescaped newlines inside string values
            # This is tricky - replace literal newlines with \n within quoted strings
            def escape_newlines_in_strings(match):
                """Escape newlines inside quoted strings"""
                string_content = match.group(1)
                # Replace literal newlines with escaped newlines
                escaped = string_content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                return f'"{escaped}"'

            # Match quoted strings and escape their contents
            json_str = re.sub(r'"((?:[^"\\]|\\.)*)(?<!\\)"', escape_newlines_in_strings, json_str)

            return json.loads(json_str)
    except Exception as parse_error:
        # Show detailed error for debugging
        st.error(f"Failed to parse Graphiti response: {parse_error}")
        with st.expander("🔍 Debug: Raw Response (click to expand)"):
            st.code(content, language="text")
            st.caption(f"Error details: {type(parse_error).__name__}: {parse_error}")
            st.caption("💡 Tip: The LLM may have generated invalid JSON. Try searching again or use a different query.")
        return {}


def visualize_knowledge_graph(entities: list, facts: list = None):
    """Visualize entities and relationships as an interactive graph using streamlit-agraph.

    Args:
        entities: List of entity dicts from Graphiti search_nodes
        facts: Optional list of relationship facts from search_memory_facts
    """
    if not entities:
        st.warning("No entities to visualize")
        return

    # Build nodes from entities
    nodes = []
    entity_ids = set()

    for entity in entities:
        entity_id = entity.get('uuid', entity.get('id', str(len(nodes))))
        entity_ids.add(entity_id)

        # Determine node color based on labels (if available)
        labels = entity.get('labels', [])
        color = "#97C2FC"  # Default blue
        if 'Person' in labels or 'people' in str(labels).lower():
            color = "#FB7E81"  # Red for people
        elif 'Organization' in labels or 'organization' in str(labels).lower():
            color = "#7BE141"  # Green for organizations
        elif 'Location' in labels or 'location' in str(labels).lower():
            color = "#FFA807"  # Orange for locations

        nodes.append(Node(
            id=entity_id,
            label=entity.get('name', 'Unknown')[:30],  # Truncate long names
            title=f"<b>{entity.get('name', 'Unknown')}</b><br>{entity.get('summary', 'No summary')[:200]}...",  # HTML tooltip
            size=400,
            color=color
        ))

    # Build edges from facts (if provided)
    edges = []
    if facts:
        for fact in facts:
            # Try to extract source/target UUIDs from fact structure
            if isinstance(fact, dict):
                source = fact.get('source_uuid') or fact.get('from')
                target = fact.get('target_uuid') or fact.get('to')
                fact_text = fact.get('fact', fact.get('name', str(fact)))

                # Only add edge if both nodes exist in our graph
                if source and target and source in entity_ids and target in entity_ids:
                    edges.append(Edge(
                        source=source,
                        target=target,
                        label=fact_text[:50] if len(fact_text) > 50 else fact_text,  # Truncate long labels
                        type="CURVE_SMOOTH"
                    ))

    # Configure visualization
    config = Config(
        width="100%",
        height=600,
        directed=True,
        physics=len(nodes) <= 50,  # Disable physics for large graphs (performance)
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False,
        node={'labelProperty': 'label'},
        link={'labelProperty': 'label', 'renderLabel': True}
    )

    # Display graph
    st.markdown("### 🌐 Interactive Graph Visualization")
    st.caption(f"📍 {len(nodes)} nodes" + (f" • 🔗 {len(edges)} relationships" if edges else ""))

    if len(nodes) > 50:
        st.info("💡 **Tip**: Physics simulation disabled for performance with >50 nodes. You can still drag nodes to arrange them.")

    return_value = agraph(nodes=nodes, edges=edges, config=config)

    return return_value


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Knowledge Graph Explorer",
        page_icon="🧠",
        layout="wide",
    )

    st.title("🧠 Knowledge Graph Explorer")

    st.markdown("""
    Explore the Graphiti knowledge graph built from RSS news articles. Search for entities
    (people, organizations, locations, events) and discover their relationships.
    """)

    # Search interface
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        query = st.text_input(
            "Search entities",
            placeholder="e.g., Iran, Microsoft, Trump, oil prices...",
            help="Search for entities in the knowledge graph by name or description",
            key="search_query"
        )
    with col2:
        max_nodes = st.selectbox("Results", [10, 20, 30], index=1)
    with col3:
        st.write("")  # Spacing
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)

    if not query:
        st.info("💡 Enter a search query above to explore the knowledge graph.")
        st.markdown("""
        ### Examples to Try
        - **Geographic entities**: Iran, Israel, China, Middle East
        - **Organizations**: Microsoft, Apple, Tesla, UN
        - **People**: Trump, Biden, Putin, Musk
        - **Topics**: oil, technology, war, economy
        """)

        # Sidebar info
        with st.sidebar:
            st.header("ℹ️ About")
            st.markdown("""
            This knowledge graph is automatically built from RSS news articles using:
            - **Graphiti**: Temporal knowledge graph framework
            - **FalkorDB**: Redis-based graph database
            - **Agno**: Multi-agent workflow orchestration

            Entities and relationships are extracted from news content and stored
            as a queryable graph structure.
            """)

            st.divider()

            st.header("🔗 Quick Links")
            st.markdown("""
            - [Main Dashboard](http://localhost:8506)
            - [Graphiti Docs](https://docs.graphiti.io)
            - [RSS Intelligence Workflow](README.md)
            """)
        return

    # Execute search
    with st.spinner("🔍 Searching knowledge graph..."):
        try:
            entities = search_entities_cached(query, max_nodes)
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.info("Make sure the Graphiti MCP server is running at http://localhost:8000/mcp/")
            return

    # Parse results
    if not entities or (isinstance(entities, dict) and not entities.get('nodes')):
        st.warning(f"No entities found matching '{query}'")
        st.info("Try a broader search term or check the examples above.")
        return

    entity_list = entities.get('nodes', []) if isinstance(entities, dict) else entities

    if not entity_list:
        st.warning(f"No entities found matching '{query}'")
        return

    # Display results
    st.success(f"Found **{len(entity_list)}** entities")

    # Add visualization toggle
    show_viz = st.checkbox("🌐 Show Graph Visualization", value=True, help="Interactive network visualization of entities and relationships")

    if show_viz:
        visualize_knowledge_graph(entity_list)

    st.divider()

    # Display each entity in expandable cards
    for i, entity in enumerate(entity_list):
        entity_name = entity.get('name', 'Unknown')
        entity_uuid = entity.get('uuid', '')
        entity_summary = entity.get('summary', 'No summary available')
        created_at = entity.get('created_at', '')

        with st.expander(f"**{i+1}. {entity_name}**", expanded=(i == 0)):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("**Summary:**")
                st.info(entity_summary)
            with col2:
                if created_at:
                    st.caption(f"Added: {format_timestamp(created_at)}")
                st.caption(f"UUID: {entity_uuid[:8]}...")

            # Relationship exploration
            if st.button(
                "🔗 Show Relationships",
                key=f"rel_{entity_uuid}",
                use_container_width=True
            ):
                with st.spinner(f"Loading relationships for {entity_name}..."):
                    try:
                        facts = search_facts_cached(entity_name, center_node_uuid=entity_uuid, max_facts=15)
                    except Exception as e:
                        st.error(f"Failed to load relationships: {e}")
                        continue

                fact_list = facts.get('facts', []) if isinstance(facts, dict) else facts

                if not fact_list:
                    st.info(f"No relationships found for {entity_name}")
                else:
                    st.write(f"**Found {len(fact_list)} relationship(s):**")
                    for j, fact in enumerate(fact_list, 1):
                        if isinstance(fact, dict):
                            fact_text = fact.get('fact', fact.get('name', str(fact)))
                        else:
                            fact_text = str(fact)

                        st.markdown(f"{j}. {fact_text}")

    # Sidebar with search stats
    with st.sidebar:
        st.header("📊 Search Stats")
        st.metric("Query", query)
        st.metric("Results", len(entity_list))
        st.metric("Max Results", max_nodes)

        st.divider()

        st.header("ℹ️ About")
        st.markdown("""
        This knowledge graph is automatically built from RSS news articles using:
        - **Graphiti**: Temporal knowledge graph framework
        - **FalkorDB**: Redis-based graph database
        - **Agno**: Multi-agent workflow orchestration

        Entities and relationships are extracted from news content and stored
        as a queryable graph structure.
        """)

        st.divider()

        st.header("🔗 Quick Links")
        st.markdown("""
        - [Main Dashboard](http://localhost:8506)
        - [Graphiti Docs](https://docs.graphiti.io)
        - [RSS Intelligence Workflow](README.md)
        """)


if __name__ == "__main__":
    main()
