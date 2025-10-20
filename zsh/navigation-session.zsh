# =============================================================================
# Navigation & Session Management Module
# =============================================================================
# Tools: zoxide (via Oh My Zsh plugin), sesh, custom session functions
# Sourced by .zshrc
#
# Note: zoxide is initialized via Oh My Zsh plugin (see .zshrc plugins array)
#       This ensures proper auto-completion and load order.

# =============================================================================
# Sesh + Tmux Session Management
# =============================================================================
if command -v sesh >/dev/null 2>&1 && command -v fzf >/dev/null 2>&1; then
    # Quick session selector with fzf
    alias ss='sesh connect $(sesh list | fzf)'

    # Kill session (interactive with fzf)
    sk() {
        local session=$(sesh list | fzf --prompt="Kill session: ")
        if [[ -n "$session" ]]; then
            tmux kill-session -t "$session"
            echo "✅ Killed session: $session"
        fi
    }

    # List all sessions
    alias sl='sesh list'

    # Connect to session in current directory
    alias sc='sesh connect .'

    # Create named session in current directory
    # Usage: sn <name>
    sn() {
        if [[ -z "$1" ]]; then
            echo "Usage: sn <session-name>"
            echo "Creates a named session in current directory"
            echo ""
            echo "Example: sn api-dev"
            return 1
        fi

        # Check if session exists
        if tmux has-session -t "$1" 2>/dev/null; then
            echo "✅ Attaching to existing session: $1"
            tmux attach -t "$1"
        else
            echo "✅ Creating new session: $1"
            tmux new -s "$1"
        fi
    }

    # Create session with automatic suffix
    # Usage: scs <suffix>
    scs() {
        if [[ -z "$1" ]]; then
            echo "Usage: scs <suffix>"
            echo "Creates a session named <current-dir>-<suffix>"
            echo ""
            echo "Example in ~/dotfiles:"
            echo "  scs test1  → creates 'dotfiles-test1'"
            echo "  scs test2  → creates 'dotfiles-test2'"
            return 1
        fi

        local dir_name=$(basename "$PWD")
        local session_name="${dir_name}-$1"

        if tmux has-session -t "$session_name" 2>/dev/null; then
            echo "✅ Attaching to existing session: $session_name"
            tmux attach -t "$session_name"
        else
            echo "✅ Creating new session: $session_name"
            tmux new -s "$session_name"
        fi
    }
fi

# =============================================================================
# CCManager - Git Worktree + Claude Session Manager (Optional)
# =============================================================================
# CCManager provides a visual TUI for managing git worktrees + Claude sessions
# Install: npm install -g ccmanager
# Usage: ccm (in any git repo)
if command -v ccmanager >/dev/null 2>&1; then
    alias ccm='ccmanager'
fi
