# OpenCode Developer Documentation

This directory contains technical documentation for developers who need to modify, maintain, or extend the OpenCode system.

## Architecture Documentation

Deep technical details about how the system works:

- **[Agent Transformation](architecture/agent-transformation.md)** - How Claude agents are converted to OpenCode format
- **[Command Transformation](architecture/command-transformation.md)** - Command processing and conversion system
- **[MCP Transformation](architecture/mcp-transformation.md)** - Model Context Protocol server integration and live synchronization

## Maintenance Documentation  

Guides for maintaining and troubleshooting the system:

- **[Shell Functions](maintenance/shell-functions.md)** - Shell function management and troubleshooting
- **[Testing Procedures](maintenance/testing.md)** - Testing framework and procedures

## Testing Infrastructure

The `../tests/` directory contains:
- Test fixtures and expected outputs
- Automated testing scripts
- Test result validation

## For End Users

If you just need to use OpenCode, see the [User Documentation](../docs/README.md).

---

**Contributing**: Before making changes, read the architecture docs to understand the transformation system, then use the testing procedures to validate your changes.