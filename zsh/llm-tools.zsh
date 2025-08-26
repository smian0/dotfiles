# =============================================================================
# LLM Tools Configuration
# =============================================================================
# This file contains all LLM tool related aliases, functions, and configuration
# Sourced from .zshrc for better organization

# AI Tool Environment Management
# Function to manage environment variables for different AI tools
ai_env_setup() {
    local tool="$1"
    shift
    
    case "$tool" in
        kimi|glm|deep)
            # Backup and unset ANTHROPIC_* variables to prevent conflicts
            # These tools use their own ANTHROPIC_* variables with different values
            if [[ -n "$ANTHROPIC_API_KEY" ]]; then
                export ANTHROPIC_API_KEY_BACKUP="$ANTHROPIC_API_KEY"
                unset ANTHROPIC_API_KEY
            fi
            if [[ -n "$ANTHROPIC_BASE_URL" ]]; then
                export ANTHROPIC_BASE_URL_BACKUP="$ANTHROPIC_BASE_URL"
                unset ANTHROPIC_BASE_URL
            fi
            if [[ -n "$ANTHROPIC_AUTH_TOKEN" ]]; then
                export ANTHROPIC_AUTH_TOKEN_BACKUP="$ANTHROPIC_AUTH_TOKEN"
                unset ANTHROPIC_AUTH_TOKEN
            fi
            ;;
        claude)
            # Restore ANTHROPIC_* variables if they were backed up
            if [[ -n "$ANTHROPIC_API_KEY_BACKUP" ]]; then
                export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY_BACKUP"
                unset ANTHROPIC_API_KEY_BACKUP
            fi
            if [[ -n "$ANTHROPIC_BASE_URL_BACKUP" ]]; then
                export ANTHROPIC_BASE_URL="$ANTHROPIC_BASE_URL_BACKUP"
                unset ANTHROPIC_BASE_URL_BACKUP
            fi
            if [[ -n "$ANTHROPIC_AUTH_TOKEN_BACKUP" ]]; then
                export ANTHROPIC_AUTH_TOKEN="$ANTHROPIC_AUTH_TOKEN_BACKUP"
                unset ANTHROPIC_AUTH_TOKEN_BACKUP
            fi
            ;;
    esac
    
    # Execute the original command
    "$@"
}

# Remove any old aliases that might interfere and set correct ones
unalias kimi glm deep 2>/dev/null || true

# Override any existing aliases with the correct dotfiles bin scripts
# These now use ai_env_setup to manage environment variables
alias kimi='ai_env_setup kimi ~/dotfiles/bin/kimi'
alias glm='ai_env_setup glm ~/dotfiles/bin/glm'
alias deep='ai_env_setup deep ~/dotfiles/bin/deep'
alias kimid="ai_env_setup kimi ~/dotfiles/bin/kimi --dangerously-skip-permissions"
alias kimir="ai_env_setup kimi ~/dotfiles/bin/kimi --dangerously-skip-permissions --resume"
alias glmd="ai_env_setup glm ~/dotfiles/bin/glm --dangerously-skip-permissions"
alias glmr="ai_env_setup glm ~/dotfiles/bin/glm --dangerously-skip-permissions --resume"
alias deepd="ai_env_setup deep ~/dotfiles/bin/deep --dangerously-skip-permissions"
alias deepr="ai_env_setup deep ~/dotfiles/bin/deep --dangerously-skip-permissions --resume"

# AI assistant chooser function
function ai() {
    local service="$1"
    shift
    local prompt="$*"
    
    case "$service" in
        kimi|moonshot)
            ai_env_setup kimi ~/dotfiles/bin/kimi "$prompt"
            ;;
        glm|chatglm)
            ai_env_setup glm ~/dotfiles/bin/glm "$prompt"
            ;;
        deep|deepseek)
            ai_env_setup deep ~/dotfiles/bin/deep "$prompt"
            ;;
        claude)
            if command_exists claude; then
                ai_env_setup claude claude "$prompt"
            else
                echo "Claude CLI not available. Install Claude Code first."
                return 1
            fi
            ;;
        help|--help|-h)
            echo "AI Assistant Tool"
            echo "Usage: ai <service> [prompt]"
            echo ""
            echo "Available services:"
            echo "  kimi, moonshot   - Kimi AI (Moonshot)"
            echo "  glm, chatglm     - ChatGLM"
            echo "  deep, deepseek   - DeepSeek AI"
            echo "  claude           - Claude Code CLI"
            echo ""
            echo "Interactive mode (no prompt):"
            echo "  kimi             - Start Kimi interactive session"
            echo "  glm              - Start ChatGLM interactive session"
            echo "  deep             - Start DeepSeek interactive session"
            echo "  ai kimi          - Start Kimi via ai wrapper"
            echo ""
            echo "One-shot examples:"
            echo "  ai kimi 'Explain git branches'"
            echo "  ai glm 'Write a Python script'"
            echo "  ai deep 'Solve this problem'"
            echo "  ai claude 'Review this code'"
            ;;
        *)
            echo "Unknown AI service: $service"
            echo "Run 'ai help' for available services"
            return 1
            ;;
    esac
}

# Quick AI aliases
alias ask='ai'
alias askimi='kimi'
alias askglm='glm'
alias askdeep='deep'

# AI setup helper
function ai-setup() {
    echo "AI Tools Setup Assistant"
    echo "======================="
    echo ""
    echo "This will help you store API keys securely using pass."
    echo ""
    
    # Check if pass is available
    if ! command_exists pass; then
        echo "Error: pass (password store) not found"
        echo "Install it first or run the dotfiles master installer"
        return 1
    fi
    
    # Setup Kimi API key
    if ! pass show llm/kimi_api_key >/dev/null 2>&1; then
        echo "🌙 Setting up Kimi AI (Moonshot):"
        echo "1. Visit: https://platform.moonshot.cn/"
        echo "2. Create account and get API key"
        echo "3. Enter your API key when prompted"
        echo ""
        echo -n "Do you want to store Kimi API key now? (y/n): "
        read -r response
        if [[ "$response" == "y" ]]; then
            pass insert llm/kimi_api_key
        fi
    else
        echo "✓ Kimi API key already configured"
    fi
    
    echo ""
    
    # Setup GLM API key
    if ! pass show api/glm >/dev/null 2>&1; then
        echo "🤖 Setting up ChatGLM:"
        echo "1. Visit: https://open.bigmodel.cn/"
        echo "2. Create account and get API key"
        echo "3. Enter your API key when prompted"
        echo ""
        echo -n "Do you want to store GLM API key now? (y/n): "
        read -r response
        if [[ "$response" == "y" ]]; then
            pass insert api/glm
        fi
    else
        echo "✓ GLM API key already configured"
    fi
    
    echo ""
    
    # Setup DeepSeek API key
    if ! pass show api/deepseek >/dev/null 2>&1; then
        echo "🧠 Setting up DeepSeek AI:"
        echo "1. Visit: https://platform.deepseek.com/"
        echo "2. Create account and get API key"
        echo "3. Enter your API key when prompted"
        echo ""
        echo -n "Do you want to store DeepSeek API key now? (y/n): "
        read -r response
        if [[ "$response" == "y" ]]; then
            pass insert api/deepseek
        fi
    else
        echo "✓ DeepSeek API key already configured"
    fi
    
    echo ""
    echo "AI Tools Setup Complete!"
    echo ""
    echo "Test your setup:"
    echo "  kimi 'Hello, how are you?'"
    echo "  glm 'Write a hello world in Python'"
    echo "  deep 'Explain quantum computing'"
    echo "  ai help"
}

# AI status checker
function ai-status() {
    echo "AI Tools Status"
    echo "==============="
    echo ""
    
    # Check dependencies
    local deps_ok=true
    
    if command_exists curl; then
        echo "✓ curl: available"
    else
        echo "✗ curl: missing (required for API calls)"
        deps_ok=false
    fi
    
    if command_exists jq; then
        echo "✓ jq: available"
    else
        echo "✗ jq: missing (required for JSON parsing)"
        echo "  Install with: brew install jq"
        deps_ok=false
    fi
    
    if command_exists pass; then
        echo "✓ pass: available"
    else
        echo "✗ pass: missing (recommended for secure API key storage)"
        deps_ok=false
    fi
    
    echo ""
    
    # Check API keys
    echo "API Key Status:"
    
    if command_exists pass && pass show api/kimi >/dev/null 2>&1; then
        echo "✓ Kimi API key: configured in pass"
    elif [[ -n "$KIMI_API_KEY" ]]; then
        echo "✓ Kimi API key: configured in environment"
    else
        echo "✗ Kimi API key: not configured"
        echo "  Run 'ai-setup' to configure"
    fi
    
    if command_exists pass && pass show api/glm >/dev/null 2>&1; then
        echo "✓ GLM API key: configured in pass"
    elif [[ -n "$GLM_API_KEY" ]]; then
        echo "✓ GLM API key: configured in environment"
    else
        echo "✗ GLM API key: not configured"
        echo "  Run 'ai-setup' to configure"
    fi
    
    if command_exists pass && pass show api/deepseek >/dev/null 2>&1; then
        echo "✓ DeepSeek API key: configured in pass"
    elif [[ -n "$DEEPSEEK_API_KEY" ]]; then
        echo "✓ DeepSeek API key: configured in environment"
    else
        echo "✗ DeepSeek API key: not configured"
        echo "  Run 'ai-setup' to configure"
    fi
    
    if command_exists claude; then
        echo "✓ Claude Code CLI: available"
    else
        echo "✗ Claude Code CLI: not installed"
    fi
    
    echo ""
    
    if [[ "$deps_ok" == true ]]; then
        echo "✅ All dependencies satisfied"
        echo "Run 'ai-setup' to configure API keys if needed"
    else
        echo "❌ Missing dependencies - install them first"
    fi
}
