# Wheel Dashboard Workflow Redesign

## Current Structure (Confusing)
```
Home (wheel_app.py) → Detailed options analysis
├─ Page 1: Advanced Analytics
└─ Page 2: Market Discovery
```

## Proposed Pipeline Structure (Intuitive)

### Phase 1: DISCOVER 🔍
**Goal:** Find high-probability wheel opportunities
**Page:** `01_🔍_Discover.py` (rename Market Discovery)
**User Action:** Scan market → shortlist candidates
**Outputs:**
- Top 10 gems with discovery scores
- Export shortlist to session state

### Phase 2: ANALYZE 📊
**Goal:** Deep dive on shortlisted stocks
**Page:** `02_📊_Analyze.py` (rename Advanced Analytics)
**User Action:** Review fundamentals, technicals, insider activity
**Inputs:** Shortlist from Phase 1
**Outputs:**
- Quality scores
- Risk metrics (beta, volatility)
- Conviction level per ticker

### Phase 3: EXECUTE 🎯
**Goal:** Find optimal strikes and size positions
**Page:** `03_🎯_Execute.py` (current home page logic)
**User Action:** Configure trade parameters
**Inputs:** Final candidates from Phase 2
**Outputs:**
- Specific strike recommendations
- Premium calculations
- Position sizing based on risk tolerance

### Phase 4: MONITOR 📈
**Goal:** Track open positions and roll decisions
**Page:** `04_📈_Monitor.py` (NEW - portfolio view)
**User Action:** Review P&L, manage rolls
**Inputs:** Active wheel positions
**Outputs:**
- Position Greeks
- Roll vs assignment decisions
- Performance attribution

## Home Page (Overview Dashboard)
**New `wheel_app.py`:**
- Market status widget
- Workflow progress tracker
- Quick stats (positions, P&L, next actions)
- "Start Workflow" button → Navigate to Discover

## Workflow State Management
Use `st.session_state` to track:
- `shortlist`: Tickers from Discover
- `analyzed_tickers`: Tickers analyzed with conviction scores
- `pending_trades`: Configured trades ready for execution
- `active_positions`: Open wheel positions

## Navigation Guidance
Each page shows:
```
┌─────────────────────────────────────────────┐
│ 🔍 DISCOVER → 📊 ANALYZE → 🎯 EXECUTE → 📈 MONITOR │
│      ✅           (current)      ⚪          ⚪      │
└─────────────────────────────────────────────┘
```

Plus:
- "Next: Analyze →" button (when ready)
- Breadcrumb showing progress
- Clear call-to-action at each step

## Session State Flow
```python
# Discover page
st.session_state['shortlist'] = [list of tickers]
st.session_state['gems'] = [HiddenGem objects]

# Analyze page reads shortlist
if 'shortlist' not in st.session_state:
    st.warning("⚠️ No shortlist found. Start with Discover page.")

# Execute page reads analyzed candidates
if 'analyzed_tickers' not in st.session_state:
    st.warning("⚠️ Analyze candidates first.")
```

## Benefits
1. **Linear progression** - No confusion about where to start
2. **Context preservation** - Data flows between pages
3. **Decision focus** - Each page has ONE clear objective
4. **Actionable** - Always know next step
5. **Comprehensive yet simple** - Complexity is staged

## Implementation Plan
1. Rename existing pages with new numbers
2. Rewrite home page as dashboard/launcher
3. Add workflow progress component
4. Implement session state management
5. Create Monitor page for portfolio tracking
6. Add navigation buttons between phases
