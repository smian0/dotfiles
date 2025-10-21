# Architecture Decision Matrix

This reference provides detailed criteria for determining whether to create a simple skill (Level 1), a skill with subagent delegation (Level 2), or a complete multi-agent system (Level 3).

## Decision Framework

### Level 1: Simple Skill

**Create a traditional skill when:**

#### Workflow Characteristics
- ✅ Single-phase, linear workflow
- ✅ Sequential steps with clear order
- ✅ No parallel execution benefits
- ✅ Workflow completes in one session

#### Complexity Indicators
- ✅ One domain of expertise
- ✅ Clear, deterministic operations
- ✅ Repeatable patterns
- ✅ No need for external research or validation

#### State Management
- ✅ Minimal state tracking
- ✅ No intermediate results to coordinate
- ✅ Each execution is independent

#### Resource Needs
- ✅ Scripts for deterministic operations
- ✅ References for domain knowledge
- ✅ Assets for templates/boilerplate

**Examples:**
- PDF editor (rotate, merge, split)
- Image processor (resize, crop, convert)
- Code formatter (style enforcement)
- Document template generator
- Configuration file validator

**Output:** Traditional skill with SKILL.md + bundled resources

---

### Level 2: Skill with Subagent Delegation

**Create a skill with delegation when:**

#### Workflow Characteristics
- ✅ Primarily single-phase
- ✅ Main workflow is straightforward
- ✅ Occasional need for specialized tasks
- ✅ Skill maintains overall control

#### Complexity Indicators
- ✅ One primary domain
- ✅ Occasional complex sub-tasks:
  - Deep research (multi-source analysis)
  - Security validation
  - Performance analysis
  - Code review
  - Documentation lookup
- ✅ Sub-tasks are separable and async
- ✅ Can proceed after delegation completes

#### State Management
- ✅ Simple state: skill's workflow state
- ✅ Passes context to subagent
- ✅ Receives results and continues
- ✅ No complex coordination needed

#### Delegation Triggers
Ask: "Does this skill need to:"
- 📚 **Research:** Multi-source documentation lookup, API exploration, best practices discovery
- 🔒 **Validate:** Security audit, compliance check, code quality review
- ⚡ **Analyze:** Performance bottlenecks, root cause analysis, comparative evaluation
- 🧪 **Test:** Integration testing, scenario validation, edge case discovery

**If yes to ANY, consider Level 2.**

**Examples:**
- MCP server builder
  - *Main workflow:* Guide through server creation
  - *Delegation:* Deep API documentation research
- Code reviewer with security focus
  - *Main workflow:* Standard code review process
  - *Delegation:* Specialized security vulnerability analysis
- Documentation generator
  - *Main workflow:* Extract and format documentation
  - *Delegation:* Research best practices for specific framework
- Infrastructure provisioner
  - *Main workflow:* Create infrastructure configs
  - *Delegation:* Validate security and compliance

**Output:** Skill with SKILL.md + bundled resources + delegation patterns

---

### Level 3: Multi-Agent System

**Delegate to meta-multi-agent when:**

#### Workflow Characteristics
- ✅ Multi-phase process (2+ distinct phases)
- ✅ Each phase has clear inputs/outputs
- ✅ Phases can run in parallel
- ✅ Phases may have different completion times

#### Complexity Indicators
- ✅ 3+ specialist roles needed
- ✅ Each specialist has distinct expertise
- ✅ Specialists work concurrently
- ✅ Results must be synthesized
- ✅ Coordination protocols required

#### State Management
- ✅ Complex state across phases
- ✅ Intermediate results shared between specialists
- ✅ Progress tracking per specialist
- ✅ Conflict resolution needed
- ✅ State persists across sessions

#### Coordination Needs
- ✅ File access coordination
- ✅ Communication protocols
- ✅ Synchronization points
- ✅ Error escalation paths
- ✅ Human oversight points

**Examples:**
- Trading analysis system
  - *Specialists:* Daily chart analyst, 4-hour analyst, 1-hour analyst, confluence coordinator
  - *Parallel:* Each timeframe analyzed concurrently
  - *Coordination:* Results synthesized for high-confidence levels
- Research pipeline
  - *Specialists:* Data collector, analyzer, fact-checker, report writer
  - *Phases:* Collection → Analysis → Validation → Synthesis
  - *State:* Research findings, sources, validations
- Complex automation workflow
  - *Specialists:* Planning agent, execution agents (parallel), validation agent
  - *Coordination:* Task distribution, progress tracking, result consolidation

**Output:** Complete `.claude/` structure with commands, agents, rules, context files

---

## Decision Tree

```
Start: User wants to create capability
│
├─ Does it need 3+ specialist roles working concurrently?
│  YES → Level 3: Delegate to meta-multi-agent
│  NO  → Continue
│
├─ Does it need occasional specialized help (research/validation)?
│  YES → Level 2: Skill with delegation
│  NO  → Continue
│
└─ Is it a linear, single-domain workflow?
   YES → Level 1: Simple skill
```

---

## Common Patterns

### Level 1 Patterns
- **Script-heavy:** Deterministic operations (PDF processing, image manipulation)
- **Reference-heavy:** Domain knowledge application (compliance checker, schema validator)
- **Asset-heavy:** Template generation (project scaffolding, document creation)

### Level 2 Patterns
- **Research-augmented:** Needs documentation lookup (MCP builder, API integrator)
- **Validation-augmented:** Needs specialized checks (security reviewer, compliance validator)
- **Analysis-augmented:** Needs deep analysis (performance optimizer, architecture reviewer)

### Level 3 Patterns
- **Parallel-processing:** Multiple specialists work simultaneously (trading analysis, content generation pipeline)
- **Multi-phase:** Distinct sequential phases with different specialists (research → analysis → synthesis)
- **Hierarchical:** Coordinator + workers pattern (task distribution, parallel execution)

---

## Red Flags: Wrong Architecture Choice

### Symptoms of Under-Engineering (Chose Level 1, should be Level 2)
- ⚠️ SKILL.md keeps saying "research the API documentation thoroughly"
- ⚠️ Instructions include "analyze multiple sources and compare"
- ⚠️ Requires validation that Claude performs inconsistently
- ⚠️ High token usage on repetitive research tasks

**Fix:** Upgrade to Level 2, delegate research/validation to specialized agents

### Symptoms of Under-Engineering (Chose Level 2, should be Level 3)
- ⚠️ Multiple specialists mentioned in skill instructions
- ⚠️ Instructions say "analyze from different perspectives"
- ⚠️ Natural parallelization opportunities ignored
- ⚠️ Complex coordination logic in SKILL.md

**Fix:** Delegate to meta-multi-agent to create proper multi-agent system

### Symptoms of Over-Engineering (Chose Level 3, should be Level 2)
- ⚠️ Only 1-2 specialists actually needed
- ⚠️ No real parallel execution opportunities
- ⚠️ Simple sequential workflow
- ⚠️ Coordination overhead exceeds benefits

**Fix:** Simplify to Level 2 with delegation or Level 1 if no delegation needed

---

## Quick Assessment Questions

Ask user these rapid-fire questions:

1. **"How many different specialist roles or perspectives are needed?"**
   - 1 → Level 1 or 2
   - 2 → Level 2 (main + helper)
   - 3+ → Level 3

2. **"Can any parts of this run in parallel?"**
   - No → Level 1 or 2
   - Yes, occasionally → Level 2
   - Yes, fundamentally → Level 3

3. **"Does this require deep research or specialized validation?"**
   - No → Level 1
   - Occasionally → Level 2
   - Continuously throughout → Level 3

4. **"Is this multi-phase with distinct sequential stages?"**
   - No, single phase → Level 1 or 2
   - Yes, 2-3 phases → Probably Level 2
   - Yes, 3+ phases → Level 3

5. **"Do different specialists need to coordinate their work?"**
   - No coordination → Level 1 or 2
   - Simple handoff → Level 2
   - Complex coordination → Level 3

---

## Architecture Verification

After making architecture decision, verify:

### Level 1 Verification
- [ ] Workflow is clearly linear
- [ ] No research/validation needs
- [ ] Single domain expertise
- [ ] Can be captured in scripts/references/assets

### Level 2 Verification
- [ ] Main workflow is clear and manageable
- [ ] Delegation points are well-defined
- [ ] Subagent responsibilities are specific
- [ ] Can proceed after delegation completes

### Level 3 Verification
- [ ] Multiple specialist roles identified
- [ ] Parallel execution opportunities clear
- [ ] Coordination requirements defined
- [ ] Justifies orchestration complexity

---

## When in Doubt

**Default to simplicity:** Start with Level 1, upgrade if needed.

**Consider Level 2 when:** User mentions "research", "validate", "analyze deeply", or "compare multiple sources"

**Only choose Level 3 when:** User explicitly describes multi-phase workflow with multiple concurrent specialists and coordination needs

**Remember:** It's easier to upgrade from Level 1 → Level 2 → Level 3 than to downgrade from complex to simple.
