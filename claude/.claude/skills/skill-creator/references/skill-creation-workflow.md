# Skill Creation Workflow - Detailed Guide

This guide provides detailed step-by-step instructions for creating skills at each architecture level.

## Table of Contents

1. [Architecture Assessment (Step 0)](#step-0-architecture-assessment)
2. [Understanding with Examples (Step 1)](#step-1-understanding-with-examples)
3. [Understand Context & Constraints (Step 1.5)](#step-15-understand-context--constraints--critical)
4. [Planning Contents (Step 2)](#step-2-planning-contents)
5. [Initializing Structure (Step 3)](#step-3-initializing-structure)
6. [Writing the Skill (Step 4)](#step-4-writing-the-skill)
7. [Testing & Iteration (Step 5-6)](#step-5-6-testing--iteration)

---

## Step 0: Architecture Assessment

**Goal**: Determine which architecture level (1, 2, or 3) is appropriate for this skill.

### Assessment Questions

Ask the user these questions to understand requirements:

#### 1. Workflow Complexity
- **Question**: "Is this a single-phase workflow or multi-phase process?"
- **Follow-up**: "Are the steps mostly sequential or can some run in parallel?"

**Indicators**:
- Single-phase: "Convert PDF to markdown" (Level 1-2)
- Multi-phase: "Research → Analyze → Synthesize → Report" (Level 3)

#### 2. Specialist Roles
- **Question**: "How many different specialist roles or perspectives are needed?"
- **Follow-up**: "Does this require coordination between multiple specialists?"

**Indicators**:
- One role: "Format code" (Level 1)
- Occasional help: "Build MCP server (needs API research)" (Level 2)
- Multiple specialists: "Trading analysis (daily + 4h + 1h timeframes)" (Level 3)

#### 3. State Management
- **Question**: "Does this need to track state across multiple phases?"
- **Follow-up**: "Are there intermediate results that need to be shared between specialists?"

**Indicators**:
- Minimal state: "Run linter and format" (Level 1)
- Simple state: "Research tech, then recommend" (Level 2)
- Complex state: "Track research findings, analyze conflicts, synthesize recommendations" (Level 3)

#### 4. Research/Analysis Needs
- **Question**: "Does this require occasional deep research or validation?"
- **Follow-up**: "Or does it need continuous multi-source analysis throughout?"

**Indicators**:
- No research: "Format files" (Level 1)
- Occasional research: "Compare two frameworks" (Level 2)
- Continuous analysis: "Comprehensive stock research with multiple sources" (Level 3)

### Decision Matrix

Use the complete [Architecture Decision Matrix](./architecture-decision-matrix.md) for detailed criteria.

**Quick decision**:

| If... | Then... |
|-------|---------|
| Single-phase + one domain + minimal state | **Level 1** |
| Single-phase + occasional help + simple state | **Level 2** |
| Multi-phase + 3+ specialists + parallel + complex state | **Level 3** |

### Step 0.1: Delegate to meta-multi-agent (Level 3 Only)

If Level 3 detected, immediately delegate:

```python
from Task import Task

Task(
    subagent_type="meta-multi-agent",
    description="Generate multi-agent system for {domain}",
    prompt="""
Create a complete multi-agent system for: {domain_name}

## Requirements
{workflow_description}

## Specialist Roles Needed
{list_of_specialist_roles}

## Parallel Execution Needs
{parallel_requirements}

## Coordination Requirements
{coordination_needs}

## State Management
{state_tracking_needs}

Generate the complete .claude/ directory structure with:
- Main orchestrator command
- Specialist agents
- Parallel worker (if needed)
- Coordination rules
- Context management files
- Communication protocols
"""
)
```

**After completion**: Review generated system and provide usage documentation. Skill creation ends here for Level 3.

**For Level 1 & 2**: Continue to Step 1.

---

## Step 1: Understanding with Examples

**Goal**: Gather concrete examples to understand how the skill will be used in practice.

### Skip Conditions
- Level 3 (already delegated)
- Usage patterns already clearly understood
- User has provided detailed specification

### Question Strategies

**Start broad**:
- "What functionality should this skill support?"
- "Can you give some examples of typical use cases?"

**Then specific**:
- "What would a user say that should trigger this skill?"
- "What should the skill output or produce?"
- "Are there any edge cases or special scenarios?"

**Avoid overwhelming**:
- Start with 2-3 questions
- Follow up based on responses
- Don't ask everything at once

### Example Collection

**For each example, document**:
1. **Trigger**: What user says
2. **Input**: What user provides
3. **Process**: What skill does
4. **Output**: What skill produces

**Example template**:
```markdown
## Example 1: Basic Usage

**User says**: "Create a REST API endpoint"

**User provides**:
- Entity name: "User"
- Fields: name, email, password

**Skill does**:
1. Generate route handler
2. Create validation schema
3. Add database model
4. Write tests

**Output**:
- src/routes/user.js
- src/models/User.js
- tests/user.test.js
```

### Completion Criteria

Stop gathering examples when you have:
- ✅ 2-3 clear use cases
- ✅ Understanding of expected inputs
- ✅ Clear sense of desired outputs
- ✅ Awareness of edge cases
- ✅ Confidence in skill scope

---

## Step 1.5: Understand Context & Constraints ⚠️ CRITICAL

**Goal**: Understand requirements and context BEFORE implementation.

**Universal Principle**: Never make assumptions about format, structure, or approach. Always research and verify first.

### Context Analysis by Skill Type

#### A. Output-Generating Skills (files, code, configs)

**Research existing patterns:**
```bash
# 1. Find similar existing files
ls -la {target-directory}/

# 2. Read example files
cat {target-directory}/example-file.{ext}

# 3. Document discovered format
```

**Document findings:**
```markdown
## Format Analysis
**Location**: {path to existing examples}
**Format**: {extension, structure, frontmatter, etc.}
**Example**: {paste relevant portions}
**Key insight**: {what you learned that differed from assumptions}
```

**Example (resume-to-yaml):**
```
Assumed: Pure YAML files (.yaml)
Actually: Markdown with YAML frontmatter (.md)
```

#### B. Workflow/Process Skills (guides, procedures)

**Research similar workflows:**
```bash
# 1. Find existing workflow documentation
find . -name "*workflow*" -o -name "*process*"

# 2. Study workflow patterns
# What steps do similar processes follow?
# What decision points exist?
# What outputs/artifacts are created?
```

**Document findings:**
```markdown
## Workflow Analysis
**Similar workflows**: {list existing workflows}
**Common patterns**: {steps, decision points, validation gates}
**Differences from assumptions**: {what you learned}
```

**Example (code-review workflow):**
```
Assumed: Simple pass/fail checklist
Actually: Multi-phase with automated + manual steps
```

#### C. Advisory/Recommendation Skills (tech choices, best practices)

**Research domain knowledge:**
```bash
# 1. What existing knowledge exists in vault/codebase?
grep -r "similar-topic" docs/ notes/

# 2. What are current best practices?
# Check documentation, recent updates, industry standards

# 3. What trade-offs matter?
# Performance vs simplicity? Cost vs features?
```

**Document findings:**
```markdown
## Domain Analysis
**Existing knowledge**: {what's already documented}
**Best practices**: {current consensus in field}
**Key trade-offs**: {what decisions need guidance}
**Example scenarios**: {real use cases}
```

**Example (tech-stack-advisor):**
```
Assumed: Generic framework comparison
Actually: Need context-specific trade-offs (team size, timeline, scale)
```

#### D. Integration/System Skills (MCP servers, API clients)

**Research target system:**
```bash
# 1. Read integration documentation
cat docs/integration-guide.md

# 2. Study existing integrations
ls examples/ reference-implementations/

# 3. Check API/protocol specifications
# What's required vs optional?
# What authentication/config needed?
```

**Document findings:**
```markdown
## Integration Analysis
**Target system**: {system name, version}
**Required components**: {what must be implemented}
**Configuration needs**: {auth, endpoints, formats}
**Example integration**: {show working example}
```

**Example (MCP server builder):**
```
Assumed: Simple tool definition
Actually: Need server lifecycle, error handling, resource management
```

### Example: resume-to-yaml lesson

**❌ What happened (WRONG)**:
```
Assumed: Generate pure YAML files (profile.yaml, projects.yaml, rates.yaml)
Reality: Consultants folder uses Markdown with YAML frontmatter (profile.md, projects.md, rates.md)
Result: Full rewrite required after user correction
```

**✅ What should have happened (RIGHT)**:
```bash
# BEFORE writing yaml_generator.py:
Read /Consultants/nhan_mai/profile.md
Discover: Markdown with YAML frontmatter!
Show user: "I'll generate profile.md in this format: [example]"
User confirms
THEN write code to match discovered format
```

### Handling Ambiguities: Socratic Method + "yolo" Escape Hatch

**When major ambiguities exist** during Step 1.5 (unclear requirements, conflicting constraints, multiple valid approaches):

#### Approach 1: Socratic Clarification (Default)

Use strategic questioning to guide discovery (inspired by `/Users/smian/dotfiles/claude/.claude/agents/socratic-mentor.md`):

**Question Progression Pattern**:
```yaml
observation_level:
  question: "What do you notice about [existing patterns]?"
  example: "Looking at existing consultants, what format do you see for profiles?"

pattern_level:
  question: "Why might that pattern be important?"
  example: "What advantages does Markdown with frontmatter have over pure YAML?"

principle_level:
  question: "What principle could explain this design?"
  example: "How does this format support both human reading and automated processing?"

application_level:
  question: "How would you apply this to the new skill?"
  example: "Given this pattern, what format should resume-to-yaml generate?"
```

**Example Socratic Exchange**:
```
Claude: "I see two potential approaches for output format:
1. Pure YAML files (.yaml) - machine-readable, structured
2. Markdown with YAML frontmatter (.md) - human + machine readable

Questions to consider:
- Will humans need to read these files directly?
- Do other systems need to parse this data?
- What pattern do existing consultant profiles use?

What pattern do you see in /Consultants/ folder?"

User: "They're all .md files"

Claude: "Exactly! What does that tell you about the preferred format?"

User: "We should generate .md files with frontmatter"

Claude: "Perfect - you've discovered the requirement by observing the pattern."
```

#### Approach 2: "yolo" Mode (Trusted Judgment)

Offer the user an escape hatch when time is limited:

```
"I have several design questions about [ambiguous aspect]. I can:

1. **Ask clarifying questions** to nail down requirements (Socratic method)
   → Takes 2-3 exchanges but ensures we get it right

2. **Proceed with my best judgment** if you trust my assessment
   → Faster, but I'll document my assumptions
   → Say 'yolo' to use this approach

Which would you prefer?"
```

**If user says "yolo"**:

1. **Document your assumptions clearly**:
```markdown
## Design Decisions (User approved "yolo" mode)

**Assumption 1**: Output format will be Markdown with YAML frontmatter
**Rationale**: Matches existing /Consultants/ pattern
**Evidence**: Analyzed /Consultants/nhan_mai/profile.md

**Assumption 2**: Quality scoring uses 0-100 scale
**Rationale**: Industry standard for percentage-based metrics
**Evidence**: Similar tools use this range

**Risk**: If assumptions are wrong, may require refactoring
**Mitigation**: User can correct in Step 2 planning review
```

2. **Proceed with most reasonable approach based on**:
   - Similar existing patterns in codebase/vault
   - Best practices for the domain
   - Simplicity and maintainability principles
   - Prior experience with similar problems

3. **Show chosen approach in Step 2 for validation**:
   - User can still correct before implementation
   - Assumptions are documented and visible

**Safety Gates for "yolo"**:

```yaml
never_yolo_for:
  - Security-sensitive decisions (auth, permissions, encryption)
  - Breaking changes to existing APIs/interfaces
  - Irreversible architectural choices
  - Data migration or loss scenarios

safe_for_yolo:
  - Format/style choices when patterns exist ✅
  - Testing approach decisions ✅
  - Documentation structure choices ✅
  - Tool selection when options are comparable ✅
  - Default values with override capability ✅
```

#### Choosing the Right Approach

| Situation | Recommended Approach |
|-----------|---------------------|
| **User is exploring requirements** | Socratic questioning |
| **Similar patterns exist in codebase** | "yolo" with pattern analysis |
| **Security/breaking changes involved** | Socratic questioning (NEVER yolo) |
| **User is experienced with domain** | Offer both, let user choose |
| **Tight timeline, low risk** | "yolo" with documented assumptions |
| **High uncertainty, high impact** | Socratic questioning |

**Key Principle**: Both approaches prevent assumptions without verification. Socratic method makes verification collaborative; "yolo" makes it rapid but documented.

### Universal Verification Protocol

Before proceeding to Step 2, verify you've done appropriate research:

**For ALL skill types:**
- [ ] Researched similar existing implementations
- [ ] Documented key constraints and patterns
- [ ] Identified assumptions vs verified facts
- [ ] Showed user your understanding for confirmation
- [ ] Have concrete examples as reference

**Red flags (STOP if you see these)**:
- ❌ "I'll assume..." (any assumption without verification)
- ❌ "It probably should..." (speculation without research)
- ❌ "Standard practice would be..." (without checking local context)
- ❌ "Most skills do..." (without studying actual examples)

**Green flags (PROCEED when you have these)**:
- ✅ "I analyzed {existing-examples} and found..." (evidence-based)
- ✅ "The pattern matches: [concrete example]" (specific, not vague)
- ✅ "User confirmed..." (validated understanding)
- ✅ "Here's what differs from my initial assumption..." (humble, learning-oriented)

### When to Show User for Approval

**Always show your understanding before implementation:**

| Skill Type | Show User |
|------------|-----------|
| **Output generator** | Exact format, sample output, integration points |
| **Workflow** | Process steps, decision points, validation gates |
| **Advisory** | Decision framework, trade-offs, example scenarios |
| **Integration** | Required components, config needs, authentication |

**Example approval requests:**

**Output generator:**
```markdown
## Planned Output: profile.md
**Format**: Markdown with YAML frontmatter (NOT pure YAML)
**Example**: [show sample]
**Integration**: Matches /Consultants/ folder structure
**Confirm this matches your expectations?**
```

**Workflow skill:**
```markdown
## Planned Workflow: code-review
**Steps**: 1) Automated checks → 2) Manual review → 3) Approval gate
**Decision points**: Security issues require escalation
**Validation**: All tests must pass before manual review
**Does this match your review process?**
```

**Advisory skill:**
```markdown
## Planned Framework: tech-stack-advisor
**Decision factors**: Team size, timeline, scale, existing knowledge
**Trade-offs**: Performance vs dev speed, cost vs features
**Example**: "Team of 2, 3-month deadline → recommend X over Y"
**Is this the guidance approach you need?**
```

### Completion Criteria

- ✅ Researched appropriate context for skill type
- ✅ Documented patterns and constraints
- ✅ Showed user your understanding
- ✅ Received confirmation
- ✅ Ready to implement with confidence

---

## Step 2: Planning Contents

**Goal**: Identify what resources to bundle with the skill.

### For Level 1 & 2 Skills

Analyze each example to identify:

#### 1. Scripts

**Question**: "What code gets rewritten repeatedly?"

**Indicators**:
- User frequently requests same operation
- Complex multi-step process
- Requires exact execution
- Deterministic behavior needed

**Examples**:
- PDF conversion scripts
- Data validation scripts
- File format converters
- Build automation

**Planning checklist**:
- [ ] What does script do?
- [ ] What inputs required?
- [ ] What outputs produced?
- [ ] What dependencies needed?
- [ ] Error handling needed?

#### 2. References

**Question**: "What documentation should be loaded on-demand?"

**Indicators**:
- External API documentation
- Configuration schemas
- Domain-specific knowledge
- Long explanations
- Decision trees

**Examples**:
- API reference docs
- Configuration schemas
- Troubleshooting guides
- Best practices

**Planning checklist**:
- [ ] What knowledge needed?
- [ ] Can it be explained briefly? (If yes, inline in SKILL.md)
- [ ] Does it change often?
- [ ] Multiple sections needed?

#### 3. Assets

**Question**: "What templates or boilerplate are needed?"

**Indicators**:
- User requests same file structure
- Common configuration files
- Standard templates
- Starter code

**Examples**:
- README templates
- Configuration templates
- Project scaffolds
- Sample data

**Planning checklist**:
- [ ] What files are templates?
- [ ] What's configurable?
- [ ] Multiple variants needed?
- [ ] How to customize?

### For Level 2 Skills (Additional)

#### 4. Delegation Points

**Question**: "Where does skill need specialized help?"

**Indicators**:
- Need current web information
- Complex security analysis
- Performance profiling
- Deep research
- Multi-source validation

**Available agents for delegation**:
- `web-researcher` - Multi-source web research
- `deep-research-agent` - Adaptive deep analysis
- `code-reviewer` - Code quality/security/performance
- `security-engineer` - Security vulnerability analysis
- `performance-engineer` - Performance bottleneck analysis
- `root-cause-analyst` - Systematic problem investigation

**Planning checklist**:
- [ ] What tasks need delegation?
- [ ] Which specialist agent to use?
- [ ] What info to pass?
- [ ] How to use results?

See [Delegation Patterns](./delegation-patterns.md) for detailed templates.

### Documentation Plan

Create a planning document:

```markdown
## Skill Plan: {skill-name}

### Purpose
{Brief description}

### Scripts
- [ ] `process_data.py` - Main data processing
- [ ] `validate.sh` - Output validation

### References
- [ ] `api-reference.md` - External API docs
- [ ] `troubleshooting.md` - Common issues

### Assets
- [ ] `templates/config.json` - Configuration template
- [ ] `templates/README.md` - README template

### Delegation Points (Level 2 only)
- [ ] API research → web-researcher
- [ ] Security review → security-engineer
```

---

## Step 3: Initializing Structure

**Goal**: Create the directory structure and initial files.

### Directory Creation

**For all skills (Level 1 & 2)**:

```bash
# Create complete directory structure
mkdir -p .claude/skills/{skill-name}/{scripts,references,assets,agents,commands}

# Verify structure
tree .claude/skills/{skill-name}
```

**Expected output**:
```
.claude/skills/{skill-name}/
├── scripts/
├── references/
├── assets/
├── agents/
└── commands/
```

### Symlink Creation (Optional)

**Only if skill needs custom agents or commands**:

```bash
# Navigate to agents directory
cd .claude/agents

# Create symlink to skill's agents directory
ln -s ../skills/{skill-name}/agents {skill-name}

# Navigate to commands directory
cd ../commands

# Create symlink to skill's commands directory
ln -s ../skills/{skill-name}/commands {skill-name}
```

**Verify symlinks**:
```bash
ls -la .claude/agents/{skill-name}
ls -la .claude/commands/{skill-name}
```

### Initial SKILL.md

Create `.claude/skills/{skill-name}/SKILL.md`:

```yaml
---
name: {skill-name}
description: When to use this skill (be specific and action-oriented)
---

# {Skill Name}

Brief description of what this skill does.

## When to Use This Skill

Describe when Claude should invoke this skill.

## Workflow

[To be filled in Step 4]
```

### Verification

**Check structure**:
```bash
# Should show all directories
ls -la .claude/skills/{skill-name}/

# Should show SKILL.md
cat .claude/skills/{skill-name}/SKILL.md
```

---

## Step 4: Writing the Skill

**Goal**: Write comprehensive SKILL.md and create bundled resources.

### For Level 1 (Simple Skills)

#### 4.1: Write SKILL.md

**Critical Decision: Determine SKILL.md Length**

Before writing, ask: **"Do executable scripts handle the core logic?"**

**If YES (scripts exist)** → Target **50-120 lines** (invocation guide):
- When to use (trigger conditions)
- How to invoke (command examples)
- Key options (table format)
- Where to find details (reference links)

**If NO (pure workflow)** → Target **200-500 lines** (step-by-step procedures):
- Detailed workflow steps
- Decision points
- Validation gates
- Comprehensive examples

**Structure for Skills WITH Scripts (50-120 lines)**:

```markdown
---
name: skill-name
description: Brief trigger description (when to use)
---

# Skill Name

One-sentence description.

## When to Use

Trigger when user requests:
- "Generate X for [item]"
- "Create Y"

## Quick Start

### Method 1: Basic Usage
```bash
cd .claude/skills/skill-name/scripts
python script_name.py {required-arg} \
  --option1 value \
  --output ../output
```

### Method 2: Advanced Usage
```bash
# With additional options
python script_name.py {arg} --dry-run --verbose
```

## Key Options

| Option | Description | Example |
|--------|-------------|---------|
| `--required` | Required parameter | `--required value` |
| `--optional` | Optional parameter | `--optional value` |
| `--dry-run` | Validate without executing | `--dry-run` |

## Output

**Location**: `.claude/skills/skill-name/output/`
**Filename**: `Generated_{Name}.ext`

## References

- **[Usage Patterns](./references/usage-patterns.md)** - Common scenarios
- **[Data Requirements](./references/data-requirements.md)** - Format specs
- **[Troubleshooting](./references/troubleshooting.md)** - Error solutions

---

**Script**: `scripts/script_name.py` handles all validation and execution.
```

**Structure for Skills WITHOUT Scripts (200-500 lines)**:

```markdown
---
name: skill-name
description: Brief trigger description
---

# Skill Name

One-paragraph overview of what this skill does.

## When to Use This Skill

Bullet points describing trigger conditions:
- ✅ When user asks for X
- ✅ When Y needs to be done
- ❌ NOT when Z (clarify boundaries)

## Workflow

### Step 1: {First Phase}

Detailed description of what to do first.
- Sub-step A
- Sub-step B
- Decision point: If X, then Y

### Step 2: {Second Phase}

Detailed description of next steps.
- Validation checkpoint
- Error handling approach
- Expected intermediate outputs

### Step 3: {Final Phase}

Detailed description of completion.
- Final validation
- Success criteria
- Next actions

## Examples

### Example 1: Basic Usage

[Show complete step-by-step example]

### Example 2: Edge Case

[Show handling of complex scenario]

## Decision Points

[Document key decision trees]

## Validation Gates

[Document validation checkpoints]

## Troubleshooting

Common issues and solutions.
```

#### 4.2: Create Scripts

For each script identified in Step 2:

```bash
#!/usr/bin/env python3
"""
Script description.

Usage:
    script_name.py --input FILE --output FILE

Arguments:
    --input   Input file path
    --output  Output file path
"""

import argparse

def main():
    parser = argparse.ArgumentParser(description='Script description')
    parser.add_argument('--input', required=True, help='Input file')
    parser.add_argument('--output', required=True, help='Output file')
    args = parser.parse_args()

    # Implementation here

if __name__ == '__main__':
    main()
```

**Make executable**:
```bash
chmod +x .claude/skills/{skill-name}/scripts/*.py
```

#### 4.3: Create References

For each reference identified:

```markdown
# Reference Title

Brief overview.

## Section 1

Detailed information.

## Section 2

More details.

## Examples

Code examples inline.
```

#### 4.4: Create Assets

For each asset identified:

```json
{
  "name": "{{project_name}}",
  "version": "{{version}}",
  "description": "{{description}}"
}
```

**Document placeholders**:
- Use `{{variable}}` format
- Add comments explaining each field
- Provide default values

### For Level 2 (Skills with Delegation)

**Everything from Level 1, PLUS**:

#### 4.5: Add Delegation Section to SKILL.md

```markdown
## Using Subagent Delegation

This skill delegates specialized tasks to expert agents.

### When to Delegate

Delegate when:
- ✅ Need current web information
- ✅ Require security analysis
- ✅ Complex research needed

Handle directly when:
- ❌ Simple, well-known information
- ❌ User already provided data
- ❌ Skill has sufficient knowledge

### Delegation Pattern

When {condition requiring specialized help}:

```python
from Task import Task

Task(
    subagent_type="{appropriate-agent}",
    description="{specific-task}",
    prompt="""
{detailed-prompt-for-subagent}

Provide structured output:
- {Expected section 1}
- {Expected section 2}
"""
)
```

### Using Results

After receiving subagent results:

1. Extract relevant information
2. Synthesize with skill knowledge
3. Provide recommendation to user
4. Include sources from research

### Example Delegation

[Show complete example with Task() call and result usage]
```

See [Delegation Patterns](./delegation-patterns.md) for more templates.

### Writing Style Guidelines

**Critical Principle**: When scripts exist, SKILL.md is an **invocation guide**, not an **implementation manual**.

#### Length Guidelines by Skill Type

| Situation | Target Length | Focus | What NOT to Include |
|-----------|--------------|-------|---------------------|
| **Scripts handle logic** | 50-120 lines | When to use, how to invoke, key options | Step-by-step protocols, error handling procedures, validation logic |
| **Pure workflow (no scripts)** | 200-500 lines | Step-by-step procedures, decision points | Code implementation, script logic |

#### Examples

**❌ Verbose SKILL.md** (324 lines for skill with 16KB script):
```markdown
## Validation Protocol

### Step 1: Data Extraction
Extract consultant data from YAML files...

### Step 2: Field Validation
For each required field:
- Check if present
- Validate format
- Apply business rules

### Step 3: Error Handling
If validation fails:
- Collect error messages
- Format error report
- Return validation result
```
*Problem*: Duplicates what the script already implements. User doesn't need step-by-step validation logic - they just need to know how to run it.

**✅ Concise SKILL.md** (103 lines for same skill):
```markdown
## Quick Start

```bash
cd .claude/skills/sow-generator/scripts
python sow_generator.py {consultant_path} \
  --addendum-number {number} \
  --output ../output
```

## Key Options

| Option | Description | Example |
|--------|-------------|---------|
| `--dry-run` | Validate without PDF | `--dry-run` |
| `--batch` | Process multiple | `--batch` |

## References

- **[Troubleshooting](./references/troubleshooting.md)** - Error solutions
```
*Correct*: Shows how to invoke, what options exist, where to find details. Script handles validation logic.

#### Universal Guidelines

**Always**:
- Use imperative/infinitive form (verb-first)
- Be objective: "To accomplish X, do Y"
- Reference bundled resources, don't duplicate them
- Include practical examples (commands, not theory)

**Never**:
- Use second person ("you should")
- Include implementation details that scripts already handle
- Duplicate reference content in SKILL.md
- Write step-by-step protocols for what scripts automate

### Quality Checklist

Before completing Step 4:

**For ALL skills**:
- [ ] SKILL.md has proper frontmatter
- [ ] Clear "When to Use" section
- [ ] Examples included
- [ ] References linked (not duplicated)
- [ ] Length matches skill type (see below)

**For skills WITH scripts (50-120 lines)**:
- [ ] Quick Start commands documented
- [ ] Key Options table included
- [ ] Output specifications clear
- [ ] NO step-by-step protocols (scripts handle logic)
- [ ] NO detailed validation procedures (scripts handle this)

**For skills WITHOUT scripts (200-500 lines)**:
- [ ] Step-by-step workflow documented
- [ ] Decision points clearly marked
- [ ] Validation gates described
- [ ] Comprehensive examples showing all paths

**For Level 2 skills (with delegation)**:
- [ ] Delegation section included
- [ ] Task() examples provided
- [ ] When to delegate vs handle directly explained

---

## Step 5-6: Testing & Iteration

### Step 5: Functional Testing & Validation ⚠️ MANDATORY

**Goal**: Verify the skill actually works with real data, not just structural correctness.

### Critical Rule: NEVER Claim Success Without Running It

**❌ Forbidden statements**:
- "I've created the structure" (structural only, not functional)
- "The code should work" (assumption, not verification)
- "I've implemented the logic" (written, not tested)
- "This will handle..." (prediction, not proof)

**✅ Required statements**:
- "I ran it with {real-input} and got {actual-output}"
- "Here's the output from {test-file}: [show actual content]"
- "Tested with {N} different inputs, all successful"
- "Quality score: {actual-number} based on {real-extraction}"

### Testing Protocol by Skill Type

**Universal principle**: Test in practice, not just theory. Show actual results, not predictions.

#### A. Output-Generating Skills (executable code)

**Phase 1: Functional Execution**
```bash
# Run with REAL input (not synthetic)
{actual-command-with-real-file}

# Capture actual output
ls -la output/

# Read actual generated content
cat output/file.md
```

**Phase 2: Output Verification**
```bash
# Compare with expected format
diff -u {existing-example} {generated-output}
```

**Verification**:
- [ ] Files in correct location
- [ ] Format matches target (.md not .yaml)
- [ ] Structure matches examples
- [ ] Data extracted correctly
- [ ] Quality metrics accurate

**Phase 3: Error Cases**
```bash
# Test edge cases
{command} {incomplete-input}
{command} {malformed-input}
```

#### B. Workflow/Process Skills (step-by-step guides)

**Phase 1: Follow the Workflow**
```markdown
Personally execute each step of the workflow with real scenario:

Step 1: [Actually do Step 1]
→ Result: [What actually happened]
→ Issues: [Any problems encountered]

Step 2: [Actually do Step 2]
→ Result: [What actually happened]
→ Issues: [Any problems encountered]
```

**Phase 2: Verify Completeness**
- [ ] All steps executable as written
- [ ] Decision points clearly marked
- [ ] Edge cases addressed
- [ ] Output/artifacts created as expected
- [ ] No missing prerequisite steps

**Phase 3: Test Variations**
- [ ] Try workflow with different scenarios
- [ ] Verify error paths work
- [ ] Check validation gates trigger correctly

**Example (brainstorming workflow)**:
```
Step 1: Ask user for rough idea → User provides "mobile app"
Step 2: Clarify purpose → "Fitness tracking for runners"
Step 3: Identify constraints → "Solo dev, 2-month timeline"
→ Workflow produces clear feature scope ✅
```

#### C. Advisory/Recommendation Skills (decision frameworks)

**Phase 1: Test with Real Scenarios**
```markdown
Scenario 1: {Real-world case}
→ Applied framework
→ Recommendation: {What skill advised}
→ Reasoning: {Why this recommendation}
→ Validate: Does this make sense? ✅/❌

Scenario 2: {Different real-world case}
→ Applied framework
→ Recommendation: {What skill advised}
→ Different from Scenario 1? Why?
```

**Phase 2: Verify Decision Quality**
- [ ] Recommendations are actionable
- [ ] Trade-offs are explained
- [ ] Context matters (not one-size-fits-all)
- [ ] Alternative options considered
- [ ] Reasoning is clear

**Phase 3: Test Edge Cases**
- [ ] Ambiguous requirements → asks clarifying questions
- [ ] Conflicting constraints → acknowledges trade-offs
- [ ] Novel scenario → adapts framework appropriately

**Example (tech-stack-advisor)**:
```
Scenario: Solo dev, 3-month deadline, CRUD app
→ Recommends: Rails/Django (fast development)
→ Not: Microservices (too complex for context)
→ Trade-off explained: Speed over scalability ✅
```

#### D. Integration/System Skills (MCP servers, API clients)

**Phase 1: Integration Testing**
```bash
# Actually run the integration
{start-server-command}

# Test integration points
{client-command}

# Verify responses
# Expected: {specification}
# Actual: {what you got}
```

**Phase 2: Verify Components**
- [ ] Server starts successfully
- [ ] Tools/endpoints accessible
- [ ] Authentication works
- [ ] Error handling functions
- [ ] Resource cleanup happens

**Phase 3: Integration Scenarios**
- [ ] Normal operation succeeds
- [ ] Auth failures handled gracefully
- [ ] Invalid requests rejected properly
- [ ] Resource limits respected

**Example (MCP server)**:
```bash
# Start server
node server.js
→ Server started on port 3000 ✅

# Test tool call
curl -X POST /tools/example
→ Response: {expected format} ✅

# Test error case
curl -X POST /tools/invalid
→ Response: {error message} ✅
```

### Example: resume-to-yaml Testing

**✅ Correct functional testing**:
```bash
# Run with real PDF
python resume_to_yaml.py incoming/cv_maksim_gritsan.pdf

# ACTUAL OUTPUT RECEIVED:
✅ Generated files:
  - profile: output/profile.md
  - projects: output/projects.md
  - rates: output/rates.md

📊 Quality Score Breakdown:
Field                     Points     Status          Notes
────────────────────────────────────────────────────────────
Name                      20/20      ✅ Found         "Maksim Gritsan"
Email                     0/20       ❌ Missing       Not in PDF
Phone                     0/10       ❌ Missing       Not in PDF
Primary Skills (≥3)       20/20      ✅ Found         8 skills
Experience (≥1)           20/20      ✅ Found         2 positions
Education                 10/10      ✅ Found         2 entries
────────────────────────────────────────────────────────────
TOTAL                     70/100

# Verify format matches target
head -20 output/profile.md
# Shows: Markdown with YAML frontmatter ✅

# Compare with existing consultant
diff -u /Consultants/nhan_mai/profile.md output/profile.md
# Structure matches ✅
```

**❌ Insufficient testing (what to avoid)**:
```bash
# Just creating structure
mkdir output && touch output/profile.yaml
# This proves NOTHING about functionality!

# Or claiming:
"I've implemented the YAML generator. It should work."
# Without actually running it = UNACCEPTABLE
```

### Testing for Level 2 (Delegation)

**Additional requirements**:

#### Test Delegation Trigger

```python
# Trigger condition that requires delegation
Skill(command="skill-name")
# User provides: {input-requiring-research}

# Verify Task() call occurs
# Expected: Task(subagent_type="web-researcher", ...)
# Actual: [show actual Task() invocation]
```

#### Test Result Usage

```python
# After subagent completes:
# Verify results integrated correctly
# Expected: [what should happen with results]
# Actual: [what actually happened]
```

#### Delegation checklist

- [ ] Delegation triggered appropriately
- [ ] Correct agent selected
- [ ] Proper prompt provided
- [ ] Results received successfully
- [ ] Results used correctly
- [ ] Final output includes subagent findings

### Completion Criteria

**Before claiming Step 5 complete**:

- [ ] Ran skill with real input (not synthetic)
- [ ] Generated actual output files
- [ ] Verified output matches target format
- [ ] Tested error cases
- [ ] Documented actual results (not predictions)
- [ ] (Level 2) Tested delegation successfully

### Red Flag Checklist

**STOP and test properly if**:
- [ ] You haven't run the actual code yet
- [ ] You're describing what "should" happen
- [ ] You haven't shown actual output
- [ ] User asks "how did you test it?"
- [ ] You can't paste actual generated content

### Quality Gate

**To pass Step 5, you must answer the appropriate questions for your skill type:**

#### For Output-Generating Skills:
1. "What input did you use?" → Specific real file/data
2. "What output did it generate?" → Actual content, not description
3. "Does the format match?" → Show side-by-side comparison
4. "What were the metrics?" → Actual numbers with breakdown
5. "Did you test errors?" → Show what happens when it fails

#### For Workflow Skills:
1. "Did you follow the workflow?" → Actual execution with real scenario
2. "Were all steps executable?" → Specific issues encountered
3. "Did it produce expected artifacts?" → Show what was created
4. "Did decision points work?" → Show examples of branching
5. "Did you test variations?" → Different scenarios attempted

#### For Advisory Skills:
1. "What scenarios did you test?" → Specific real-world cases
2. "What recommendations resulted?" → Actual advice given
3. "Were trade-offs explained?" → Show reasoning
4. "Did context matter?" → Different scenarios → different advice
5. "Did you test ambiguity?" → How skill handles unclear requirements

#### For Integration Skills:
1. "Did you run the integration?" → Server/client actually started
2. "Did you test endpoints?" → Actual requests/responses
3. "Does it match specifications?" → Compare expected vs actual
4. "Did you test errors?" → Auth failures, invalid requests
5. "Does cleanup work?" → Resource management verified

**If you cannot answer the appropriate questions with actual data, YOU HAVE NOT TESTED PROPERLY.**

### Step 6: Iteration

**After initial use**:

1. **Collect feedback**:
   - What worked well?
   - What was confusing?
   - What was missing?
   - What could be improved?

2. **Identify improvements**:
   - Add missing scripts
   - Clarify confusing sections
   - Add more examples
   - Update delegation logic
   - Create additional references

3. **Implement changes**:
   - Update SKILL.md
   - Add/modify bundled resources
   - Test changes
   - Document updates

4. **Track versions**:
```bash
git add .claude/skills/{skill-name}/
git commit -m "skill({skill-name}): {description of changes}"
```

**Iteration cycle**:

```
Use skill → Notice issues → Identify fixes → Implement → Test → Repeat
```

**Common iterations**:

- **Iteration 1**: Fix unclear instructions
- **Iteration 2**: Add missing examples
- **Iteration 3**: Improve delegation logic
- **Iteration 4**: Optimize workflow steps
- **Iteration 5**: Add edge case handling

### Maintenance

**Regular updates**:

1. **Review usage patterns**:
   - Which features are most used?
   - Where do users struggle?
   - What gets skipped?

2. **Update references**:
   - Check for API changes
   - Update deprecated patterns
   - Add new best practices

3. **Refine scripts**:
   - Fix bugs
   - Add error handling
   - Improve performance

4. **Expand assets**:
   - Add new templates
   - Create variants
   - Update boilerplate

5. **Improve delegation**:
   - Refine prompts
   - Try different agents
   - Better result usage

**Version control**:

```bash
# Create feature branch for significant changes
git checkout -b skill/{skill-name}/improvement

# Make changes
# Test thoroughly
# Commit with descriptive message

git add .claude/skills/{skill-name}/
git commit -m "skill({skill-name}): add error handling to scripts"

# Merge back
git checkout main
git merge skill/{skill-name}/improvement
```

---

## Quick Reference

### Level 1 Workflow Summary

```
Step 0: Confirm Level 1 (single-phase, one domain)
Step 1: Gather 2-3 examples
Step 1.5: Analyze target environment (if generating output)
Step 2: Plan scripts, references, assets
Step 3: mkdir + SKILL.md
Step 4: Write SKILL.md + create resources
Step 5: Functional testing with real data
Step 6: Iterate based on usage
```

### Level 2 Workflow Summary

```
Step 0: Confirm Level 2 (occasional delegation needed)
Step 1: Gather examples including delegation scenarios
Step 1.5: Analyze target environment (if generating output)
Step 2: Plan scripts, references, assets, + delegation points
Step 3: mkdir + SKILL.md
Step 4: Write SKILL.md + resources + Task() patterns
Step 5: Functional testing including delegation
Step 6: Iterate, refining delegation logic
```

### Level 3 Workflow Summary

```
Step 0: Confirm Level 3 → Delegate to meta-multi-agent immediately
Step 0.1: Review generated system, provide docs
[End - no further steps needed]
```

---

## Additional Resources

- [Architecture Decision Matrix](./architecture-decision-matrix.md) - Detailed criteria for choosing levels
- [Delegation Patterns](./delegation-patterns.md) - Task() templates and best practices
- [Bundled Resources Guide](./bundled-resources-guide.md) - Deep dive on scripts, references, assets
- [Skill Organization](./skill-organization.md) - Symlink pattern explained

---

**Remember**: Skill creation is iterative. Start simple, gather feedback, improve continuously. The best skills evolve through real usage, not perfect planning.
