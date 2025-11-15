# Workflow Output Control Patterns

## Overview

Agno workflows support two output modes:
1. **Production Mode** - Clean, concise output for CLI/automation
2. **Development Mode** - Rich formatted output with step details

Choose the right mode based on your use case.

---

## CRITICAL: Async Tools Require Async Methods

**Problem:** `workflow.print_response()` is synchronous and fails with async tools like MCPTools.

**Solution:** Use `workflow.aprint_response()` for async tools.

```python
# ❌ FAILS with async tools (MCPTools, etc)
workflow.print_response(input=query)

# ✅ WORKS with async tools
await workflow.aprint_response(input=query)
```

**Error you'll see if using sync with async tools:**
```
Exception: Async tool MCPTools can't be used with synchronous 
agent.run() or agent.print_response(). Use agent.arun() or 
agent.aprint_response() instead.
```

---

## Production Mode (Clean Output)

**Use case:** CLI tools, automation scripts, production deployments

```python
async def execute_workflow(user_request: str):
    workflow = Workflow(
        steps=[step1, step2, step3],
        debug_mode=False  # Clean output
    )
    
    # Programmatic access - returns result
    result = await workflow.arun(user_request)
    return result.content

# Output: Only final result + minimal INFO logs
```

**CLI Example:**
```bash
./my_workflow.py "query"
```

**Output:**
```
INFO Executing async step: parse_query
INFO Executing async step: validate
INFO Executing async step: execute

[Final result only - clean and concise]
```

**Best for:**
- Production use
- Scripting/automation
- When you need to parse output
- Piping to other commands

---

## Development Mode (Rich Output)

**Use case:** Development, debugging, demos, understanding workflow behavior

```python
async def execute_workflow(user_request: str, show_details: bool = False):
    workflow = Workflow(
        steps=[step1, step2, step3],
        debug_mode=False  # Still set to False for workflow-level
    )
    
    if show_details:
        # Rich formatted output with step details
        await workflow.aprint_response(
            input=user_request,
            markdown=True,           # Rich markdown formatting
            show_time=True,          # Execution time per step
            show_step_details=True,  # Show structured outputs
            stream=False,            # Set True for real-time streaming
            stream_events=False,     # Set True to stream step events
        )
        return ""  # Output already printed
    else:
        # Clean programmatic mode
        result = await workflow.arun(user_request)
        return result.content
```

**CLI Example with Flags:**
```bash
# Clean mode (default)
./my_workflow.py "query"

# Rich mode with details
./my_workflow.py --show-steps --show-time "query"
```

**Rich Output:**
```
┏━ Workflow Information ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Workflow: My Workflow                                  ┃
┃ Description: Multi-step processing                     ┃
┃ Steps: 3 steps                                         ┃
┃ Message: query                                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

[Live spinner during execution]

┏━ Step 1: parse_query (Completed) ━━━━━━━━━━━━━━━━━━━━━━┓
┃ Structured Output:                                     ┃
┃ {                                                      ┃
┃   "action": "list",                                    ┃
┃   "entity": "contact",                                 ┃
┃   "parameters": {...}                                  ┃
┃ }                                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━ Step 2: validate (Completed) ━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Structured Output:                                     ┃
┃ {                                                      ┃
┃   "is_valid": true,                                    ┃
┃   "validated_params": {...}                            ┃
┃ }                                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━ Step 3: execute (Completed) ━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [Final execution result formatted beautifully]         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Completed in 8.5s
```

**Best for:**
- Development & debugging
- Verifying structured outputs work correctly
- Understanding agent behavior
- Demos & presentations
- Performance profiling

---

## CLI Implementation Pattern

**Add flags for output control:**

```python
import click

@click.command()
@click.argument('query', nargs=-1, required=True)
@click.option('--show-steps', is_flag=True, help='Show detailed step execution')
@click.option('--show-time', is_flag=True, help='Show execution time')
@click.option('--stream', is_flag=True, help='Stream output in real-time')
def main(query, show_steps, show_time, stream):
    """Execute workflow with optional detailed output."""
    user_request = " ".join(query)
    
    asyncio.run(execute_workflow(
        user_request,
        show_steps=show_steps,
        show_time=show_time,
        stream=stream
    ))

async def execute_workflow(
    user_request: str,
    show_steps: bool = False,
    show_time: bool = False,
    stream: bool = False
):
    workflow = Workflow(steps=[...], debug_mode=False)
    
    # Choose output mode based on flags
    if show_steps or show_time or stream:
        # Rich development mode
        await workflow.aprint_response(
            input=user_request,
            markdown=True,
            show_time=show_time,
            show_step_details=show_steps,
            stream=stream,
            stream_events=stream,
        )
        return ""
    else:
        # Clean production mode
        result = await workflow.arun(user_request)
        return result.content

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
# Production mode
./workflow.py "query"

# Show step details
./workflow.py --show-steps "query"

# Show execution time
./workflow.py --show-time "query"

# Show both
./workflow.py --show-steps --show-time "query"

# Stream results in real-time
./workflow.py --stream "long query"
```

---

## Agent-Level Debug Control

```python
# Development: Enable agent debug
agent = Agent(
    model=Ollama(id="glm-4.6:cloud"),
    debug_mode=True,  # Shows token counts, tool calls, timing
    tools=[...]
)

# Production: Disable agent debug
agent = Agent(
    model=Ollama(id="glm-4.6:cloud"),
    debug_mode=False,  # Clean output
    tools=[...]
)
```

**Debug mode shows:**
- Token counts (input/output/total)
- Tokens per second
- Tool call details
- Model responses
- Timing per agent run

---

## Workflow-Level Debug Control

```python
# Clean workflow execution
workflow = Workflow(
    steps=[...],
    debug_mode=False  # No workflow-level debug logs
)

# Verbose workflow execution
workflow = Workflow(
    steps=[...],
    debug_mode=True  # Shows step transitions, state changes
)
```

---

## Streaming Output

**Use case:** Long-running operations, real-time feedback

```python
await workflow.aprint_response(
    input=user_request,
    stream=True,        # Stream final result as it's generated
    stream_events=True, # Stream step events in real-time
    markdown=True
)
```

**Output:**
- Shows progress as agents work
- Updates in real-time
- Good for user feedback during long operations

---

## Best Practices

### 1. Default to Clean Output
```python
# Good: Clean by default, detailed when needed
if args.debug:
    await workflow.aprint_response(...)
else:
    result = await workflow.arun(...)
```

### 2. Use Flags for Development Features
```python
# Good: Opt-in to detailed output
--show-steps    # See structured outputs
--show-time     # Performance metrics
--debug         # Full debug mode
--stream        # Real-time updates
```

### 3. Disable Debug in Production
```python
# Production settings
agent = Agent(debug_mode=False)
workflow = Workflow(debug_mode=False)

# Use arun() for clean output
result = await workflow.arun(input)
```

### 4. Use aprint_response for Demos
```python
# Great for showing workflow behavior
await workflow.aprint_response(
    input="demo query",
    show_step_details=True,
    show_time=True,
    markdown=True
)
```

---

## Comparison Matrix

| Mode | Method | Use Case | Output Style |
|------|--------|----------|--------------|
| **Production** | `workflow.arun()` | CLI tools, automation | Clean, minimal logs |
| **Development** | `workflow.aprint_response(show_step_details=True)` | Debugging, development | Rich formatted boxes |
| **Streaming** | `workflow.aprint_response(stream=True)` | Long operations | Real-time updates |
| **Performance** | `workflow.aprint_response(show_time=True)` | Profiling | Execution time metrics |

---

## Real-World Example: Xero Workflow CLI

From `xero_workflow_cli.py`:

```python
@click.command()
@click.argument('query', nargs=-1, required=True)
@click.option('--show-steps', is_flag=True)
@click.option('--show-time', is_flag=True)
@click.option('--stream', is_flag=True)
def query_command(query, show_steps, show_time, stream):
    user_request = " ".join(query)
    asyncio.run(execute_query(user_request, show_steps, show_time, stream))

async def execute_query(request, show_steps, show_time, stream):
    workflow = Workflow(steps=[...], debug_mode=False)
    
    if show_steps or show_time or stream:
        # Rich output with aprint_response (async tools support)
        await workflow.aprint_response(
            input=request,
            markdown=True,
            show_time=show_time,
            show_step_details=show_steps,
            stream=stream,
            stream_events=stream,
        )
        return ""
    else:
        # Clean output with arun
        result = await workflow.arun(request)
        return result.content
```

**Usage:**
```bash
# Production: Clean output
./xero_workflow_cli.py "list contacts"

# Development: See all steps
./xero_workflow_cli.py --show-steps --show-time "list contacts"

# Streaming: Real-time updates for large operations
./xero_workflow_cli.py --stream "list all invoices"
```

---

## Key Takeaways

1. **Use `aprint_response()`** (not `print_response()`) for async tools
2. **Default to clean output** in production
3. **Provide CLI flags** for detailed output when needed
4. **`show_step_details=True`** reveals structured Pydantic outputs
5. **`show_time=True`** helps with performance profiling
6. **`stream=True`** for long-running operations
7. **`debug_mode=False`** for workflows, even when using `aprint_response()`

Proper output control makes workflows production-ready while keeping excellent developer experience for debugging.

