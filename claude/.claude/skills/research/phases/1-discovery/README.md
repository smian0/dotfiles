# Phase 1: Discovery (PARALLEL)

**Execution**: ⚡ **PARALLEL** ⚡
**Duration**: 5-15 minutes per stream
**Dependencies**: Phase 0 complete

## Overview

**CRITICAL**: This phase executes **MULTIPLE AGENTS IN PARALLEL** using the Task tool.

Spawn 3-5 web-researcher agents simultaneously, each exploring a different research angle. This parallelization significantly reduces total research time.

## Execution Pattern

**⚡ PARALLEL EXECUTION - Single Message with Multiple Task Calls ⚡**

```python
# CRITICAL: Call ALL Task tools in SINGLE message
# This ensures parallel execution

# Task 1: Stream 1
Task(subagent_type="web-researcher", ...)

# Task 2: Stream 2
Task(subagent_type="web-researcher", ...)

# Task 3: Stream 3
Task(subagent_type="web-researcher", ...)

# Task 4: Stream 4
Task(subagent_type="web-researcher", ...)

# All execute simultaneously ⚡
```

## Default Configuration

- **Stream count**: 4 parallel streams
- **Sources per stream**: 10-20 quality sources
- **Source credibility**: A/B/C tier classification
- **Source diversity**: Primary, secondary, geographic

## Stream Responsibilities

Each stream focuses on one dimension of the research question:

- **Stream 1**: Primary angle (most critical dimension)
- **Stream 2**: Secondary angle (supporting perspective)
- **Stream 3**: Tertiary angle (contextual factors)
- **Stream 4**: Fourth angle (often contrarian or niche view)

## Outputs

Each stream produces:
- `./research-output/sources/stream-[N]-sources-YYYY-MM-DD.md`

Contains:
- Executive summary (3-5 bullets)
- 10-20 quality sources with credibility tiers
- Key findings with specific data points
- Relevant quotes and context

## Research Rigor Requirements

Each web-researcher agent MUST use:

1. **Multiple search queries** - Different angles on the same topic
2. **Adversarial search** - Test contrary perspectives
3. **Source diversity** - Not just top results
4. **Primary source prioritization** - Official data, government docs
5. **Date verification** - Ensure current information

## Quality Gates

Before proceeding to Phase 2:

- [ ] All streams completed successfully (minimum 2 required)
- [ ] Each stream has 10-20 sources
- [ ] Source credibility tiers assigned (A/B/C)
- [ ] Specific data points with dates included
- [ ] Geographic/institutional diversity achieved

## Common Pitfalls

1. **Sequential execution** - Calling Task tools in separate messages (SLOW!)
2. **Insufficient sources** - Less than 10 sources per stream
3. **Source overlap** - Multiple streams citing same sources
4. **Missing dates** - Data points without temporal context
5. **Low credibility** - Too many C-tier sources

## Transition to Phase 2

Once all discovery streams complete:
→ Proceed to Phase 2: Validation (Sequential)

## Related Files

- `protocol.md` - Detailed discovery protocol
- `prompts/web-researcher.md` - Template for web-researcher agent prompts
