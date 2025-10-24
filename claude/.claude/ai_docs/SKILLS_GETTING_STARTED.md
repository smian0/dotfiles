# Claude Code Skills - Getting Started

Skills are modular capabilities that Claude automatically invokes when contextually appropriate. Unlike slash commands that you explicitly trigger, Skills work in the background based on your requests.

## Quick Start

### 1. Use the skill-creator Tool

The easiest way to create a new skill is using the official `skill-creator` skill:

```bash
# Initialize a new skill with proper structure
python3 ~/.claude/skills/skill-creator/scripts/init_skill.py my-skill-name --path ~/.claude/skills

# Or for project-specific skills
python3 ~/.claude/skills/skill-creator/scripts/init_skill.py my-skill-name --path .claude/skills
```

This automatically creates the proper directory structure with example files.

### 2. Manual Creation (Alternative)

You can also create skills manually:

**Personal Skills** (available across all projects):
```bash
mkdir -p ~/.claude/skills/my-skill
```

**Project Skills** (specific to current project):
```bash
mkdir -p .claude/skills/my-skill
```

### 3. Create SKILL.md

Every skill needs a `SKILL.md` file with frontmatter and instructions:

```markdown
---
name: PDF Processor
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing Skill

You can extract text, tables, images from PDFs. You can also fill PDF forms and merge multiple PDFs.

## When to Use This Skill
- User mentions working with PDF files
- Need to extract data from documents
- Filling out PDF forms
- Merging or splitting PDFs

## Available Operations
1. Extract text: Read and parse text content
2. Extract tables: Convert tables to structured data
3. Fill forms: Populate PDF form fields
4. Merge PDFs: Combine multiple documents
```

### 3. Optional: Add Supporting Files

```
~/.claude/skills/my-skill/
├── SKILL.md              # Required: Core instructions
├── reference.md          # Optional: Detailed API docs
├── examples.md           # Optional: Usage examples
├── scripts/             # Optional: Helper scripts
│   └── process.sh
└── templates/           # Optional: Templates
    └── template.md
```

## Key vs Slash Commands

| Feature | Skills | Slash Commands |
|---------|--------|----------------|
| **Invocation** | Automatic (model-invoked) | Manual (user types `/command`) |
| **Trigger** | Claude decides based on context | User explicitly calls it |
| **File** | `SKILL.md` | `command.md` |
| **Use Case** | Background capabilities | Explicit workflows |

## Frontmatter Options

```yaml
---
name: Skill Name                    # Required: Display name
description: When to use this...    # Required: Triggers and purpose
allowed-tools: Read, Grep, Glob     # Optional: Restrict tools
---
```

## Writing Effective Descriptions

**❌ Vague**: "Helps with documents"

**✅ Specific**: "Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."

**Include**:
- What the skill does
- When to use it
- Keywords users would mention
- Concrete use cases

## Examples

### Simple Skill: Commit Messages
```markdown
---
name: Commit Message Generator
description: Generate conventional commit messages following semantic versioning. Use when creating git commits or when user asks for commit message help.
---

Generate commit messages in format: `type(scope): message`

Types: feat, fix, docs, style, refactor, test, chore
```

### Tool-Restricted Skill: Code Analysis
```markdown
---
name: Code Analyzer
description: Analyze code quality, patterns, and best practices without making changes. Use for code reviews or when user asks to analyze code.
allowed-tools: Read, Grep, Glob
---

Perform read-only code analysis focusing on:
- Code quality metrics
- Design patterns
- Best practice adherence
```

### Multi-file Skill: Testing Framework

```
.claude/skills/test-framework/
├── SKILL.md              # Main instructions
├── reference.md          # Testing best practices
├── scripts/
│   └── run-tests.sh     # Test execution script
└── templates/
    ├── unit-test.md     # Unit test template
    └── e2e-test.md      # E2E test template
```

## Best Practices

1. **One skill, one purpose**: Keep skills focused on a single domain
2. **Specific descriptions**: Include keywords and use cases
3. **Progressive loading**: Claude loads supporting files only when needed
4. **Tool restrictions**: Use `allowed-tools` for read-only or limited operations
5. **Clear triggers**: Describe when Claude should invoke the skill

## Managing Skills

```bash
# View available skills
ls ~/.claude/skills/

# Validate a skill
python3 ~/.claude/skills/skill-creator/scripts/quick_validate.py ~/.claude/skills/my-skill

# Package a skill for distribution (validates + creates zip)
python3 ~/.claude/skills/skill-creator/scripts/package_skill.py ~/.claude/skills/my-skill

# Remove a skill
# Note: Use trash/rm -r instead of rm -rf for safety
trash ~/.claude/skills/skill-name

# Update a skill
# Just edit the SKILL.md file - changes take effect immediately
```

## Troubleshooting

**Skill not being invoked?**
- Check description specificity
- Include more trigger keywords
- Mention the skill domain explicitly in your request

**Want manual control?**
- Use slash commands instead (`/command`)
- Slash commands give you explicit control over invocation

**Need to restrict tools?**
- Add `allowed-tools` frontmatter
- Example: `allowed-tools: Read, Grep, Glob` for read-only

---
Last Updated: 2025-10-17
