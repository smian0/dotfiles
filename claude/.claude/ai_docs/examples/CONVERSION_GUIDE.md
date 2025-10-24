# Converting Claude Code Tasks to Agent SDK Scripts

This guide shows how to convert interactive Claude Code tasks into Agent SDK scripts that can be automated.

## Why Convert?

| Interactive Claude Code | Agent SDK Script |
|------------------------|------------------|
| One-time manual task | Repeatable automation |
| Human oversight required | Runs autonomously |
| Direct conversation | Batch processing |
| Exploratory | Production-ready |

## Conversion Process

### Step 1: Identify the Task Pattern

**Example interactive session:**
```
You: Analyze all Python files and create a summary report
Claude Code: [Uses Read, Glob, analyzes files, creates report]
```

### Step 2: Extract the Core Task

**Task components:**
- **Input**: Directory to analyze
- **Tools needed**: Read, Glob
- **Output**: Summary report
- **Permissions**: Auto-approve reads

### Step 3: Create Agent SDK Script

#### Before (Interactive)
```bash
$ claude

You: Please analyze all Python files in this directory and
     create a summary report with:
     - Total files
     - Lines of code
     - Common patterns
     - Suggestions

Claude: [Performs analysis using tools...]
```

#### After (Agent SDK)
```python
#!/usr/bin/env python3
"""Python Code Analyzer Agent"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        cwd=".",
        permission_mode='auto'
    )

    task = """
    Analyze all Python files in this directory and create a summary:
    - Total files
    - Lines of code
    - Common patterns
    - Suggestions for improvement
    """

    async for message in query(task, options):
        print(message)

asyncio.run(main())
```

## Real Examples

### Example 1: TODO Finder

#### Interactive Version
```
You: Find all TODO comments in the codebase
Claude: [Uses Grep to search files]
```

#### Agent SDK Version
```python
#!/usr/bin/env python3
"""TODO Finder Agent"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

async def find_todos(directory: str = "."):
    options = ClaudeAgentOptions(
        allowed_tools=["Grep", "Read"],
        cwd=directory,
        permission_mode='auto'
    )

    task = """
    Find all TODO comments in the codebase:
    1. Search for TODO, FIXME, HACK patterns
    2. List each with file and line number
    3. Categorize by priority or type
    4. Create a summary report
    """

    print(f"Searching for TODOs in {directory}...")

    async for message in query(task, options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

if __name__ == "__main__":
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    asyncio.run(find_todos(directory))
```

### Example 2: Test Runner with Analysis

#### Interactive Version
```
You: Run the tests and analyze any failures
Claude: [Uses Bash to run tests, analyzes output]
```

#### Agent SDK Version
```python
#!/usr/bin/env python3
"""Test Analysis Agent"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_and_analyze_tests(test_command: str = "pytest"):
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write"],
        cwd=".",
        permission_mode='acceptEdits'
    )

    task = f"""
    Run the test suite and analyze results:
    1. Execute: {test_command}
    2. If tests fail:
       - Identify failing tests
       - Analyze error messages
       - Suggest fixes
    3. Create a summary report
    4. Save report to test_analysis.md
    """

    print(f"Running tests with: {test_command}")

    async for message in query(task, options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

if __name__ == "__main__":
    import sys
    command = sys.argv[1] if len(sys.argv) > 1 else "pytest"
    asyncio.run(run_and_analyze_tests(command))
```

### Example 3: Code Review Agent

#### Interactive Version
```
You: Review the changes in main.py and suggest improvements
Claude: [Reads file, analyzes code, provides feedback]
```

#### Agent SDK Version with Custom Tool
```python
#!/usr/bin/env python3
"""Code Review Agent with Custom Scoring Tool"""
import asyncio
from typing import Any
from claude_agent_sdk import query, ClaudeAgentOptions, tool, AssistantMessage, TextBlock

@tool("code_quality_score", "Calculate code quality score", {
    "complexity": int,
    "documentation": int,
    "test_coverage": int
})
async def code_quality_score(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate weighted code quality score."""
    score = (
        args["complexity"] * 0.3 +
        args["documentation"] * 0.3 +
        args["test_coverage"] * 0.4
    )

    return {
        "content": [{
            "type": "text",
            "text": f"Quality Score: {score:.1f}/10"
        }]
    }

async def review_code(file_path: str):
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "code_quality_score"],
        custom_tools=[code_quality_score],
        cwd="."
    )

    task = f"""
    Review {file_path} and provide:
    1. Code structure analysis
    2. Potential bugs or issues
    3. Style and best practices
    4. Calculate quality score using code_quality_score tool
    5. Concrete improvement suggestions
    """

    print(f"Reviewing: {file_path}")

    async for message in query(task, options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 code_review_agent.py <file_path>")
        sys.exit(1)

    asyncio.run(review_code(sys.argv[1]))
```

## Adding Permission Control

When converting, add permission handlers for safety:

```python
async def safe_permission_handler(tool_name, input_data, context):
    """Prevent dangerous operations."""
    # Block system directory writes
    if tool_name == "Write":
        path = input_data.get("file_path", "")
        if any(d in path for d in ["/etc", "/sys", "/boot"]):
            return {"behavior": "deny", "message": "System path blocked"}

    # Require confirmation for deletions
    if tool_name == "Bash":
        cmd = input_data.get("command", "")
        if any(c in cmd for c in ["rm ", "del ", "sudo"]):
            return {"behavior": "deny", "message": "Destructive command blocked"}

    return {"behavior": "allow"}

# Add to options
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Bash"],
    permission_handler=safe_permission_handler
)
```

## Adding Logging with Hooks

Monitor agent execution:

```python
async def log_hook(input_data, tool_use_id, context):
    """Log all tool usage."""
    import json
    from datetime import datetime

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": context.get("tool_name"),
        "input": input_data
    }

    with open("agent_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {}

# Add to options
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write"],
    hooks={'pre_tool_use': log_hook}
)
```

## Making Scripts Reusable

### 1. Accept Command-Line Arguments
```python
import argparse

parser = argparse.ArgumentParser(description='Analyze codebase')
parser.add_argument('directory', help='Directory to analyze')
parser.add_argument('--output', help='Output file', default='report.md')
args = parser.parse_args()
```

### 2. Add Configuration Files
```python
import json

with open('agent_config.json') as f:
    config = json.load(f)

options = ClaudeAgentOptions(
    allowed_tools=config['allowed_tools'],
    cwd=config['working_directory']
)
```

### 3. Create a Template
```python
#!/usr/bin/env python3
"""Reusable Agent Template"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_agent(task: str, tools: list, cwd: str = "."):
    """Generic agent runner."""
    options = ClaudeAgentOptions(
        allowed_tools=tools,
        cwd=cwd,
        permission_mode='auto'
    )

    async for message in query(task, options):
        print(message)

# Use the template
if __name__ == "__main__":
    asyncio.run(run_agent(
        task="Your task here",
        tools=["Read", "Write"],
        cwd="."
    ))
```

## Testing Your Converted Agent

### 1. Test in Safe Environment
```bash
# Create test directory
mkdir /tmp/agent_test
cd /tmp/agent_test

# Run agent there first
python3 your_agent.py /tmp/agent_test
```

### 2. Add Dry-Run Mode
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()

if args.dry_run:
    print("DRY RUN: Would execute task but skipping...")
    sys.exit(0)
```

### 3. Add Verbose Output
```python
import logging

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
logger = logging.getLogger(__name__)

logger.debug("Starting agent execution...")
```

## Deployment Patterns

### 1. Cron Job
```bash
# Add to crontab
0 */6 * * * cd /path/to/project && python3 agent.py >> agent.log 2>&1
```

### 2. GitHub Actions
```yaml
name: Run Agent
on:
  schedule:
    - cron: '0 0 * * *'
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python3 agent.py
```

### 3. Docker Container
```dockerfile
FROM python:3.11
RUN pip install claude-agent-sdk
COPY agent.py /app/
CMD ["python3", "/app/agent.py"]
```

## Checklist for Conversion

- [ ] Identified the core task
- [ ] Extracted required tools
- [ ] Set appropriate working directory
- [ ] Configured permission mode
- [ ] Added error handling
- [ ] Made script executable: `chmod +x agent.py`
- [ ] Added docstring explaining purpose
- [ ] Tested in safe environment
- [ ] Added logging if needed
- [ ] Created usage examples
- [ ] Documented in README

## Common Pitfalls

1. **Missing API Key**: Always check for ANTHROPIC_API_KEY
2. **Wrong Working Directory**: Set `cwd` correctly in options
3. **Permission Issues**: Use appropriate permission_mode
4. **No Error Handling**: Wrap in try/except blocks
5. **Hard-coded Paths**: Use arguments or config files
6. **No Output**: Remember to print TextBlock content
7. **Tool Not Allowed**: Include all needed tools in allowed_tools

## Next Steps

1. Start with simple conversions (read-only tasks)
2. Add custom tools for specific needs
3. Implement permission handlers for safety
4. Add hooks for monitoring
5. Package for deployment

---

*For more examples, see the `examples/` directory*
*For Agent SDK reference, see `claude_agent_sdk_python.md`*
