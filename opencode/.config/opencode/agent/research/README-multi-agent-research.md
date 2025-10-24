# Multi-Agent Deep Research System

**Version**: 2.1 (with critique-driven iteration)
**Last Updated**: 2025-09-29

## Overview

This is a research system designed for Claude Code that enables comprehensive, multi-source investigations with automatic quality refinement through critique-driven iteration (v2.1 feature).

**v2.1 adds**: After initial synthesis, a critique agent evaluates report quality using a 25-point framework. Reports scoring below "Excellent" (24/25) are automatically revised up to 2 additional times, achieving typical quality scores of 24-25/25.

## Architecture

### Key Constraint
Claude Code subagents cannot use the Task tool to spawn other subagents. This is a fundamental limitation (see GitHub issue #4182).

### Solution: Slash Command Orchestration
The `/research` slash command orchestrates the entire workflow directly. Since slash commands execute in the main conversation context (not as subagents), they can spawn research agents without hitting the nesting limitation.

## The Four Phases

### Phase 0: Archive Initialization (First Use Only)
Automatically creates `.research/` directory in project root with README, config, and .gitignore.

### Phase 1: Planning
**Agent**: `research-planning-agent`
**Model**: Sonnet (cost-effective for planning)
**Input**: Research question/topic
**Output**: Detailed research plan with explicit subagent prompts

The planning agent analyzes the research question and creates:
- Project-based directory structure at `$PROJECT_ROOT/.research/YYYY-MM-DD-topic/`
- 3-7 parallel research streams
- Copy-paste-ready prompts for each web-researcher subagent
- Metadata and tracking files
- Success criteria and validation requirements
- Archive and indexing instructions for Phase 4

### Phase 2: Parallel Research Execution
**Agents**: Multiple `web-researcher` instances
**Model**: Sonnet (efficient for web search/synthesis)
**Input**: Individual research prompts from plan
**Output**: Domain-specific findings files

The parent agent:
1. Reads the research plan from Phase 1
2. Launches multiple web-researcher subagents **in parallel** (single message, multiple Task calls)
3. Each web-researcher investigates a specific domain/aspect
4. Results are saved to separate files in `$PROJECT_ROOT/.research/YYYY-MM-DD-topic/findings/`

**Key**: All web-researcher agents run in parallel for maximum efficiency.

### Phase 3: Synthesis and Validation
**Agents**: `report-synthesizer` + `fact-checker`
**Models**: Opus (synthesis) + Sonnet (fact-checking)
**Input**: All finding files from Phase 2
**Output**: Comprehensive, validated research report

The parent agent:
1. Invokes report-synthesizer to read all findings and create comprehensive report
2. Invokes fact-checker to validate critical claims
3. Updates report if needed based on fact-check results
4. Proceeds to Phase 4 for archival

### Phase 4: Archive and Index
**Actions**: Update metadata, index research, optionally commit to git
**Output**: Permanent, discoverable research archive

The parent agent:
1. Updates metadata.json with completion info and key insights
2. Appends entry to `.research/README.md` index
3. Optionally commits to git (based on config)
4. Presents final report location to user

## Usage Example

### Quick Start: `/research` Slash Command (Recommended)

Use the `/research` command for fully automatic research:

```
/research Claude Code 2.x features
```

The command orchestrates all 4 phases automatically and returns:
```
🎉 Research Complete!

📄 Report: .research/2025-09-29-claude-code-2x-features/final/claude-code-2x-analysis.md
📊 Word Count: 15,234 words
📚 Sources: 200+ sources (72% Grade A, 23% Grade B, 5% Grade C)
🔄 Iterations: 2 synthesis passes
   - Quality Score: 24/25 (Excellent)

Key Findings:
- Revolutionary autonomous features (checkpoints, subagents, hooks)
- Unique MCP architecture with 100+ integrations
- 4x cost premium vs competitors
- Quality crisis resolved but trust impacted
- Best for complex multi-repo projects
```

**Time**: 10-30 minutes for complete research with zero manual steps, including critique-driven iteration.

---

### Advanced: Manual Orchestration

If you need fine-grained control, orchestrate each phase manually:

#### Step 1: Invoke Planning Agent

```
Task(subagent_type="research-planning-agent",
     description="Create research plan for global macro",
     prompt="Create a comprehensive research plan for analyzing current global macroeconomic conditions, including US, Europe, and Asia-Pacific regions, inflation trends, and central bank policies.")
```

**Output**: A detailed research plan with explicit prompts for 5-7 web-researcher subagents, saved at `$PROJECT_ROOT/.research/YYYY-MM-DD-topic/plan.md`.

#### Step 2: Execute Research Streams (Parent Agent)

Based on the plan, the parent agent launches subagents **in a single message**:

```
# In ONE message, call Task tool multiple times:

Task(subagent_type="web-researcher",
     description="Research US economic conditions",
     prompt="""[Detailed prompt from plan for US economy]

     Output to: $RESEARCH_DIR/findings/01-us-economy.md""")

Task(subagent_type="web-researcher",
     description="Research EU economic policy",
     prompt="""[Detailed prompt from plan for EU]

     Output to: $RESEARCH_DIR/findings/02-eu-economy.md""")

Task(subagent_type="web-researcher",
     description="Research Asia-Pacific growth",
     prompt="""[Detailed prompt from plan for APAC]

     Output to: $RESEARCH_DIR/findings/03-apac-economy.md""")

# ... continue for all streams ...
```

**Critical**: All Task calls must be in the same message for parallel execution.

### Step 3: Synthesize Results (Parent Agent)

After all web-researcher agents complete:

```
Task(subagent_type="report-synthesizer",
     description="Synthesize global macro research",
     prompt="""Read all files in $RESEARCH_DIR/findings/ and create a comprehensive report.

**Report Requirements:**
- Executive summary
- Key findings by region
- Inflation and monetary policy analysis
- Risks and opportunities
- Complete citations

**Output to:** $RESEARCH_DIR/final/global-macro-report.md
""")
```

### Step 4: Validate Critical Claims (Parent Agent)

```
Task(subagent_type="fact-checker",
     description="Validate macro data claims",
     prompt="""Validate these critical claims from the report:
- US inflation rate of X%
- Fed funds rate of Y%
- ECB policy stance of Z
[etc.]

**Output to:** $RESEARCH_DIR/validation/fact-check-results.md
""")
```

### Step 5: Archive and Present

Parent agent executes Phase 4 archival steps, then presents final report location.

## Directory Structure

```
<project-root>/
├── .research/                       # Research archive
│   ├── README.md                    # Index of all research
│   ├── config.json                  # Configuration
│   ├── .gitignore                   # Git integration settings
│   │
│   ├── 2025-09-29-ai-coding-agents/
│   │   ├── metadata.json            # Research metadata
│   │   ├── plan.md                  # Phase 1 output
│   │   ├── findings/                # Phase 2 outputs
│   │   │   ├── 01-features.md
│   │   │   ├── 02-adoption.md
│   │   │   ├── 03-performance.md
│   │   │   ├── 04-pricing.md
│   │   │   └── 05-integration.md
│   │   ├── validation/              # Phase 3 validation
│   │   │   └── fact-check.md
│   │   └── final/                   # Phase 3 deliverable
│   │       └── ai-coding-agents-analysis.md
│   │
│   └── 2025-09-15-macro-economics/
│       └── [same structure]
│
└── [your project code]
```

## Agent Roles

### research-coordinator (Recommended Entry Point)
- **Purpose**: Single-command research automation
- **Model**: Sonnet
- **Tools**: TodoWrite, Read, Write, Task, Bash
- **Orchestrates**: All 4 phases automatically
- **Output**: Final report location + summary
- **Use case**: "Just give me the research report"

### research-planning-agent
- **Purpose**: Create actionable research plans
- **Model**: Sonnet
- **Tools**: Read, Write
- **Cannot**: Spawn subagents, do web research
- **Output**: Structured plan with explicit subagent prompts

### web-researcher
- **Purpose**: Universal web research for any domain
- **Model**: Sonnet
- **Tools**: WebSearch, WebFetch, Read, Write
- **Cannot**: Spawn subagents
- **Output**: Domain-specific findings with citations

### report-synthesizer
- **Purpose**: Combine multiple finding files into cohesive report
- **Model**: Opus (needs advanced synthesis)
- **Tools**: Read, Write, Edit
- **Cannot**: Spawn subagents, do web research
- **Output**: Comprehensive research report

### fact-checker
- **Purpose**: Validate critical claims
- **Model**: Sonnet
- **Tools**: WebSearch, WebFetch, Read
- **Cannot**: Spawn subagents
- **Output**: Validation results with confidence levels

## Project-Based Research Archive

### Benefits

**Permanent Storage**
- Research saved in `.research/` within project root
- Survives system reboots (unlike `/tmp`)
- Travels with the codebase when cloned

**Discoverability**
- Chronological naming: `YYYY-MM-DD-topic-slug/`
- Searchable index in `.research/README.md`
- Metadata JSON for programmatic access

**Auditability**
- Complete trail from plan → findings → report
- Fact-check validation results preserved
- Can review research methodology anytime

**Git Integration**
- Three strategies: selective, full, or none
- Default: commit only final reports (`.research/.gitignore`)
- Team can share conclusions without intermediate artifacts

**Context for Future Work**
- Past research informs new investigations
- Avoid duplicating research efforts
- Build on previous findings

### Configuration

Edit `.research/config.json`:
```json
{
  "archive_enabled": true,
  "git_integration": "selective",  // "selective", "full", or "none"
  "auto_index": true,
  "metadata_generation": true
}
```

### Quick Commands

```bash
# View most recent research
cat $(ls -t .research/*/final/*.md | head -1)

# Search all research
rg "keyword" .research/

# List all research projects
ls -1 .research/ | grep -E '^[0-9]{4}-'

# View research index
cat .research/README.md
```

## Why This Architecture Works

### Respects Constraints
- Subagents never spawn other subagents
- Parent agent does all orchestration
- Task tool only used at parent level

### Maximizes Efficiency
- Phase 2 runs in parallel (3-7 concurrent agents)
- Appropriate models for each phase (Sonnet vs Opus)
- Context isolation keeps token usage low

### Ensures Quality
- Structured planning prevents ad-hoc research
- Parallel streams provide comprehensive coverage
- Synthesis step integrates findings coherently
- Fact-checking validates critical claims

### Maintains Traceability
- All intermediate outputs saved to files
- Clear audit trail of research process
- Reproducible methodology

## Comparison to DeepAgents

| Feature | DeepAgents | Claude Code Multi-Agent |
|---------|-----------|------------------------|
| Subagent spawning | Coordinator spawns others | Parent orchestrates all |
| Planning | Coordinator decides | Dedicated planning agent |
| Execution | Coordinator delegates | Parent launches in parallel |
| Synthesis | Coordinator combines | Dedicated synthesis agent |
| Architecture | Hierarchical (tree) | Flat (parent + children) |

## Best Practices

### DO:
- ✅ Launch all Phase 2 agents in a single message (parallel execution)
- ✅ Use research-planning-agent for complex queries
- ✅ Save all intermediate outputs to files
- ✅ Invoke fact-checker before finalizing reports
- ✅ Use appropriate models (Sonnet for research, Opus for synthesis)

### DON'T:
- ❌ Try to have subagents spawn other subagents (won't work)
- ❌ Launch Phase 2 agents sequentially (wastes time)
- ❌ Skip the planning phase for complex research
- ❌ Forget to validate critical claims
- ❌ Use Opus for simple web research (expensive)

## Troubleshooting

### Problem: Agents not executing in parallel
**Solution**: Ensure all Task calls are in the same message block.

### Problem: Planning agent trying to spawn subagents
**Solution**: Update agent file - it should only create a plan, not execute it.

### Problem: Web-researcher not finding relevant info
**Solution**: Make prompts more specific in the research plan.

### Problem: Report missing key information
**Solution**: Add more research streams in Phase 2, or improve prompts.

### Problem: Fact-checker contradicting report claims
**Solution**: This is working as intended - update the report based on validation.

## Performance Characteristics

### Token Efficiency
- Planning phase: ~5-10K tokens (Sonnet)
- Each research stream: ~10-20K tokens (Sonnet)
- Synthesis: ~20-40K tokens (Opus)
- Fact-checking: ~5-15K tokens (Sonnet)

**Total for 5-stream research**: ~100-150K tokens
**Compared to monolithic approach**: 90-95% savings

### Time Efficiency
- Planning: 30-60 seconds
- Research (parallel): 2-5 minutes (vs 10-25 minutes sequential)
- Synthesis: 1-3 minutes
- Fact-checking: 1-2 minutes

**Total**: 5-11 minutes for comprehensive research

### Quality Metrics
- Coverage: Excellent (multiple parallel perspectives)
- Accuracy: High (dedicated fact-checking)
- Depth: Comprehensive (specialized agents per domain)
- Coherence: Strong (dedicated synthesis)

## Future Enhancements

Possible improvements:
1. **Iterative refinement**: Add Phase 4 for follow-up questions
2. **Domain-specific agents**: Create specialized researchers (finance, tech, policy)
3. **Multi-format output**: Add agents for slides, visualizations, summaries
4. **Continuous monitoring**: Long-running research projects
5. **Cross-project synthesis**: Connect findings across multiple research sessions

## Files

- `/Users/smian/dotfiles/claude/.claude/agents/research-planning-agent.md`
- `/Users/smian/dotfiles/claude/.claude/agents/web-researcher.md`
- `/Users/smian/dotfiles/claude/.claude/agents/report-synthesizer.md`
- `/Users/smian/dotfiles/claude/.claude/agents/fact-checker.md`

All symlinked to `~/.claude/agents/` for use in any session.

## License

Part of the Claude Code agent ecosystem. Use and modify freely.

---

**Last Updated**: 2025-09-29
**Architecture Version**: 1.0 (Parent-orchestrated, three-phase)