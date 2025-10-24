---
description: Run a Claude Agent SDK script from within Claude Code
---

You are tasked with creating and executing a Claude Agent SDK script.

## Context

The user wants to run an Agent SDK script. Agent SDK scripts:
- Run as separate Python scripts with independent sessions
- Use the Claude Agent SDK library (claude-agent-sdk)
- Can create custom tools and permission handlers
- Execute via the Bash tool

## Your Task

1. **Understand the requirement**: Ask clarifying questions if needed about what the agent should do

2. **Create the agent script**:
   - Use the `Write` tool to create a Python file (e.g., `agent_task.py`)
   - Follow this template structure:

```python
#!/usr/bin/env python3
"""
Agent description here
"""
import asyncio
import sys
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    # Configure agent
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash", "Glob", "Grep"],
        cwd="/path/to/working/directory",
        permission_mode='auto'  # or 'prompt' or 'acceptEdits'
    )

    # Define the task
    task = """
    Your task description here
    """

    # Execute
    async for message in query(task, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

if __name__ == "__main__":
    asyncio.run(main())
```

3. **Add custom tools if needed** (optional):

```python
from claude_agent_sdk import tool
from typing import Any

@tool("tool_name", "Tool description", {"param": str})
async def custom_tool(args: dict[str, Any]) -> dict[str, Any]:
    # Tool implementation
    result = process(args["param"])
    return {
        "content": [{
            "type": "text",
            "text": f"Result: {result}"
        }]
    }

# Add to options
options = ClaudeAgentOptions(
    allowed_tools=["tool_name"],
    custom_tools=[custom_tool]
)
```

4. **Execute the script**:
   - Use the `Bash` tool to run: `python3 agent_task.py`
   - Monitor the output and report results to the user

5. **Handle errors**:
   - If the SDK is not installed, provide installation instructions
   - If there are runtime errors, debug and fix them
   - Explain any issues clearly to the user

## Important Notes

- **Separate sessions**: The agent script runs independently - it doesn't share context with this Claude Code session
- **API key required**: The script needs ANTHROPIC_API_KEY environment variable set
- **File paths**: Use absolute paths or ensure working directory is set correctly
- **Tools**: The agent can use all standard Claude Code tools (Read, Write, Bash, Edit, Glob, Grep, etc.)

## Example Use Cases

1. **Code analysis**: "Run an agent to analyze all Python files and find code smells"
2. **Documentation**: "Create an agent that generates API documentation from code"
3. **Testing**: "Run an agent to execute tests and summarize failures"
4. **Refactoring**: "Create an agent to refactor old-style Python to modern syntax"
5. **Data processing**: "Run an agent to process CSV files and generate reports"

## Output Format

After execution, summarize:
1. What the agent did
2. Key findings or results
3. Any errors or issues encountered
4. Next steps or recommendations

Be concise but comprehensive in reporting results.
