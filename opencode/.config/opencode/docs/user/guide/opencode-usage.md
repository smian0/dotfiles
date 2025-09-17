# OpenCode Integration with CCPM

This directory contains opencode configuration that extends Claude Code Project Management (CCPM) with local model support and **automatic agent transformation**. The system integrates opencode as an interface layer for AI-powered development workflows using local models like gpt-oss:120b.

## Agent & Command Transformation System

This configuration includes automatic transformation of Claude Code agents and commands to OpenCode format:

- **Agent Transformation**: Claude agents from `~/dotfiles/claude/.claude/agents/` automatically work in OpenCode
- **Command Transformation**: Claude commands automatically converted to OpenCode format
- **Universal Command Support**: Both `oc` and `opencode` commands supported
- **Triple-Mechanism System**: Pre-launch + runtime + shell function for maximum reliability

For complete details see: **[AGENT-TRANSFORMATION-ARCHITECTURE.md](AGENT-TRANSFORMATION-ARCHITECTURE.md)**

## Directory Structure

**Note**: OpenCode itself is flexible about directory structure. The structure below is specific to this CCPM (Claude Code Project Management) integration and is not required by standard OpenCode.

### Standard OpenCode Structure
OpenCode supports this structure:
```
project/
├── opencode.json            # Main configuration file (optional)
├── .opencode/               # Project-specific OpenCode directory (optional)
│   └── command/             # Project-specific commands (optional)
│       └── *.md             # Command files (filename = command name)
├── prompts/                 # Custom prompt files (optional)
└── [your files]             # Project files
```

**Global commands location:**
```
~/.config/opencode/
└── command/                 # Global commands directory
    └── *.md                 # Global command files
```

**Command locations:**
- **Inline**: Commands defined inside `opencode.json` 
- **Global**: Markdown files in `~/.config/opencode/command/` (can include subfolders)
- **Project**: Markdown files in `.opencode/command/` (can include subfolders)

**Command directory structure:**
- **Flat structure**: Commands directly in command folder (e.g., `test.md` → `/test`)
- **Subfolder support**: Commands organized in subfolders (e.g., `pm/help.md` → `/pm/help`)
- **Nested organization**: Group related commands by functional area

**Command file naming:**
- Filename becomes the command name (e.g., `test.md` → `/test` command)
- Subfolder path included in command name (e.g., `pm/help.md` → `/pm/help` command)
- Use `.md` extension for markdown command files

### Example Directory Structure
A typical OpenCode project structure:

```
.opencode/
├── opencode.json              # Main configuration file
├── agents/                    # Optional agent definitions
│   ├── reviewer.md            # Code review agent
│   └── assistant.md           # General purpose agent
├── command/                   # Commands directory
│   ├── test.md                # Simple command: /test
│   ├── build.md               # Simple command: /build
│   └── deploy/                # Namespaced commands
│       ├── staging.md         # Command: /deploy:staging
│       └── production.md      # Command: /deploy:production
├── modes/                     # Optional mode definitions
│   ├── development.md         # Development mode
│   └── production.md          # Production mode
├── rules/                     # Optional behavior rules
│   ├── code-style.md          # Coding standards
│   └── patterns.md            # Common patterns
└── README.md                  # Project documentation
```

### Key Components

- **opencode.json** - Main configuration with models, providers, and global settings
- **agents/** - Optional specialized agents for task automation (auto-transformed from Claude)
- **command/** - Command implementations as markdown files (auto-transformed from Claude)
- **modes/** - Optional mode definitions for different workflows
- **rules/** - Optional behavioral guidelines and patterns
- **README.md** - Project documentation

### Transformation Components

- **scripts/pre-launch-transform.js** - Pre-launch agent transformation
- **plugin/agent-transformer.js** - Runtime agent transformation plugin
- **plugin/command-transformer.js** - Runtime command transformation plugin
- **~/.local/bin/opencode** - Universal binary wrapper for shell function support

### OpenCode Flexibility

**Commands can be located:**
1. **Inline in opencode.json** - All commands defined in JSON configuration
2. **Global directory** - Markdown files in `~/.config/opencode/command/`
3. **Project directory** - Markdown files in `.opencode/command/`

**Agents can be located:**
1. **Inline in opencode.json** - All agents defined in JSON configuration  
2. **Separate markdown files** - Individual files anywhere in the project
3. **Mixed approach** - Some inline, some as files

**Important**: 
- **Commands** support both flat structure (`.opencode/command/`) and nested subdirectories (`.opencode/commands/pm/`)
- **Agents** can be defined in JSON (`opencode.json`) or as markdown files anywhere in the project
- **Flexibility**: OpenCode supports multiple organizational patterns - use what works best for your project

## Model Configuration

### Available Models (Confirmed on Ollama.com)
- **gpt-oss:120b** - Primary model for all agents and commands (High Quality)
- **gpt-oss:20b** - Alternative lighter model (Fast)
- **deepseek-v3.1:671b** - Advanced reasoning model (Very Large)

### Additional Models (Configuration Ready)
- **qwen3-coder:480b** - Qwen3 Coder 480B (Coding Focus)*

*Check `oc models` or `opencode models` for current availability.

### Model Providers
- **Local (ollama)**: `http://localhost:3304/v1` - For local inference
- **Remote (ollamat)**: `https://ollama.com/api` - For cloud inference (requires OLLAMA_API_KEY)
- **ZhipuAI**: Default model `zhipuai/glm-4.5` for transformed agents

## Command Usage

### Basic Commands (Universal Support)
```bash
# Start opencode TUI in this directory (either command works)
oc
opencode

# Run with direct message
oc run "message"
opencode run "message"

# Use specific agent (automatic transformation)
oc --agent claude-test-agent "analyze this file"
opencode --agent claude-test-agent "analyze this file"

# Continue previous session
oc --continue
opencode --continue
```

### Model Selection
```bash
# Use specific model (both commands work identically)
oc -m ollamat/gpt-oss:120b "message"
opencode -m ollamat/gpt-oss:120b "message"

# Use local model
oc -m ollama/gpt-oss:120b "message"
opencode -m ollama/gpt-oss:120b "message"
```

## Documentation Reference

### OpenCode Documentation
When encountering discrepancies with opencode behavior or when unable to determine proper opencode usage patterns:

1. **Consult Context7** for the latest opencode documentation:
   - Use `mcp__context7__resolve-library-id` with "opencode" to get the library ID
   - Use `mcp__context7__get-library-docs` to fetch current documentation
   - Context7 provides up-to-date docs that may be more current than built-in knowledge

2. **Common scenarios requiring documentation lookup**:
   - Agent configuration issues
   - Model provider setup problems  
   - Command syntax discrepancies
   - New features or updated APIs
   - Configuration schema changes

3. **Fallback resources**:
   - Check `opencode.json` schema and configuration examples
   - Review agent definitions in `.opencode/agents/`
   - Examine command patterns in `.opencode/commands/`

## Agent Architecture

### Agent Frontmatter Schema

**Note**: If using automatic transformation, Claude agents are automatically converted to OpenCode format. For manual agent creation in `.opencode/agents/`, use this frontmatter schema:

```yaml
---
description: "Brief description starting with 'Use this agent when...'"
mode: subagent
model: ollamat/gpt-oss:120b
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
  read: true
  grep: true
  glob: true
  websearch: true
permission:
  edit: deny
  bash: ask
  webfetch: allow
---
```

**Required Fields:**
- `description` - Clear explanation of when to use this agent
- `mode` - Use `"subagent"` for specialized agents, `"primary"` for main agents
- `model` - Specify model (e.g., `"ollamat/gpt-oss:120b"`)

**Optional Fields:**
- `temperature` - Creativity level (0.1 = focused, 0.8 = creative)
- `tools` - Object with boolean values for tool availability
- `permission` - Override global permissions for this agent
- `prompt` - Custom system prompt file: `"{file:./prompts/agent-name.txt}"`
- `reasoningEffort` - `"low"`, `"medium"`, `"high"` for reasoning depth
- `textVerbosity` - `"low"`, `"medium"`, `"high"` for output detail
- `disable` - Set to `true` to disable the agent

**Tool Options:**
- `write`, `edit`, `bash`, `read`, `grep`, `glob`, `websearch`
- Each tool: `true` (allow), `false` (deny)

**Permission Options:**
- `edit`, `bash`, `webfetch`
- Each permission: `"allow"`, `"ask"`, `"deny"`

**Note:** Agent name is determined by filename (e.g., `code-analyzer.md` → `code-analyzer` agent)

### Command Frontmatter Schema

**Note**: If using automatic transformation, Claude commands are automatically converted to OpenCode format. For manual command creation in `.opencode/command/`, use this frontmatter schema:

```yaml
---
description: "Brief description of what this command does"
agent: build
model: ollamat/gpt-oss:120b
temperature: 0.3
---

The command prompt/template goes here as the main content.
This text will be sent to the LLM when the command is executed.

Use clear, specific instructions for what you want the agent to do.
```

**Available Fields:**
- `description` - Short description shown in TUI and help
- `agent` - Which agent to use (defaults to `"build"` if not specified)
- `model` - Override model for this command (optional)
- `temperature` - Creativity level for this command (optional)

**Command Types:**
- **Markdown files** - Content serves as the prompt template
- **JSON config** - Use `template` field for the prompt

**Examples:**

**Simple command:**
```yaml
---
description: Run tests with coverage
---

Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

**Advanced command:**
```yaml
---
description: Security audit with detailed analysis
agent: code-analyzer
model: ollamat/gpt-oss:120b
temperature: 0.1
---

Perform a comprehensive security audit of the codebase.
Focus on potential vulnerabilities and provide specific recommendations.
```

**Command in JSON config:**
```json
{
  "command": {
    "test": {
      "template": "Run tests and analyze failures",
      "description": "Execute test suite",
      "agent": "build",
      "model": "ollamat/gpt-oss:120b"
    }
  }
}
```

**Note:** Command name is determined by filename (e.g., `security-audit.md` → `/security-audit` command)

## Commands Reference

*Based on https://opencode.ai/docs/commands*

### Command Creation Methods

**1. Markdown Files**
Place `.md` files in:
- Global: `~/.config/opencode/command/` (supports subfolders: `pm/help.md` → `/pm/help`)
- Project: `.opencode/command/` (supports subfolders: `testing/run.md` → `/testing/run`)

**2. JSON Configuration**
Define inline in `opencode.json`:
```json
{
  "command": {
    "command-name": {
      "template": "Your prompt here",
      "description": "Brief description",
      "agent": "agent-name",
      "model": "model-name"
    }
  }
}
```

### Command Configuration Options

**Required:**
- `template` - The prompt sent to the LLM

**Optional:**
- `description` - Brief explanation shown in TUI
- `agent` - Which agent executes the command (defaults to "build")
- `model` - Override default model for this command

### Dynamic Features

**Arguments Placeholder (`$ARGUMENTS`)**
```markdown
---
description: Create a new component
---
Create a new React component named $ARGUMENTS with TypeScript support.
```
Usage: `/component Button` → Creates component named "Button"

**Shell Command Injection (`!command`)**
```markdown
---
description: Analyze test results
---
Here are the current test results:
!`npm test`

Based on these results, suggest improvements.
```

**File Content Injection (`@filename`)**
```markdown
---
description: Review component
---
Review the component in @src/components/Button.tsx.
Check for performance issues and suggest improvements.
```

### Command Examples

**Simple Command:**
```markdown
---
description: Run tests with coverage
---
Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

**Dynamic Component Creation:**
```markdown
---
description: Create a new component
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---
Create a new React component named $ARGUMENTS with TypeScript support.
Include proper typing and basic structure.
```

**Code Review with File Reference:**
```markdown
---
description: Review specific file
---
Review the code in @$ARGUMENTS for:
- Performance issues
- Security vulnerabilities
- Best practices compliance
```

**Test Analysis with Shell Output:**
```markdown
---
description: Analyze test coverage
---
Here are the current test results:
!`npm test -- --coverage`

Based on these results:
1. Identify areas with low coverage
2. Suggest additional test cases
3. Recommend testing strategies
```

### Best Practices

**Command Naming:**
- Use descriptive filenames (filename becomes command name)
- Use kebab-case for multi-word commands (`code-review.md`)
- Organize with subfolders for logical grouping

**Subfolder Organization Examples:**
```
.opencode/command/
├── pm/                    # Project management commands
│   ├── help.md           # → /pm/help
│   ├── status.md         # → /pm/status
│   └── init.md           # → /pm/init
├── testing/              # Testing workflow commands
│   ├── run.md            # → /testing/run
│   └── coverage.md       # → /testing/coverage
└── utils/                # Utility commands
    ├── format.md         # → /utils/format
    └── lint.md           # → /utils/lint
```

**Template Design:**
- Be specific about desired output format
- Include context about project conventions
- Use placeholders for reusable commands

**Dynamic Content:**
- Combine `$ARGUMENTS` with file injection for flexible workflows
- Use shell injection for current state analysis
- Chain multiple dynamic features in single commands

### Command Execution

**Basic Usage:**
```bash
/command-name
```

**With Arguments:**
```bash
/component Button
/review src/utils/helper.js
```

**In TUI:**
Commands appear in the command palette and can be executed by typing `/` followed by the command name.

### Mode Frontmatter Schema

When creating or modifying mode files in `.opencode/modes/`, use this frontmatter schema:

```yaml
---
model: ollamat/gpt-oss:120b
temperature: 0.2
tools:
  write: true
  edit: true
  bash: false
  read: true
  grep: true
  glob: true
permission:
  edit: allow
  bash: ask
  webfetch: deny
---

You are in [mode name] mode. Focus on:

- Specific instructions for this mode
- Clear guidelines and constraints
- Expected behavior and outputs
```

**Mode Fields:**
- `model` - Override default model for this mode
- `temperature` - Creativity level (0.1 = focused, 0.8 = creative)
- `tools` - Tool availability (same format as agents)
- `permission` - Permission overrides (edit, bash, webfetch)

**Mode Examples:**
- **readonly** - `write: false, edit: false, bash: false`
- **debug** - `write: false, edit: false` but `bash: true, read: true, grep: true`
- **docs** - `write: true, edit: true, bash: false` for documentation tasks

### Provider Configuration Schema

Configure custom AI providers in `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "custom-provider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Custom Provider Display Name",
      "options": {
        "baseURL": "https://api.custom.com/v1",
        "apiKey": "{env:CUSTOM_API_KEY}",
        "headers": {
          "Authorization": "Bearer token"
        }
      },
      "models": {
        "custom-model": {
          "name": "Custom Model Display Name",
          "options": {
            "reasoningEffort": "high",
            "textVerbosity": "low"
          }
        }
      }
    }
  }
}
```

**Provider Fields:**
- `npm` - NPM package for provider integration
- `name` - Display name in UI
- `options.baseURL` - API endpoint URL
- `options.apiKey` - API key (use `{env:VAR_NAME}` for environment variables)
- `options.headers` - Custom headers
- `models` - Available models and their configurations

### MCP Server Configuration Schema

Configure MCP servers in `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "local-server": {
      "type": "local",
      "command": ["uv", "run", "server.py"],
      "enabled": true,
      "environment": {
        "ENV_VAR": "value"
      }
    },
    "remote-server": {
      "type": "remote", 
      "url": "https://api.example.com/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:API_KEY}"
      }
    }
  },
  "tools": {
    "mcp-server*": true,
    "other-mcp*": false
  }
}
```

**MCP Server Types:**
- **Local**: `type: "local"` with `command` array
- **Remote**: `type: "remote"` with `url` and optional `headers`

**MCP Fields:**
- `enabled` - Enable/disable the server
- `environment` - Environment variables (local only)
- `headers` - Custom headers (remote only)
- `tools` - Global tool patterns (use `*` wildcards)

### Permission Configuration Schema

Configure permissions globally or per-agent:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "ask",
    "bash": {
      "*": "allow",
      "git push": "ask", 
      "terraform *": "deny"
    },
    "webfetch": "allow"
  }
}
```

**Permission Levels:**
- `"allow"` - Permit without asking
- `"ask"` - Prompt user for approval
- `"deny"` - Block completely

**Permission Types:**
- `edit` - File modification permissions
- `bash` - Shell command permissions (supports patterns)
- `webfetch` - Web request permissions

**Pattern Matching for Bash:**
- `"*"` - All commands
- `"git *"` - All git commands
- `"git push"` - Specific command

### Formatter Configuration Schema

Configure code formatters in `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": {
    "prettier": {
      "disabled": true
    },
    "custom-formatter": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "environment": {
        "NODE_ENV": "development"
      },
      "extensions": [".js", ".ts", ".jsx", ".tsx"]
    }
  }
}
```

**Formatter Fields:**
- `disabled` - Set to `true` to disable built-in formatters
- `command` - Command array (use `$FILE` placeholder)
- `environment` - Environment variables for formatter
- `extensions` - File extensions to format

### Global Configuration Schema

Main `opencode.json` structure:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollamat/gpt-oss:120b",
  "small_model": "ollamat/gpt-oss:20b",
  "theme": "opencode",
  "share": "manual",
  "autoupdate": true,
  "provider": {},
  "agent": {},
  "mode": {},
  "command": {},
  "mcp": {},
  "tools": {},
  "permission": {},
  "formatter": {},
  "keybinds": {}
}
```

**Top-Level Fields:**
- `model` - Default model for all agents/modes
- `small_model` - Lightweight model for simple tasks
- `theme` - UI theme
- `share` - Session sharing mode (`"auto"`, `"manual"`)
- `autoupdate` - Automatic updates (`true`/`false`)

### Specialized Agents

**code-analyzer** - Deep code analysis and bug hunting
- Traces logic flow across multiple files
- Identifies potential regressions and vulnerabilities
- Maintains context efficiency while providing thorough analysis

**file-analyzer** - File content summarization
- Processes verbose files (logs, configs, documentation)
- Extracts key insights while reducing context usage
- Ideal for understanding large documentation or output files

**test-runner** - Test execution and analysis
- Runs tests and captures comprehensive logs
- Analyzes failures and provides actionable insights
- Preserves main conversation context by containing verbose output

**parallel-worker** - Coordinated parallel execution
- Manages multiple concurrent work streams
- Consolidates results from parallel agents
- Optimizes for git worktree-based parallel development

### Agent Design Principles
- **Context Preservation**: Agents shield main thread from verbose output
- **Concise Returns**: Only essential information returns to conversation
- **Specialization**: Each agent has a single, well-defined purpose
- **Error Handling**: Graceful failure with specific guidance

## Command Structure

### Command Implementation

OpenCode commands are implemented as markdown files in the `command/` directory. Commands can be organized in subdirectories for namespacing (e.g., `command/pm/help.md` creates `/pm:help`).

For project-specific command documentation, see `CLAUDE.md`.

## Rules and Patterns

### Standard Command Patterns
1. **Fail Fast** - Check critical prerequisites first
2. **Trust the System** - Don't over-validate reliable components
3. **Clear Errors** - Provide exact error messages with fix instructions
4. **Minimal Output** - Show essential information only

### Validation Approach
- Minimal preflight checks for required files/directories
- Trust git, npm, and other standard tools to work correctly
- When validation fails, provide specific commands to fix issues

## MCP Server Integration

### Enabled MCP Servers
- **markdown** - Local MCP server for markdown processing
- **streamable-mcp-server** - Remote server (disabled by default)

### MCP Tools
- `mcp__markdown__*` - Markdown processing tools available to agents

## Development Workflow

### Starting Work
1. Use `oc` to start opencode TUI
2. Load project context with `/context:prime`
3. Initialize PM system with `/pm:init` if needed

### Code Analysis
- Use `code-analyzer` agent for deep code review
- Use `file-analyzer` for documentation/log analysis
- All agents maintain conversation context efficiency

### Testing
- Use `test-runner` agent for comprehensive test execution
- Testing commands automatically capture and analyze results

### Project Management
- Use PM commands for GitHub Issues integration
- Commands support git worktree-based parallel development
- Full traceability from requirements to implementation

## Architecture Philosophy

This system implements a **layered architecture**:
1. **OpenCode Layer** - Interface and model management
2. **CCPM Layer** - Project management and workflow orchestration  
3. **Agent Layer** - Specialized task execution with context optimization
4. **Tool Layer** - MCP servers and external integrations

The design prioritizes **context preservation** and **parallel execution** while maintaining full integration with GitHub Issues and git workflows.