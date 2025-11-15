# Markdown Query Skill

**A Claude Code skill for advanced markdown processing with MQ-style selectors, Obsidian features, and intelligent linting.**

Converted from the `mcp_markdown` MCP server to a self-contained Claude skill for direct Python invocation without MCP protocol overhead.

## Installation

This skill is ready to use - it's located at:
```
.claude/skills/markdown-query/
```

## Usage

Invoke via the skill system or import directly:

```python
from .claude.skills.markdown_query.scripts.cli import query, bulk_query, lint_document

# Extract headers
result = query("README.md", ".h1")

# Query multiple files
results = bulk_query("/vault", ".h2")

# Lint and fix
lint_document("file.md")
```

See `SKILL.md` for complete invocation guide.

## Structure

```
markdown-query/
├── SKILL.md              # Main skill guide (111 lines)
├── scripts/              # Implementation (8 modules)
├── references/           # Documentation (4 guides)
└── assets/              # Examples (query patterns)
```

## Key Features

- **70x faster** than external MQ command-line tools
- **Intelligent caching** with automatic invalidation
- **Obsidian support**: wiki links, embeds, callouts, dataview
- **Auto-fixing**: headers, whitespace, task formatting
- **Spec validation**: completeness scoring and analysis

## Performance

| Vault Size | Files | Processing Time |
|------------|-------|----------------|
| Small      | <100  | <50ms          |
| Medium     | 100-500| 2-5 seconds    |
| Large      | 500+  | 5-15 seconds   |

## References

- [MQ Selectors](./references/mq-selectors.md) - Complete selector syntax
- [Obsidian Features](./references/obsidian-features.md) - Wiki links, embeds, etc.
- [Linting Rules](./references/linting-rules.md) - Issue detection & fixing
- [Performance Tips](./references/performance-tips.md) - Optimization strategies
- [Example Queries](./assets/example-queries.md) - Common patterns

## Original MCP Server

This skill was converted from:
```
claude/.claude/mcp_servers/mcp_markdown/
```

**Why convert to skill?**
- ✅ No MCP serialization overhead (10-100x faster for local operations)
- ✅ Direct Python imports vs protocol calls
- ✅ Better documentation structure (progressive disclosure)
- ✅ Self-contained with all dependencies
- ✅ Easier to version control and maintain

**When to use MCP instead:**
- Cross-IDE tool integration needed
- Language-agnostic interface required
- External process communication necessary

---

**Last Updated**: 2024-11-15

