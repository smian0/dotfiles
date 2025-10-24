# ⚠️ OpenCode Upgrade Hold

**DO NOT upgrade OpenCode until PR #3083 is merged!**

## Current Status

- **Installed Version:** 0.15.8 (PR #3083 with hang fix)
- **Latest Official:** 0.15.14
- **Auto-update:** Disabled (`autoupdate: false` in config)

## Why Hold?

You're running a custom build from PR #3083 that fixes the critical hang bug where `opencode run` never exits. The official npm version (0.15.14) still has this bug.

## Upgrade Instructions (When PR is Merged)

### 1. Check PR Status

Visit https://github.com/sst/opencode/pull/3083 to verify it's merged.

### 2. Check Latest Version Includes Fix

```bash
# Check changelog/release notes
npm view opencode-ai version
# Verify version is > 0.15.14 (or check release notes mention the fix)
```

### 3. Re-enable Auto-update

Edit `~/.config/opencode/opencode.json`:
```json
"autoupdate": true
```

### 4. Upgrade

```bash
# Install latest official version
npm install -g opencode-ai@latest

# Verify hang is still fixed
timeout 30 oc -T run --model "github-copilot/claude-sonnet-4" "What is 2+2?"
# Should complete and exit cleanly
```

### 5. Clean Up

```bash
# Remove backup
rm ~/.npm-global/bin/opencode.backup-0.15.14

# Remove this hold file
rm ~/dotfiles/docs/OPENCODE_UPGRADE_HOLD.md
rm ~/dotfiles/docs/OPENCODE_PR3083_INSTALL.md
```

## If You Accidentally Upgrade Before PR Merge

The hang bug will return. To restore the PR version:

```bash
# Restore from backup
cp ~/.npm-global/bin/opencode.backup-0.15.14 ~/.npm-global/bin/opencode

# Or rebuild from source
cd /tmp
git clone https://github.com/sst/opencode.git
cd opencode
git fetch origin pull/3083/head:pr-3083
git checkout pr-3083
bun install
bun build packages/opencode/src/index.ts --compile --outfile opencode-pr3083
chmod +x opencode-pr3083
mv opencode-pr3083 ~/.npm-global/bin/opencode
```

## PR Tracking

- **PR:** https://github.com/sst/opencode/pull/3083
- **Branch:** `bugfix/opencode-hangs-after-exit`
- **Status:** Monitor for merge
- **Related Issues:** #1717, #2692, #2940, #2380

---

**Created:** 2025-10-23
**Check Status:** Weekly until merged
