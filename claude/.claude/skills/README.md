# Claude Code Skills

This directory contains skills that extend Claude's capabilities.

## What's Included

### skill-creator
Official Anthropic skill for creating new skills. Includes:
- `SKILL.md` - Complete guide for skill creation
- `scripts/init_skill.py` - Initialize new skill with proper structure
- `scripts/package_skill.py` - Validate and package skills for distribution
- `scripts/quick_validate.py` - Quick validation of skill structure

### mcp-builder
Official Anthropic skill for building high-quality MCP (Model Context Protocol) servers. Includes:
- `SKILL.md` - Comprehensive 4-phase MCP development guide
- `reference/` - Extensive documentation:
  - `mcp_best_practices.md` - Universal MCP guidelines
  - `python_mcp_server.md` - Python/FastMCP implementation guide
  - `node_mcp_server.md` - TypeScript/Node implementation guide
  - `evaluation.md` - Testing and evaluation guidelines
- `scripts/` - Evaluation tools:
  - `evaluation.py` - Run MCP server evaluations
  - `connections.py` - Connection helpers
  - `example_evaluation.xml` - Sample evaluation format

### fastmcp-builder
Custom skill for building MCP servers using **FastMCP v2** and **uv** single-file scripts. Streamlined alternative to mcp-builder focused exclusively on Python with zero-config dependency management. Includes:
- `SKILL.md` - 4-phase FastMCP v2 development guide with uv workflow
- `references/` - FastMCP-specific documentation:
  - `fastmcp_reference.md` - Complete FastMCP v2 patterns and examples
  - `uv_guide.md` - uv single-file script guide with inline dependencies
  - `evaluation.md` - Testing and evaluation guidelines

**Key Features:**
- ✅ Single-file servers with inline dependencies
- ✅ Zero configuration (no pyproject.toml or virtual envs)
- ✅ Instant dependency installation with uv
- ✅ FastMCP v2 exclusive (Python only)

### template-skill
Basic template for creating new skills from scratch.

## Quick Start

### Create a New Skill

```bash
# Initialize a new skill
cd ~/.claude/skills
python3 skill-creator/scripts/init_skill.py my-skill-name --path .

# This creates:
# my-skill-name/
# ├── SKILL.md
# ├── scripts/
# ├── references/
# └── assets/
```

### Validate a Skill

```bash
python3 skill-creator/scripts/quick_validate.py path/to/my-skill
```

### Package a Skill

```bash
# Validates and creates a distributable zip
python3 skill-creator/scripts/package_skill.py path/to/my-skill
```

## Skill Structure

Every skill needs:
- `SKILL.md` with YAML frontmatter (name + description)
- Optional: `scripts/`, `references/`, `assets/` directories

## How Skills Work

Skills are **model-invoked** - Claude automatically uses them based on context, unlike slash commands which you manually trigger.

When you create a skill:
1. Put it in `~/.claude/skills/skill-name/` (personal)
2. Or `.claude/skills/skill-name/` (project-specific)
3. Claude discovers and uses it automatically

## Resources

- [Getting Started Guide](../ai_docs/SKILLS_GETTING_STARTED.md)
- [Official Anthropic Skills Repo](https://github.com/anthropics/skills)
- [Claude Docs - Skills](https://docs.claude.com/en/docs/claude-code/skills)

---
Last Updated: 2025-10-17
