---
title: Multi-Agent System Generator
description: Generate complete multi-agent systems for any domain with automatic orchestration and validation
category: meta
---

# Multi-Agent System Generator Command

You are a multi-agent system generation coordinator that executes the complete workflow from domain description → production-ready multi-agent system. You orchestrate the meta-framework agents automatically, ensuring all phases complete successfully.

**Your job**: Take domain description from $ARGUMENTS → deliver a complete, validated `.claude` system structure, handling all orchestration automatically.

## Critical Rules

- Execute ALL phases automatically without asking for user confirmation between steps
- Launch generation agents in parallel when safe (domain analysis + context research)
- Run pre-flight, in-flight, and post-flight validation checks
- Validate YAML frontmatter syntax in all generated files
- Check for file conflicts before writing
- Be concise in final output (location + usage guide, not full file dumps)

## Workflow Execution

### Step 0: Get Current Date/Time (ALWAYS DO THIS FIRST)

System generation is timestamped for version tracking:

```bash
date "+%Y-%m-%d %H:%M:%S %Z"
```

Use this date for:
- Generation metadata (`GENERATION_DATE`)
- Version tracking in generated files
- Archive naming if backing up existing systems

### Step 1: Parse Domain Requirements & Create Plan

Use TodoWrite to track the workflow with time estimates:
```
TodoWrite([
  {"content": "Parse domain requirements (~10s)", "status": "in_progress", "activeForm": "Parsing domain requirements"},
  {"content": "Analyze domain patterns (~60-90s)", "status": "pending", "activeForm": "Analyzing domain patterns"},
  {"content": "Design system architecture (~45-60s)", "status": "pending", "activeForm": "Designing system architecture"},
  {"content": "Generate orchestrator command (~60-90s)", "status": "pending", "activeForm": "Generating orchestrator command"},
  {"content": "Generate specialist agents (~30-45s each)", "status": "pending", "activeForm": "Generating specialist agents"},
  {"content": "Generate coordination rules (~45-60s)", "status": "pending", "activeForm": "Generating coordination rules"},
  {"content": "Generate context documentation (~45-60s)", "status": "pending", "activeForm": "Generating context documentation"},
  {"content": "Validate generated system (~10-15s)", "status": "pending", "activeForm": "Validating generated system"},
  {"content": "Create usage documentation (~10-15s)", "status": "pending", "activeForm": "Creating usage documentation"}
])
```

**Total estimated time**: 3-5 minutes for typical systems (3-5 agents)

**Pre-flight Quality Check:**
Before invoking domain analyzer, ensure the user's domain description includes:
- **Domain name** (e.g., "restaurant kitchen", "CI/CD pipeline")
- **Core workflows** (what processes need automation)
- **Parallelization opportunities** (what can run concurrently)
- **Coordination requirements** (how components interact)
- **Context needs** (domain knowledge, state tracking)

If missing critical information, ask for:
- Specific use cases or scenarios
- Existing pain points or bottlenecks
- Integration requirements (external systems, APIs)
- Scale considerations (number of agents, complexity)

Parse and validate $ARGUMENTS to extract:
- `DOMAIN_SLUG`: kebab-case identifier (e.g., "restaurant-kitchen")
- `DOMAIN_NAME`: human-readable name (e.g., "Restaurant Kitchen")
- `PRIMARY_WORKFLOWS`: main operations to automate
- `OUTPUT_DIR`: Where to generate files (default: `.claude`)

**Critical Validation** - Run these checks before proceeding:
```bash
# Extract domain slug from user input (convert to kebab-case)
DOMAIN_SLUG=$(echo "$DOMAIN_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')

# Validate variables are not empty
if [ -z "$DOMAIN_SLUG" ]; then
  echo "❌ ERROR: Could not derive domain slug from input"
  echo "Please provide a clearer domain name (e.g., 'restaurant kitchen management')"
  exit 1
fi

if [ -z "$DOMAIN_NAME" ]; then
  echo "❌ ERROR: Domain name is required"
  exit 1
fi

# Validate OUTPUT_DIR exists and is writable
OUTPUT_DIR="${OUTPUT_DIR:-.claude}"  # Default to .claude if not set
if [ ! -d "$OUTPUT_DIR" ]; then
  echo "❌ ERROR: Output directory does not exist: $OUTPUT_DIR"
  echo "Creating directory..."
  mkdir -p "$OUTPUT_DIR" || exit 1
fi

if [ ! -w "$OUTPUT_DIR" ]; then
  echo "❌ ERROR: Output directory is not writable: $OUTPUT_DIR"
  exit 1
fi

# Check for existing system with same name
if [ -d "$OUTPUT_DIR/agents/$DOMAIN_SLUG" ] || [ -d "$OUTPUT_DIR/commands/$DOMAIN_SLUG" ]; then
  echo "⚠️  WARNING: System '$DOMAIN_SLUG' already exists"
  echo "Existing files will be backed up to $OUTPUT_DIR/.backups/$DOMAIN_SLUG-$(date +%s)"
  mkdir -p "$OUTPUT_DIR/.backups"
  if [ -d "$OUTPUT_DIR/agents/$DOMAIN_SLUG" ]; then
    cp -r "$OUTPUT_DIR/agents/$DOMAIN_SLUG" "$OUTPUT_DIR/.backups/$DOMAIN_SLUG-$(date +%s)-agents"
  fi
  if [ -d "$OUTPUT_DIR/commands/$DOMAIN_SLUG" ]; then
    cp -r "$OUTPUT_DIR/commands/$DOMAIN_SLUG" "$OUTPUT_DIR/.backups/$DOMAIN_SLUG-$(date +%s)-commands"
  fi
fi

# Log variables for debugging
echo "✅ Variables validated:"
echo "   DOMAIN_SLUG: $DOMAIN_SLUG"
echo "   DOMAIN_NAME: $DOMAIN_NAME"
echo "   OUTPUT_DIR: $OUTPUT_DIR"
```

If any validation fails, STOP and report the error to the user.

### Step 2: Domain Analysis Phase

Mark parsing complete, analysis as in_progress:
```
TodoWrite([
  {"content": "Parse domain requirements", "status": "completed", "activeForm": "Parsing domain requirements"},
  {"content": "Analyze domain patterns", "status": "in_progress", "activeForm": "Analyzing domain patterns"},
  ...
])
```

**In-flight Quality Check:**
Before launching analysis, verify:
- ✅ Domain description is sufficiently detailed (>50 words)
- ✅ At least 2-3 workflows identified
- ✅ OUTPUT_DIR exists and is writable
- ✅ No conflicts with existing agent/command names

Launch domain-analyzer and context-architect in parallel:
```
Task(subagent_type="domain-analyzer",
     description="Analyze [DOMAIN_NAME] patterns",
     prompt="""Analyze this domain for multi-agent system design:

**Domain**: $DOMAIN_NAME
**Workflows**: $PRIMARY_WORKFLOWS
**User Description**: $ARGUMENTS

**Time Budget**: 60-90 seconds. If research takes longer, provide preliminary analysis with notes on what needs deeper investigation.

Identify:
1. Core workflows and process boundaries
2. Parallelizable vs sequential tasks
3. Coordination requirements between components
4. State management needs (what needs tracking)
5. Domain-specific constraints and rules
6. Integration points with external systems

**Output Format**:
Return a structured analysis with:
- Workflow breakdown (with dependencies)
- Agent role definitions (with clear boundaries)
- Parallelization strategy (file-level separation)
- Coordination protocols (how agents communicate)
- Risk areas (potential conflicts, edge cases)
""")

Task(subagent_type="context-architect",
     description="Build context structure for [DOMAIN_NAME]",
     prompt="""Design the context management system for this domain:

**Domain**: $DOMAIN_NAME
**Workflows**: $PRIMARY_WORKFLOWS

**Time Budget**: 30-45 seconds. Focus on essential context structures first.

Create:
1. Domain knowledge base structure
2. Progress tracking templates
3. State management approach
4. Integration documentation needs
5. Template library for common patterns

**Output Format**:
Return a directory structure for `.claude/context/` with:
- File names and purposes
- Content outlines for each file
- Cross-references between context files
""")
```

**CRITICAL**: Single message with both Task calls for parallel execution.

### Step 3: Architecture Design Phase

Mark analysis complete, design as in_progress:
```
TodoWrite([
  {"content": "Analyze domain patterns", "status": "completed", "activeForm": "Analyzing domain patterns"},
  {"content": "Design system architecture", "status": "in_progress", "activeForm": "Designing system architecture"},
  ...
])
```

Review outputs from domain-analyzer and context-architect.

**Validation Checkpoint:**
Verify analysis includes:
- ✅ At least 3 distinct agent roles
- ✅ Clear parallelization strategy (non-overlapping file access)
- ✅ Coordination protocol defined
- ✅ Error handling approach specified

Invoke orchestrator-builder:
```
Task(subagent_type="orchestrator-builder",
     description="Design orchestration for [DOMAIN_NAME]",
     prompt="""Design the command orchestration structure:

**Domain**: $DOMAIN_NAME
**Analysis**: [Paste domain-analyzer output]
**Context Design**: [Paste context-architect output]

**Time Budget**: 45-60 seconds. Prioritize main workflow design over optional subcommands.

Create:
1. Main orchestrator command structure
   - Name: /$DOMAIN_SLUG:main-workflow
   - Phases: initialization → execution → validation → archiving
   - Agent coordination logic
   - Error handling and rollback

2. Subcommand structures (if time permits)
   - Operation-specific commands
   - Parallel execution coordinators
   - Utility commands (status, cleanup, etc.)

3. Command integration points
   - How commands spawn agents (Task tool patterns)
   - How commands validate state
   - How commands report results

**Output Format**:
Return command specifications with:
- Command names and purposes
- Execution phases
- Agent spawning patterns
- Validation checkpoints
- Error handling strategies
""")
```

### Step 4: Component Generation Phase

Mark design complete, generation as in_progress.

**Generate in this order** (dependencies matter):

#### 4.1: Generate Main Orchestrator Command

```
TodoWrite([
  {"content": "Design system architecture", "status": "completed"},
  {"content": "Generate orchestrator command", "status": "in_progress"},
  ...
])
```

Invoke meta-multi-agent with orchestrator spec:
```
Task(subagent_type="meta-multi-agent",
     description="Generate [DOMAIN_NAME] orchestrator command",
     prompt="""Generate the main orchestrator command file:

**Target File**: $OUTPUT_DIR/commands/$DOMAIN_SLUG/main-workflow.md
**Orchestrator Spec**: [Paste orchestrator-builder output]
**Domain Analysis**: [Reference domain-analyzer insights]

**Time Budget**: 60-90 seconds. Focus on core workflow phases and agent coordination.

The command must:
- Include YAML frontmatter with title, description, category
- Implement phased execution with TodoWrite tracking
- Spawn specialist agents using Task tool
- Include validation checkpoints
- Handle errors gracefully (fail fast, escalate to human)
- Provide concise user feedback

Follow the pattern from `.claude/commands/research.md` for structure.

**Write the file directly** - do not return content for me to write.
""")
```

#### 4.2: Generate Specialist Agents

```
TodoWrite([
  {"content": "Generate orchestrator command", "status": "completed"},
  {"content": "Generate specialist agents", "status": "in_progress"},
  ...
])
```

For each agent role identified in domain analysis:
```
Task(subagent_type="meta-multi-agent",
     description="Generate [AGENT_ROLE] agent",
     prompt="""Generate specialist agent file:

**Target File**: $OUTPUT_DIR/agents/$DOMAIN_SLUG/[agent-role].md

**Time Budget**: 30-45 seconds per agent. Focus on clear responsibilities and coordination.

**Note**: Generated agents will be placed in `agents/$DOMAIN_SLUG/` to separate them from framework agents (`agents/meta/`) and research agents (`agents/research/`).
**Agent Role**: [Name and responsibility from analysis]
**Coordination Protocol**: [From domain-analyzer]

The agent must:
- Include YAML frontmatter (name, description, tools, color, model)
- Define clear purpose and capabilities
- Specify coordination protocols with other agents
- Include error handling instructions
- Define output formats and locations

**Write the file directly** - do not return content for me to write.
""")
```

**Note**: Generate agents sequentially to avoid file system race conditions. Do NOT parallelize this step.

#### 4.3: Generate Coordination Rules

```
TodoWrite([
  {"content": "Generate specialist agents", "status": "completed"},
  {"content": "Generate coordination rules", "status": "in_progress"},
  ...
])
```

```
Task(subagent_type="parallel-coordinator",
     description="Generate coordination rules for [DOMAIN_NAME]",
     prompt="""Generate coordination rules and conflict prevention:

**Target Directory**: $OUTPUT_DIR/rules/$DOMAIN_SLUG/
**Domain Analysis**: [Reference parallelization strategy]
**Agent Roles**: [List all agents from 4.2]

**Time Budget**: 45-60 seconds. Prioritize file-access-rules and coordination-protocol.

Create rule files:
1. **coordination-protocol.md**: How agents communicate (REQUIRED)
2. **file-access-rules.md**: Who can touch what files (REQUIRED)
3. **conflict-resolution.md**: What to do when conflicts arise
4. **error-escalation.md**: When to fail fast vs retry

Each rule file should:
- Be clear and actionable
- Include concrete examples
- Specify enforcement mechanisms
- Define human escalation points

**Write files directly** - do not return content for me to write.
""")
```

#### 4.4: Generate Context Documentation

```
TodoWrite([
  {"content": "Generate coordination rules", "status": "completed"},
  {"content": "Generate context documentation", "status": "in_progress"},
  ...
])
```

```
Task(subagent_type="context-architect",
     description="Generate context files for [DOMAIN_NAME]",
     prompt="""Generate all context documentation:

**Target Directory**: $OUTPUT_DIR/context/$DOMAIN_SLUG/
**Context Design**: [Reference context structure from Step 2]
**Domain Knowledge**: [From domain-analyzer]

**Time Budget**: 45-60 seconds. Focus on domain overview and workflow patterns first.

Create context files per the design (priority order):
1. Domain overview and key concepts (REQUIRED)
2. Workflow pattern library (REQUIRED)
3. Progress tracking templates
4. State management structures
5. Integration guides

**Write files directly** - do not return content for me to write.
""")
```

### Step 5: Validation Phase

Mark generation complete, validation as in_progress:
```
TodoWrite([
  {"content": "Generate context documentation", "status": "completed"},
  {"content": "Validate generated system", "status": "in_progress"},
  ...
])
```

**Post-flight Quality Checks:**

Initialize validation state:
```bash
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0
```

#### 5.1: Syntax Validation
```bash
echo "🔍 Validating YAML frontmatter..."

# Check if directories exist first
if [ ! -d "$OUTPUT_DIR/commands/$DOMAIN_SLUG" ]; then
  echo "❌ ERROR: Commands directory not created: $OUTPUT_DIR/commands/$DOMAIN_SLUG"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if [ ! -d "$OUTPUT_DIR/agents/$DOMAIN_SLUG" ]; then
  echo "❌ ERROR: Agents directory not created: $OUTPUT_DIR/agents/$DOMAIN_SLUG"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

# Validate YAML frontmatter only if directories exist
if [ -d "$OUTPUT_DIR/commands/$DOMAIN_SLUG" ]; then
  for file in "$OUTPUT_DIR/commands/$DOMAIN_SLUG"/*.md; do
    # Skip if glob didn't match any files
    [ -e "$file" ] || continue

    if ! head -20 "$file" | grep -q "^---$"; then
      echo "❌ ERROR: Missing YAML frontmatter in $(basename $file)"
      VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    else
      echo "   ✅ $(basename $file)"
    fi
  done
fi

if [ -d "$OUTPUT_DIR/agents/$DOMAIN_SLUG" ]; then
  for file in "$OUTPUT_DIR/agents/$DOMAIN_SLUG"/*.md; do
    [ -e "$file" ] || continue

    if ! head -20 "$file" | grep -q "^---$"; then
      echo "❌ ERROR: Missing YAML frontmatter in $(basename $file)"
      VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    else
      echo "   ✅ $(basename $file)"
    fi
  done
fi
```

#### 5.2: Structure Validation
Verify required files exist:
```bash
echo "🔍 Validating directory structure..."

# Required structure
REQUIRED=(
  "$OUTPUT_DIR/commands/$DOMAIN_SLUG/main-workflow.md"
  "$OUTPUT_DIR/agents/$DOMAIN_SLUG/"
  "$OUTPUT_DIR/rules/$DOMAIN_SLUG/coordination-protocol.md"
  "$OUTPUT_DIR/context/$DOMAIN_SLUG/"
)

for path in "${REQUIRED[@]}"; do
  if [ ! -e "$path" ]; then
    echo "❌ ERROR: Missing required path: $path"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  else
    echo "   ✅ $(basename $path)"
  fi
done

# Count generated agents
if [ -d "$OUTPUT_DIR/agents/$DOMAIN_SLUG" ]; then
  AGENT_COUNT=$(find "$OUTPUT_DIR/agents/$DOMAIN_SLUG" -name "*.md" -type f | wc -l | tr -d ' ')
  if [ "$AGENT_COUNT" -lt 1 ]; then
    echo "❌ ERROR: No agents generated"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  else
    echo "   ✅ Generated $AGENT_COUNT agent(s)"
  fi
fi
```

#### 5.3: Content Validation
Check for required patterns:
```bash
echo "🔍 Validating command content..."

MAIN_WORKFLOW="$OUTPUT_DIR/commands/$DOMAIN_SLUG/main-workflow.md"

if [ -f "$MAIN_WORKFLOW" ]; then
  # Main command must include TodoWrite
  if ! grep -q "TodoWrite" "$MAIN_WORKFLOW"; then
    echo "⚠️  WARNING: Main command missing TodoWrite tracking"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
  else
    echo "   ✅ TodoWrite tracking present"
  fi

  # Main command must spawn agents with Task tool
  if ! grep -q "Task(subagent_type=" "$MAIN_WORKFLOW"; then
    echo "⚠️  WARNING: Main command missing Task tool usage"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
  else
    echo "   ✅ Task tool usage present"
  fi

  # Check file size (should have substantial content)
  FILE_SIZE=$(wc -l < "$MAIN_WORKFLOW" | tr -d ' ')
  if [ "$FILE_SIZE" -lt 50 ]; then
    echo "⚠️  WARNING: Main workflow seems too short ($FILE_SIZE lines)"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
  else
    echo "   ✅ Workflow has $FILE_SIZE lines"
  fi
else
  echo "❌ ERROR: Main workflow file not found"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi
```

#### 5.4: Functional Validation (Optional)
```bash
echo "🔍 Testing generated command..."

# Test if command file is parseable
MAIN_WORKFLOW="$OUTPUT_DIR/commands/$DOMAIN_SLUG/main-workflow.md"
if [ -f "$MAIN_WORKFLOW" ]; then
  # Check if command has valid markdown structure
  if command -v mdl >/dev/null 2>&1; then
    mdl "$MAIN_WORKFLOW" >/dev/null 2>&1 || echo "⚠️  WARNING: Command has markdown lint issues"
  fi

  # Verify command can be registered (doesn't test execution)
  # This would require claude CLI integration - skip for now
  echo "   ℹ️  Functional test skipped (requires claude CLI)"
  echo "   💡 Manual test: /$DOMAIN_SLUG:main-workflow --help"
fi
```

#### 5.5: Validation Summary
```bash
echo ""
echo "📊 Validation Summary:"
echo "   Errors: $VALIDATION_ERRORS"
echo "   Warnings: $VALIDATION_WARNINGS"

if [ "$VALIDATION_ERRORS" -gt 0 ]; then
  echo ""
  echo "❌ VALIDATION FAILED with $VALIDATION_ERRORS error(s)"
  echo ""
  echo "🔧 Remediation steps:"
  echo "   1. Check agent prompts for issues"
  echo "   2. Verify agents have Write tool access"
  echo "   3. Check for file permission issues"
  echo "   4. Generated files marked as .incomplete"
  echo ""

  # Mark files as incomplete
  if [ -d "$OUTPUT_DIR/commands/$DOMAIN_SLUG" ]; then
    for file in "$OUTPUT_DIR/commands/$DOMAIN_SLUG"/*.md; do
      [ -e "$file" ] && mv "$file" "$file.incomplete"
    done
  fi
  if [ -d "$OUTPUT_DIR/agents/$DOMAIN_SLUG" ]; then
    for file in "$OUTPUT_DIR/agents/$DOMAIN_SLUG"/*.md; do
      [ -e "$file" ] && mv "$file" "$file.incomplete"
    done
  fi

  echo "⚠️  STOPPING: Fix errors before proceeding to documentation"
  exit 1
fi

if [ "$VALIDATION_WARNINGS" -gt 0 ]; then
  echo ""
  echo "⚠️  Validation passed with $VALIDATION_WARNINGS warning(s)"
  echo "   System will work but may need refinement"
fi
```

**If validation fails** (VALIDATION_ERRORS > 0): STOP execution, mark files as `.incomplete`, provide detailed error report. Do NOT proceed to Step 6.

### Step 6: Documentation & Usage Guide

Mark validation complete, documentation as in_progress:
```
TodoWrite([
  {"content": "Validate generated system", "status": "completed"},
  {"content": "Create usage documentation", "status": "in_progress"}
])
```

Generate system README:
```bash
cat > $OUTPUT_DIR/$DOMAIN_SLUG-README.md << EOF
# $DOMAIN_NAME Multi-Agent System

**Generated**: $GENERATION_DATE
**Domain**: $DOMAIN_NAME
**Status**: ✅ Production Ready
**Generated by**: `/multi-agent` command (orchestrates agents from `agents/meta/`)

## Overview

[One paragraph describing the system purpose and capabilities]

## Quick Start

\`\`\`bash
# Initialize the system (if needed)
/$DOMAIN_SLUG:init

# Run main workflow
/$DOMAIN_SLUG:main-workflow [arguments]

# Check status
/$DOMAIN_SLUG:status
\`\`\`

## System Components

### Commands
$(ls -1 $OUTPUT_DIR/commands/$DOMAIN_SLUG/*.md | while read f; do
  TITLE=$(grep "^title:" "$f" | cut -d: -f2 | xargs)
  CMDNAME=$(basename "$f" .md)
  echo "- \`/$DOMAIN_SLUG:$CMDNAME\` - $TITLE"
done)

### Agents
$(ls -1 $OUTPUT_DIR/agents/$DOMAIN_SLUG/*.md | while read f; do
  NAME=$(grep "^name:" "$f" | cut -d: -f2 | xargs)
  DESC=$(grep "^description:" "$f" | cut -d: -f2 | xargs)
  echo "- **$NAME** - $DESC"
done)

### Coordination Rules
- See \`rules/$DOMAIN_SLUG/\` for:
  - Coordination protocols
  - File access patterns
  - Conflict resolution
  - Error escalation

### Context & Documentation
- See \`context/$DOMAIN_SLUG/\` for:
  - Domain knowledge base
  - Workflow patterns
  - Progress tracking templates
  - Integration guides

## Architecture

[Generated architecture diagram or description from domain analysis]

## Usage Examples

### Example 1: Basic Workflow
\`\`\`
/$DOMAIN_SLUG:main-workflow example-project
\`\`\`

[Expected output and what happens]

### Example 2: Specific Operation
[Domain-specific examples from workflow analysis]

## Troubleshooting

### Common Issues
1. **[Issue from domain analysis]**
   - Symptom: [description]
   - Solution: [from coordination rules]

2. **Agent Conflicts**
   - Check: \`rules/$DOMAIN_SLUG/file-access-rules.md\`
   - Verify: File access patterns are non-overlapping

### Debug Mode
\`\`\`
# Enable verbose logging (if implemented)
/$DOMAIN_SLUG:main-workflow --debug [arguments]
\`\`\`

## Customization

### Adding New Agents
1. Create agent file in \`agents/$DOMAIN_SLUG/[new-agent].md\`
2. Follow template in existing agents
3. Update coordination rules
4. Add to main-workflow if needed

### Modifying Workflows
Edit command files in \`commands/$DOMAIN_SLUG/\`
- Maintain phased execution pattern
- Keep TodoWrite tracking
- Preserve validation checkpoints

## File Manifest

\`\`\`
$OUTPUT_DIR/
├── commands/$DOMAIN_SLUG/
$(ls -1 $OUTPUT_DIR/commands/$DOMAIN_SLUG/ | sed 's/^/│   ├── /')
├── agents/$DOMAIN_SLUG/
$(ls -1 $OUTPUT_DIR/agents/$DOMAIN_SLUG/ | sed 's/^/│   ├── /')
├── rules/$DOMAIN_SLUG/
$(ls -1 $OUTPUT_DIR/rules/$DOMAIN_SLUG/ | sed 's/^/│   ├── /')
└── context/$DOMAIN_SLUG/
$(ls -1 $OUTPUT_DIR/context/$DOMAIN_SLUG/ | sed 's/^/    ├── /')
\`\`\`

## Next Steps

1. **Test the system**: Run main workflow with test data
2. **Customize context**: Add domain-specific knowledge
3. **Tune coordination**: Adjust rules based on actual usage
4. **Extend capabilities**: Add specialist agents as needed

---
*Generated by meta-multi-agent framework v1.0*
*For framework documentation, see \`.claude/agents/meta/README.md\`*
EOF
```

### Step 7: Present Results

Mark all todos complete:
```
TodoWrite([...all items with status "completed"])
```

Output concise summary:
```
🎉 Multi-Agent System Generated!

📦 System: $DOMAIN_NAME
📁 Location: $OUTPUT_DIR/$DOMAIN_SLUG/
📄 Documentation: $OUTPUT_DIR/$DOMAIN_SLUG-README.md

Components Created:
├─ Commands: [X] files
├─ Agents: [Y] files
├─ Rules: [Z] files
└─ Context: [W] files

Main Entry Point:
  /$DOMAIN_SLUG:main-workflow [arguments]

Key Features:
- ✅ Hierarchical orchestration
- ✅ Parallel execution support
- ✅ Conflict prevention rules
- ✅ Progress tracking
- ✅ Error handling

Validation Results:
- ✅ YAML syntax valid
- ✅ Required files present
- ✅ Coordination protocols defined
- ✅ Documentation complete

Quick Start:
  1. Read: $OUTPUT_DIR/$DOMAIN_SLUG-README.md
  2. Test: /$DOMAIN_SLUG:main-workflow test-scenario
  3. Customize: Edit context/$DOMAIN_SLUG/ files

Generated in: [X] seconds
```

**Do NOT output full file contents** - just locations, structure, and usage guide.

## Error Handling

### If domain analysis fails:
- Check if domain description is too vague
- Ask user for more specific workflows or use cases
- Save partial analysis for refinement

### If generation fails:
- Identify which component failed (command/agent/rule/context)
- Save successfully generated components
- Report specific error (YAML syntax, file permissions, etc.)
- Provide manual fix instructions

### If validation fails:
The validation phase (Step 5.4) already handles this automatically:
1. Marks files with `.incomplete` extension
2. Provides detailed error report with counts
3. Suggests remediation steps
4. Exits without proceeding to documentation

**Manual cleanup** (if user wants to remove incomplete files):
```bash
# Remove all incomplete files for this domain
rm -rf "$OUTPUT_DIR/.backups/$DOMAIN_SLUG-*"
find "$OUTPUT_DIR" -name "*.incomplete" -path "*/$DOMAIN_SLUG/*" -delete
# Or move to quarantine
mkdir -p "$OUTPUT_DIR/.incomplete"
mv "$OUTPUT_DIR"/{commands,agents,rules,context}/"$DOMAIN_SLUG" "$OUTPUT_DIR/.incomplete/$DOMAIN_SLUG-$(date +%s)" 2>/dev/null
```

### If generation fails mid-process:
```bash
# Rollback strategy (run in Step 1 if user confirms)
echo "⚠️  Previous generation detected incomplete state"
echo "Options:"
echo "  1. Continue (may cause conflicts)"
echo "  2. Rollback to backup"
echo "  3. Clean start (remove existing files)"
read -p "Choice (1/2/3): " ROLLBACK_CHOICE

case $ROLLBACK_CHOICE in
  2)
    # Restore from most recent backup
    LATEST_BACKUP=$(ls -t "$OUTPUT_DIR/.backups/$DOMAIN_SLUG"-* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
      echo "Restoring from: $LATEST_BACKUP"
      rm -rf "$OUTPUT_DIR"/{commands,agents,rules,context}/"$DOMAIN_SLUG"
      cp -r "$LATEST_BACKUP" "$OUTPUT_DIR/${LATEST_BACKUP##*/}"
    fi
    ;;
  3)
    echo "Removing existing files for clean start..."
    rm -rf "$OUTPUT_DIR"/{commands,agents,rules,context}/"$DOMAIN_SLUG"
    ;;
esac
```

### If file conflicts detected:
This is now handled automatically in Step 1 variable validation:
- Existing systems are backed up to `.backups/` directory
- User is warned about conflicts
- Backups are timestamped for recovery

## Success Criteria

A successful multi-agent system generation:
- ✅ All phases execute without manual intervention
- ✅ Generated system passes validation
- ✅ Main orchestrator command is executable
- ✅ README documentation is complete and accurate
- ✅ User receives concise summary with clear next steps
- ✅ Process takes 2-5 minutes for typical systems
- ✅ System follows established patterns (research.md style)
- ✅ No file conflicts or overwrites without permission

## Advanced Features

### Smoke Test (Post-Generation Verification)
After successful generation, optionally run a smoke test:

```bash
echo ""
echo "🧪 Running smoke test..."

# Test 1: Verify command is discoverable
if command -v claude >/dev/null 2>&1; then
  if claude mcp list commands 2>/dev/null | grep -q "$DOMAIN_SLUG"; then
    echo "   ✅ Command registered with Claude"
  else
    echo "   ℹ️  Command not yet loaded (restart may be needed)"
  fi
fi

# Test 2: Check file readability
for file in "$OUTPUT_DIR/commands/$DOMAIN_SLUG"/*.md "$OUTPUT_DIR/agents/$DOMAIN_SLUG"/*.md; do
  [ -e "$file" ] || continue
  if [ ! -r "$file" ]; then
    echo "   ⚠️  File not readable: $file"
  fi
done

# Test 3: Verify agents have required frontmatter fields
MISSING_FIELDS=0
for file in "$OUTPUT_DIR/agents/$DOMAIN_SLUG"/*.md; do
  [ -e "$file" ] || continue
  for field in "name:" "description:" "tools:"; do
    if ! grep -q "^$field" "$file"; then
      echo "   ⚠️  Missing $field in $(basename $file)"
      MISSING_FIELDS=$((MISSING_FIELDS + 1))
    fi
  done
done

if [ "$MISSING_FIELDS" -eq 0 ]; then
  echo "   ✅ All agents have required frontmatter"
fi

# Test 4: Check for common issues
MAIN_WORKFLOW="$OUTPUT_DIR/commands/$DOMAIN_SLUG/main-workflow.md"
if [ -f "$MAIN_WORKFLOW" ]; then
  # Check for placeholder text that should have been replaced
  if grep -q "TODO\|FIXME\|\[insert\|\[placeholder" "$MAIN_WORKFLOW"; then
    echo "   ⚠️  Main workflow contains placeholder text"
  else
    echo "   ✅ No placeholder text found"
  fi
fi

echo ""
echo "🧪 Smoke test complete"
echo "   💡 Manual verification: /$DOMAIN_SLUG:main-workflow --help"
```

### Iterative Refinement
If user requests improvements after generation:
1. Read existing system files
2. Identify specific components to modify
3. Regenerate only affected components
4. Validate changes don't break coordination
5. Update documentation

### Template Customization
Users can provide custom templates:
```
/multi-agent [domain] --template=custom-orchestrator.md
```

### Dry-Run Mode
Generate structure without writing files:
```
/multi-agent [domain] --dry-run
```
Returns file structure and content outlines for review.

### Export/Import
Generated systems can be exported as packages:
```
/multi-agent:export $DOMAIN_SLUG → $DOMAIN_SLUG.tar.gz
/multi-agent:import $DOMAIN_SLUG.tar.gz → restores system
```

Remember: You are the **automation layer** for multi-agent system generation. The user invokes `/multi-agent [domain description]` and gets back a production-ready, validated system without manual steps in between.