---
title: yfinance MCP Server Creation
description: "Complete MCP server creation workflow for yfinance API using research, FastMCP builder, and vtree visualization. Executes 3-phase workflow: Research API → Build Server → Document Structure"
category: dev
---

# yfinance MCP Server Creation Workflow Command

Executes complete yfinance MCP Server Creation workflow using $ARGUMENTS as context.

**Usage**: `/dev:yfinance-mcp <description>`

**Example**: `/dev:yfinance-mcp Create MCP server for yfinance stock data`

---

## What This Command Does

Automatically executes the following workflow phases:

1. **Research API**: Research yfinance API
2. **Build Server**: Build MCP server
3. **Document Structure**: Visualize structure

**Input**: $ARGUMENTS contains: Optional API features or specific yfinance functions to include

**Output**: Working yfinance MCP server with stock data tools

---

## Workflow Execution

### Phase 1: Research API

Use Skill tool to invoke research:

```
Skill("research")
```

**Context to provide**:
- Task description from $ARGUMENTS
- Focus on commonly used endpoints (Ticker, download, etc.)
- Document rate limits and error handling

**Expected result**: Clear understanding of yfinance capabilities

**Verification before Phase 2**:
API research complete with endpoints and schemas

---

### Phase 2: Build Server

Use Skill tool to invoke fastmcp-builder:

```
Skill("fastmcp-builder")
```

**Context to provide**:
- Output from Phase 1 (API documentation summary with endpoints, parameters, and response schemas)
- Use FastMCP v2 framework patterns
- Include error handling for API failures

**Expected result**: Functional MCP server ready for testing

**Verification before Phase 3**:
Server built and validates successfully

---

### Phase 3: Document Structure

Use Skill tool to invoke vtree:

```
Skill("vtree")
```

**Context to provide**:
- Output from Phase 2 (Working MCP server file with yfinance tools and resources)
- Highlight MCP-specific components (tools, resources)
- Show dependency structure if applicable

**Expected result**: Clear visual representation of server organization

**Final verification**:
Structure visualization complete

---

---

## Completion

After all phases complete successfully, report to user:

```
✅ yfinance MCP Server Creation workflow completed for: $ARGUMENTS

Results:
- Research API: yfinance API structure documented with examples
- Build Server: MCP server created with yfinance integration
- Document Structure: Server structure documented with visual tree

Deliverables: MCP server file (typically mcp_servers/yfinance_server.py)
```

## Failure Handling

If any phase fails:
1. Report which phase failed
2. Show phase-specific error
3. Ask user if they want to:
   - Retry failed phase
   - Skip and continue (if safe)
   - Abort workflow

**Do not proceed to next phase if current phase fails verification.**

## Quick Reference

**Command**: `/dev:yfinance-mcp <args>`

**Phases**: Research API → Build Server → Document Structure

**Skills used**: research, fastmcp-builder, vtree

**Estimated time**: 20-30 minutes

## Project Customization

To customize this command for your project:

1. Edit phase context items to include project-specific requirements
2. Modify verification criteria for your standards
3. Add project-specific checks or gates
4. Extend with additional phases as needed

This file is project-specific - changes here won't affect other projects.
