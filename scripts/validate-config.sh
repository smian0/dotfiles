#!/usr/bin/env bash
# Configuration Validation Script
# Validates dotfiles installation and configuration integrity

set -euo pipefail

# Source OS detection for environment setup  
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/os-detect.sh" ]]; then
    source "$SCRIPT_DIR/os-detect.sh"
else
    # Fallback if os-detect.sh is not available
    OS_TYPE="unknown"
    DOTFILES_OS="unknown"
    DOTFILES_DISTRO="unknown"
    DOTFILES_PKG_MANAGER="unknown"
    
    # Define missing functions
    log() { echo "[INFO] $1"; }
    info() { echo "[INFO] $1"; }
    warn() { echo "[WARN] $1"; }
    error() { echo "[ERROR] $1"; return 1; }
    success() { echo "✓ $1"; }
    
    command_exists() {
        command -v "$1" >/dev/null 2>&1
    }
    
    detect_os() {
        if [[ "$OSTYPE" == "darwin"* ]]; then
            OS_TYPE="macos"
            DOTFILES_OS="macos"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            OS_TYPE="linux"  
            DOTFILES_OS="linux"
        fi
    }
    
    export_environment() {
        export DOTFILES_OS
        export DOTFILES_DISTRO
        export DOTFILES_PKG_MANAGER
    }
fi

# Additional validation-specific variables
DOTFILES_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOME_DIR="${HOME:-/home/$(whoami)}"
ERRORS_FOUND=0
WARNINGS_FOUND=0

# Validation results tracking
declare -A validation_results

# Record validation result
record_result() {
    local component=$1
    local status=$2
    local message=$3
    
    validation_results["$component"]="$status:$message"
    
    case "$status" in
        "PASS")
            success "$component: $message"
            ;;
        "WARN")
            warn "$component: $message"
            ((WARNINGS_FOUND++))
            ;;
        "FAIL")
            error "$component: $message" || true
            ((ERRORS_FOUND++))
            ;;
    esac
}

# Validate directory structure
validate_directory_structure() {
    log "Validating directory structure..."
    
    local required_dirs=(
        "git"
        "zsh"
        "vim"
        "claude-default"
        "claude-experimental"
        "pass/scripts"
        "scripts"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$DOTFILES_ROOT/$dir" ]]; then
            record_result "Directory: $dir" "PASS" "exists"
        else
            record_result "Directory: $dir" "FAIL" "missing"
        fi
    done
}

# Validate Stow configuration
validate_stow_config() {
    log "Validating GNU Stow configuration..."
    
    # Check for .stow-global-ignore
    if [[ -f "$DOTFILES_ROOT/.stow-global-ignore" ]]; then
        record_result "Stow config" "PASS" ".stow-global-ignore exists"
        
        # Validate ignore patterns
        local required_patterns=(
            "\.git"
            "\.gitignore"
            "README"
            "\.DS_Store"
        )
        
        for pattern in "${required_patterns[@]}"; do
            if grep -q "$pattern" "$DOTFILES_ROOT/.stow-global-ignore"; then
                record_result "Stow pattern: $pattern" "PASS" "configured"
            else
                record_result "Stow pattern: $pattern" "WARN" "not found in ignore file"
            fi
        done
    else
        record_result "Stow config" "FAIL" ".stow-global-ignore missing"
    fi
}

# Validate symlinks
validate_symlinks() {
    log "Validating symlinks..."
    
    # Check if any packages are stowed
    local stowed_packages=()
    
    for package_dir in "$DOTFILES_ROOT"/*; do
        if [[ -d "$package_dir" ]] && [[ "$(basename "$package_dir")" != "scripts" ]]; then
            local package_name
            package_name=$(basename "$package_dir")
            
            # Check for symlinks pointing to this package
            local has_symlinks=false
            
            # Look for dotfiles in home directory
            for file in "$HOME_DIR"/.*; do
                if [[ -L "$file" ]]; then
                    local target
                    target=$(readlink "$file")
                    if [[ "$target" == *"$DOTFILES_ROOT/$package_name"* ]]; then
                        has_symlinks=true
                        stowed_packages+=("$package_name")
                        break
                    fi
                fi
            done
            
            if [[ "$has_symlinks" == true ]]; then
                record_result "Package: $package_name" "PASS" "stowed"
            else
                record_result "Package: $package_name" "WARN" "not stowed"
            fi
        fi
    done
    
    if [[ ${#stowed_packages[@]} -eq 0 ]]; then
        record_result "Symlinks" "WARN" "No packages are currently stowed"
    else
        record_result "Symlinks" "PASS" "${#stowed_packages[@]} package(s) stowed"
    fi
}

# Validate Claude configuration
validate_claude_config() {
    log "Validating Claude configuration..."
    
    # Check for Claude settings files
    local claude_configs=(
        "claude-default/.claude/settings.json"
        "claude-default/.claude.json"
        "claude-experimental/.claude/settings.json"
        "claude-experimental/.claude.json"
    )
    
    for config in "${claude_configs[@]}"; do
        if [[ -f "$DOTFILES_ROOT/$config" ]]; then
            record_result "Claude: $config" "PASS" "exists"
            
            # Validate JSON syntax
            if command_exists jq; then
                if jq empty "$DOTFILES_ROOT/$config" 2>/dev/null; then
                    record_result "Claude: $config syntax" "PASS" "valid JSON"
                else
                    record_result "Claude: $config syntax" "FAIL" "invalid JSON"
                fi
            fi
        else
            record_result "Claude: $config" "WARN" "not found"
        fi
    done
    
    # Check for MCP configuration
    if [[ -f "$DOTFILES_ROOT/claude-default/.mcp.json" ]] || [[ -f "$DOTFILES_ROOT/claude-experimental/.mcp.json" ]]; then
        record_result "Claude MCP" "PASS" "MCP configuration found"
    else
        record_result "Claude MCP" "WARN" "No MCP configuration found"
    fi
}

# Validate pass configuration
validate_pass_config() {
    log "Validating pass configuration..."
    
    # Check if pass is initialized
    if [[ -d "$HOME_DIR/.password-store" ]]; then
        record_result "Pass store" "PASS" "initialized"
        
        # Check for GPG key
        if command_exists gpg; then
            if [[ -f "$HOME_DIR/.password-store/.gpg-id" ]]; then
                record_result "Pass GPG" "PASS" "GPG key configured"
            else
                record_result "Pass GPG" "WARN" "GPG key not configured"
            fi
        fi
        
        # Check for pass scripts
        if [[ -d "$DOTFILES_ROOT/pass/scripts" ]]; then
            local script_count
            script_count=$(find "$DOTFILES_ROOT/pass/scripts" -name "*.sh" 2>/dev/null | wc -l)
            if [[ $script_count -gt 0 ]]; then
                record_result "Pass scripts" "PASS" "$script_count script(s) available"
            else
                record_result "Pass scripts" "WARN" "No scripts found"
            fi
        fi
    else
        record_result "Pass store" "WARN" "not initialized"
    fi
}

# Validate Git configuration
validate_git_config() {
    log "Validating Git configuration..."
    
    # Check for gitconfig
    if [[ -f "$DOTFILES_ROOT/git/.gitconfig" ]]; then
        record_result "Git config" "PASS" ".gitconfig exists"
        
        # Check for user configuration
        if grep -q "name =" "$DOTFILES_ROOT/git/.gitconfig" && grep -q "email =" "$DOTFILES_ROOT/git/.gitconfig"; then
            record_result "Git user" "PASS" "user configured"
        else
            record_result "Git user" "WARN" "user not configured"
        fi
    else
        record_result "Git config" "WARN" ".gitconfig not found"
    fi
    
    # Check for gitignore global
    if [[ -f "$DOTFILES_ROOT/git/.gitignore_global" ]]; then
        record_result "Git ignore" "PASS" ".gitignore_global exists"
    else
        record_result "Git ignore" "WARN" ".gitignore_global not found"
    fi
}

# Validate shell configuration
validate_shell_config() {
    log "Validating shell configuration..."
    
    # Check for zsh configuration
    if [[ -f "$DOTFILES_ROOT/zsh/.zshrc" ]]; then
        record_result "Zsh config" "PASS" ".zshrc exists"
        
        # Check if zsh is the default shell
        if [[ "$SHELL" == */zsh ]]; then
            record_result "Default shell" "PASS" "zsh is default"
        else
            record_result "Default shell" "WARN" "zsh is not default shell"
        fi
        
        # Check for AI tools integration
        if grep -q "AI Tools Integration" "$DOTFILES_ROOT/zsh/.zshrc"; then
            record_result "AI tools" "PASS" "AI integration found in .zshrc"
            
            # Check for required dependencies
            if command_exists jq; then
                record_result "AI tools: jq" "PASS" "jq available for JSON parsing"
            else
                record_result "AI tools: jq" "WARN" "jq missing (install with: brew install jq)"
            fi
            
            if command_exists curl; then
                record_result "AI tools: curl" "PASS" "curl available for API calls"
            else
                record_result "AI tools: curl" "FAIL" "curl missing (required for AI API calls)"
            fi
        else
            record_result "AI tools" "WARN" "AI integration not found in .zshrc"
        fi
    else
        record_result "Zsh config" "WARN" ".zshrc not found"
    fi
    
    # Check for vim configuration
    if [[ -f "$DOTFILES_ROOT/vim/.vimrc" ]]; then
        record_result "Vim config" "PASS" ".vimrc exists"
    else
        record_result "Vim config" "WARN" ".vimrc not found"
    fi
}

# Check for conflicts
check_for_conflicts() {
    log "Checking for potential conflicts..."
    
    local conflict_found=false
    
    # Check for existing dotfiles that aren't symlinks
    local dotfiles_to_check=(
        ".gitconfig"
        ".zshrc"
        ".vimrc"
        ".claude"
    )
    
    for dotfile in "${dotfiles_to_check[@]}"; do
        local target="$HOME_DIR/$dotfile"
        if [[ -e "$target" ]] && [[ ! -L "$target" ]]; then
            record_result "Conflict: $dotfile" "WARN" "exists but is not a symlink"
            conflict_found=true
        fi
    done
    
    if [[ "$conflict_found" == false ]]; then
        record_result "Conflicts" "PASS" "no conflicts detected"
    fi
}

# Generate validation report
generate_report() {
    echo ""
    echo "==================================="
    echo "     Validation Report Summary"
    echo "==================================="
    echo ""
    
    local pass_count=0
    local warn_count=0
    local fail_count=0
    
    for component in "${!validation_results[@]}"; do
        IFS=':' read -r status message <<< "${validation_results[$component]}"
        case "$status" in
            "PASS") ((pass_count++)) ;;
            "WARN") ((warn_count++)) ;;
            "FAIL") ((fail_count++)) ;;
        esac
    done
    
    echo "Results:"
    echo "  ✓ Passed: $pass_count"
    echo "  ⚠ Warnings: $warn_count"
    echo "  ✗ Failed: $fail_count"
    echo ""
    
    if [[ $ERRORS_FOUND -eq 0 ]]; then
        success "Configuration validation completed successfully!"
        echo ""
        info "All critical checks passed. Your dotfiles are properly configured."
    else
        error "Configuration validation found $ERRORS_FOUND error(s)" || true
        echo ""
        warn "Please fix the errors above before proceeding with installation."
    fi
    
    if [[ $WARNINGS_FOUND -gt 0 ]]; then
        echo ""
        info "Found $WARNINGS_FOUND warning(s). These are non-critical but should be reviewed."
    fi
    
    # Return exit code based on errors
    if [[ $ERRORS_FOUND -gt 0 ]]; then
        return 1
    fi
    return 0
}

# Fix common issues
fix_issues() {
    echo ""
    echo "Would you like to attempt to fix some issues automatically? (y/n)"
    read -r response
    
    if [[ "$response" != "y" ]]; then
        return
    fi
    
    log "Attempting to fix issues..."
    
    # Create missing directories
    for component in "${!validation_results[@]}"; do
        if [[ "$component" == Directory:* ]]; then
            IFS=':' read -r status message <<< "${validation_results[$component]}"
            if [[ "$status" == "FAIL" ]]; then
                local dir_name="${component#Directory: }"
                log "Creating missing directory: $dir_name"
                mkdir -p "$DOTFILES_ROOT/$dir_name"
                success "Created $dir_name"
            fi
        fi
    done
    
    # Create missing config files from templates
    if [[ ! -f "$DOTFILES_ROOT/.stow-global-ignore" ]]; then
        log "Creating .stow-global-ignore..."
        cat > "$DOTFILES_ROOT/.stow-global-ignore" << 'EOF'
# Files to ignore when stowing
\.git
\.gitignore
README.*
LICENSE
\.DS_Store
Thumbs.db
\#.*\#
\.\#.*
.*~
*.swp
*.swo
EOF
        success "Created .stow-global-ignore"
    fi
}

# Main validation function
main() {
    echo "==================================="
    echo "   Dotfiles Configuration Validator"
    echo "==================================="
    echo ""
    
    # Initialize environment
    detect_os
    export_environment
    
    # Run validations
    validate_directory_structure
    validate_stow_config
    validate_symlinks
    validate_claude_config
    validate_pass_config
    validate_git_config
    validate_shell_config
    check_for_conflicts
    
    # Generate report
    generate_report
    
    # Offer to fix issues if any were found
    if [[ $ERRORS_FOUND -gt 0 ]] || [[ $WARNINGS_FOUND -gt 0 ]]; then
        fix_issues
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi