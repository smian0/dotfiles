# Plan: # Streamlit Audit Dashboard Implementation Plan
**Date**: 2025-11-15 08:55
**Status**: Approved, ready for implementation
**Saved by**: PostToolUse hook (ExitPlanMode)

---

# Streamlit Audit Dashboard Implementation Plan

## Overview
Create a simple, intuitive Streamlit app to visualize RSS Intelligence workflow audit data, making it easy to inspect runs, debug issues, and view artifacts.

## What We'll Build

**Single-file Streamlit app** (`audit_dashboard.py`) with 3 main views:

1. **Recent Runs Dashboard** - Overview of workflow executions
2. **Run Details** - Step-by-step execution for a specific run
3. **Step Inspector** - Deep dive into individual steps with artifacts

## Implementation Steps

### Phase 1: Core Setup (15 min)
- Create `audit_dashboard.py` 
- Add Streamlit dependencies to requirements
- Setup page config and navigation
- Import existing `WorkflowAuditInspector` class (reuse, don't duplicate)

### Phase 2: Recent Runs Page (30 min)
- Display recent runs in cards/table format
- Show: Run ID, timestamp, status, version
- Add filters (limit, date range)
- Click to navigate to run details

### Phase 3: Run Details Page (45 min)
- Show run metadata (session_id, workflow_id, timestamps)
- Display step timeline with success/failure indicators
- Show session state summary
- Link to individual step inspection

### Phase 4: Step Inspector Page (45 min)
- Show step details (executor, output, errors, metrics)
- Display artifacts with:
  - JSON: Pretty-print with syntax highlighting
  - Markdown: Rendered view
  - Download buttons
- Show file sizes and paths

### Phase 5: Polish (30 min)
- Add auto-refresh toggle
- Loading spinners
- Error handling
- Responsive layout
- Help tooltips

## Key Features

✅ **Reuses existing audit system** - No database duplication  
✅ **Simple navigation** - Tabs/radio buttons for pages  
✅ **Visual status indicators** - ✅/❌ for step success/failure  
✅ **Artifact preview** - View JSON/MD inline  
✅ **Auto-refresh** - Real-time updates (optional)  
✅ **Download artifacts** - One-click downloads  

## File Structure
```
tools/rss-intelligence/
├── audit_dashboard.py          # NEW - Main Streamlit app (~300 lines)
├── requirements.txt            # UPDATE - Add streamlit, plotly, pandas
├── .audit/
│   └── inspector.py            # REUSE - No changes needed
└── rss_intelligence.db         # EXISTING - Data source
```

## Running the App
```bash
streamlit run audit_dashboard.py
```

## Dependencies to Add
- streamlit >= 1.28.0
- plotly >= 5.17.0
- pandas >= 2.0.0

## Estimated Time
- Core functionality: ~2.5 hours
- Testing & polish: ~30 minutes
- **Total: ~3 hours**

## Success Criteria
Non-technical users can:
- View recent runs at a glance
- Identify failed runs quickly
- Drill into run details
- See step execution flow
- View/download artifacts

---

**Implementation Notes**:
- This plan was approved and saved automatically
- Track progress by updating task checkboxes
- Mark status as "In Progress" or "Completed" as work proceeds
