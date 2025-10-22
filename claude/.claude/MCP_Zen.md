# Zen MCP Server

**Purpose**: Advanced reasoning and problem-solving with multi-step workflows, extended thinking, and expert model validation

## 🚀 Proactive Usage for Complex Problems

**ALWAYS use Zen tools when:**
- Complex debugging requiring systematic investigation (use `debug`)
- Architectural decisions needing structured analysis (use `planner` or `consensus`)
- Code review before merge/PR (use `codereview`)
- Pre-commit validation of changes (use `precommit`)
- Multi-step planning for complex features (use `planner`)
- Exploring alternatives and trade-offs (use `explore`)
- Deep research requiring hypothesis testing (use `thinkdeep`)
- Need expert validation from multiple models (use `consensus`)
- Challenging assumptions or playing devil's advocate (use `challenge`)

**AVOID using simple chat tools when Zen's structured workflows provide better results.**

## Tool Selection Guide

### When to Use Each Tool

**`debug`** - Bug fixing and troubleshooting
- Authentication bugs, crashes, mysterious errors
- Performance issues, race conditions, memory leaks
- Integration problems requiring root cause analysis
- Systematic investigation with hypothesis testing

**`thinkdeep`** - Deep structured investigation
- Complex bugs requiring methodical analysis
- Production issues with multiple potential causes
- Evidence-based architectural decisions
- Hypothesis-driven reasoning with confidence tracking

**`explore`** - Creative problem-solving
- Theoretical exploration and research phases
- Non-linear reasoning with thought revision
- Exploring alternatives and trade-offs
- Adapts thinking depth to problem complexity

**`planner`** - Complex project planning
- System design and architectural planning
- Migration strategies and refactoring plans
- Breaking down complex features into steps
- Interactive planning with revision capabilities

**`consensus`** - Multi-model decision making
- Technology stack evaluations
- Architectural choices requiring validation
- Feature proposals needing multiple perspectives
- Complex decisions benefiting from debate

**`codereview`** - Comprehensive code review
- Pre-merge quality assessment
- Security vulnerability scanning
- Performance and architecture review
- Audit preparation and compliance validation

**`precommit`** - Git change validation
- Multi-repository validation
- Security review of changes
- Change impact assessment
- Completeness verification before commit

**`chat`** - General Q&A and explanations
- Simple questions across any domain
- Learning concepts, discussing theories
- Quick information lookup
- Web search for current information

**`challenge`** - Critical evaluation
- Testing assumptions and exploring contrarian views
- Playing devil's advocate
- Critique thinking and proposals
- Only when explicitly requested

**`suggest`** - Tool recommendation
- Unsure which Zen tool to use
- Get recommendation based on problem description
- Learn about tool capabilities

## Triggers

### Complexity Indicators
- "Complex", "systematic", "thorough", "comprehensive"
- "Why is this happening?", "root cause", "investigate"
- "Review this PR", "validate changes", "check before commit"
- "Plan this migration", "design this system", "architect this"
- "What's the best approach?", "evaluate options", "compare"

### Explicit Requests
- "Debug this issue" → `debug`
- "Review this code" → `codereview`
- "Plan this feature" → `planner`
- "Check my changes before commit" → `precommit`
- "What do you think about X?" → `consensus`
- "Challenge my assumptions" → `challenge`

### Problem Characteristics
- Multi-step investigation needed → `thinkdeep` or `debug`
- Creative exploration needed → `explore`
- Need architectural planning → `planner`
- Need multiple perspectives → `consensus`
- Quality gate required → `codereview` or `precommit`

## Choose When

**Over basic Claude responses:**
- When structured workflows provide better results
- When expert validation is valuable
- When hypothesis testing is needed
- When multiple perspectives help

**Over native tools:**
- Native Read/Edit: For simple file operations
- Zen debug/codereview: For comprehensive analysis
- Native Grep: For simple searches
- Zen explore: For understanding complex patterns

**Over other MCPs:**
- Serena: For code symbol operations
- Zen: For reasoning and problem-solving workflows
- Context7: For documentation lookup
- Zen consensus: For framework/library decisions

## Works Best With

**Serena + Zen**: Serena provides code context → Zen analyzes and reasons
```
Example: Use Serena's find_symbol to understand code structure,
then Zen's debug to investigate why it's failing
```

**Context7 + Zen**: Context7 provides docs → Zen evaluates approaches
```
Example: Use Context7 for React patterns,
then Zen's consensus to choose best implementation
```

**Sequential workflow**:
1. Serena explores code structure
2. Zen debugs or reviews
3. Serena applies fixes via symbol operations

## Tool Usage Patterns

### Debugging Workflow
1. **Start investigation**: `debug(step=1, hypothesis="initial theory")`
2. **Gather evidence**: Use Serena or Read to examine code
3. **Test hypothesis**: `debug(step=2, findings="evidence", confidence="medium")`
4. **Continue until**: `confidence="very_high"` or `"certain"`
5. **Expert validation**: Automatic if `use_assistant_model=true`

### Planning Workflow
1. **Describe problem**: `planner(step=1, problem_description)`
2. **Get plan outline**: Review initial breakdown
3. **Refine iteratively**: `planner(step=2, refinements)`
4. **Branch alternatives**: Use `branch_from_step` if needed
5. **Finalize**: Set `next_step_required=false`

### Code Review Workflow
1. **Submit for review**: `codereview(files, review_type="full")`
2. **Get analysis**: Security, performance, quality, architecture
3. **Expert validation**: Automatic with `review_validation_type="external"`
4. **Address findings**: Fix issues with appropriate severity

### Consensus Workflow
1. **Define question**: `consensus(step=1, proposal)`
2. **Specify models**: List models with stances (for/against/neutral)
3. **Collect opinions**: Automatic consultation
4. **Get synthesis**: Final recommendation with reasoning

## Key Features

### Extended Thinking
All Zen tools support `thinking_mode` parameter:
- `minimal`: Quick analysis
- `low`: Basic reasoning
- `medium`: Balanced (default)
- `high`: Deep analysis
- `max`: Maximum reasoning depth

### Expert Validation
Most tools support `use_assistant_model=true` (default):
- Automatically validates your work with expert model
- Provides second opinion and catches errors
- Can be disabled for faster iteration

### Multi-Turn Conversations
All tools support `continuation_id`:
- Continue previous investigations
- Build on prior context
- Maintain conversation state

### Web Search Integration
Tools support `use_websearch=true`:
- Access current information
- Look up documentation
- Verify facts and patterns

## Model Selection

Zen tools support various models via `model` parameter:
- **Gemini models**: `gemini-2.5-pro`, `gemini-2.5-flash`
- **OpenAI models**: `gpt-5`, `o3`, `o3-mini`, `o4-mini`
- **X.AI models**: `grok-4`, `grok-3`
- **Custom models**: Via `http://localhost:11434/v1`

Choose based on task requirements (see model capabilities in tool descriptions).

## Examples

```
"This authentication flow is broken"
→ Zen debug (systematic investigation with hypothesis testing)

"Review this PR before I merge"
→ Zen codereview (comprehensive quality assessment)

"Should we use React or Vue for this project?"
→ Zen consensus (multi-model evaluation with debate)

"Plan the migration from REST to GraphQL"
→ Zen planner (interactive planning with revision)

"Why is this query so slow?"
→ Zen debug or thinkdeep (root cause investigation)

"Check my changes before I commit"
→ Zen precommit (git validation and impact assessment)

"Challenge my assumption that microservices are best here"
→ Zen challenge (critical evaluation and alternatives)

"Explore different approaches to caching"
→ Zen explore (creative problem-solving with branching)

"What's the Axios API for interceptors?"
→ Context7 (documentation lookup, not Zen)

"Rename this function everywhere"
→ Serena (symbol operation, not Zen)

"Just explain this code to me"
→ Native Claude chat (simple explanation, not Zen)
```

## Anti-Patterns

**DON'T use Zen when:**
- Simple questions that don't need structured reasoning
- Code symbol operations (use Serena instead)
- Documentation lookup (use Context7 instead)
- File operations (use native Read/Edit/Write)
- Pattern-based edits (use native Edit or Morphllm)

**DO use Zen when:**
- Problem requires systematic investigation
- Need expert validation or multiple perspectives
- Complexity benefits from structured workflow
- Quality gates and comprehensive review needed
- Planning and architectural decisions

## Token Efficiency

Zen tools are **designed for complex problems** where extended reasoning provides value:
- Each tool step builds on previous context
- Multi-turn conversations maintain state
- Expert validation adds overhead but catches errors
- Use `thinking_mode` to control depth vs speed

**Rule of thumb**: If problem can be solved in one simple step, use native Claude. If it requires investigation, validation, or structured reasoning, use Zen.

## Best Practices

1. **Choose the right tool**: Use `suggest` if unsure
2. **Start with clear description**: Provide context and goals
3. **Build iteratively**: Use multi-step workflows for complex problems
4. **Leverage expert validation**: Keep `use_assistant_model=true` for important work
5. **Use web search**: Enable for current information
6. **Track confidence**: In debug/thinkdeep, watch confidence levels
7. **Branch when needed**: Explore alternatives with planning/exploration tools
8. **Combine with other MCPs**: Use Serena for code, Context7 for docs, Zen for reasoning
