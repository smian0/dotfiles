# =============================================================================
# LLM Tools Configuration
# =============================================================================
# This file contains all LLM tool related aliases, functions, and configuration
# Sourced from .zshrc for better organization



# Remove any old aliases that might interfere and set correct ones
unalias kimi glm deep claude 2>/dev/null || true

# Set up direct aliases to the LLM tools
alias kimi='~/dotfiles/bin/kimi'
alias glm='~/dotfiles/bin/glm'
alias deep='~/dotfiles/bin/deep'

# Claude aliases (using global npm installation)
alias clauded='claude --dangerously-skip-permissions'
alias clauder='claude --dangerously-skip-permissions --resume'

# LLM tools with --dangerously-skip-permissions
alias kimid="~/dotfiles/bin/kimi --dangerously-skip-permissions"
alias kimir="~/dotfiles/bin/kimi --dangerously-skip-permissions --resume"
alias glmd="~/dotfiles/bin/glm --dangerously-skip-permissions"
alias glmr="~/dotfiles/bin/glm --dangerously-skip-permissions --resume"
alias deepd="~/dotfiles/bin/deep --dangerously-skip-permissions"
alias deepr="~/dotfiles/bin/deep --dangerously-skip-permissions --resume"

# LLM tools with --dangerously-skip-permissions --continue
alias kimic="~/dotfiles/bin/kimi --dangerously-skip-permissions --continue"
alias glmc="~/dotfiles/bin/glm --dangerously-skip-permissions --continue"
alias deepc="~/dotfiles/bin/deep --dangerously-skip-permissions --continue"
alias claudec="claude --dangerously-skip-permissions --continue"

# Claude wrapper function - automatically adds current date as system prompt
claude() {
    local current_date=$(date '+%A, %B %d, %Y')
    local timezone=$(date '+%Z (%z)')
    local date_prompt="Today is $current_date, timezone $timezone."

    # Call original claude with date prompt appended
    /Users/smian/.npm-global/bin/claude --append-system-prompt "$date_prompt" "$@"
}

# Claude bypass alias - access original claude without automatic date injection
alias claude-original='/Users/smian/.npm-global/bin/claude'




