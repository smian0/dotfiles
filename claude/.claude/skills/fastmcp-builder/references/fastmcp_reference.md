# FastMCP v2 Reference Guide

Complete implementation guide for FastMCP v2, the high-level Python framework for MCP servers.

---

## Server Initialization

```python
from mcp.server.fastmcp import FastMCP

# Initialize server with service name
mcp = FastMCP("service_mcp")

# Server name format: {service}_mcp (lowercase with underscores)
# Examples: github_mcp, jira_mcp, stripe_mcp
```

---

## Tool Registration

### Basic Tool Pattern

```python
from pydantic import BaseModel, Field, ConfigDict

class ToolInput(BaseModel):
    '''Input validation model.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    query: str = Field(..., description="Search query", min_length=1)
    limit: int = Field(default=20, description="Max results", ge=1, le=100)

@mcp.tool(
    name="service_search",
    annotations={
        "title": "Search Service Resources",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def service_search(params: ToolInput) -> str:
    '''
    Search for resources in the service.

    Detailed description of what this tool does and when to use it.

    Args:
        params (ToolInput): Validated input parameters

    Returns:
        str: JSON or Markdown formatted response
    '''
    try:
        results = await fetch_data(params.query, params.limit)
        return format_response(results)
    except Exception as e:
        return handle_error(e)
```

---

## Pydantic v2 Input Validation

### Basic Model

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict

class UserInput(BaseModel):
    '''User creation input model.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    name: str = Field(..., description="User's full name", min_length=1, max_length=100)
    email: str = Field(..., description="Email address", pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., description="User's age", ge=0, le=150)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Email cannot be empty")
        return v.lower()
```

### Response Format Enum

```python
from enum import Enum

class ResponseFormat(str, Enum):
    '''Output format for responses.'''
    MARKDOWN = "markdown"
    JSON = "json"

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )
```

---

## Response Formatting

### Markdown Format

```python
def format_markdown(users: List[Dict]) -> str:
    '''Format users as Markdown.'''
    lines = ["# User Results", ""]

    for user in users:
        lines.append(f"## {user['name']} ({user['id']})")
        lines.append(f"- **Email**: {user['email']}")
        lines.append(f"- **Status**: {user['status']}")
        lines.append("")

    return "\n".join(lines)
```

### JSON Format

```python
import json

def format_json(users: List[Dict], total: int) -> str:
    '''Format users as JSON.'''
    response = {
        "total": total,
        "count": len(users),
        "users": users
    }
    return json.dumps(response, indent=2)
```

---

## Pagination Implementation

```python
class ListInput(BaseModel):
    limit: Optional[int] = Field(
        default=20,
        description="Maximum results to return",
        ge=1,
        le=100
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of results to skip",
        ge=0
    )

async def list_items(params: ListInput) -> str:
    data = await api_request(limit=params.limit, offset=params.offset)

    has_more = data["total"] > params.offset + len(data["items"])
    next_offset = params.offset + len(data["items"]) if has_more else None

    response = {
        "total": data["total"],
        "count": len(data["items"]),
        "offset": params.offset,
        "has_more": has_more,
        "next_offset": next_offset,
        "items": data["items"]
    }

    return json.dumps(response, indent=2)
```

---

## Character Limits and Truncation

```python
# Module-level constant
CHARACTER_LIMIT = 25000

async def search_tool(params: SearchInput) -> str:
    result = await generate_response(data)

    if len(result) > CHARACTER_LIMIT:
        # Truncate and add notice
        truncated_data = data[:len(data) // 2]
        response["data"] = truncated_data
        response["truncated"] = True
        response["truncation_message"] = (
            f"Response truncated from {len(data)} to {len(truncated_data)} items. "
            f"Use 'offset' or add filters to see more."
        )
        result = json.dumps(response, indent=2)

    return result
```

---

## Error Handling

### Centralized Error Handler

```python
import httpx

def handle_api_error(e: Exception) -> str:
    '''Consistent error formatting.'''
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error: {type(e).__name__}"
```

---

## Shared Utilities

### API Request Helper

```python
async def make_api_request(endpoint: str, method: str = "GET", **kwargs) -> dict:
    '''Reusable API request function.'''
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}/{endpoint}",
            timeout=30.0,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
```

### Authentication Helper

```python
import os

def get_auth_headers() -> Dict[str, str]:
    '''Get authentication headers.'''
    api_key = os.getenv("SERVICE_API_KEY")
    if not api_key:
        raise ValueError("SERVICE_API_KEY environment variable not set")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
```

---

## Advanced Features

### Context Parameter Injection

```python
from mcp.server.fastmcp import FastMCP, Context

@mcp.tool()
async def advanced_search(query: str, ctx: Context) -> str:
    '''Tool with context access for logging and progress.'''

    # Report progress
    await ctx.report_progress(0.25, "Starting search...")

    # Log information
    await ctx.log_info("Processing query", {"query": query})

    # Perform search
    results = await search_api(query)
    await ctx.report_progress(0.75, "Formatting results...")

    return format_results(results)

@mcp.tool()
async def interactive_tool(resource_id: str, ctx: Context) -> str:
    '''Request additional input from users.'''

    api_key = await ctx.elicit(
        prompt="Please provide your API key:",
        input_type="password"
    )

    return await api_call(resource_id, api_key)
```

**Context capabilities:**
- `ctx.report_progress(progress, message)` - Report progress
- `ctx.log_info(message, data)` - Logging
- `ctx.elicit(prompt, input_type)` - Request user input
- `ctx.fastmcp.name` - Access server config
- `ctx.read_resource(uri)` - Read MCP resources

### Resource Registration

```python
@mcp.resource("file://documents/{name}")
async def get_document(name: str) -> str:
    '''Expose documents as MCP resources.'''
    document_path = f"./docs/{name}"
    with open(document_path, "r") as f:
        return f.read()
```

**Use Resources for:**
- Simple data access with URI templates
- Static or semi-static content
- Template-based retrieval

**Use Tools for:**
- Complex operations
- Business logic
- Input validation

### Lifespan Management

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    '''Manage resources for server lifetime.'''
    # Initialize
    db = await connect_to_database()
    config = load_configuration()

    yield {"db": db, "config": config}

    # Cleanup
    await db.close()

mcp = FastMCP("example_mcp", lifespan=app_lifespan)

@mcp.tool()
async def query_data(query: str, ctx: Context) -> str:
    '''Access lifespan resources through context.'''
    db = ctx.request_context.lifespan_state["db"]
    results = await db.query(query)
    return format_results(results)
```

---

## Complete Example

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

'''MCP Server for Example Service.'''

from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
import json
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# Initialize server
mcp = FastMCP("example_mcp")

# Constants
API_BASE_URL = "https://api.example.com/v1"
CHARACTER_LIMIT = 25000

# Enums
class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

# Input Models
class SearchInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    query: str = Field(..., description="Search query", min_length=2)
    limit: Optional[int] = Field(default=20, description="Max results", ge=1, le=100)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

# Utilities
async def make_api_request(endpoint: str, **kwargs) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/{endpoint}", **kwargs)
        response.raise_for_status()
        return response.json()

def handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        return f"Error: API request failed ({e.response.status_code})"
    return f"Error: {type(e).__name__}"

# Tools
@mcp.tool(
    name="example_search",
    annotations={
        "title": "Search Example Resources",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def example_search(params: SearchInput) -> str:
    '''Search for resources in Example service.'''
    try:
        data = await make_api_request(
            "search",
            params={"q": params.query, "limit": params.limit}
        )

        if params.response_format == ResponseFormat.MARKDOWN:
            return format_markdown(data["results"])
        else:
            return json.dumps(data, indent=2)
    except Exception as e:
        return handle_error(e)

def format_markdown(results: List[Dict]) -> str:
    lines = ["# Search Results", ""]
    for item in results:
        lines.append(f"## {item['title']}")
        lines.append(f"- ID: {item['id']}")
        lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    mcp.run()
```

---

## Best Practices Checklist

**Tool Design:**
- [ ] Server name follows `{service}_mcp` format
- [ ] Tool names are snake_case and action-oriented
- [ ] Tools enable workflows, not just API wrappers
- [ ] Response formats support both JSON and Markdown

**Input Validation:**
- [ ] All inputs use Pydantic v2 models
- [ ] Models have `model_config` with strict validation
- [ ] Fields have descriptions with examples
- [ ] Constraints use Field() parameters (min_length, ge, le)

**Implementation:**
- [ ] All I/O operations use async/await
- [ ] Shared utilities extracted (no duplication)
- [ ] Error handling is consistent
- [ ] Character limits enforced (25,000)
- [ ] Pagination implemented where needed

**Documentation:**
- [ ] Every tool has comprehensive docstrings
- [ ] Docstrings include Args and Returns sections
- [ ] Error scenarios documented
- [ ] Usage examples provided
