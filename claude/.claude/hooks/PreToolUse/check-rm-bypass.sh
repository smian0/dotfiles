#!/bin/bash
# Dual-layer protection: Nuclear safety net for catastrophic rm patterns
#
# Layer 1 (Primary): Shell alias in ~/.zshenv (alias rm=trash-cli)
#   - Handles 98% of normal rm usage
#   - Can be bypassed if needed (/bin/rm, \rm, etc.)
#
# Layer 2 (This Hook): Prevents catastrophic disasters
#   - Only blocks truly dangerous patterns that could destroy the system
#   - Focuses on: rm -rf /, rm -rf ~, rm -rf /*, etc.
#   - Minimal friction, maximum safety
#
# Requires: TRASH_CONFIGURED=1 environment variable (set in ~/.zshenv)

# Read JSON input and extract the bash command
COMMAND=$(jq -r '.tool_input.command // ""' 2>/dev/null)

# Exit if no command or jq failed
[[ -z "$COMMAND" ]] && exit 0

# Verify trash is configured (environment variable from .zshenv)
if [[ -z "$TRASH_CONFIGURED" ]]; then
  # Only warn if this is an rm command (improved word boundary check)
  if echo "$COMMAND" | grep -qE '(^|[[:space:]])rm[[:space:]]'; then
    cat >&2 <<EOF
⚠️  CONFIGURATION WARNING

Trash protection is not configured. Add to ~/.zshenv:
  export TRASH_CONFIGURED=1
  alias rm="\$HOME/.npm-global/bin/trash"

Command allowed but NOT protected: $COMMAND
EOF
  fi
  exit 0  # Allow command to proceed
fi

# CATASTROPHIC PATTERN DETECTION
# Block only patterns that could cause irreversible system damage
# Matches: rm -rf /, /bin/rm -rf /, env rm -r /, etc.
# Enhanced to catch all flag variants and critical system paths
if echo "$COMMAND" | grep -qE 'rm[[:space:]]+(-[a-z]*[rf][a-z]*|-[rf]+|-r[[:space:]]+-f|-f[[:space:]]+-r|--recursive|--force)[[:space:]]+(~/?([[:space:]]|$)|/([[:space:]]|$)|/\*|/System|/Library|/Applications|/usr|/bin|/sbin|/opt|/etc|/boot|/private|/cores|/var/db)'; then
  cat >&2 <<EOF
🛑 NUCLEAR SAFETY BLOCK

Command: $COMMAND

This command targets critical system paths and could cause CATASTROPHIC damage:
  / (root filesystem)
  ~ (home directory)
  /System, /Library, /Applications (macOS system directories)
  /usr, /bin, /sbin, /opt (Unix system binaries)
  /etc (system configuration)
  /boot (boot files)
  /private (macOS private system files)
  /var/db (system databases)

This is blocked to prevent system destruction.

If you ABSOLUTELY need to run this (think twice!):
  1. Is there a safer alternative?
  2. Do you have recent backups?
  3. Run manually in your terminal (not through Claude)
EOF

  # Log the blocked attempt with secure permissions
  LOG_DIR="$HOME/.claude/hooks/logs"
  mkdir -p "$LOG_DIR"
  chmod 700 "$LOG_DIR" 2>/dev/null || true
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] NUCLEAR-BLOCK: $COMMAND" >> "$LOG_DIR/rm-bypass.log"

  exit 1  # BLOCK the command
fi

# All other commands allowed (including deliberate bypasses like /bin/rm)
# The shell alias handles normal protection
# This hook only prevents nuclear disasters
exit 0
