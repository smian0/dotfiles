---
name: fastmcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers using FastMCP v2 and uv single-file scripts. Use when building MCP servers to integrate external APIs or services with Python. This skill exclusively uses FastMCP v2 framework and uv for dependency management.
---

# FastMCP v2 Server Development Guide

## Overview

This skill guides you in creating production-ready MCP servers using **FastMCP v2** (Python) with **uv** for zero-configuration dependency management. All servers are single-file Python scripts with inline metadata, making them portable and easy to deploy.

**Key Technologies:**
- **FastMCP v2**: Python framework for MCP server development
- **uv**: Zero-config Python package manager with inline dependencies
- **Pydantic v2**: Input validation and schema generation
- **httpx**: Async HTTP client for API calls

---

# Process

## 🚀 High-Level Workflow

Creating a FastMCP server involves four phases:

### Phase 1: Deep Research and Planning

#### 1.1 Understand Agent-Centric Design Principles

**Build for Workflows, Not Just API Endpoints:**
- Don't simply wrap existing API endpoints - build thoughtful, high-impact workflow tools
- Consolidate related operations (e.g., `schedule_event` that both checks availability and creates event)
- Focus on tools that enable complete tasks, not just individual API calls
- Consider what workflows agents actually need to accomplish

**Optimize for Limited Context:**
- Agents have constrained context windows - make every token count
- Return high-signal information, not exhaustive data dumps
- Provide "concise" vs "detailed" response format options
- Default to human-readable identifiers over technical codes (names over IDs)

**Design Actionable Error Messages:**
- Error messages should guide agents toward correct usage patterns
- Suggest specific next steps: "Try using filter='active_only' to reduce results"
- Make errors educational, not just diagnostic

**Follow Natural Task Subdivisions:**
- Tool names should reflect how humans think about tasks
- Group related tools with consistent prefixes for discoverability
- Design tools around natural workflows, not just API structure

**Use Evaluation-Driven Development:**
- Create realistic evaluation scenarios early
- Let agent feedback drive tool improvements
- Prototype quickly and iterate based on actual agent performance

#### 1.2 Study MCP Protocol Documentation

**Fetch the latest MCP protocol documentation:**
Use WebFetch to load: `https://modelcontextprotocol.io/llms-full.txt`

#### 1.3 Study FastMCP Documentation

**CRITICAL: Always use Context7 MCP for FastMCP documentation lookup.**

```python
# Use Context7 to get latest FastMCP v2 documentation
from mcp__context7__resolve_library_id import resolve_library_id
from mcp__context7__get_library_docs import get_library_docs

# Get FastMCP library ID
library_id = resolve_library_id("fastmcp")  # Returns: /jlowin/fastmcp

# Get comprehensive documentation
docs = get_library_docs(
    context7CompatibleLibraryID="/jlowin/fastmcp",
    topic="tool decoration, Context usage, Pydantic validation, sampling, resources",
    tokens=8000
)
```

**What to look up:**
- Tool decorator patterns (`@mcp.tool`, `@mcp.tool(name="...")`)
- Input validation (Pydantic models vs `Annotated[Type, Field()]`)
- Context usage (`ctx.info()`, `ctx.sample()`, `ctx.read_resource()`)
- Advanced features (sampling for LLM completions, resource access, prompts)
- Server configuration options

**Load the FastMCP reference guide:**
Read [📋 FastMCP Reference](./reference/fastmcp_reference.md) for complete implementation patterns

#### 1.4 Exhaustively Study API Documentation

To integrate a service, read through **ALL** available API documentation:
- Official API reference documentation
- Authentication and authorization requirements
- Rate limiting and pagination patterns
- Error responses and status codes
- Available endpoints and their parameters
- Data models and schemas

**Delegation Strategy:**

For complex API research requiring comprehensive analysis, delegate to specialized agents:

```python
# Use web-researcher agent for comprehensive API documentation analysis
from Task import Task

Task(
    subagent_type="web-researcher",
    description="Research API documentation",
    prompt="""Research the {service_name} API comprehensively:

1. Find official API documentation
2. Identify authentication methods and requirements
3. List all available endpoints with parameters
4. Document rate limits and pagination patterns
4. Extract error response formats and status codes
5. Identify data models and response schemas

Provide a structured summary with:
- API base URL
- Auth method (API key, OAuth, etc.)
- Top 10 most useful endpoints for workflow tools
- Common response formats
- Rate limiting details
"""
)
```

**When to delegate to subagents:**
- ✅ API has 50+ endpoints (needs comprehensive analysis)
- ✅ Complex authentication flows (OAuth, JWT, etc.)
- ✅ Multiple documentation sources (official docs, blog posts, examples)
- ✅ Need to compare similar APIs or services
- ✅ Technical research requiring cross-referencing

**When to do research directly:**
- ❌ Simple API with clear documentation (< 10 endpoints)
- ❌ Well-known APIs you're already familiar with
- ❌ Quick fact lookups from docs

#### 1.5 Create a Comprehensive Implementation Plan

Based on your research, create a detailed plan that includes:

**Tool Selection:**
- List the most valuable endpoints/operations to implement
- Prioritize tools that enable the most common and important use cases
- Consider which tools work together to enable complex workflows

**Shared Utilities and Helpers:**
- Identify common API request patterns
- Plan pagination helpers
- Design filtering and formatting utilities
- Plan error handling strategies

**Input/Output Design:**
- Define input validation models (Pydantic v2)
- Design consistent response formats (JSON or Markdown)
- Plan for large-scale usage (thousands of users/resources)
- Implement character limits and truncation strategies (25,000 tokens)

**Error Handling Strategy:**
- Plan graceful failure modes
- Design clear, actionable, LLM-friendly error messages
- Consider rate limiting and timeout scenarios
- Handle authentication and authorization errors

---

### Phase 2: Implementation with uv

#### 2.0 Setup Project Structure

**CRITICAL: Always use organized directory structure for MCP servers.**

```bash
# 1. Determine project root (current working directory or ask user)
PROJECT_ROOT=$(pwd)

# 2. Create mcp_servers directory and service subdirectory
mkdir -p mcp_servers/<service_name>
cd mcp_servers/<service_name>

# 3. Initialize the MCP server script
uv init --script <service>_mcp.py --python 3.12

# 4. Add dependencies
uv add --script <service>_mcp.py 'fastmcp>=2.0.0' httpx pydantic

# Directory structure created:
# <projectroot>/
# ├── .mcp.json (or .claude/.mcp.json)
# └── mcp_servers/
#     └── <service_name>/
#         └── <service>_mcp.py
```

**Directory Structure Benefits:**
- ✅ All MCP servers in one place
- ✅ Easy to find and maintain
- ✅ Service-specific subdirectories for multi-file servers
- ✅ Test files colocated with servers
- ✅ Clear separation from project code

#### 2.1 Initialize the Script

Create a single-file Python script with uv inline metadata:

```bash
# Initialize script with Python version
uv init --script <service>_mcp.py --python 3.12

# Add FastMCP v2 dependency
uv add --script <service>_mcp.py 'fastmcp>=2.0.0'

# Add other dependencies
uv add --script <service>_mcp.py httpx pydantic
```

This creates a script with inline dependency metadata:

```python
# /// script
# dependencies = [
#   "fastmcp>=2.0.0",
#   "httpx",
#   "pydantic>=2.0.0",
# ]
# requires-python = ">=3.12"
# ///

# Your code here...
```

#### 2.2 Server Structure Template

Use this template structure:

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "fastmcp>=2.0.0",
#   "httpx",
#   "pydantic>=2.0.0",
# ]
# requires-python = ">=3.12"
# ///

'''
MCP Server for [Service Name].

This server provides tools to interact with [Service] API, including [key features].
'''

from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("[service]_mcp")

# Constants
API_BASE_URL = "https://api.example.com/v1"
CHARACTER_LIMIT = 25000

# ... Pydantic models, utilities, and tools ...

if __name__ == "__main__":
    mcp.run()
```

#### 2.3 Implement Core Infrastructure

**Create shared utilities before implementing tools:**
- API request helper functions using httpx
- Error handling utilities
- Response formatting functions (JSON and Markdown)
- Pagination helpers
- Authentication/token management

See [📋 FastMCP Reference](./reference/fastmcp_reference.md) for complete examples.

#### 2.4 Implement Tools with FastMCP Patterns

**Choose the Right Input Validation Pattern:**

**Pattern 1: Simple Parameters with Annotated (Preferred for 1-3 simple params)**
```python
from typing import Annotated, Literal
from pydantic import Field

@mcp.tool
async def process_image(
    image_url: Annotated[str, Field(description="URL of the image to process")],
    resize: Annotated[bool, Field(description="Whether to resize")] = False,
    width: Annotated[int, Field(description="Width in pixels", ge=1, le=2000)] = 800,
    format: Annotated[Literal["jpeg", "png", "webp"], Field(description="Output format")] = "jpeg"
) -> dict:
    """Process an image with optional resizing."""
    # Implementation
    return {"status": "success", "url": image_url}
```

**Pattern 2: Multiple Parameters with Annotated (Recommended for 2-5 params)**
```python
@mcp.tool
async def search(
    query: Annotated[str, Field(description="Search query", min_length=1, max_length=200)],
    limit: Annotated[int, Field(description="Max results", ge=1, le=100)] = 10,
    sort_by: Annotated[Literal["relevance", "date"], Field(description="Sort order")] = "relevance"
) -> str:
    """Search with multiple validated parameters."""
    # Input validation happens automatically via Pydantic Field constraints
    query = query.strip().lower()
    return f"Found {limit} results for: {query}"
```

**⚠️ Pattern 2b: Pydantic Models (Use only when truly necessary)**

**IMPORTANT**: Pydantic models as single parameters have **compatibility issues** with some MCP clients (including Claude Code). Prefer the `Annotated` pattern above for better compatibility.

Only use Pydantic models when you need:
- Complex custom validation logic
- Reusable input models across multiple tools
- Nested object structures

```python
class SearchInput(BaseModel):
    """Input model for search operation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    query: str = Field(..., description="Search query", min_length=1, max_length=200)
    limit: int = Field(default=10, description="Max results", ge=1, le=100)

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        return v.strip().lower()

@mcp.tool
async def search(params: SearchInput) -> str:
    """Search with validated parameters.

    ⚠️ Note: May not work correctly in all MCP clients due to nested parameter structure.
    """
    # Implementation
    return f"Found results for: {params.query}"
```

**Better Alternative - Flatten to Annotated:**
```python
# Instead of Pydantic model, expand fields as individual Annotated parameters
@mcp.tool
async def search(
    query: Annotated[str, Field(description="Search query", min_length=1, max_length=200)],
    limit: Annotated[int, Field(description="Max results", ge=1, le=100)] = 10
) -> str:
    """Search with validated parameters - better MCP client compatibility."""
    query = query.strip().lower()  # Manual validation if needed
    return f"Found {limit} results for: {query}"
```

**Pattern 3: Simple No-Parameter Tools**
```python
@mcp.tool
async def get_status() -> dict:
    """Get current system status."""
    return {"status": "healthy", "uptime": 3600}
```

**Pattern 4: Tools with Context (Advanced - for LLM sampling, logging, resources)**
```python
from fastmcp import Context

@mcp.tool
async def analyze_data(uri: str, ctx: Context) -> str:
    """Analyze data from a resource with LLM assistance."""
    # Log progress to client
    await ctx.info(f"Loading data from {uri}...")

    # Read resource from server
    data = await ctx.read_resource(uri)

    # Ask client's LLM to analyze
    summary = await ctx.sample(
        f"Summarize this data in 3 bullet points:\n{data.content[:500]}"
    )

    return summary.text
```

**Tool Decorator Options (Official FastMCP v2):**
```python
@mcp.tool(
    name="custom_name",           # Optional: Override function name
    description="Tool purpose",   # Optional: Override docstring
    tags=["category", "feature"],  # Optional: Categorization
    enabled=True,                  # Optional: Disable tool
    output_schema={                # Optional: Validate output structure
        "type": "object",
        "properties": {
            "result": {"type": "string"},
            "count": {"type": "integer"}
        }
    }
)
async def my_tool() -> dict:
    return {"result": "success", "count": 42}
```

#### 2.5 Advanced MCP Features

**Resources: Provide Data Access**
```python
# Static resource
@mcp.resource("config://settings")
def get_settings() -> str:
    """Provide application settings."""
    return json.dumps({"api_version": "2.0", "max_retries": 3})

# Parameterized resource (template)
@mcp.resource("users://{user_id}/profile")
async def get_user_profile(user_id: str) -> dict:
    """Get user profile by ID."""
    user = await fetch_user(user_id)
    return {"name": user.name, "email": user.email}

# Resource with Context
@mcp.resource("data://{dataset}")
async def get_dataset(dataset: str, ctx: Context) -> str:
    """Load dataset with progress logging."""
    await ctx.info(f"Loading dataset: {dataset}")
    data = await load_large_dataset(dataset)
    return json.dumps(data)
```

**Prompts: Pre-built LLM Conversations**
```python
from fastmcp.utilities.types import Message

@mcp.prompt
def analyze_code(file_path: str) -> list[Message]:
    """Generate prompt for code analysis."""
    code = read_file(file_path)
    return [
        {
            "role": "user",
            "content": f"Analyze this code for bugs and improvements:\n\n```\n{code}\n```"
        }
    ]

# Prompt with Context
@mcp.prompt
async def review_pr(pr_number: int, ctx: Context) -> list[Message]:
    """Generate PR review prompt with fetched data."""
    await ctx.info(f"Fetching PR #{pr_number}")
    pr_data = await fetch_pull_request(pr_number)

    return [
        {
            "role": "user",
            "content": f"Review this pull request:\n\nTitle: {pr_data.title}\n\nChanges:\n{pr_data.diff}"
        }
    ]
```

**Sampling: Request LLM Completions from Client**
```python
@mcp.tool
async def smart_summary(url: str, ctx: Context) -> str:
    """Fetch content and ask client's LLM to summarize."""
    # Fetch content
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        content = response.text[:5000]

    # Ask client's LLM to process
    result = await ctx.sample(
        f"Summarize this webpage in 3 bullet points:\n\n{content}",
        max_tokens=200
    )

    return result.text

@mcp.tool
async def analyze_with_context(data: str, question: str, ctx: Context) -> str:
    """Use LLM to answer questions about data."""
    # Build prompt with context
    prompt = f"""Given this data:
{data}

Answer this question: {question}

Provide a detailed analysis with evidence from the data."""

    # Get LLM analysis
    analysis = await ctx.sample(prompt, temperature=0.7, max_tokens=500)

    return analysis.text
```

**Context Logging and Progress**
```python
@mcp.tool
async def process_batch(items: list[str], ctx: Context) -> dict:
    """Process items with progress updates."""
    results = []

    await ctx.info(f"Starting batch processing of {len(items)} items")

    for i, item in enumerate(items):
        await ctx.info(f"Processing item {i+1}/{len(items)}: {item}")

        try:
            result = await process_item(item)
            results.append(result)
        except Exception as e:
            await ctx.error(f"Failed to process {item}: {e}")

    await ctx.info(f"Completed: {len(results)}/{len(items)} successful")

    return {
        "processed": len(results),
        "total": len(items),
        "results": results
    }
```

**Server Configuration Options**
```python
from fastmcp import FastMCP

# Configure server behavior
mcp = FastMCP(
    name="MyServer",

    # Strict input validation (no type coercion)
    strict_input_validation=True,

    # Error on duplicate tool names
    on_duplicate_tools="error",  # or "warn", "ignore"

    # Custom output serializer for all tools
    tool_serializer=lambda data: yaml.dump(data) if isinstance(data, dict) else str(data)
)

# Example: Strict validation prevents "5" from becoming 5
@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """With strict_input_validation=True, passing strings will error."""
    return a + b
```

**Async Patterns for CPU-Intensive Work**
```python
import anyio

# Wrap synchronous blocking functions
def cpu_intensive_task(data: str) -> str:
    # Heavy computation
    return processed_data

@mcp.tool
async def wrapped_task(data: str) -> str:
    """CPU-intensive task that won't block the event loop."""
    return await anyio.to_thread.run_sync(cpu_intensive_task, data)
```

---

### Phase 3: Testing and Configuration

#### 3.0 Auto-Generate Test Script

**CRITICAL: Always create a test script after implementing the MCP server.**

Create `test_<service>_mcp.py` in the same directory:

```python
#!/usr/bin/env python3
"""
Automated test suite for <service>_mcp.py server.

Tests all tools with sample inputs and validates tool registration using
proper FastMCP v2 in-memory testing patterns with Client class.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


async def test_server():
    """Test all MCP server tools using FastMCP Client."""
    # Import server and Client for in-memory testing
    from <service>_mcp import mcp
    from fastmcp import Client

    print("=" * 60)
    print(f"Testing <Service> MCP Server (FastMCP v2)")
    print("=" * 60)

    # Use Client for in-memory testing (proper FastMCP v2 pattern)
    async with Client(mcp) as client:
        # Test 1: Tool with no parameters
        print("\n[TEST 1] Testing tool_name (no parameters)...")
        try:
            result1 = await client.call_tool("tool_name", {})
            print(f"✅ Result: {result1.content[0].text}")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 2: Tool with Annotated parameters
        print("\n[TEST 2] Testing tool_name (Annotated pattern)...")
        try:
            result2 = await client.call_tool("tool_name", {
                "param1": "value1",
                "param2": "value2"
            })
            print(f"✅ Result: {result2.content[0].text}")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 3: Tool returning dict (use result.data)
        print("\n[TEST 3] Testing tool_returning_dict...")
        try:
            result3 = await client.call_tool("tool_name", {
                "param": "value"
            })
            # For dict returns, use result.data
            print(f"✅ Result: {result3.data}")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test N: Check registered tools
        print(f"\n[TEST N] Checking registered tools...")
        try:
            tools = await client.list_tools()
            print(f"✅ Registered tools: {len(tools)}")
            for tool in tools:
                desc_preview = tool.description[:60] if tool.description else "No description"
                print(f"   - {tool.name}: {desc_preview}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_server())
```

**Make test executable and run:**
```bash
chmod +x test_<service>_mcp.py
uv run --with 'fastmcp>=2.0.0' python3 test_<service>_mcp.py
```

**Test Script Template Checklist:**
- [ ] Import server and all tool functions
- [ ] Import all input models
- [ ] Test each tool with realistic sample data
- [ ] Test error cases (invalid inputs, missing auth, etc.)
- [ ] Validate tool registration count
- [ ] Print clear pass/fail status for each test

#### 3.1 Auto-Configure .mcp.json

**CRITICAL: Always add the server to the project root's .mcp.json after testing successfully.**

**Step 1: Use project root .mcp.json**
```bash
# Always use project root .mcp.json
PROJECT_ROOT=$(pwd)
MCP_CONFIG="$PROJECT_ROOT/.mcp.json"
```

**Step 2: Get absolute path to server**
```bash
SERVER_PATH=$(realpath mcp_servers/<service_name>/<service>_mcp.py)
```

**Step 3: Update .mcp.json (merge, don't overwrite)**

If file doesn't exist, create with:
```json
{
  "mcpServers": {
    "<service-name>": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "reloaderoo",
        "proxy",
        "--",
        "uv",
        "run",
        "--script",
        "<ABSOLUTE_PATH>/mcp_servers/<service_name>/<service>_mcp.py"
      ],
      "description": "Brief description of what this server does",
      "env": {
        "MCPDEV_PROXY_AUTO_RESTART": "true",
        "SERVICE_API_KEY": "${SERVICE_API_KEY}"
      }
    }
  }
}
```

If file exists, add new server entry to existing `mcpServers` object:
```json
{
  "mcpServers": {
    "existing-server": { ... },
    "<service-name>": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "reloaderoo",
        "proxy",
        "--",
        "uv",
        "run",
        "--script",
        "<ABSOLUTE_PATH>/mcp_servers/<service_name>/<service>_mcp.py"
      ],
      "description": "Brief description of what this server does",
      "env": {
        "MCPDEV_PROXY_AUTO_RESTART": "true",
        "SERVICE_API_KEY": "${SERVICE_API_KEY}"
      }
    }
  }
}
```

**Use the update_mcp_json.py helper script from scripts/ directory:**

The helper script at `scripts/update_mcp_json.py` provides a CLI for managing .mcp.json configurations. It automatically adds the proper format with reloaderoo for auto-restart.

**Usage:**
```bash
# Add server with auto-restart enabled (recommended)
python3 scripts/update_mcp_json.py add \
  <service-name> \
  mcp_servers/<service_name>/<service>_mcp.py \
  --description "Brief description" \
  --auto-restart

# Add environment variables
python3 scripts/update_mcp_json.py add \
  <service-name> \
  mcp_servers/<service_name>/<service>_mcp.py \
  --description "Brief description" \
  --env "SERVICE_API_KEY=${SERVICE_API_KEY}" \
  --auto-restart

# List all configured servers
python3 scripts/update_mcp_json.py list

# Remove a server
python3 scripts/update_mcp_json.py remove <service-name>
```

**Example:**
```bash
python3 scripts/update_mcp_json.py add \
  github \
  mcp_servers/github/github_mcp.py \
  --description "GitHub API integration for repositories and issues" \
  --env "GITHUB_TOKEN=${GITHUB_TOKEN}" \
  --auto-restart
```

**Configuration Checklist:**
- [ ] Use absolute path to server script
- [ ] Use `uv run --script` as command
- [ ] Preserve existing servers (merge, don't overwrite)
- [ ] Add environment variables for API keys
- [ ] Use `${VAR_NAME}` syntax for env var expansion
- [ ] Validate JSON syntax after update
- [ ] Document required environment variables

#### 3.2 Run with uv

**Make script executable:**
```bash
chmod +x my_service_mcp.py
```

**Run directly (uv auto-manages dependencies):**
```bash
# Using uv run
uv run my_service_mcp.py

# Or if script has shebang
./my_service_mcp.py
```

**Test in Claude Code:**

Add to `.claude/.mcp.json`:
```json
{
  "mcpServers": {
    "my-service": {
      "command": "uv",
      "args": ["run", "--script", "/absolute/path/to/my_service_mcp.py"]
    }
  }
}
```

#### 3.2 Quality Review

**Code Quality Checklist:**
- [ ] DRY Principle: No duplicated code between tools
- [ ] Composability: Shared logic extracted into functions
- [ ] Consistency: Similar operations return similar formats
- [ ] Error Handling: All external calls have error handling
- [ ] Type Safety: Full type hints throughout
- [ ] Documentation: Comprehensive docstrings for every tool

**FastMCP v2 Checklist:**
- [ ] Server name follows format: `{service}_mcp`
- [ ] All tools use `@mcp.tool` decorator (no `annotations` parameter)
- [ ] **Prefer `Annotated[Type, Field()]` pattern for all parameters** (best MCP client compatibility)
- [ ] Avoid Pydantic models as single parameters (causes issues with some MCP clients)
- [ ] Use Pydantic models only for complex validation or reusable inputs (if necessary)
- [ ] Async/await for all I/O operations
- [ ] Tools with LLM interaction use `Context` parameter
- [ ] Context methods used: `ctx.info()`, `ctx.sample()`, `ctx.read_resource()`
- [ ] Character limits enforced (25,000 chars)
- [ ] Response formats support both JSON and Markdown
- [ ] CPU-intensive work wrapped with `anyio.to_thread.run_sync()`

#### 3.3 Dependency Locking (Optional)

For reproducible environments:
```bash
# Lock dependencies
uv lock --script my_service_mcp.py

# Creates my_service_mcp.py.lock file
```

---

### Phase 4: Create Evaluations

Create comprehensive evaluations to test effectiveness.

**Load [✅ Evaluation Guide](./reference/evaluation.md) for complete guidelines.**

#### 4.1 Create 10 Evaluation Questions

Each question must be:
- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations required
- **Complex**: Requiring multiple tool calls and deep exploration
- **Realistic**: Based on real use cases
- **Verifiable**: Single, clear answer
- **Stable**: Answer won't change over time

#### 4.2 Output Format

```xml
<evaluation>
  <qa_pair>
    <question>Complex question requiring multiple tool calls...</question>
    <answer>Expected answer</answer>
  </qa_pair>
  <!-- More qa_pairs... -->
</evaluation>
```

---

# Reference Files

## 📚 Documentation Library

Load these resources as needed:

### Core Documentation
- **MCP Protocol**: `https://modelcontextprotocol.io/llms-full.txt`
- **FastMCP SDK**: `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`

### Local References
- [📋 FastMCP Reference](./reference/fastmcp_reference.md) - Complete FastMCP v2 patterns
- [🔧 uv Guide](./reference/uv_guide.md) - uv single-file script patterns
- [✅ Evaluation Guide](./reference/evaluation.md) - Testing and evaluation

---

# Complete Automated Workflow

## Quick Start Example (GitHub MCP Server)

```bash
# 1. Setup directory structure
mkdir -p mcp_servers/github
cd mcp_servers/github

# 2. Initialize server with dependencies
uv init --script github_mcp.py --python 3.12
uv add --script github_mcp.py 'fastmcp>=2.0.0' httpx pydantic

# 3. Implement server (see template above)
# ... write github_mcp.py ...

# 4. Auto-generate test script
cat > test_github_mcp.py <<'EOF'
#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_server():
    from github_mcp import mcp, github_search, SearchInput

    print("Testing GitHub MCP Server")

    # Test tool
    params = SearchInput(query="fastmcp", limit=5)
    result = await github_search(params)
    print(f"✅ Search result: {len(result)} chars")

    # Validate registration
    tools = await mcp.list_tools()
    print(f"✅ Registered {len(tools)} tools")

if __name__ == "__main__":
    asyncio.run(test_server())
EOF

# 5. Run tests
chmod +x test_github_mcp.py
uv run --with 'fastmcp>=2.0.0' python3 test_github_mcp.py

# 6. Auto-configure .mcp.json
cd ../..  # Return to project root
python3 mcp_servers/github/update_mcp_json.py \
  "github" \
  "mcp_servers/github/github_mcp.py" \
  '{"GITHUB_TOKEN":"${GITHUB_TOKEN}"}'

# 7. Final structure:
# <projectroot>/
# ├── .mcp.json ✅
# └── mcp_servers/
#     └── github/
#         ├── github_mcp.py ✅
#         ├── test_github_mcp.py ✅
#         └── update_mcp_json.py ✅
```

## Automation Checklist

When implementing a new MCP server, verify:

**Phase 1: Planning**
- [ ] Research API documentation thoroughly
- [ ] Design workflow-focused tools (not just API wrappers)
- [ ] Plan input validation and error handling

**Phase 2: Implementation**
- [ ] Create directory: `mcp_servers/<service_name>/`
- [ ] Initialize with uv: `uv init --script <service>_mcp.py`
- [ ] Add dependencies: FastMCP, httpx, pydantic
- [ ] Implement server with proper structure
- [ ] Use Context7 MCP to look up FastMCP v2 patterns
- [ ] **Prefer `Annotated[Type, Field()]` for ALL parameters** (best MCP client compatibility)
- [ ] Avoid Pydantic models as single parameters (compatibility issues)
- [ ] Use Pydantic models only when truly necessary (complex validation, reusable inputs)
- [ ] Add `Context` parameter for LLM sampling and logging
- [ ] Follow async/await patterns throughout

**Phase 3: Testing**
- [ ] Auto-generate `test_<service>_mcp.py`
- [ ] Test all tools with realistic data
- [ ] Validate tool registration
- [ ] Run: `uv run --with 'fastmcp>=2.0.0' python3 test_*.py`

**Phase 4: Configuration**
- [ ] Get absolute path: `realpath mcp_servers/<service>/<service>_mcp.py`
- [ ] Auto-update `.mcp.json` (merge, don't overwrite)
- [ ] Use uv command: `["uv", "run", "--script", "<path>"]`
- [ ] Add environment variables for API keys
- [ ] Document required environment variables

**Phase 5: Deployment**
- [ ] Restart IDE/Claude Code to load new server
- [ ] Test tools through MCP interface
- [ ] Create evaluation questions
- [ ] Document usage and examples
```

---

**Key Advantages:**
- ✅ **Zero configuration**: No pyproject.toml, no virtual envs
- ✅ **Portable**: Single file with inline dependencies
- ✅ **Fast**: uv installs dependencies instantly
- ✅ **Simple**: Just `uv run script.py`
- ✅ **Reproducible**: Optional lock files for exact versions
