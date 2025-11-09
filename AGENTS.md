# AI Agent Instructions

<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available
skills below can help complete the task more effectively.

How to use skills:
- Invoke: Bash("openskills read <skill-name>")
- The skill content will load with detailed instructions
- Base directory provided in output for resolving bundled resources

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
</usage>

<available_skills>

<skill>
<name>research</name>
<description>Comprehensive multi-source research with strict grounding (100% citation requirement). NO DATA > BAD DATA.</description>
<location>project</location>
</skill>

<skill>
<name>skill-creator</name>
<description>Guide for creating effective skills with intelligent architecture assessment. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities. Automatically determines whether to create a simple skill, a skill with subagent delegation, or a complete multi-agent system based on complexity analysis.</description>
<location>project</location>
</skill>

<skill>
<name>mcp-builder</name>
<description>Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).</description>
<location>project</location>
</skill>

<skill>
<name>fastmcp-builder</name>
<description>Guide for creating high-quality MCP (Model Context Protocol) servers using FastMCP v2 and uv single-file scripts. Use when building MCP servers to integrate external APIs or services with Python. This skill exclusively uses FastMCP v2 framework and uv for dependency management.</description>
<location>project</location>
</skill>

<skill>
<name>pdf-analysis</name>
<description>Analyze PDFs with automatic PII redaction. Use when user provides PDF path(s) and analysis question. Supports single PDF or batch processing with parallel execution.</description>
<location>project</location>
</skill>

<skill>
<name>mcp-manager</name>
<description>Comprehensive MCP server configuration management with smart workflow routing for user and project levels. Use when adding, removing, syncing, validating, or wrapping MCP servers.</description>
<location>project</location>
</skill>

<skill>
<name>tech-stack-advisor</name>
<description>Advises on technology stack choices through comparative analysis. Use when comparing frameworks, libraries, or technical approaches.</description>
<location>project</location>
</skill>

<skill>
<name>cursor-openskills-setup</name>
<description>Set up OpenSkills for Cursor IDE with proper configuration, global user rules, and verification. Use when setting up a new machine or project with Cursor + OpenSkills integration.</description>
<location>project</location>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>

## Dotfiles Project Context

This dotfiles repository uses OpenSkills for cross-IDE skill compatibility (Claude Code + Cursor).

### Using Skills

**In Claude Code:** Use the `Skill` tool to invoke skills automatically.

**In Cursor/Other IDEs:** Invoke via Bash command:
```bash
openskills read <skill-name>
```

**List available skills:**
```bash
openskills list
```

### Skills Location

Skills are stored at `~/.claude/skills/` (global) and automatically discovered by OpenSkills.

For more information, see the [OpenSkills documentation](https://github.com/numman-ali/openskills).
