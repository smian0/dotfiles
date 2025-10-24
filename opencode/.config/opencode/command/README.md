# Claude Code Commands

This directory contains commands organized by purpose:
- **`trading/`** - Stock trading and market analysis commands
- **`research/`** - Research tools and templates
- **`dev/`** - Development and meta-framework tools
- **`tools/`** - General utility commands

Commands coordinate multiple agents to execute complex workflows automatically.

## Available Orchestrators

### `/research` - Research System Orchestrator
**Purpose**: Conduct comprehensive multi-source research with automatic quality refinement

**What it orchestrates** (from `agents/research/`):
- `research-planning-agent` - Creates structured research plans
- `web-researcher` - Executes parallel research streams
- `report-synthesizer` - Consolidates findings into reports
- `report-critique-agent` - Validates quality and iterates

**Example Usage**:
```bash
/research What are the latest developments in quantum computing error correction?
```

**Key Features**:
- v2.1 with critique-driven iteration (max 3 synthesis passes)
- Parallel research stream execution
- Evidence grading (A/B/C/D)
- Source diversity validation
- Automatic archiving to `.research/`

**Typical Runtime**: 8-15 minutes for 3-5 stream research

---

### `/multi-agent` - Multi-Agent System Generator
**Purpose**: Generate complete multi-agent systems for any domain with automatic validation

**What it orchestrates** (from `agents/meta/`):
- `domain-analyzer` - Analyzes domain patterns and requirements
- `context-architect` - Designs context management structure
- `orchestrator-builder` - Creates command coordination logic
- `parallel-coordinator` - Designs safe parallel execution
- `meta-multi-agent` - Generates actual system files

**Example Usage**:
```bash
/multi-agent Create a multi-agent system for restaurant kitchen management that handles order processing, station coordination, inventory tracking, and quality control
```

**Key Features**:
- Generates complete `.claude` directory structure
- Creates orchestrator commands + specialist agents
- Generates coordination rules and context docs
- YAML syntax validation
- Conflict prevention checks
- Produces usage documentation

**Typical Runtime**: 2-5 minutes for typical systems

---

### `/deep-stock-research` - Stock Analysis Orchestrator
**Purpose**: Execute stock research with multiple analysis types (comprehensive, swing trading, daily updates)

**What it orchestrates**:
- Multi-turn Perplexity queries across 5 dimensions (Fundamentals, Catalysts, Technical, Risks, Outlook)
- Browser automation via `comet-devtools` MCP (Comet Browser on port 9223)
- Audit trail creation (query, response, metadata preservation)
- Multi-stock portfolio consolidation

**Example Usage**:
```bash
# Comprehensive deep research (6-8 Perplexity queries)
/deep-stock-research NVDA

# Focused swing trading analysis
/deep-stock-research LSCC --type=swing-trading

# Daily technical update with audit trail
/deep-stock-research AMBA --type=daily-update

# Multi-stock portfolio - reads tickers from CSV file (RECOMMENDED)
/deep-stock-research --portfolio=AI-chips-hidden-gems --type=daily-update

# Multi-stock portfolio - explicit tickers (still creates consolidated summary)
/deep-stock-research LSCC,AMBA,BRCHF,GSIT --type=daily-update --portfolio=AI-chips-hidden-gems
```

**Key Features**:
- **Research Types**: Comprehensive (default), swing trading, daily updates
- **CSV Portfolio Files**: Define stock lists in `~/dotfiles/research/stocks/portfolios/{name}.csv`
- **Audit Trails**: Full transparency with raw query/response preservation
- **Consolidated Summaries**: Multi-stock portfolio aggregation with action priorities
- **Browser Automation**: Direct Perplexity Finance page interaction via MCP
- **Automatic Archiving**: Saves to `~/dotfiles/research/stocks/YYYY-MM/`

**Outputs**:
- **Daily Update**: `daily-update_YYYY-MM-DD.md` + audit trail (3 files)
- **Portfolio Summary**: `daily-summary_YYYY-MM-DD.md` (multi-stock only)
- **Comprehensive Research**: `comprehensive-research_YYYY-MM-DD.md`

**Typical Runtime**:
- Daily update: 2-4 minutes (single query)
- Swing trading: 5-10 minutes (3-4 queries)
- Comprehensive: 15-25 minutes (6-8 queries)
- Multi-stock daily: 8-16 minutes (4 stocks × 2-4 min)

**Documentation**: See `~/dotfiles/research/stocks/CLAUDE.md` for detailed workflow

---

### `/flight-search` - Flight Search Command
**Purpose**: Search for flights using Google Flights with predefined preferences

**What it does**:
- Searches Google Flights with specific filters (Economy exclude Basic, nonstop only, United Airlines)
- Provides flexible date and route options
- Returns formatted flight information with prices, times, and details

**Example Usage**:
```bash
# Basic search
/flight-search Find flights from MCO to SFO in December 2025

# With city names
/flight-search Search for flights from Orlando to San Francisco in December 2025

# With specific return date
/flight-search Look for flights from JFK to LAX in January 2026 returning January 10, 2026

# One-way flight
/flight-search Find one-way flights from Chicago to Miami in February 2025
```

**Key Features**:
- Economy (exclude Basic) class by default
- Nonstop flights only
- United Airlines only
- Flexible date ranges (full month or specific dates)
- Handles both airport codes and city names
- Provides price insights and booking recommendations

**Output Format**:
```
## United Airlines Nonstop Flights from [ORIGIN] to [DESTINATION] in [MONTH] [YEAR]
### Economy (Exclude Basic) Fares

1. **$[PRICE] round trip** - [DATE]
   - Departure: [TIME] from [ORIGIN] ([ORIGIN_CODE])
   - Arrival: [TIME] at [DESTINATION] ([DESTINATION_CODE])
   - Duration: [DURATION]
   - Includes: [BAGGAGE_INFO]

### Additional Information:
- [NUMBER] nonstop flight options available
- Price insights: [PRICE_INSIGHTS]
- Booking recommendations: [BOOKING_RECOMMENDATIONS]
- Alternative dates: [ALTERNATIVE_DATES]
```

**Implementation Files**:
- `flight-search.md` - Command definition and usage
- `flight-search-implementation.md` - Detailed Chrome automation steps
- `flight-search-example.md` - Usage examples and expected outputs

**Typical Runtime**: 1-2 minutes

---

## Pattern Comparison

All orchestrators follow the same architectural pattern:

| Phase | `/research` | `/multi-agent` | `/deep-stock-research` | `/flight-search` |
|-------|-------------|----------------|------------------------|-----------------|
| **Input** | Research question | Domain description | Stock ticker(s) + type | Flight search request |
| **Planning** | research-planning-agent | domain-analyzer + orchestrator-builder | Query formulation (adaptive) | Parse route and dates |
| **Execution** | Parallel web-researcher agents | Sequential file generation | Browser automation (Perplexity) | Chrome automation (Google Flights) |
| **Quality** | report-critique-agent (iterative) | YAML + structure validation | Audit trail preservation | Filter validation + result formatting |
| **Output** | Research report in `.research/` | Working system in `.claude/` | Stock analysis in `research/stocks/` | Formatted flight results |
| **Tracking** | TodoWrite (6 phases) | TodoWrite (9 phases) | TodoWrite (varies by type) | Not applicable (single operation) |

## Design Principles

### 1. Full Automation
Both commands execute end-to-end without manual intervention:
- User provides input → System delivers output
- No confirmation prompts between phases
- All orchestration logic is internal

### 2. Phased Execution
Clear phases with validation checkpoints:
- Pre-flight: Validate input quality
- In-flight: Monitor execution correctness
- Post-flight: Verify output meets standards

### 3. Parallel Execution When Safe
- `/research`: Parallel web-researcher streams (no conflicts)
- `/multi-agent`: Sequential generation (file system safety)
- `/deep-stock-research`: Sequential per-stock (browser state), parallel for multi-stock portfolios

### 4. Quality Gates
- `/research`: Evidence grading, source diversity, critique iteration
- `/multi-agent`: YAML syntax, structure validation, coordination checks
- `/deep-stock-research`: Audit trail preservation, multi-stock consolidation, entry zone validation

### 5. Progress Visibility
All use TodoWrite extensively:
- Users see phase transitions
- Clear status on what's happening
- Failures are obvious

### 6. Concise Results
None dump full content:
- `/research`: Location + summary + key findings
- `/multi-agent`: Location + structure + usage guide
- `/deep-stock-research`: Summary table + file locations + action priorities

## Creating New Orchestrators

To create a new orchestration command:

1. **Identify the workflow**: What phases are needed?
2. **Map the agents**: Which specialist agents will execute?
3. **Design coordination**: Sequential or parallel execution?
4. **Define validation**: What makes output "good"?
5. **Plan error handling**: What can go wrong and how to recover?

**Template Structure**:
```markdown
---
title: [Orchestrator Name]
description: [One-line purpose]
category: [Category]
---

# [Orchestrator Name] Command

You are a [workflow] coordinator...

## Critical Rules
- Execute ALL phases automatically
- Use TodoWrite for progress tracking
- Run validation checkpoints
- Be concise in final output

## Workflow Execution

### Step 0: Get Current Date/Time
### Step 1: Parse Input & Create Plan
### Step 2: [Domain-Specific Phase]
### Step 3: [Execution Phase]
### Step 4: [Quality Phase]
### Step 5: [Output Phase]

## Error Handling
## Success Criteria
```

## Agent Organization

Agents are organized by system in subdirectories:

```
.claude/agents/
├── meta/               # Meta-framework agents (system generation)
│   ├── domain-analyzer.md
│   ├── context-architect.md
│   ├── orchestrator-builder.md
│   ├── parallel-coordinator.md
│   ├── meta-multi-agent.md
│   ├── meta-sub-agent.md
│   └── README.md
│
├── research/           # Research system agents
│   ├── research-planning-agent.md
│   ├── web-researcher.md
│   ├── report-synthesizer.md
│   ├── report-critique-agent.md
│   ├── fact-checker.md
│   └── research-planner.md
│
└── [domain]/          # Domain-specific agents (e.g., restaurant/)
    └── [specialist agents generated by /multi-agent]
```

## Comparison with Agent Files

| Type | Location | Purpose | Execution |
|------|----------|---------|-----------|
| **Command** | `.claude/commands/*.md` | Orchestrate workflow | User invokes with `/command` |
| **Agent** | `.claude/agents/[system]/*.md` | Specialist capability | Spawned by commands via `Task` tool |

**Key Difference**:
- Commands drive the workflow (the conductor)
- Agents perform specialized work (the musicians)
- Agents are grouped by the system they belong to

## Testing New Orchestrators

Before committing a new orchestrator:

1. **Syntax check**: Validate YAML frontmatter
   ```bash
   head -10 commands/new-command.md | grep -q "^---$"
   ```

2. **Pattern check**: Ensure TodoWrite usage
   ```bash
   grep -q "TodoWrite" commands/new-command.md
   ```

3. **Dry run**: Test with simple input
   ```bash
   /new-command test-scenario
   ```

4. **Validation check**: Verify quality gates work
   - Do they catch bad input?
   - Do they prevent bad output?

5. **Documentation**: Ensure usage is clear
   - Examples provided?
   - Expected runtime noted?
   - Error cases covered?

## Maintenance

When updating orchestrators:

- **Preserve backward compatibility**: Existing usage patterns should keep working
- **Version breaking changes**: If changing interface, consider new command
- **Update this README**: Document new features or behavior changes
- **Test end-to-end**: Full workflow, not just modified phase

---

**Framework Version**: v1.0
**Last Updated**: 2025-09-29
**Pattern Source**: Based on `/research` v2.1 architecture
