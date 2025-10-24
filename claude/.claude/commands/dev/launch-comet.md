---
description: Launch Comet Browser (Perplexity's browser)
gitignore: project
---

Launch Comet Browser using your Default profile.

Execute this command:
```bash
bash ~/dotfiles/scripts/launch-comet.sh
```

This will:
1. Stop any running Comet instances
2. Launch Comet with your Default profile
3. Normal browser mode (no remote debugging)

**To enable remote debugging** (for automation), use:
```bash
bash ~/dotfiles/scripts/launch-comet.sh Default enable-debug
```

This enables Chrome DevTools Protocol on port 9223 for use with the `comet-devtools` MCP server.
