# Vanilla .zshrc for testing Claude environment
# Basic shell configuration

# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Basic PATH
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Basic environment variables for Claude
# IMPORTANT: Never set ANTHROPIC_API_KEY="" (empty) as it blocks OAuth authentication

# Source system-wide zsh configuration
if [[ -f /etc/zshrc ]]; then
  source /etc/zshrc
fi

# Basic prompt
PS1='%n@%m %~ %# '

# Browser forwarding configuration for VS Code Remote SSH
export BROWSER="open"
export DISPLAY=":0"
export XAUTHORITY="$HOME/.Xauthority"

# Ensure browser opens in local environment
export BROWSER_FORWARDING_ENABLED=1

# Claude Code OAuth Token (for SSH sessions)
export CLAUDE_CODE_OAUTH_TOKEN="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"

# Claude Code Authentication Protection
# Prevent empty ANTHROPIC_API_KEY from blocking OAuth authentication
claude_auth_protection() {
    if [[ -n "$ANTHROPIC_API_KEY" && -z "$ANTHROPIC_API_KEY" ]]; then
        echo "⚠️  Warning: Empty ANTHROPIC_API_KEY detected, unsetting to allow OAuth"
        unset ANTHROPIC_API_KEY
    fi
}

# Run protection check on shell startup
claude_auth_protection

# Convenience function to fix Claude auth issues
fix_claude_auth() {
    echo "🔧 Fixing Claude Code authentication..."
    unset ANTHROPIC_API_KEY
    if [[ -z "$CLAUDE_CODE_OAUTH_TOKEN" ]]; then
        echo "💡 No OAuth token found. Run 'claude /login' to authenticate."
    else
        echo "✅ OAuth token present: ${CLAUDE_CODE_OAUTH_TOKEN:0:20}..."
    fi
    echo "✅ Authentication environment fixed!"
    echo "💡 Test manually with: claude -p 'test'"
}
