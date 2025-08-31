---
name: Streamlit
description: Interactive Streamlit apps with visualizations and drill-downs
---

After completing analysis or data processing tasks, generate complete, self-contained Streamlit applications with interactive visualizations and drill-down capabilities:

## Workflow

1. After you complete the user's request do the following:
2. Understand what data and insights need to be visualized
3. Design an interactive Streamlit application structure
4. Create a complete Python file with all necessary imports and components
5. Save the app to `/tmp/` with a descriptive name and `.py` extension (see `## File Output Convention` below)
6. Provide clear instructions to run the app with `streamlit run`

## Streamlit App Requirements
- Generate COMPLETE Python scripts that run without errors
- Include all necessary imports at the top of the file
- Add proper error handling and data validation
- Create self-contained apps that work without external data files (embed sample data if needed)
- Use modern Streamlit features (columns, containers, tabs, metrics)
- Include docstrings and comments for clarity
- Support both light and dark themes through Streamlit's native theming

## Visual Design Patterns
Apply consistent design patterns to all Streamlit apps:

### Layout Structure
- Use `st.set_page_config()` for page title, icon, and layout settings
- Implement sidebar for navigation and filters
- Use columns for responsive layouts
- Leverage tabs for organizing multiple views
- Include expandable sections for detailed information

### Color Scheme
```python
# Define consistent colors for visualizations
COLORS = {
    'primary': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#2c3e50',
    'secondary': '#95a5a6'
}
```

### Component Patterns
- **Headers**: Use `st.title()`, `st.header()`, `st.subheader()` hierarchy
- **Metrics**: Display KPIs with `st.metric()` including deltas
- **Charts**: Use plotly for interactive visualizations
- **Tables**: Implement `st.dataframe()` with sorting/filtering
- **Filters**: Place in sidebar with `st.sidebar` components
- **Drill-downs**: Use `st.expander()` and `st.tabs()` for detail views

## App Structure Template
```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="[Descriptive Title]",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (optional)
st.markdown("""
<style>
    .stMetric .metric-label { font-size: 14px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📊 [Main Title]")
st.markdown("[Brief description of the dashboard]")

# Sidebar for filters
with st.sidebar:
    st.header("⚙️ Configuration")
    # Add filters, date ranges, selections
    
# Main content area
tab1, tab2, tab3 = st.tabs(["📈 Overview", "🔍 Details", "📊 Analysis"])

with tab1:
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Metric 1", value, delta)
    # ... more metrics
    
    # Visualizations
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Detailed views with drill-downs
    with st.expander("Click to expand details"):
        st.write("Detailed information...")

with tab3:
    # Interactive analysis section
    selected = st.selectbox("Choose analysis:", options)
    # Display corresponding analysis

# Footer
st.markdown("---")
st.caption("Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
```

## Interactive Components

### Data Tables with Drill-down
```python
# Interactive dataframe with selection
selected_rows = st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

if selected_rows.selection.rows:
    selected_index = selected_rows.selection.rows[0]
    st.write("Details for selected row:")
    # Show detailed view
```

### Dynamic Visualizations
```python
# Plotly interactive chart
fig = px.line(df, x='date', y='value', 
              title='Interactive Chart',
              hover_data=['additional_info'])
fig.update_layout(
    hovermode='x unified',
    showlegend=True,
    height=400
)
st.plotly_chart(fig, use_container_width=True)
```

### Session State for Persistence
```python
# Initialize session state
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# Use session state for maintaining user selections
if st.button("Increment"):
    st.session_state.counter += 1
```

## Data Handling

### Caching for Performance
```python
@st.cache_data
def load_data():
    # Expensive data loading operation
    return pd.read_csv('data.csv')

@st.cache_resource
def init_model():
    # Initialize ML model or connection
    return model
```

### Error Handling
```python
try:
    data = process_data()
    st.success("✅ Data processed successfully")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.stop()
```

## File Output Convention
When generating Streamlit apps:
1. Save to the appropriate output directory (e.g., `outputs/<timestamp>/` if available, otherwise `/tmp/`)
2. Use `.py` extension
3. Include timestamp in filename: `streamlit_app_<description>_YYYYMMDD_HHMMSS.py`
4. Provide run command with full path: `streamlit run <full_path>/streamlit_app_<description>_YYYYMMDD_HHMMSS.py`
5. Include port specification if needed: `streamlit run app.py --server.port 8501`
6. When part of a larger analysis, save alongside related outputs for organization

## Response Pattern
1. First, briefly describe what Streamlit app will be generated
2. Create the complete Python file with all code
3. Save to `/tmp/` directory
4. Provide clear run instructions with the exact command
5. Explain key features and how to interact with the app
6. Optionally suggest customizations or extensions

## Key Features to Include
- **Multi-page navigation**: Use tabs or sidebar navigation
- **Interactive filters**: Date ranges, multi-select, sliders
- **Real-time updates**: Use `st.empty()` and `st.container()` for dynamic content
- **Download capabilities**: Add `st.download_button()` for data export
- **Responsive design**: Use columns and containers for layout
- **Progress indicators**: Include `st.progress()` and `st.spinner()` for long operations
- **Help text**: Add tooltips with `help` parameter and `st.info()` boxes

## Example Components

### Metrics Dashboard
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total Revenue",
        value=f"${revenue:,.2f}",
        delta=f"{delta:.1f}%",
        delta_color="normal"
    )
```

### Interactive Filters
```python
with st.sidebar:
    date_range = st.date_input(
        "Select Date Range",
        value=(start_date, end_date),
        min_value=min_date,
        max_value=max_date
    )
    
    categories = st.multiselect(
        "Select Categories",
        options=all_categories,
        default=default_categories
    )
```

### Drill-down Sections
```python
with st.expander("📊 Detailed Analysis", expanded=False):
    tab1, tab2 = st.tabs(["Charts", "Data"])
    with tab1:
        st.plotly_chart(detailed_chart)
    with tab2:
        st.dataframe(detailed_data)
```

## Response Guidelines
- After generating the app: Summarize its features and provide the exact run command
- The response should include:
  - The complete file path: `/tmp/streamlit_app_<description>_YYYYMMDD_HHMMSS.py`
  - The run command: `streamlit run /tmp/streamlit_app_<description>_YYYYMMDD_HHMMSS.py`
  - Key features and how to interact with them
  - Any required dependencies (though try to use only standard libraries + streamlit + plotly)

Always create production-ready Streamlit applications that provide immediate value through interactivity and visual insights.