# Plan: Add a "Newsletters" page to the Streamlit audit dashboard to display final newsletter results with rendered markdown.
**Date**: 2025-11-15 09:54
**Status**: Approved, ready for implementation
**Saved by**: PostToolUse hook (ExitPlanMode)

---

Add a "Newsletters" page to the Streamlit audit dashboard to display final newsletter results with rendered markdown.

## Implementation Summary

**Single file to modify:** `audit_dashboard.py`

**Changes:**
1. Add "Newsletters" to navigation options (line ~408)
2. Add 3 new functions (~200 lines total):
   - `show_newsletters(inspector)` - Main page with run selector, tabs, and metadata
   - `get_runs_with_newsletters(inspector)` - Hybrid discovery (filesystem + audit correlation)
   - `display_newsletter(path, newsletter_type)` - Markdown rendering with download button
3. Add routing for Newsletters page (line ~443)

## Key Features

**Newsletter Discovery (Hybrid Approach):**
- Scans `newsletters/` directory for all newsletter files
- Matches to audit runs via timestamp correlation
- Falls back to filesystem-only if audit data missing
- Returns sorted list (newest first) with metadata

**User Interface:**
- Summary metrics (total runs, last 24h, complete pairs)
- Dropdown selector with formatted timestamps and age
- Two-tab layout (Technical/Consumer newsletters)
- Metadata display (file size, word count, last modified)
- Download buttons for both newsletter types
- Proper markdown rendering with `st.markdown()`

**Error Handling:**
- Missing newsletter files → shows warning with expected path
- Orphaned newsletters → works without audit data
- Corrupted content → shows preview of raw text
- Partial data (only one newsletter) → graceful degradation

## Benefits

✅ Robust: Works even if audit data incomplete  
✅ User-friendly: Clear navigation, tabs, download buttons  
✅ Performance: Efficient filesystem scan  
✅ Scalable: Handles 50+ newsletter runs  
✅ Integrates seamlessly with existing 3-page dashboard

---

**Implementation Notes**:
- This plan was approved and saved automatically
- Track progress by updating task checkboxes
- Mark status as "In Progress" or "Completed" as work proceeds
