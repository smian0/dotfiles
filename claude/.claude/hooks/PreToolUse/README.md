# Dual-Layer File Deletion Protection

## Overview

This system provides two independent layers of protection against accidental file deletion, balancing safety with usability.

## Architecture

### Layer 1: Shell Alias (Primary - 98% Coverage)
**File:** `~/.zshenv`
**Protection:** `alias rm="$HOME/.npm-global/bin/trash"`

**What it does:**
- Intercepts ALL `rm` commands in all shells
- Redirects to [trash-cli](https://github.com/sindresorhus/trash-cli)
- Moves files to macOS Trash instead of permanently deleting
- Accepts all standard rm flags (-f, -rf, -i, etc.) for compatibility

**Can be bypassed (deliberately):**
- `/bin/rm` - Use full path to native rm
- `\rm` - Escape the alias
- `command rm` - Use command builtin
- `env rm` - Use env wrapper
- `'rm'` or `"rm"` - Quote the command

### Layer 2: PreToolUse Hook (Nuclear Safety - 2% Coverage)
**File:** `check-rm-bypass.sh` (this directory)
**Protection:** Blocks catastrophic patterns only

**What it blocks:**
- `rm -rf /` (root filesystem)
- `rm -rf ~` (entire home directory)
- `rm -rf /*` (root wildcard)
- `rm -rf /System` (macOS system files)
- `rm -rf /Library` (macOS libraries)
- `rm -rf /Applications` (installed apps)
- `rm -rf /usr`, `/bin`, `/opt` (Unix system directories)
- `rm -rf /var/db` (system databases)

**What it allows:**
- Normal rm commands (handled by Layer 1)
- Deliberate bypasses on safe paths (`/bin/rm /tmp/file.txt`)
- Any rm without force flags on critical paths

## Decision Matrix

| Command | Layer 1 Result | Layer 2 Result | Final Outcome |
|---------|----------------|----------------|---------------|
| `rm file.txt` | → Trash | Not triggered | ✅ Moved to trash |
| `rm -rf dir/` | → Trash | Not triggered | ✅ Moved to trash |
| `/bin/rm /tmp/file` | Bypassed | Allowed (safe path) | ✅ Permanently deleted |
| `\rm file.txt` | Bypassed | Allowed (safe path) | ✅ Permanently deleted |
| `rm -rf /` | → Trash | 🛑 BLOCKED | 🛑 Blocked by hook |
| `rm -rf ~` | → Trash | 🛑 BLOCKED | 🛑 Blocked by hook |
| `/bin/rm -rf /System` | Bypassed | 🛑 BLOCKED | 🛑 Blocked by hook |

## Philosophy

### Why Two Layers?

**Layer 1 (Alias):**
- **Purpose:** Make safe deletion the default behavior
- **Friction:** Zero - completely transparent
- **Override:** Easy when needed (use full path)
- **Coverage:** Daily usage

**Layer 2 (Hook):**
- **Purpose:** Prevent catastrophic system damage
- **Friction:** Only for nuclear patterns
- **Override:** Requires manual terminal execution
- **Coverage:** Disaster prevention

### Why Not Just One Layer?

**Just Alias:**
- ❌ Can be bypassed accidentally in scripts
- ❌ No protection against catastrophic mistakes
- ✅ But 98% coverage is pretty good

**Just Hook:**
- ❌ Doesn't protect normal usage
- ❌ Only activates for dangerous patterns
- ❌ Requires Claude Code to work

**Both (Current):**
- ✅ Defense in depth
- ✅ Minimal friction (hook rarely triggers)
- ✅ Deliberate bypasses allowed on safe paths
- ✅ Nuclear disasters prevented
- ✅ Works everywhere (alias) and in Claude (hook)

## Installation

### Prerequisites

1. **Install trash-cli:**
   ```bash
   npm install -g trash-cli
   ```

2. **Verify installation:**
   ```bash
   which trash
   # Should show: /Users/[user]/.npm-global/bin/trash
   ```

### Setup

1. **Layer 1 is already configured** in `~/.zshenv` (symlinked from dotfiles)

2. **Layer 2 is already configured** in this directory (managed by Claude Code)

3. **Verify both layers:**
   ```bash
   # Check alias
   type rm
   # Should show: rm is an alias for /Users/[user]/.npm-global/bin/trash

   # Check environment variable
   echo $TRASH_CONFIGURED
   # Should show: 1
   ```

## Testing

Run the test suite:
```bash
cd /tmp
rm -rf protection-test
mkdir protection-test && cd protection-test

# Test 1: Normal rm (should use trash)
echo "test" > file1.txt
rm file1.txt
# File moved to trash ✅

# Test 2: Bypass on safe path (should work)
echo "test" > file2.txt
/bin/rm file2.txt
# File permanently deleted ✅

# Test 3: Flags work correctly
echo "test" > file3.txt
rm -fv file3.txt
# File moved to trash with flags accepted ✅
```

## Override Methods

### For Normal Files (Layer 1)

If you need permanent deletion on safe paths:
```bash
# Use full path
/bin/rm file.txt

# Or escape the alias
\rm file.txt

# Or use command
command rm file.txt
```

### For Catastrophic Patterns (Layer 2)

If the hook blocks something and you're ABSOLUTELY SURE:
```bash
# Hook will provide a bypass ID like: CLAUDE_BYPASS_ID=1234567890
# Run in manual terminal (NOT in Claude Code):
CLAUDE_BYPASS_ID=1234567890 rm -rf /dangerous/path
```

**⚠️ Think twice before doing this!**

## Maintenance

### Logs

Blocked attempts are logged to:
```
~/.claude/hooks/logs/rm-bypass.log
```

View recent blocks:
```bash
tail -20 ~/.claude/hooks/logs/rm-bypass.log
```

### Uninstall

To remove protection:

1. **Remove Layer 1 (alias):**
   ```bash
   # Edit ~/.zshenv and remove the alias line
   ```

2. **Remove Layer 2 (hook):**
   ```bash
   rm ~/.claude/hooks/PreToolUse/check-rm-bypass.sh
   ```

3. **Keep trash-cli** (useful for manual trash commands):
   ```bash
   # Keep: trash-cli is still useful
   # Remove: npm uninstall -g trash-cli
   ```

## Troubleshooting

### "Un-recognized argument -f"

This means the alias is pointing to native `/usr/bin/trash` instead of trash-cli:
```bash
# Fix: Verify npm bin is in PATH
echo $PATH | grep npm

# If not found, source .zshenv
source ~/.zshenv
```

### Hook not triggering

1. Verify `TRASH_CONFIGURED` is set:
   ```bash
   echo $TRASH_CONFIGURED  # Should be: 1
   ```

2. Check hook is executable:
   ```bash
   ls -la ~/.claude/hooks/PreToolUse/check-rm-bypass.sh
   ```

3. Test in Claude Code Bash tool (hooks only work there)

### False positives

If the hook blocks something safe, the pattern may need adjustment. Edit this file's regex on line 41.

## Benefits

1. **✅ Peace of Mind:** Files go to Trash by default
2. **✅ Recoverable:** Trash can be emptied or files restored
3. **✅ Compatible:** Works with all rm flags
4. **✅ Flexible:** Easy to bypass when needed
5. **✅ Safe:** Nuclear patterns always blocked
6. **✅ Transparent:** No behavior change for normal usage
7. **✅ Auditable:** Blocked attempts logged

## See Also

- [trash-cli](https://github.com/sindresorhus/trash-cli) - CLI for trash functionality
- [Claude Code Hooks](https://docs.claude.com/hooks) - PreToolUse hook documentation
- [dotfiles/zsh/.zshenv](../../zsh/.zshenv) - Layer 1 configuration

---

*Last Updated: 2025-10-20*
*Status: ✅ Active and tested*
