#!/usr/bin/env python3
"""Streamlit Dashboard for RSS Intelligence Workflow Audit System.

A simple, visual interface for inspecting workflow runs, debugging issues,
and viewing artifacts from the Agno-native audit system.

Usage:
    streamlit run audit_dashboard.py
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import sys

# Add .audit to path for inspector import
audit_dir = Path(__file__).parent / ".audit"
if str(audit_dir) not in sys.path:
    sys.path.insert(0, str(audit_dir))

from inspector import WorkflowAuditInspector


# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="RSS Intelligence Audit Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# Utilities
# ============================================================================

def get_inspector():
    """Initialize a fresh inspector instance for each request.

    Note: SQLite connections cannot be shared across threads,
    so we create a new instance instead of caching.
    """
    try:
        return WorkflowAuditInspector("rss_intelligence.db")
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        st.stop()


def format_timestamp(ts_str):
    """Format ISO timestamp for display."""
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts_str


def get_status_icon(success):
    """Get emoji icon for success/failure status."""
    return "✅" if success else "❌"


def render_json(data):
    """Render JSON data with syntax highlighting."""
    st.json(data)


def render_markdown(content):
    """Render markdown content."""
    st.markdown(content)


# ============================================================================
# Page: Recent Runs
# ============================================================================

def show_recent_runs(inspector):
    """Display recent workflow runs."""
    st.title("📋 Recent Workflow Runs")

    # Controls
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        limit = st.slider("Number of runs to display", 5, 50, 10)
    with col2:
        workflow_filter = st.selectbox(
            "Filter by workflow",
            ["All", "rss-intelligence", "rss-intelligence-test"]
        )
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Fetch runs
    try:
        runs = inspector.list_runs(limit=limit)

        # Apply filter
        if workflow_filter != "All":
            runs = [r for r in runs if r['workflow_id'] == workflow_filter]

        if not runs:
            st.info("No workflow runs found.")
            return

        # Display runs
        st.write(f"**Showing {len(runs)} runs**")

        for run in runs:
            # Determine status
            status_icon = "🟢" if run.get('audit_run_id') != 'N/A' else "🔴"

            with st.expander(
                f"{status_icon} **{run['audit_run_id']}** - {format_timestamp(run['created_at'])}",
                expanded=False
            ):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Workflow", run['workflow_id'])
                with col2:
                    st.metric("Version", run.get('audit_version', 'N/A'))
                with col3:
                    st.metric("Run Count", run.get('run_count', 0))
                with col4:
                    st.metric("Session ID", run['session_id'][:8] + "...")

                # Action button
                if st.button(
                    "View Details →",
                    key=f"view_{run['session_id']}",
                    use_container_width=True
                ):
                    st.session_state['selected_session_id'] = run['session_id']
                    st.session_state['current_page'] = 'Run Details'
                    
                    st.rerun()

    except Exception as e:
        st.error(f"Error loading runs: {e}")


# ============================================================================
# Page: Run Details
# ============================================================================

def show_run_details(inspector):
    """Display detailed information about a specific run."""
    st.title("🔍 Run Details")

    # Session selector
    session_id = st.session_state.get('selected_session_id')

    if not session_id:
        st.info("Select a run from the Recent Runs page to view details.")
        if st.button("← Back to Recent Runs"):
            st.session_state['current_page'] = 'Recent Runs'
            
            st.rerun()
        return

    try:
        # Fetch run data
        with st.spinner("Loading run details..."):
            run_data = inspector.inspect_run(session_id)
            steps = inspector.get_step_history(session_id)

        # Header with back button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"Run: {run_data.get('audit_run_id', 'N/A')}")
        with col2:
            if st.button("← Back to Recent Runs", use_container_width=True):
                st.session_state['current_page'] = 'Recent Runs'
                
                st.rerun()

        # Metadata
        st.write("### Metadata")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Workflow ID", run_data['workflow_id'])
        with col2:
            st.metric("Created At", format_timestamp(run_data['created_at']))
        with col3:
            st.metric("Version", run_data.get('audit_workflow_version', 'N/A'))
        with col4:
            st.metric("Total Steps", len(steps))

        # Session ID (expandable)
        with st.expander("Session Details"):
            st.code(f"Session ID: {run_data['session_id']}")
            if run_data.get('audit_start_time'):
                st.write(f"Start Time: {run_data['audit_start_time']}")

        # Steps timeline
        st.write("### Steps Execution Timeline")

        if not steps:
            st.info("No step execution data available.")
        else:
            for i, step in enumerate(steps, 1):
                status_icon = get_status_icon(step.get('success', False))

                with st.container():
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        st.write(f"**Step {i}**")
                        st.write(status_icon)
                    with col2:
                        st.write(f"**{step['step_name']}**")
                        st.write(f"_Executor: {step.get('executor_name', 'N/A')}_")

                        # Output
                        if step.get('content'):
                            st.text(f"Output: {step['content']}")

                        # Error
                        if step.get('error'):
                            st.error(f"Error: {step['error']}")

                        # Metrics
                        if step.get('metrics'):
                            st.json(step['metrics'])

                        # Link to step inspector
                        if st.button(
                            "Inspect Step Details →",
                            key=f"inspect_{step['step_id']}",
                            use_container_width=True
                        ):
                            st.session_state['selected_step_name'] = step['step_name']
                            st.session_state['current_page'] = 'Step Inspector'
                            
                            st.rerun()

                if i < len(steps):
                    st.divider()

        # Session state (expandable)
        with st.expander("Session State"):
            if run_data.get('session_data'):
                render_json(run_data['session_data'])
            else:
                st.info("No session data available.")

    except Exception as e:
        st.error(f"Error loading run details: {e}")
        if st.button("← Back to Recent Runs"):
            st.session_state['current_page'] = 'Recent Runs'
            
            st.rerun()


# ============================================================================
# Page: Step Inspector
# ============================================================================

def show_step_inspector(inspector):
    """Display detailed information about a specific step."""
    st.title("🔬 Step Inspector")

    session_id = st.session_state.get('selected_session_id')
    step_name = st.session_state.get('selected_step_name')

    if not session_id or not step_name:
        st.info("Select a step from the Run Details page to inspect.")
        if st.button("← Back to Run Details"):
            st.session_state['current_page'] = 'Run Details'
            
            st.rerun()
        return

    try:
        # Fetch step data
        with st.spinner("Loading step details..."):
            step_detail = inspector.get_step_detail(session_id, step_name)

        # Header with back button
        col1, col2 = st.columns([3, 1])
        with col1:
            status_icon = get_status_icon(step_detail.get('success', False))
            st.subheader(f"{status_icon} Step: {step_name}")
        with col2:
            if st.button("← Back to Run Details", use_container_width=True):
                st.session_state['current_page'] = 'Run Details'
                
                st.rerun()

        # Metadata
        st.write("### Step Metadata")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Executor", step_detail.get('executor_name', 'N/A'))
        with col2:
            st.metric("Status", "Success" if step_detail.get('success') else "Failed")
        with col3:
            st.metric("Step ID", step_detail.get('step_id', 'N/A')[:8] + "...")

        # Output
        st.write("### Output")
        if step_detail.get('content'):
            st.text_area(
                "Step Content",
                step_detail['content'],
                height=100,
                disabled=True
            )
        else:
            st.info("No output content.")

        # Error
        if step_detail.get('error'):
            st.write("### Error")
            st.error(step_detail['error'])

        # Metrics
        if step_detail.get('metrics'):
            st.write("### Metrics")
            render_json(step_detail['metrics'])

        # Artifacts
        st.write("### Artifacts")
        artifacts = step_detail.get('artifacts', [])

        if not artifacts:
            st.info("No artifacts saved for this step.")
        else:
            st.write(f"Found **{len(artifacts)}** artifact(s)")

            for artifact in artifacts:
                filename = artifact['filename']
                file_path = Path(artifact['path'])
                file_size = artifact['size']

                with st.expander(f"📄 {filename} ({file_size:,} bytes)"):
                    # Show file path
                    st.code(artifact['path'], language="text")

                    # Preview content
                    try:
                        if file_path.suffix == '.json':
                            st.write("**JSON Preview:**")
                            content = json.loads(file_path.read_text())
                            render_json(content)
                        elif file_path.suffix == '.md':
                            st.write("**Markdown Preview:**")
                            content = file_path.read_text()
                            render_markdown(content)
                        else:
                            st.write("**Text Preview:**")
                            content = file_path.read_text()
                            st.text(content[:1000])  # Limit preview
                            if len(content) > 1000:
                                st.info("(Preview truncated - download to view full content)")

                        # Download button
                        st.download_button(
                            "⬇️ Download",
                            file_path.read_bytes(),
                            filename,
                            key=f"download_{filename}"
                        )
                    except Exception as e:
                        st.error(f"Error loading artifact: {e}")

    except Exception as e:
        st.error(f"Error loading step details: {e}")
        if st.button("← Back to Run Details"):
            st.session_state['current_page'] = 'Run Details'
            
            st.rerun()


# ============================================================================
# Page: Newsletters
# ============================================================================

def get_runs_with_newsletters(inspector):
    """Get all workflow runs that have newsletters with metadata.

    Uses a hybrid approach:
    1. Scan newsletters/ directory for all newsletter files
    2. Parse filenames to extract timestamps
    3. Attempt to correlate with audit runs via timestamp matching
    4. Return unified list with filesystem + audit metadata
    """
    import re
    from datetime import datetime, timedelta

    newsletters_dir = Path(__file__).parent / "newsletters"

    if not newsletters_dir.exists():
        return []

    # Pattern: newsletter_{technical|consumer}_{timestamp}.md
    pattern = re.compile(r'newsletter_(technical|consumer)_(\d{8}_\d{6})\.md')

    # Group newsletters by timestamp
    newsletter_groups = {}

    for file in newsletters_dir.glob("newsletter_*.md"):
        match = pattern.match(file.name)
        if match:
            newsletter_type, timestamp = match.groups()

            if timestamp not in newsletter_groups:
                newsletter_groups[timestamp] = {
                    'timestamp': timestamp,
                    'technical': None,
                    'consumer': None,
                    'audit_run_id': None,
                    'workflow_id': None,
                    'article_count': None
                }

            newsletter_groups[timestamp][newsletter_type] = str(file)

    # Attempt to correlate with audit runs
    try:
        runs = inspector.list_runs(limit=100)

        for timestamp, group in newsletter_groups.items():
            # Parse newsletter timestamp
            try:
                newsletter_dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            except ValueError:
                continue

            # Find matching run within 30 minutes (newsletters generated at end of workflow)
            for run in runs:
                try:
                    run_dt = datetime.fromisoformat(run['created_at'])
                    if abs((run_dt - newsletter_dt).total_seconds()) < 1800:
                        group['audit_run_id'] = run['audit_run_id']
                        group['workflow_id'] = run['workflow_id']

                        # Try to extract article count from session data
                        try:
                            session_id = run['session_id']
                            steps = inspector.get_step_history(session_id)
                            for step in steps:
                                if step['step_name'] == 'log_rss_articles':
                                    metrics = step.get('metrics', {})
                                    group['article_count'] = metrics.get('article_count')
                                    break
                        except:
                            pass
                        break
                except:
                    continue
    except Exception as e:
        print(f"Warning: Failed to correlate with audit runs: {e}")

    # Convert to sorted list (newest first)
    results = sorted(
        newsletter_groups.values(),
        key=lambda x: x['timestamp'],
        reverse=True
    )

    return results


def display_newsletter(path, newsletter_type):
    """Display a single newsletter with metadata and download button."""
    try:
        file_path = Path(path)

        if not file_path.exists():
            st.error(f"Newsletter file not found: {path}")
            return

        # Read content
        content = file_path.read_text()

        # Metadata
        file_size = file_path.stat().st_size
        word_count = len(content.split())
        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)

        # Display metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{file_size:,} bytes")
        with col2:
            st.metric("Word Count", f"{word_count:,}")
        with col3:
            st.metric("Last Modified", last_modified.strftime("%Y-%m-%d %H:%M:%S"))

        st.divider()

        # Render markdown
        st.markdown(content)

        st.divider()

        # Download button
        st.download_button(
            f"⬇️ Download {newsletter_type.title()} Newsletter",
            content,
            file_path.name,
            "text/markdown",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Error displaying newsletter: {e}")


def show_newsletters(inspector):
    """Display newsletters page with run selector and markdown rendering."""
    st.title("📰 Newsletters")

    # Fetch runs with newsletters
    with st.spinner("Loading newsletters..."):
        runs = get_runs_with_newsletters(inspector)

    if not runs:
        st.info("No newsletters found. Run the full workflow to generate newsletters.")
        return

    # Summary metrics
    st.write("### Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Runs", len(runs))
    with col2:
        # Count runs from last 24 hours
        from datetime import datetime, timedelta
        now = datetime.now()
        recent = sum(1 for r in runs
                    if (now - datetime.strptime(r['timestamp'], "%Y%m%d_%H%M%S")).total_seconds() < 86400)
        st.metric("Last 24h", recent)
    with col3:
        # Count complete pairs
        complete = sum(1 for r in runs if r['technical'] and r['consumer'])
        st.metric("Complete Pairs", complete)

    st.divider()

    # Run selector
    st.write("### Select Newsletter Run")

    # Format options with timestamps and metadata
    def format_option(run):
        from datetime import datetime, timedelta

        timestamp = run['timestamp']
        dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")

        # Calculate age
        age = datetime.now() - dt
        if age.total_seconds() < 3600:
            age_str = f"{int(age.total_seconds() / 60)}m ago"
        elif age.total_seconds() < 86400:
            age_str = f"{int(age.total_seconds() / 3600)}h ago"
        else:
            age_str = f"{int(age.total_seconds() / 86400)}d ago"

        # Build label
        label = f"{dt.strftime('%Y-%m-%d %H:%M:%S')} ({age_str})"

        if run['audit_run_id']:
            label += f" - {run['audit_run_id']}"
        if run['article_count']:
            label += f" - {run['article_count']} articles"

        return label

    options = [format_option(r) for r in runs]
    selected_index = st.selectbox(
        "Choose a run",
        range(len(options)),
        format_func=lambda i: options[i],
        label_visibility="collapsed"
    )

    selected_run = runs[selected_index]

    st.divider()

    # Display newsletters in tabs
    st.write("### Newsletter Content")

    has_technical = selected_run['technical'] is not None
    has_consumer = selected_run['consumer'] is not None

    if not has_technical and not has_consumer:
        st.warning("No newsletters found for this run.")
        return

    # Create tabs
    tab_labels = []
    if has_technical:
        tab_labels.append("📊 Technical")
    if has_consumer:
        tab_labels.append("📰 Consumer")

    tabs = st.tabs(tab_labels)

    tab_index = 0
    if has_technical:
        with tabs[tab_index]:
            display_newsletter(selected_run['technical'], "technical")
        tab_index += 1

    if has_consumer:
        with tabs[tab_index]:
            display_newsletter(selected_run['consumer'], "consumer")


# ============================================================================
# Page: Knowledge Graph
# ============================================================================

import asyncio
from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama


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
    Handles common LLM JSON generation issues like trailing commas.
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
            # Remove trailing commas before closing braces/brackets
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

            return json.loads(json_str)
    except Exception as parse_error:
        # Show detailed error for debugging
        st.error(f"Failed to parse Graphiti response: {parse_error}")
        with st.expander("🔍 Debug: Raw Response (click to expand)"):
            st.code(content, language="text")
            st.caption(f"Error details: {type(parse_error).__name__}: {parse_error}")
        return {}


def show_knowledge_graph(inspector):
    """Display Knowledge Graph research tool with entity search and relationship exploration."""
    st.title("🧠 Knowledge Graph Explorer")

    st.markdown("""
    Explore the Graphiti knowledge graph built from RSS news articles. Search for entities
    (people, organizations, locations, events) and discover their relationships.
    """)

    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "Search entities",
            placeholder="e.g., Iran, Microsoft, Trump, oil prices...",
            help="Search for entities in the knowledge graph by name or description"
        )
    with col2:
        max_nodes = st.selectbox("Results", [10, 20, 30], index=1)

    if not query:
        st.info("💡 Enter a search query above to explore the knowledge graph.")

        st.markdown("""
        ### Examples to Try
        - **Geographic entities**: Iran, Israel, China, Middle East
        - **Organizations**: Microsoft, Apple, Tesla, UN
        - **People**: Trump, Biden, Putin, Musk
        - **Topics**: oil, technology, war, economy
        """)
        return

    with st.spinner("🔍 Searching knowledge graph..."):
        try:
            entities = search_entities_cached(query, max_nodes)
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.info("Make sure the Graphiti MCP server is running at http://localhost:8000/mcp/")
            return

    if not entities or (isinstance(entities, dict) and not entities.get('nodes')):
        st.warning(f"No entities found matching '{query}'")
        return

    entity_list = entities.get('nodes', []) if isinstance(entities, dict) else entities

    if not entity_list:
        st.warning(f"No entities found matching '{query}'")
        return

    st.success(f"Found **{len(entity_list)}** entities")
    st.divider()

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


# ============================================================================
# Main App
# ============================================================================

def main():
    """Main application entry point."""
    # Initialize inspector
    inspector = get_inspector()

    # Initialize navigation state (buttons will update this)
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Recent Runs'

    # Sidebar
    with st.sidebar:
        st.title("📊 Audit Dashboard")

        # Navigation - radio widget is display only, buttons control actual navigation
        st.write("### Navigation")

        # Show current page in radio for visual feedback
        page_options = ["Recent Runs", "Run Details", "Step Inspector", "Newsletters", "Knowledge Graph"]
        current_index = page_options.index(st.session_state['current_page'])

        # Radio widget for display/manual navigation
        selected_page = st.radio(
            "Select Page",
            page_options,
            index=current_index,
            label_visibility="collapsed",
            key="page_selector"
        )

        # If user manually changed radio, update current_page
        if selected_page != st.session_state['current_page']:
            st.session_state['current_page'] = selected_page
            st.rerun()

        st.divider()

        # Auto-refresh
        st.write("### Settings")
        auto_refresh = st.checkbox("Auto-refresh", value=False)
        if auto_refresh:
            refresh_interval = st.selectbox(
                "Refresh interval (seconds)",
                [5, 10, 30, 60],
                index=2
            )
            st.info(f"Auto-refreshing every {refresh_interval}s")
            import time
            time.sleep(refresh_interval)
            st.rerun()

        st.divider()

        # Info
        st.write("### About")
        st.caption("RSS Intelligence Workflow Audit System")
        st.caption("Powered by Agno + Streamlit")

    # Main content - route based on current_page
    if st.session_state['current_page'] == "Recent Runs":
        show_recent_runs(inspector)
    elif st.session_state['current_page'] == "Run Details":
        show_run_details(inspector)
    elif st.session_state['current_page'] == "Step Inspector":
        show_step_inspector(inspector)
    elif st.session_state['current_page'] == "Newsletters":
        show_newsletters(inspector)
    elif st.session_state['current_page'] == "Knowledge Graph":
        show_knowledge_graph(inspector)


if __name__ == "__main__":
    main()
