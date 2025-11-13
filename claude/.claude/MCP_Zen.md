# Zen MCP Server

**Purpose**: Advanced reasoning and problem-solving with multi-step workflows, extended thinking, and expert model validation

## Quick Reference - When in Doubt, Use Keywords!

**Explicit keywords guarantee correct routing:**
- Say **"ultrathink"** → Zen explore (deep reasoning)
- Say **"zen debug"** → Zen debug (systematic investigation)
- Say **"zen review"** → Zen codereview (comprehensive PR review)
- Say **"zen consensus"** → Zen consensus (multi-model evaluation)
- Say **"zen plan"** → Zen planner (interactive planning)
- Say **"challenge this"** → Zen challenge (devil's advocate)

**If you don't use a keyword, Zen will only trigger on clear quantifiable indicators (see below).**

## Triggers

**Primary (Explicit Keywords):**
- **"ultrathink"** - deep reasoning with extended thinking (explore tool)
- **"zen debug"** - systematic bug investigation
- **"zen review"** - comprehensive code review
- **"zen consensus"** - multi-model evaluation
- **"zen plan"** - interactive planning workflow
- **"challenge this"** / **"devil's advocate"** - critical analysis

**Secondary (Quantifiable Indicators):**
- Multi-file bugs (3+ files) requiring systematic investigation
- Technology/framework selection with 3+ viable alternatives
- Pre-merge PR reviews (100+ lines changed)
- Planning work spanning 5+ distinct steps
- Research requiring hypothesis testing across multiple sources

**Tertiary (Context Clues - Use Sparingly):**
- Explicit requests for "thorough", "comprehensive", or "systematic" analysis
- Pre-commit validation of changes
- Expert validation needed from multiple perspectives

## Choose When
- **Over basic Claude**: When you need structured workflows (debugging, planning, consensus)
- **Over native tools**: Use Zen tools for comprehensive analysis, not simple Read/Edit operations
- **Over other MCPs**: Serena for code symbols, Context7 for docs, Zen for reasoning

## NOT For
**Use native Claude instead:**
- Single-file bugs or syntax errors
- Obvious decisions with only 1 clear answer
- Questions answerable in 1-2 sentences
- Simple code explanations

**Use other MCPs instead:**
- Documentation lookup → Context7 MCP
- Symbol operations (rename, find references) → Serena MCP
- File operations (read, write, edit) → Native tools

## Examples

**✅ Use Zen:**
```
"ultrathink: analyze the performance bottleneck"
→ Zen explore (deep reasoning with extended thinking)

"zen debug: authentication flow broken across 5 files"
→ Zen debug (systematic investigation)

"zen review: review this PR before I merge (200+ lines)"
→ Zen codereview (comprehensive quality assessment)

"zen consensus: should we use React or Vue?"
→ Zen consensus (multi-model evaluation)

"zen plan: plan the migration from REST to GraphQL"
→ Zen planner (interactive planning)

"challenge this: microservices are always better than monoliths"
→ Zen challenge (devil's advocate analysis)

"Check my changes before I commit"
→ Zen precommit (git validation)
```

**❌ Don't Use Zen:**
```
"What's the Axios API for interceptors?"
→ Context7 (documentation lookup, not Zen)

"Rename this function everywhere"
→ Serena (symbol operation, not Zen)

"This function has a syntax error on line 10"
→ Native Claude (single-file fix, not Zen)

"Explain what this function does"
→ Native Claude (simple explanation, not Zen)
```

## Model Cost Optimization

Prefer free Ollama Cloud models (`deepseek-v3.1:671b-cloud` for reasoning, `qwen3-coder:480b-cloud` for code, `glm-4.6:cloud` for speed) before escalating to paid models (gemini-2.5-pro, gpt-5, o3).

For automated multi-step workflows with cost optimization, use the `zen-workflow` skill.
