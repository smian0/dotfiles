# Claude Project Settings

Project-level Claude Code configuration template that can be deployed to any project directory using GNU Stow.

## Installation

```bash
# From the dotfiles directory, deploy to a specific project
stow -d /path/to/dotfiles -t /path/to/your/project claude-project

# Or using the deployment script
./scripts/deploy-claude-project.sh /path/to/your/project
```

## What This Provides

1. **Project-specific Claude Code settings** (`.claude/settings.json`)
   - Project environment variables
   - Project-specific permissions
   - Tool allowlists for the project

2. **Memory Bank System** (`CLAUDE.md`)
   - Structured context files for maintaining project state
   - Architecture decisions and patterns documentation
   - Troubleshooting knowledge base

3. **Project-specific agents and commands**
   - Code searcher agent for navigating your codebase
   - Memory bank synchronizer
   - Project-specific slash commands

## After Installation

1. Customize `CLAUDE.md` with your project-specific guidance
2. Modify `.claude/settings.json` for your project's needs
3. Create `.claude/settings.local.json` for personal project preferences (not committed to git)
4. Run `/init` in Claude Code to initialize the memory bank system

## MCP Servers (Optional)

You may also want to install these MCP servers:

* [Gemini CLI MCP](https://github.com/upstash/gemini-cli-mcp-server)
* [Cloudflare Documentation MCP](https://github.com/cloudflare/mcp-server-cloudflare/tree/main/apps/docs-vectorize)
* [Context 7 MCP](https://github.com/upstash/context7)
* [Notion MCP](https://github.com/makenotion/notion-mcp-server)

## Claude Code Subagents

Claude Code subagents are specialized tools designed to handle complex, multi-step tasks autonomously.

### memory-bank-synchronizer

- **Purpose**: Synchronizes memory bank documentation with actual codebase state
- **Location**: `.claude/agents/memory-bank-synchronizer.md`
- **Key Responsibilities**: Pattern documentation synchronization, architecture decision updates, technical specification alignment

### code-searcher

- **Purpose**: Efficient codebase navigation and search with Chain of Draft (CoD) ultra-concise mode
- **Location**: `.claude/agents/code-searcher.md`
- **Key Responsibilities**: Codebase navigation, function location, pattern identification, CoD mode for 80% token reduction

### get-current-datetime

- **Purpose**: DateTime utility for accurate Brisbane, Australia (GMT+10) timezone values
- **Location**: `.claude/agents/get-current-datetime.md`
- **Key Responsibilities**: Execute timezone-specific date commands, support multiple format options

### ux-design-expert

- **Purpose**: Comprehensive UX/UI design guidance with Tailwind CSS and Highcharts
- **Location**: `.claude/agents/ux-design-expert.md`
- **Key Responsibilities**: UX flow optimization, premium UI design, scalable design systems, data visualization

## Claude Code Slash Commands

### `/anthropic` Commands

- **`/apply-thinking-to`** - Expert prompt engineering with extended thinking patterns
- **`/convert-to-todowrite-tasklist-prompt`** - Convert complex prompts to efficient task delegation
- **`/update-memory-bank`** - Update CLAUDE.md and memory bank files

### `/ccusage` Commands

- **`/ccusage-daily`** - Generate comprehensive Claude Code usage cost analysis

### `/cleanup` Commands

- **`/cleanup-context`** - Memory bank optimization for 15-25% token reduction

### `/documentation` Commands

- **`/create-readme-section`** - Generate professional README sections

### `/security` Commands

- **`/security-audit`** - Comprehensive security audit using OWASP guidelines
- **`/check-best-practices`** - Language-specific best practices analysis
- **`/secure-prompts`** - Enterprise-grade security analyzer for prompt injection detection

### `/architecture` Commands

- **`/explain-architecture-pattern`** - Identify and explain architectural patterns

### `/promptengineering` Commands

- **`/convert-to-test-driven-prompt`** - Transform requests into TDD style prompts
- **`/batch-operations-prompt`** - Optimize prompts for multiple file operations

### `/refactor` Commands

- **`/refactor-code`** - Analysis-only refactoring with comprehensive plans

## Claude Code Plan Weekly Rate Limits

If you are using Claude monthly subscription plans for Claude Code, new weekly rate limits will apply from August 28, 2025 in addition to max 50x 5hr session limits per month:

| Plan               | Sonnet 4 (hrs/week) | Opus 4 (hrs/week) |
|--------------------|---------------------|-------------------|
| Pro                | 40–80               | –                 |
| Max ($100 /mo)     | 140–280             | 15–35             |
| Max ($200 /mo)     | 240–480             | 24–40             |

## Claude Code Settings

Configure Claude Code with global and project-level settings through `settings.json` files.

### Settings files

- **User settings**: `~/.claude/settings.json` (applies to all projects)
- **Project settings**: `.claude/settings.json` (shared) and `.claude/settings.local.json` (personal)

### Available settings

| Key                   | Description                                                                                | Example                         |
| :-------------------- | :----------------------------------------------------------------------------------------- | :------------------------------ |
| `apiKeyHelper`        | Custom script to generate auth values                                                      | `/bin/generate_temp_api_key.sh` |
| `cleanupPeriodDays`   | Local chat transcript retention (default: 30 days)                                         | `20`                            |
| `env`                 | Environment variables applied to every session                                             | `{"FOO": "bar"}`                |
| `includeCoAuthoredBy` | Include `co-authored-by Claude` byline in git operations (default: `true`)                 | `false`                         |
| `permissions`         | Tool permission rules and working directories                                               |                                 |

### Tools available to Claude

| Tool             | Description                                          | Permission Required |
| :--------------- | :--------------------------------------------------- | :------------------ |
| **Agent**        | Runs a sub-agent to handle complex, multi-step tasks | No                  |
| **Bash**         | Executes shell commands in your environment          | Yes                 |
| **Edit**         | Makes targeted edits to specific files               | Yes                 |
| **Glob**         | Finds files based on pattern matching                | No                  |
| **Grep**         | Searches for patterns in file contents               | No                  |
| **LS**           | Lists files and directories                          | No                  |
| **MultiEdit**    | Performs multiple edits on a single file atomically  | Yes                 |
| **NotebookEdit** | Modifies Jupyter notebook cells                      | Yes                 |
| **NotebookRead** | Reads and displays Jupyter notebook contents         | No                  |
| **Read**         | Reads the contents of files                          | No                  |
| **TodoRead**     | Reads the current session's task list                | No                  |
| **TodoWrite**    | Creates and manages structured task lists            | No                  |
| **WebFetch**     | Fetches content from a specified URL                 | Yes                 |
| **WebSearch**    | Performs web searches with domain filtering          | Yes                 |
| **Write**        | Creates or overwrites files                          | Yes                 |

## Claude Code MCP Servers

### Gemini CLI MCP Server

[Gemini CLI MCP](https://github.com/upstash/gemini-cli-mcp-server)

```bash
claude mcp add gemini-cli /pato/to/.venv/bin/python /pato/to//mcp_server.py -s user -e GEMINI_API_KEY='GEMINI_API_KEY' -e OPENROUTER_API_KEY='OPENROUTER_API_KEY'
```

### Cloudflare MCP Documentation

[Cloudflare Documentation MCP](https://github.com/cloudflare/mcp-server-cloudflare/tree/main/apps/docs-vectorize)

```bash
claude mcp add --transport sse cf-docs https://docs.mcp.cloudflare.com/sse -s user
```

### Context 7 MCP Server

[Context 7 MCP](https://github.com/upstash/context7)

```bash
claude mcp add --transport sse context7 https://mcp.context7.com/sse -s user
```

### Notion MCP Server

[Notion MCP](https://github.com/makenotion/notion-mcp-server)

```bash
claude mcp add-json notionApi '{"type":"stdio","command":"npx","args":["-y","@notionhq/notion-mcp-server"],"env":{"OPENAPI_MCP_HEADERS":"{\"Authorization\": \"Bearer ntn_API_KEY\", \"Notion-Version\": \"2022-06-28\"}"}}' -s user
```