---
title: "Build and Deploy"
description: "Build the project and deploy to staging"
allowed-tools: Read, Write, Bash, Grep, Task
category: deployment
author: developer
version: 1.0
---

# Build and Deploy Command

This command builds the project and deploys it to staging environment.

## Usage

Run this command with:
```bash
claude run "/build-and-deploy"
```

## Steps

1. Use the Task tool to run build process
2. Check .claude/ directory for configuration
3. Validate build outputs
4. Deploy to staging

## Configuration

The command expects:
- Build scripts in Claude Code project
- Deployment configuration in .claude/deploy.yaml
- Environment variables for staging

## Troubleshooting

If deployment fails:
1. Check Task tool output
2. Verify Claude Code environment
3. Review .claude/ configurations