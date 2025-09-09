#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["agno>=1.7.0", "ollama>=0.5.3", "fastmcp>=2.0.0"]
# ///

"""
MCP Configuration for Claude CLI:

JSON Configuration (add to ~/.claude.json):
{
  "mcpServers": {
    "joke-server": {
      "command": "/Users/smian/dotfiles/claude/.claude/mcp_servers/joke_mcp_server.py",
      "transport": "stdio"
    }
  }
}

Command Line Setup:
claude mcp add joke-server /Users/smian/dotfiles/claude/.claude/mcp_servers/joke_mcp_server.py
claude mcp remove joke-server -s local  # to remove
"""

from fastmcp import FastMCP
from agno.agent import Agent
from agno.models.ollama import Ollama

# Create MCP server instance
mcp = FastMCP("joke_server")

# Initialize agno agent  
agent = Agent(
    model=Ollama(id="llama3.1:8b"),
    instructions="You are a joke-telling agent. Tell different types of jokes based on user requests: programming jokes, dad jokes, puns, knock-knock jokes, etc. Keep jokes clean and family-friendly."
)

@mcp.tool()
def tell_joke(prompt: str) -> str:
    """Tell jokes based on user requests - programming, dad jokes, puns, etc.
    
    Args:
        prompt: User request for joke type or category
        
    Returns:
        str: A clean, family-friendly joke
    """
    response = agent.run(prompt)
    return response.content

# Optional: Add model configuration tool
@mcp.tool()
def set_model(model_id: str) -> str:
    """Change the agent's Ollama model
    
    Args:
        model_id: Ollama model ID (e.g., 'llama3.1:8b', 'qwen3:14b')
        
    Returns:
        str: Confirmation message
    """
    agent.model = Ollama(id=model_id)
    return f"Agent model changed to {model_id}"

if __name__ == "__main__":
    # Run with stdio transport (default for Claude Code)
    mcp.run(transport="stdio")