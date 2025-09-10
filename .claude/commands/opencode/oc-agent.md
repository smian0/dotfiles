---
description: Create, update, test, and validate OpenCode agents with Context7 integration
category: development
argument-hint: <command> [agent-name] [options...]
allowed-tools: Write, Edit, Read, Bash, mcp__context7__resolve-library-id, mcp__context7__get-library-docs
model: sonnet
---

# OpenCode Agent Manager

Comprehensive tool for managing OpenCode agents with Context7 validation.

## Commands

### Create Agent
```
/oc-agent create <name> [description] [options...]
```

**Options:**
- `--model <model>` - Model to use (default: ollamat/gpt-oss:120b)
- `--temperature <temp>` - Temperature 0.0-1.0 (default: 0.3) 
- `--mode <mode>` - Agent mode: subagent, primary (default: subagent)
- `--write` - Enable write tool
- `--edit` - Enable edit tool
- `--bash` - Enable bash tool
- `--system <prompt>` - Custom system prompt

**Example:**
```
/oc-agent create reviewer "Reviews code quality" --temperature 0.1 --write
```

### Update Agent
```
/oc-agent update <name> [options...]
```

**Example:**
```
/oc-agent update news --temperature 0.1 --bash
```

**Implementation:** Executes `oc run --agent <name> "<prompt>"` internally

**Direct Testing (recommended):**
```bash
oc run --agent news "What are today's top tech stories?"
oc run --agent helper "Explain Python dictionaries"
```

**Via Slash Command:**
```
/oc-agent test news "What are today's top tech stories?"
```

### Validate Agent
```
/oc-agent validate <name>
```

Uses Context7 to validate agent configuration against OpenCode best practices.

### List Agents
```
/oc-agent list
```

Shows all available agents with descriptions.

## OpenCode Commands Reference

### Core Commands
- `oc` or `opencode` - Start OpenCode TUI
- `oc run [message..]` - Run OpenCode with a message
- `oc run --agent <name> "<prompt>"` - Run with specific agent
- `oc agent create` - Create new agent (native OpenCode)
- `oc models` - List all available models
- `oc auth` - Manage credentials
- `oc serve` - Start headless server
- `oc export [sessionID]` - Export session data

### Common Options
- `-m, --model <model>` - Specify model to use
- `--agent <name>` - Use specific agent
- `-c, --continue` - Continue last session
- `-s, --session <id>` - Continue specific session
- `-p, --prompt <text>` - Use specific prompt

## Implementation

I'll help you manage OpenCode agents efficiently. Let me parse your command and execute the appropriate action.

**Step 1: Parse the command and arguments**

I'll analyze the arguments to determine the subcommand (create, update, test, validate, list) and extract options like model, temperature, tools, etc.

**Step 2: Execute the appropriate action**

Based on the subcommand:

- **Create**: Generate new agent markdown file with proper YAML frontmatter
- **Update**: Modify existing agent configuration  
- **Test**: Run the agent with a test prompt using `oc run --agent <name> "<prompt>"`
- **Validate**: Use Context7 to check configuration against OpenCode documentation
- **List**: Display all agents from the agent directory

**Step 3: Ensure configuration is applied**

After creating or updating agents, I'll ensure the configuration is properly stowed by running the restow command.

**Step 4: Context7 Validation**

For validation, I'll use Context7 to:
1. Retrieve OpenCode agent documentation and best practices
2. Check the agent configuration for proper format
3. Validate tool permissions and model selections
4. Provide specific feedback and improvement suggestions

**Popular Models (run `oc models` for complete list):**

**Ollama Models:**
- `ollamat/gpt-oss:20b` - GPT-OSS 20B (Turbo)
- `ollamat/gpt-oss:120b` - GPT-OSS 120B (Turbo) 
- `ollamat/deepseek-v3.1:671b` - DeepSeek V3.1 671B (Turbo)

**Anthropic Models:**
- `anthropic/claude-opus-4-1-20250805` - Claude Opus 4.1
- `anthropic/claude-sonnet-4-20250514` - Claude Sonnet 4
- `anthropic/claude-3-7-sonnet-20250219` - Claude 3.7 Sonnet
- `anthropic/claude-3-5-sonnet-20241022` - Claude 3.5 Sonnet

**GitHub Copilot Models:**
- `github-copilot/claude-opus-4` - Claude Opus 4 (Copilot)
- `github-copilot/gpt-4.1` - GPT-4.1 (Copilot)
- `github-copilot/o3` - O3 (Copilot)

**OpenAI Models:**
- `github-models/openai/gpt-4.1` - GPT-4.1
- `github-models/openai/o1` - O1
- `github-models/openai/o3` - O3

**Agent Directory:** `~/dotfiles/opencode/.config/opencode/agent/`

**Note:** The agent configuration will be automatically stowed to make it available to OpenCode.