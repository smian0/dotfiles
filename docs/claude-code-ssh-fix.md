# Claude Code SSH Authentication - Complete Fix

## Problem

Claude Code works perfectly in local terminals but fails with "Invalid API key · Please run /login" error in SSH sessions, even after successful browser authentication.

## Root Cause

**Empty `ANTHROPIC_API_KEY=""` environment variables interfere with Claude Code's OAuth authentication.**

Claude Code checks `ANTHROPIC_API_KEY` first, and if it finds an empty value, it fails without falling back to the valid `CLAUDE_CODE_OAUTH_TOKEN`.

## The Simple Solution

Remove all empty `ANTHROPIC_API_KEY` and `CLAUDE_OAUTH_TOKEN` exports from shell configuration files.

**That's it.** No SSH configuration changes, no special forwarding, no complex setup needed.

## Automated Fix

### Option 1: Use the Fix Script
```bash
~/dotfiles/scripts/fix-claude-ssh-auth.sh
```

### Option 2: Use Built-in Functions (if you've stowed zsh)
```bash
claude_status      # Check current status
fix_claude_auth    # Quick fix
```

## Manual Fix (if needed)

1. **Find conflicting variables:**
   ```bash
   grep -rn "ANTHROPIC_API_KEY.*=\"\"" ~/.zshrc ~/.zshenv ~/.profile ~/.bashrc 2>/dev/null
   ```

2. **Remove empty exports:**
   Remove lines like:
   ```bash
   export ANTHROPIC_API_KEY=""
   export CLAUDE_OAUTH_TOKEN=""
   ```

3. **Restart shell:**
   ```bash
   source ~/.zshrc
   ```

4. **Test:**
   ```bash
   ssh your-remote-host
   claude -p "test"  # Should work now
   ```

## Automatic Protection (New Machines)

**Your dotfiles now include automatic protection!**

```bash
cd ~/dotfiles
stow zsh  # Deploys Claude Code auth protection automatically
```

The stowed `.zshrc` includes:
- **Automatic detection** of empty `ANTHROPIC_API_KEY` on shell startup
- **Auto-removal** with warning message
- **`claude_status`** - Check authentication status  
- **`fix_claude_auth`** - Quick fix function
- **Built-in protection** prevents this issue from recurring

## Verification

After applying the fix:

```bash
# This should be unset or have actual value (not empty):
echo $ANTHROPIC_API_KEY

# This should have your OAuth token:  
echo $CLAUDE_CODE_OAUTH_TOKEN

# Test Claude Code:
claude -p "test authentication"
```

## Why This Works

- **Before:** `ANTHROPIC_API_KEY=""` → Claude Code fails immediately
- **After:** `ANTHROPIC_API_KEY` unset → Claude Code uses `CLAUDE_CODE_OAUTH_TOKEN` → Success

## Available Commands

After stowing dotfiles, you get:

- `claude_status` - Full authentication diagnostics
- `fix_claude_auth` - Quick fix for auth issues
- `~/dotfiles/scripts/fix-claude-ssh-auth.sh` - Complete cleanup script

## Future Prevention

- ✅ **Never set `ANTHROPIC_API_KEY=""` in shell configs**
- ✅ **Use `unset ANTHROPIC_API_KEY` instead of empty value**
- ✅ **Stow deployment includes automatic protection**
- ✅ **Built-in detection prevents recurrence**

## Status: ✅ SOLVED

Claude Code now works seamlessly in SSH sessions with the same experience as local terminals. The fix is permanent and automatically deployed to new machines via dotfiles.

---
*This is the definitive guide to the Claude Code SSH authentication fix. All complex workarounds were unnecessary - the issue was simply empty environment variables blocking OAuth.*