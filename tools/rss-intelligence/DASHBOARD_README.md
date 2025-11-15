# RSS Intelligence Audit Dashboard

Simple Streamlit web interface for visualizing workflow audit data.

## Quick Start

### 1. Install Dependencies

```bash
# Install Streamlit and visualization libraries
pip install streamlit plotly pandas
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run audit_dashboard.py
```

The app will open in your default browser at `http://localhost:8501`

### 3. Navigate the Dashboard

**Recent Runs Page** (Default view)
- See recent workflow executions
- Filter by workflow type
- Click "View Details" to drill down

**Run Details Page**
- View step-by-step execution timeline
- See success/failure status for each step
- Check session metadata
- Click "Inspect Step Details" for artifacts

**Step Inspector Page**
- View step output and errors
- Preview artifacts (JSON, Markdown)
- Download artifacts
- See execution metrics

## Features

✅ **Visual Status Indicators** - Quick identification of success/failures
✅ **Real-time Data** - Queries live database
✅ **Artifact Preview** - View JSON/Markdown inline
✅ **One-Click Downloads** - Export artifacts easily
✅ **Auto-Refresh** - Optional periodic updates
✅ **Responsive Design** - Works on different screen sizes

## Screenshots

### Recent Runs View
```
📋 Recent Workflow Runs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 20251115_085019 - 2025-11-15 08:50:19
  Workflow: rss-intelligence-test
  Version: 1.0.0-test
  Steps: 2
  [View Details →]
```

### Run Details View
```
🔍 Run Details: 20251115_085019
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Steps Execution Timeline:
  Step 1: fetch_feeds ✅
  Output: Fetched 10 new articles from 5 feeds
  [Inspect Step Details →]

  Step 2: log_rss_articles ✅
  Output: Logged 10 articles to rss_logs/...
  [Inspect Step Details →]
```

### Step Inspector View
```
🔬 Step: log_rss_articles ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Artifacts:
  📄 articles.json (4,233 bytes)
    [JSON Preview]
    [⬇️ Download]
```

## Navigation

**Sidebar Navigation**
- Recent Runs
- Run Details
- Step Inspector

**Auto-Refresh**
- Enable in sidebar
- Choose interval: 5s, 10s, 30s, 60s

## Troubleshooting

### App won't start
```bash
# Check Streamlit installation
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

### Database connection error
- Ensure `rss_intelligence.db` exists
- Check file permissions
- Verify database is not corrupted

### No runs displayed
- Run the workflow first: `python test_audit_system.py`
- Check database has data: `python .audit/inspector.py list`

## Architecture

```
audit_dashboard.py
    ↓
WorkflowAuditInspector (.audit/inspector.py)
    ↓
SQLite Database (rss_intelligence.db)
    ↓
Streamlit UI Rendering
```

**Key Design:**
- Reuses existing `inspector.py` - no code duplication
- Single-file app for simplicity
- Cached database connections for performance
- Handles double-encoded JSON automatically

## Customization

### Change default settings

Edit `audit_dashboard.py`:

```python
# Line 30 - Page config
st.set_page_config(
    page_title="Your Custom Title",  # Change title
    layout="wide",                     # "wide" or "centered"
    initial_sidebar_state="expanded"   # "expanded" or "collapsed"
)

# Line 94 - Default run limit
limit = st.slider("Number of runs to display", 5, 50, 20)  # Change default to 20
```

### Add custom filters

Insert after line 94:

```python
status_filter = st.selectbox("Filter by status", ["All", "Success", "Failed"])
```

## Development

### File structure
```
audit_dashboard.py    # Main app (~400 lines)
requirements.txt      # Dependencies
.audit/
  └── inspector.py    # Database queries (reused)
```

### Adding new pages

1. Create page function:
```python
def show_my_page(inspector):
    st.title("My Custom Page")
    # Your code here
```

2. Add to navigation (line 454):
```python
page = st.radio(
    "Select Page",
    ["Recent Runs", "Run Details", "Step Inspector", "My Custom Page"]
)
```

3. Add routing (line 490):
```python
elif page == "My Custom Page":
    show_my_page(inspector)
```

## Performance Tips

- Use auto-refresh sparingly (30s+ interval recommended)
- Limit number of runs displayed (10-20 is optimal)
- Large artifacts (>1MB) may slow preview - use download instead

## Support

For issues with:
- **Dashboard UI**: Check `audit_dashboard.py`
- **Data not showing**: Check `.audit/inspector.py`
- **Database errors**: Check `rss_intelligence.db`

## Version

- **Dashboard**: 1.0.0
- **Streamlit**: >= 1.28.0
- **Last Updated**: 2025-11-15

---
**Tip**: Keep the dashboard running while workflows execute to see real-time updates!
