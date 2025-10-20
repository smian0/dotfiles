# Phase 0 Initialization Protocol

## Step 0.1: Get Current Date/Time (CRITICAL)

**Before starting any research**, get the current timestamp:

```bash
date "+%Y-%m-%d %H:%M:%S %Z"
```

**Use this timestamp for**:
- All file headers and metadata
- Ensuring searches are time-appropriate (don't search for future data)
- Including "as of [DATE]" context in findings
- Timestamping all reports and outputs

## Step 0.2: Parse Research Question

Analyze the user's research question to identify:

1. **Primary research question** - The core question to answer
2. **Key dimensions** - Different perspectives or angles to explore
3. **Depth level** - Default: deep (15-20 sources per stream)
4. **Stream count** - Default: 4 parallel streams (range: 3-5)

### Example: "Why is crypto suffering?"

**Dimensions identified**:
- Market analysis & price trends
- Regulatory & policy impact
- Economic & macro factors
- Industry events & technology

**Stream allocation**:
- Stream 1: Market analysis
- Stream 2: Regulatory impact
- Stream 3: Economic factors
- Stream 4: Industry events

## Step 0.3: Initialize Research Workspace

Create organized directory structure:

```bash
# Option 1: Use script
./phases/0-initialization/workspace-setup.sh

# Option 2: Manual
mkdir -p ./research-output/{progress,sources,analysis,report}
```

## Step 0.4: Create Coordinator Status File

Generate tracking file at `./research-output/progress/coordinator-status.md`:

Use template from `assets/coordinator-status.template.md` and fill in:
- research_question
- streams (number)
- depth level
- started timestamp
- initial status: discovery_phase

## Validation Checklist

Before proceeding to Phase 1:

- [ ] Timestamp obtained and recorded
- [ ] Research question parsed and dimensions identified
- [ ] Stream count determined (3-5)
- [ ] Workspace directories created
- [ ] Coordinator status file generated
- [ ] All streams have clear focus areas defined

## Common Pitfalls

1. **Skipping timestamp** - Always get timestamp first!
2. **Unclear dimensions** - Ensure research angles are distinct and comprehensive
3. **Too many streams** - More than 5 streams creates coordination overhead
4. **Too few streams** - Less than 3 streams may miss important perspectives
5. **Overlapping streams** - Each stream should have unique focus

## Transition to Phase 1

Once initialization complete:
→ Proceed to Phase 1: Discovery (Parallel)
