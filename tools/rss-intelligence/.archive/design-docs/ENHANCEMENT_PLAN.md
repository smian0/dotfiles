# RSS Intelligence Enhancement Plan

**Document Version**: 1.0
**Date**: November 13, 2025
**Status**: Ready for Implementation

## Executive Summary

Based on comprehensive multi-model consensus review (DeepSeek, Qwen, GPT-5), the RSS Intelligence system is **excellent (8/10)** but can achieve **maximum compelling-ness** with two critical enhancements:

1. **Cross-Phase Correlation** - Identifies compound crises (HIGH priority, 2-3 hours)
2. **Network Visualizations** - Shows cascade paths visually (HIGH priority, 4-6 hours)

---

## Phase 1: Cross-Phase Correlation (CRITICAL)

### Problem Statement

Current implementation treats intelligence phases independently:
- Velocity inflection: Shows momentum changes
- Cascade potential: Shows ripple effect risk
- **Missing**: Correlation between velocity and cascade to identify compound crises

**Example Gap:**
```
Russia Kyiv Attack:
- Velocity: 1.8x (EXPLOSIVE) ⚡
- Cascade: 0.75 (HIGH) 📊
- Current: Reported separately
- Missing: COMPOUND CRISIS ALERT 🚨

Valve Gaming:
- Velocity: 1.8x (EXPLOSIVE) ⚡
- Cascade: 0.45 (MODERATE) 📊
- Current: Looks equally urgent
- Missing: MONITOR status (fast but contained)
```

### Solution Design

**Compound Score Formula:**
```
s = p_velocity × p_cascade

Where:
- p_velocity = percentile rank of velocity (0-1)
- p_cascade = percentile rank of cascade score (0-1)
- s = compound crisis score (0-1)
```

**Alert Thresholds:**
- `s ≥ 0.85` → **EXTREME ALERT** 🔴
- `0.70 ≤ s < 0.85` → **HIGH ALERT** 🟠
- `0.50 ≤ s < 0.70` → **MONITOR** 🟡
- `s < 0.50` → **NORMAL** 🟢

### Implementation Steps

#### Step 1.1: Add Percentile Normalization (30 min)

**Location**: `rss_intelligence_workflow.py` - Phase 1 intelligence agent instructions

Add after line 1060 (after Coverage Asymmetry section):

```python
6. CROSS-PHASE CORRELATION (COMPOUND CRISIS DETECTION):
   CRITICAL: This identifies true emergencies by correlating velocity with cascade potential

   a) Collect all entities with velocity and cascade metrics:
      - entities = [{name, velocity_6h, cascade_score}]

   b) Normalize to percentiles (0-1 range):
      - Sort velocity values, assign percentile rank
      - Sort cascade values, assign percentile rank
      - Formula: percentile = (rank - 0.5) / total_count

   c) Compute compound score:
      - compound_score = percentile_velocity × percentile_cascade

   d) Classify alert level:
      - compound_score ≥ 0.85: EXTREME_ALERT
      - compound_score ≥ 0.70: HIGH_ALERT
      - compound_score ≥ 0.50: MONITOR
      - compound_score < 0.50: NORMAL

   e) Generate rationale:
      - "Explosive velocity (p{percentile_velocity:.0%}) + High cascade risk (p{percentile_cascade:.0%})"
      - List top 3 cascade paths contributing to risk

   f) Output format:
      COMPOUND_SCORE: {entity_name}: score={compound_score:.2f}, alert={alert_level}
      - Velocity: {velocity_description} (p{percentile_velocity:.0%})
      - Cascade: {cascade_description} (p{percentile_cascade:.0%})
      - Rationale: {why_this_matters}
      - Top cascade paths: {list_of_paths}
```

#### Step 1.2: Update Newsletter Prompts (30 min)

**Technical Newsletter** - Add after Enhanced Intelligence section (line ~665):

```markdown
8. **🚨 COMPOUND CRISIS ALERTS**

Use "COMPOUND_SCORE" section from Phase 1 intelligence output.

For each EXTREME_ALERT or HIGH_ALERT entity:

**{Alert Level} ({compound_score:.2f}): {Entity Name}**
- **Velocity**: {velocity_description} (percentile {XX}%)
- **Cascade**: {cascade_description} (percentile {XX}%)
- **Why critical**: {Fast-moving AND high-impact explanation}
- **Top cascade paths**: {List top 3 paths with entity names}
- **Action implication**: {What this means for decision-makers}

Example:
**EXTREME ALERT (0.92): Russia-Kyiv Attack**
- **Velocity**: Explosive acceleration (p95) - mentions tripled in 6h
- **Cascade**: High ripple risk (p97) - affects 12+ entities directly, 20+ indirectly
- **Why critical**: Fast-moving AND structurally dangerous = immediate crisis
- **Top cascade paths**:
  1. Ukraine power grid → EU gas prices (economic dependency)
  2. Regional security → NATO response (political escalation)
  3. Humanitarian → International aid (resource strain)
- **Action implication**: Requires immediate attention and response planning
```

**Consumer Newsletter** - Add after "Under the Radar" section (line ~798):

```markdown
## 🚨 CRISIS ALERT BOARD

Translate "COMPOUND_SCORE" section into plain language:

**{Alert Badge}: {Story Name}**
- **What's happening**: {Simple description}
- **Why urgent**: Both fast-moving AND high-impact
- **Speed**: {Velocity in plain language - "Activity tripled in 6 hours"}
- **Reach**: {Cascade in plain language - "Could directly affect 12+ areas"}
- **Chain reaction risk**: {List top 3 cascade paths in plain English}
- **What it means for you**: {Practical implication}

Example:
**🔴 EXTREME CRISIS: Russia's Kyiv Attack**
- **What's happening**: Every district attacked simultaneously
- **Why urgent**: Situation is both escalating rapidly AND has far-reaching consequences
- **Speed**: Attack intensity tripled in past 6 hours
- **Reach**: Directly affects Ukrainian cities, indirectly impacts European security
- **Chain reaction risk**:
  1. Power infrastructure damage → Energy crisis
  2. Security response → Military coordination across Europe
  3. Refugee movement → Humanitarian systems under strain
- **What it means for you**: Major international crisis requiring attention
```

#### Step 1.3: Update Output Format Section (30 min)

**Location**: `rss_intelligence_workflow.py` line ~1200

Add new section before "EMERGING/RECURRING":

```markdown
=== COMPOUND CRISIS SCORING ===

For all entities with both velocity and cascade metrics:

COMPOUND_SCORE:
1. {Entity}: score={0.XX}, alert={EXTREME_ALERT/HIGH_ALERT/MONITOR/NORMAL}
   - Velocity: {description} (p{XX}%)
   - Cascade: {description} (p{XX}%)
   - Rationale: {explanation}
   - Top cascade paths:
     * {Entity A} → {Entity B} ({type})
     * {Entity C} → {Entity D} ({type})
     * {Entity E} → {Entity F} ({type})

Example:
COMPOUND_SCORE:
1. Russia: score=0.92, alert=EXTREME_ALERT
   - Velocity: Explosive acceleration (p95) - 6h activity 3x baseline
   - Cascade: High ripple risk (p97) - 12 direct, 20+ indirect connections
   - Rationale: Fast-moving crisis with structural danger across multiple domains
   - Top cascade paths:
     * Ukraine → European Union (political response)
     * Energy infrastructure → EU gas markets (economic)
     * Humanitarian crisis → NATO (security escalation)
```

#### Step 1.4: Test and Validate (1 hour)

1. Run workflow: `python3 rss_intelligence_workflow.py`
2. Verify Phase 1 intelligence output contains COMPOUND_SCORE section
3. Check newsletters contain Compound Crisis Alerts section
4. Validate scoring logic:
   - High velocity + High cascade = EXTREME/HIGH alert
   - High velocity + Low cascade = MONITOR
   - Low velocity + High cascade = MONITOR

---

## Phase 2: Network Visualizations (HIGH VALUE)

### Problem Statement

Abstract network concepts are hard to understand from text:
- "Cascade potential 0.75" is meaningless without context
- "12 direct connections, 20 indirect" doesn't show the paths
- Readers can't visualize which entities connect to which

### Solution Design

**Visualization Types:**

1. **Cascade Path Diagram** - Shows ripple effect chains
2. **Entity Network Graph** - Shows connection density
3. **Timeline Evolution** - Shows centrality changes over time

### Implementation Steps

#### Step 2.1: Add Visualization Generation (2 hours)

**New file**: `rss_intelligence_workflow.py` - Add visualization step

```python
async def generate_visualizations(step_input: StepInput, session_state: dict) -> StepOutput:
    """Generate network visualizations for top compound crisis alerts."""
    import matplotlib.pyplot as plt
    import networkx as nx
    from datetime import datetime

    intelligence_summary = session_state.get('intelligence_summary', '')

    # Parse compound crisis alerts from intelligence output
    # Extract top 3 EXTREME_ALERT or HIGH_ALERT entities

    visualizations = []

    for entity in top_alerts:
        # Create cascade path diagram
        G = nx.DiGraph()

        # Add center node
        G.add_node(entity['name'], node_type='center')

        # Add cascade paths
        for path in entity['cascade_paths']:
            G.add_edge(path['from'], path['to'],
                      edge_type=path['type'],
                      weight=path['weight'])

        # Layout and render
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Draw nodes
        center_nodes = [n for n, attr in G.nodes(data=True)
                       if attr.get('node_type') == 'center']
        other_nodes = [n for n in G.nodes() if n not in center_nodes]

        nx.draw_networkx_nodes(G, pos, nodelist=center_nodes,
                              node_color='red', node_size=1000, alpha=0.8)
        nx.draw_networkx_nodes(G, pos, nodelist=other_nodes,
                              node_color='lightblue', node_size=500, alpha=0.6)

        # Draw edges with different colors for types
        edge_colors = {'economic': 'green', 'political': 'blue',
                      'security': 'red', 'humanitarian': 'orange'}

        for edge_type, color in edge_colors.items():
            edges = [(u, v) for u, v, attr in G.edges(data=True)
                    if attr.get('edge_type') == edge_type]
            nx.draw_networkx_edges(G, pos, edgelist=edges,
                                  edge_color=color, width=2, alpha=0.6,
                                  arrows=True, arrowsize=20)

        # Labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

        plt.title(f"Cascade Analysis: {entity['name']}\n"
                 f"Compound Score: {entity['score']:.2f} ({entity['alert']})",
                 fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()

        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"visualizations/cascade_{entity['name']}_{timestamp}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        visualizations.append(filepath)

    return StepOutput(
        data={
            'visualization_paths': visualizations
        }
    )
```

#### Step 2.2: Update Newsletter Generation (1 hour)

Add visualization references to newsletter context:

```python
def prepare_newsletter_context(step_input: StepInput, session_state: dict) -> StepOutput:
    intelligence_text = f"""
    # Phase 1 Enhanced Intelligence Insights

    {intelligence_summary}

    # Network Visualizations

    Cascade diagrams available at:
    {', '.join(session_state.get('visualization_paths', []))}

    Include reference to visualizations in Compound Crisis Alerts section:
    "See cascade diagram: visualizations/cascade_Russia_20251113.png"
    """
```

#### Step 2.3: Add to Workflow (30 min)

Insert visualization step after `analyze_knowledge_graph`:

```python
workflow.add_step(
    name="generate_visualizations",
    fn=generate_visualizations,
)
```

#### Step 2.4: Test Visualizations (1 hour)

1. Create `visualizations/` directory
2. Run workflow and verify PNG files are generated
3. Check cascade diagrams show:
   - Center node (red, large)
   - Connected entities (blue, medium)
   - Edge types with different colors
   - Clear labels and title

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Compound score calculation in Phase 1 intelligence output
- ✅ Alert level classification (EXTREME/HIGH/MONITOR/NORMAL)
- ✅ Technical newsletter shows "🚨 Compound Crisis Alerts" section
- ✅ Consumer newsletter shows "🚨 Crisis Alert Board" section
- ✅ Real examples like Russia Kyiv attack show EXTREME_ALERT

### Phase 2 Complete When:
- ✅ Cascade diagrams generated for top 3 alerts
- ✅ PNG files saved to `visualizations/` directory
- ✅ Network graphs show center node + cascade paths
- ✅ Edge types color-coded (economic=green, political=blue, etc.)
- ✅ Newsletter references visualization files

---

## Timeline

**Total Estimated Time**: 6-9 hours

| Phase | Task | Duration | Priority |
|-------|------|----------|----------|
| 1.1 | Add percentile normalization | 30 min | CRITICAL |
| 1.2 | Update newsletter prompts | 30 min | CRITICAL |
| 1.3 | Update output format | 30 min | CRITICAL |
| 1.4 | Test and validate | 1 hour | CRITICAL |
| **Phase 1 Total** | | **2.5 hours** | |
| 2.1 | Visualization generation code | 2 hours | HIGH |
| 2.2 | Update newsletter context | 1 hour | HIGH |
| 2.3 | Add to workflow | 30 min | HIGH |
| 2.4 | Test visualizations | 1 hour | HIGH |
| **Phase 2 Total** | | **4.5 hours** | |

---

## Future Enhancements (Deferred)

These are valuable but not critical for initial compelling newsletter:

### Phase 3: Sentiment Analysis (2-3 days)
- Add transformers library for tone detection
- Track emotional shifts (fear, optimism, urgency)
- Integrate sentiment into compound scoring

### Phase 4: Temporal Decay (1 day)
- Weight recent facts higher than old facts
- Improve relevance scoring over time

### Phase 5: Geographic Intelligence (2-3 days)
- Geospatial clustering for regional hotspots
- Spatial pattern detection

### Phase 6: Entity Clustering (1-2 days)
- Group related entities (Russia + Ukraine + NATO = conflict cluster)
- Simplify network graphs

### Phase 7: Backtesting Framework (3-5 days)
- Historical validation of predictive accuracy
- Confidence intervals for predictions

---

## Risk Mitigation

**Risk**: Percentile normalization fails with small datasets
**Mitigation**: Require minimum 10 entities for compound scoring

**Risk**: Visualization generation crashes workflow
**Mitigation**: Wrap in try-except, continue newsletter generation on failure

**Risk**: Alert thresholds too sensitive (too many EXTREME alerts)
**Mitigation**: Track alert frequency, adjust thresholds if >3 EXTREME per day

**Risk**: Cascade path extraction fails
**Mitigation**: Fall back to simple connection count if path data unavailable

---

## Notes

**Consensus Review Results:**
- DeepSeek: 8/10 confidence, recommended cross-phase correlation + sentiment
- Qwen: 8/10 confidence, recommended cross-phase correlation + geospatial
- GPT-5: Very high confidence, identified cross-phase as highest ROI

**Key Insight**: Current implementation is excellent. Cross-phase correlation is the single fastest path to "most compelling" newsletters.

**Implementation Philosophy**:
- Minimum viable enhancement first (compound scoring)
- Visual comprehension second (cascade diagrams)
- Advanced features deferred until core value proven

---

**Document End**
