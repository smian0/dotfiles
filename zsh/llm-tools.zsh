# =============================================================================
# LLM Tools Configuration
# =============================================================================
# This file contains all LLM tool related aliases, functions, and configuration
# Sourced from .zshrc for better organization



# Remove any old aliases that might interfere and set correct ones
unalias kimi glm deep claude kimic glmc deepc claudec 2>/dev/null || true

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




