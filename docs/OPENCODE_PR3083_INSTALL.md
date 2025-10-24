# OpenCode PR #3083 Installation (Hang Fix)

**Installed:** 2025-10-23
**PR Version:** 0.15.8 with hang fix from PR #3083
**Previous Version:** 0.15.14 (backed up)

## What This Fixes

PR #3083 fixes the bug where `opencode run` completes tasks but never exits, requiring Ctrl+C to regain shell control.

**Root Cause:** Subprocesses (particularly Docker-based MCP servers) not receiving proper termination signals unless explicitly configured.

**Fix:** Adds `process.exit()` and improved cleanup to ensure CLI properly terminates.

## Installation Details

### Binaries
- **Current (PR version):** `~/.npm-global/bin/opencode` (compiled from PR #3083)
- **Backup (0.15.14):** `~/.npm-global/bin/opencode.backup-0.15.14`

### Auto-Update Disabled
Updated `~/.config/opencode/opencode.json`:
```json
"autoupdate": false
```

## Features Comparison

### PR Version (0.15.8) Has:
- ✅ **Hang fix** - `opencode run` exits properly
- ✅ **Skills support** - Plugin system works
- ✅ **MCP servers** - All 5 MCP servers functional
- ✅ **Plugin system** - `opencode-skills` plugin loads

### PR Version Missing (vs 0.15.14):
- ⚠️ Session diff API (v0.15.10)
- ⚠️ ACP support improvements (v0.15.10)
- ⚠️ Astro language server (v0.15.9)
- ⚠️ File execution flag `-f/--file` (v0.15.11)
- ⚠️ Model management in sessions (v0.15.14)
- ⚠️ Turn summarization (v0.15.14)

## Testing

**Confirmed working:**
```bash
# No hang - exits immediately after completion
oc -T run --model "github-copilot/claude-sonnet-4" "What is 2+2?"

# Skills plugin loads correctly
oc -T run "Test prompt"  # Shows skill warnings
```

## Rollback Instructions

If you need to revert to 0.15.14:

```bash
# Restore backup
cp ~/.npm-global/bin/opencode.backup-0.15.14 ~/.npm-global/bin/opencode

# Re-enable auto-update
# Edit ~/.config/opencode/opencode.json and set:
"autoupdate": true

# Verify
opencode --version  # Should show 0.15.14
```

## Upgrade Path

When PR #3083 is merged and released:

```bash
# Re-enable auto-update
# Edit ~/.config/opencode/opencode.json:
"autoupdate": true

# Upgrade normally
npm install -g opencode-ai@latest

# Clean up
rm ~/.npm-global/bin/opencode.backup-0.15.14
```

## PR Status

- **PR:** https://github.com/sst/opencode/pull/3083
- **Branch:** `bugfix/opencode-hangs-after-exit`
- **Author:** veracioux (Haris Gušić)
- **Status:** Open, active discussion
- **Checks:** ✅ All passing
- **Review:** Approved by collaborators

## Notes

- The PR is targeting `dev` branch, not `main`
- Active refinements happening as of Oct 20, 2025
- Expected to merge soon based on discussion

---

**Last Updated:** 2025-10-23
