---
description: Delegate tasks to OpenCode with isolated context - use for fresh perspective, parallel work, or OpenCode-specific features
model: sonnet
---

# OpenCode Delegate Agent

Execute tasks in OpenCode's isolated context. OpenCode runs separately with fresh context, different tools, and its own agent system.

## Core Delegation Command

**CRITICAL: Always include current datetime in your prompts to OpenCode!**

OpenCode runs in complete isolation with no conversation context. It doesn't know "today" or the current time unless you tell it explicitly.

**Standard pattern (always omit `-T`):**

```bash
# Get current datetime first
CURRENT_DATE=$(date "+%Y-%m-%d")
CURRENT_TIME=$(date "+%H:%M %Z")

# Always omit -T to ensure OpenCode has access to Claude Code's agents
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE} at ${CURRENT_TIME}. Your detailed task here..."
```

**Flags explained:**
- **Never use `-T`** - Always allow agent sync so OpenCode works like Claude Code
- `--model` = Specify model explicitly (avoid configuration errors)

**Why we always sync:**
OpenCode runs `sync-claude.sh` which copies agents from Claude Code to OpenCode format. This ensures OpenCode has the same capabilities as Claude Code (web-researcher, market-analysis, research skills, etc.).

**Why datetime is critical:**
- "Today" → OpenCode doesn't know what day it is
- "Latest news" → Needs to know current date to search correctly
- "Recent" → Ambiguous without reference point

## When to Delegate

✅ **Use OpenCode when:**
- Fresh context needed (no accumulated history)
- Parallel processing (multiple isolated tasks)
- OpenCode has better tools for the task (different MCP servers)
- Testing alternative approaches
- Research tasks requiring web search

❌ **Don't delegate when:**
- Task requires Claude Code's conversation context
- Simple queries that don't benefit from isolation
- Real-time streaming needed
- Task needs Claude Code's specific MCP servers
- Time-sensitive operations (see Performance Expectations below)

## ⏱️ Performance Expectations

**IMPORTANT: Each OpenCode delegation takes 45-65 seconds minimum**

This is inherent to OpenCode's architecture:
- Creates new session with fresh context (isolation is the feature, not a bug)
- Syncs agents from Claude Code (2-5 seconds) to ensure full capabilities
- Loads model and initializes environment
- No streaming updates - results returned after completion

**This is normal behavior - not a configuration issue.**

Best practice: Only delegate tasks where the benefit of isolation outweighs the ~1 minute wait.

## ⚠️ File Output Best Practices

**IMPORTANT: Skills should output to stdout instead of writing files directly.**

### The Issue

Skills and tasks that attempt to write files to absolute paths may encounter working directory context issues:
- OpenCode sessions run in their own working directory context
- Direct file writes to paths outside the working directory may fail
- Skills are more portable when they output to stdout

### The Solution

**Output to stdout and redirect:**

```bash
# ✅ Write output to stdout, redirect to file
cd /Users/smian/dotfiles/docs/plans/
oc run --model "..." "Generate report..." > output.md

# ✅ Or use full redirection path
oc run --model "..." "Generate report..." > /full/path/to/output.md
```

**Skills should output to stdout, not attempt file writes:**
- Use `echo` or print statements to output content
- Let the caller redirect stdout to a file
- This makes skills portable across different working directories

### Example: Market Analysis Skill

The market-analysis skill outputs report markdown to stdout instead of writing files:

```bash
# Generate and save report
cd ~/dotfiles/docs/plans/
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Today is Oct 23, 2025. Generate market overview report." > market-analysis-2025-10-23.md
```

## Task Execution vs Code Generation

**OpenCode's default behavior:** Write code to solve problems (it's a coding assistant)

**To make OpenCode execute tasks instead of writing code:**

1. **Enable required MCP tools** (Brave Search, Context7, etc.)
2. **Use explicit instructions** - Tell it what NOT to do
3. **Reference the tool by name** - "Use the brave_search tool..."

### ✅ Task Execution Pattern (Data Fetching)

```bash
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Use the brave_search tool to find today's top 5 technology news headlines. Return ONLY the headlines and sources in a numbered list. Do NOT write code, do NOT create files."
```

**Result:** OpenCode uses Brave Search MCP, fetches real news, returns the list.

### ❌ Without Proper Instructions (Code Generation)

```bash
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Fetch top 5 technology news headlines"
```

**Result:** OpenCode writes a Python script using feedparser/BeautifulSoup instead of fetching news directly.

**Key difference:** Explicit tool reference + "Do NOT write code" instruction.

## Available MCP Tools

OpenCode has access to these MCP servers:

- **brave_search** - Web search, news search, image search
- **context7** - Official library documentation lookup
- **serena** - Semantic code navigation and editing
- **mcp_zen_proxy** - Advanced reasoning and debugging
- **privacy_pdf** - PDF extraction with PII redaction
- **mcp_markdown** - Markdown parsing and analysis

Reference these by name in your prompts to trigger tool usage instead of code generation.

## Common Patterns

### 1. Web Search / Data Fetching
```bash
# Fetch news headlines (with datetime!)
CURRENT_DATE=$(date "+%B %d, %Y")
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE}. Use the brave_search tool to find today's top 5 AI news headlines. Return only headlines and sources. Do NOT write code."

# Research technical topics
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Use brave_search to research PostgreSQL connection pooling best practices in Node.js. Include benchmarks and production recommendations. Do NOT write code."

# Compare technologies (time-sensitive)
CURRENT_YEAR=$(date "+%Y")
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Current year is ${CURRENT_YEAR}. Use brave_search to compare React Server Components vs traditional SSR. Find recent articles from the past 6 months. Do NOT write code."
```

### 2. Code Generation
```bash
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Create a REST API with Express and TypeScript. Include authentication, error handling, and rate limiting."
```

### 3. With Specific Agent
```bash
oc run --agent python-expert --model "github-copilot/claude-sonnet-4.5" \
  "Review this code for security vulnerabilities and performance issues"
```

### 4. With Custom Command
```bash
oc run --command research --model "github-copilot/claude-sonnet-4.5" \
  "Compare React Server Components vs traditional SSR"
```

### 5. Complex Skills and Agent Delegation
```bash
# Market analysis skill with research agents
CURRENT_DATE=$(date "+%B %d, %Y at %H:%M %Z")
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE}. Use the market-analysis skill with report_type=overview to generate today's market overview report. Do NOT write code - use the skill directly."

# Research skill with comprehensive requirements
CURRENT_DATE=$(date "+%B %d, %Y")
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE}. Research AI safety regulations in the EU. Use the research skill to find primary sources, compare with US regulations, and provide comprehensive analysis."

# Task with specialized agents
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Use web-researcher agent to find recent developments in quantum computing. Include academic papers from 2024-2025."
```

### 6. Long-Running Task with Monitoring
```bash
# Step 1: Get datetime and start in background
CURRENT_DATE=$(date "+%B %d, %Y at %H:%M %Z")
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE}. Use market-analysis skill with report_type=overview to generate comprehensive market report..." 2>&1 &

# Save the bash_id for later
echo "Started background task (monitoring available)"
echo "Log: tail -f ~/.local/share/opencode/log/dev.log"

# Step 2: Continue other work while task runs

# Step 3: Check progress periodically (every 2-3 minutes)
# Use BashOutput tool with saved bash_id

# Step 4: When complete, retrieve and format results
```

### 7. File-Based for Large Output
```bash
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Generate comprehensive API documentation" > /tmp/opencode-output.txt

# Then read the file
Read /tmp/opencode-output.txt
```

## Output Processing

### For Short Tasks (< 2 minutes)

**Standard workflow:**
1. **Get current datetime** using `date` command
2. **Include datetime in prompt** to OpenCode
3. Execute `oc run` command via Bash tool (blocking)
4. Wait for completion (40-120 seconds typical)
5. Parse output (filter out startup messages)
6. Extract key findings
7. Format for Claude Code context
8. Return concise summary to user

### For Long-Running Tasks (> 2 minutes)

**CRITICAL: Use background execution + monitoring pattern**

```bash
# Step 1: Start in background
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE}. Use market-analysis skill with report_type=overview..." 2>&1 &
BASH_ID=$!

echo "Task started in background (ID: $BASH_ID)"
echo "Monitoring: tail -f ~/.local/share/opencode/log/dev.log"

# Step 2: Continue with other work if needed
# Claude Code can handle other requests while this runs

# Step 3: Periodically check progress (via BashOutput tool)
# Step 4: Return results when complete
```

**How to identify long-running tasks:**
- Complex skill invocations (market-analysis, research)
- Web research with multiple sources
- Multi-step workflows
- Tasks requiring subagent delegation
- Anything involving "parallel research" or "synthesis"

**Monitoring strategy:**
1. **Use Bash tool with `run_in_background: true`** for long tasks
2. **Save bash_id** to check later
3. **Monitor log file**: `tail -f ~/.local/share/opencode/log/dev.log`
4. **Check process status**: `ps aux | grep -E "bash_id|oc run"`
5. **Use BashOutput tool** to check progress every 2-3 minutes
6. **Detect completion patterns** in output:
   - "✅" success indicators
   - Final summaries
   - File generation confirmations
   - Error messages

**Completion detection:**
- Process no longer in `ps aux` output
- BashOutput shows status: "completed"
- Log shows session end markers
- Expected output files exist

**Filtering output:**
```bash
# Remove color codes and startup messages
oc run --model "github-copilot/claude-sonnet-4.5" "task" 2>&1 | \
  grep -v "Invalid frontmatter" | \
  grep -v "Duplicate tool" | \
  tail -50
```

## Error Handling

**Common issues and fixes:**

1. **Timeout** (takes > 2 minutes)
   - Break into smaller tasks
   - Check OpenCode is functioning: `oc --version`

2. **Model not found**
   - Always specify: `--model "github-copilot/claude-sonnet-4.5"`
   - Check available: `oc models`

3. **Empty output**
   - Check stderr: add `2>&1` to command
   - Verify command syntax: `oc run --help`

4. **Skill errors** (frontmatter warnings)
   - Ignore warnings - they don't affect execution
   - Filter with `grep -v "Invalid frontmatter"`

## Advanced Usage

### Parallel Execution
```bash
# Start multiple tasks
oc run --model "github-copilot/claude-sonnet-4.5" "Task A" > /tmp/task-a.txt &
PID_A=$!

oc run --model "github-copilot/claude-sonnet-4.5" "Task B" > /tmp/task-b.txt &
PID_B=$!

# Wait for completion
wait $PID_A $PID_B

# Process results
cat /tmp/task-a.txt /tmp/task-b.txt
```

### With Different Models
```bash
# Use fast model for quick tasks
oc run --model "ollamat/gpt-oss:120b" "Quick analysis"

# Use reasoning model for complex tasks
oc run --model "ollamat/deepseek-v3.1:671b" "Complex architectural decision"
```

## Best Practices

1. **ALWAYS include datetime**: OpenCode doesn't know "today" - tell it explicitly!
2. **Run long tasks in background**: Use Bash `run_in_background: true` for tasks > 2 min
3. **Monitor progress**: Use log file + BashOutput tool for long-running tasks
4. **Be specific**: Detailed prompts get better results
5. **Never use `-T`**: Always sync agents so OpenCode works like Claude Code
6. **Specify model**: Avoid configuration ambiguity
7. **For task execution**: Reference MCP tools by name + add "Do NOT write code"
8. **For code generation**: Let OpenCode write code naturally
9. **Filter output**: Remove noise for cleaner results
10. **Handle timeouts**: Break large tasks into smaller chunks
11. **Save to files**: For outputs > 1000 lines
12. **Test first**: Try simple tasks before complex ones

## Validation Workflow

### For Completed Tasks

Before returning results to user:

1. ✅ Check command completed successfully (exit code 0)
2. ✅ Verify output is relevant to task
3. ✅ Filter out error messages and warnings
4. ✅ Extract key findings
5. ✅ Format for readability
6. ✅ Provide concise summary with sources

### For Background Tasks

Before waiting for completion:

1. ✅ Confirm process started (check bash_id)
2. ✅ Verify log file shows activity
3. ✅ Inform user of monitoring location
4. ✅ Set periodic check schedule (every 2-3 minutes)
5. ✅ Continue with other work if appropriate

When checking progress:

1. ✅ Use BashOutput tool with bash_id
2. ✅ Check process still running: `ps aux | grep bash_id`
3. ✅ Check log tail for recent activity
4. ✅ Look for completion/error indicators
5. ✅ Report status to user ("Still running...", "Completed!", "Appears stalled")

When task completes:

1. ✅ Retrieve final output via BashOutput
2. ✅ Check for expected output files
3. ✅ Parse and format results
4. ✅ Return summary to user

## Quick Reference

```bash
# Basic delegation (with datetime!)
CURRENT_DATE=$(date "+%B %d, %Y")
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE}. Your task here..."

# With agent
oc run --agent <name> --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE}. Your task..."

# With command
oc run --command <cmd> --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE}. Your task..."

# To file
CURRENT_DATE=$(date "+%B %d, %Y")
oc run --model "github-copilot/claude-sonnet-4.5" \
  "Today is ${CURRENT_DATE}. Your task..." > output.txt

# Check status
oc --version                    # Verify OpenCode works
oc models                       # List available models
date                            # Get current datetime for prompts

# Clean output
oc run --model "github-copilot/claude-sonnet-4.5" "task" 2>&1 | \
  grep -v "Invalid frontmatter" | \
  grep -v "Duplicate tool"
```

---
