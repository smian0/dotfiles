# CLAUDE.md Best Practices Guide (2025)

## Core Principles

### 1. Token Efficiency is Critical
- **Target**: Keep under 500 tokens (ideally 400-450)
- **Why**: CLAUDE.md is prepended to EVERY prompt, consuming token budget
- **Impact**: Bloated files increase costs and introduce noise

### 2. CLAUDE.md Supremacy Principle
- CLAUDE.md instructions **override** user prompts consistently
- Persists throughout entire session vs contextual user prompts
- Use this power strategically for non-negotiable behaviors

### 3. Behavioral Programming, Not Education
> "You're writing for Claude, not onboarding a junior dev" - Anthony Calzadilla

Every line should modify Claude's behavior, not explain concepts.

## Optimal Structure Template

```markdown
# Role (1-2 lines max)
Senior developer focused on [specific focus areas]

# Core Rules (bullets only)
- EDIT existing files > create new
- NO unsolicited docs/README
- Match project patterns
- Verify before responding

# File Operations (critical section)
1. ALWAYS scan for existing files first
2. UPDATE/EXTEND existing code
3. CREATE only when explicitly needed

# Response Constraints
- Direct, concise answers
- Skip explanations unless asked
- < 4 lines for simple queries
- Code-only for implementations

# Verification (< 90% confidence = ASK)
- Syntax ✓ Logic ✓ Paths ✓ Dependencies ✓
```

## High-Impact Behavioral Modifiers

### Power Words That Work
- **ALWAYS** / **NEVER** - Absolute rules
- **MANDATORY** - Critical protocols
- **STRICTLY ENFORCE** - Non-negotiable
- **< 90% confidence** - Uncertainty threshold
- **Priority Order** with numbers (1, 2, 3)

### Formatting for Impact
- **Bold** for emphasis on key actions
- CAPS for critical words (NEVER, ALWAYS)
- Numbered lists for priority/hierarchy
- Bullet points for equal-weight items
- Arrow syntax for process flow (→)

## Common Mistakes to Avoid

### ❌ DON'T Include
1. **Code templates** - Claude knows patterns
   ```markdown
   # BAD - Wastes ~80 tokens
   ### Function Structure
   ```language
   function name(param) {
       // logic
   }
   ```
   ```

2. **Verbose explanations**
   ```markdown
   # BAD - Too wordy
   When encountering an error, you should first 
   analyze the error message, then consider possible
   causes, and finally implement a solution...
   
   # GOOD - Direct
   Error → Analyze → Fix
   ```

3. **Duplicate instructions**
   - Check for redundancy between sections
   - Consolidate similar rules

4. **Generic programming advice**
   - "Write clean code" (too vague)
   - "Follow best practices" (implicit)

5. **Multi-paragraph descriptions**
   - Use bullets instead
   - One concept per line

## Advanced Techniques

### 1. Hierarchical CLAUDE.md
```
project/
├── CLAUDE.md              # Project-wide rules
├── frontend/
│   └── CLAUDE.md         # Frontend-specific
└── backend/
    └── CLAUDE.md         # Backend-specific
```

### 2. Custom Slash Commands
Store in `.claude/commands/` for repeated workflows:
```markdown
# .claude/commands/debug.md
Run tests, analyze failures, fix issues, re-run tests
```

### 3. Agent Triggers
```markdown
## Agent Triggers
### agents-md-manager
Launch when user mentions:
- Creating AGENTS.md files
- Setting up agent configuration
```

## Proven Rule Categories

### 1. File Operations (Highest Priority)
```markdown
1. ALWAYS EDIT existing files first
2. ANALYZE before creating
3. UPDATE/EXTEND existing tests
4. CREATE only when no alternative
5. NEVER generate docs unless requested
```

### 2. Response Behavior
```markdown
- Direct, concise
- Skip explanations unless asked
- Trust user intent
- < 4 lines for simple queries
```

### 3. Code Guidelines
```markdown
- NO docstrings/comments/print unless requested
- Match existing patterns
- Clean, minimal, modern syntax
```

### 4. Performance & Tools
```markdown
- ripgrep (rg) > grep
- Batch file operations
- Parallelize independent tasks
- NO commits without explicit request
```

### 5. Verification Protocol
```markdown
### Before Finalizing (< 90% confidence = ASK)
Syntax ✓ Logic ✓ Paths ✓ Dependencies ✓
```

## Optimization Checklist

Before finalizing your CLAUDE.md:

- [ ] Under 500 tokens?
- [ ] All rules are behavioral (not educational)?
- [ ] No duplicate instructions?
- [ ] Using power words (ALWAYS, NEVER)?
- [ ] Bullets over paragraphs?
- [ ] No code templates?
- [ ] Clear priority order for conflicts?
- [ ] Specific, actionable directives?

## Token Counting Tips

### Quick Estimates
- 1 token ≈ 4 characters
- 1 line of text ≈ 10-15 tokens
- Code block ≈ 50-100 tokens

### Reduction Strategies
1. **Combine related rules**
   ```markdown
   # Before (3 lines, ~30 tokens)
   - NO docstrings unless requested
   - NO comments unless requested
   - NO print statements unless requested
   
   # After (1 line, ~10 tokens)
   - NO docstrings/comments/print unless requested
   ```

2. **Use symbols over words**
   ```markdown
   # Before
   - First analyze, then implement, finally verify
   
   # After
   - Analyze → Implement → Verify
   ```

3. **Remove obvious context**
   ```markdown
   # Before
   - Check if existing test files can be extended
   
   # After
   - Extend existing tests
   ```

## Real-World Examples

### Minimal Effective CLAUDE.md (~250 tokens)
```markdown
# Senior developer, security-focused

## File Ops (STRICT)
1. EDIT existing > create new
2. NEVER create docs unless asked
3. Extend tests, don't create new

## Response
- Concise, direct
- Skip explanations
- Code-only for implementations

## Verify (< 90% = ASK)
Syntax ✓ Logic ✓ Paths ✓

## Code
- NO comments/docstrings/print
- Match patterns
- Modern syntax
```

### Feature-Rich CLAUDE.md (~450 tokens)
```markdown
# Expert developer, clean/secure code

## Agent Triggers
### agents-md-manager
Launch for: AGENTS.md, agent rules, memory config

## File Operations - MANDATORY
1. ALWAYS EDIT existing first
2. ANALYZE before creating
3. UPDATE/EXTEND tests
4. CREATE only if no alternative
5. NEVER generate *.md unless requested

### Rules
- Tests: Extend existing
- Config: Update existing
- Scripts: Add functions
- Debug: use -debug suffix

## Response Behavior
- Direct, concise
- Trust user intent
- < 4 lines simple queries
- Code-only implementations

## Output Constraints
### ALWAYS
- READ existing code first
- FOLLOW project patterns
- VALIDATE dependencies
- TEST logic mentally

### NEVER
- BREAK compatibility
- IGNORE error handling
- MAKE assumptions

## Verification - MANDATORY
Before finalizing:
1. Syntax ✓
2. Logic ✓
3. Paths ✓
4. Dependencies ✓

< 90% confidence = STOP & ASK

## Problem Solving
Break down → Analyze → Implement → Verify

## Code
- NO docstrings/comments/print
- Match patterns
- Clean, minimal

## Performance
- rg > grep
- Batch operations
- NO commits without request
```

## Testing Your CLAUDE.md

### Effectiveness Test
1. Start fresh Claude Code session
2. Ask Claude to create a test file
3. Check if it searches for existing tests first
4. Verify it follows your rules

### Token Count Test
```bash
# Rough token count
wc -c CLAUDE.md | awk '{print $1/4 " tokens (approx)"}'
```

### Behavior Override Test
1. In prompt: "Add detailed comments to this code"
2. If CLAUDE.md has "NO comments unless requested"
3. Claude should skip comments (CLAUDE.md wins)

## Community Resources

- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) - Curated commands and workflows
- [Anthropic Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - Official guidelines
- [ClaudeLog](https://claudelog.com) - Tips and tutorials

## Key Takeaways

1. **Every token counts** - CLAUDE.md loads with every prompt
2. **Behavior over education** - Direct Claude, don't teach
3. **CLAUDE.md wins** - It overrides user prompts
4. **Concise is powerful** - Bullets > paragraphs
5. **Test and iterate** - Refine based on actual usage

---

*Last Updated: 2025*
*Based on research from Anthropic documentation, community best practices, and production usage patterns*