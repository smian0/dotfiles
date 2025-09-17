---
description: "Build and Deploy"
agent: build
category: deployment
author: developer
version: 1.0
---

# Build and Deploy Command

This command builds the project and deploys it to staging environment.

## Usage

Run this command with:
```bash
opencode run "/build-and-deploy"
```

## Steps

1. Use the agent tool to run build process
2. Check .opencode/ directory for configuration
3. Validate build outputs
4. Deploy to staging

## Configuration

The command expects:
- Build scripts in OpenCode project
- Deployment configuration in .opencode/deploy.yaml
- Environment variables for staging

## Troubleshooting

If deployment fails:
1. Check agent tool output
2. Verify OpenCode environment
3. Review .opencode/ configurations