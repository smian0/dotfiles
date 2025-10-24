---
description: Launch Comet Browser with remote debugging enabled
---

Launch Comet Browser with remote debugging enabled on port 9223, using your existing Comet profile.

Execute this command:
```bash
bash ~/dotfiles/scripts/launch-comet-debug.sh 9223
```

This will:
1. Stop any running Comet instances
2. Launch Comet with your existing Default profile
3. Enable remote debugging on port 9223

After launching, you can use the `comet-devtools` MCP server to automate Comet Browser.

**Note:** You must restart Claude Code to load the `comet-devtools` MCP server configuration.
