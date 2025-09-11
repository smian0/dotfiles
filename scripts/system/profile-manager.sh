#!/usr/bin/env bash
# Profile Manager for Selective Dotfiles Installation
# Manages different installation profiles for various use cases

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Available profiles
declare -A PROFILES=(
    ["minimal"]="Essential tools only (git, zsh, claude-cli)"
    ["development"]="Development tools + basic npm packages"
    ["full"]="Complete setup with all packages and configurations"
    ["work"]="Work-specific configuration (no personal tools)"
    ["personal"]="Personal machine setup with all customizations"
)

# Package mappings for each profile
declare -A PROFILE_PACKAGES=(
    ["minimal"]="git zsh claude-default"
    ["development"]="git zsh zed claude-default claude-experimental npm-configs config bin"
    ["full"]="git zsh vim zed claude-default claude-experimental npm-configs config bin pass"
    ["work"]="git zsh zed claude-default npm-configs"
    ["personal"]="git zsh vim zed claude-default claude-experimental npm-configs config bin pass"
)

# Logging functions
log() { echo "[INFO] $1"; }
info() { echo "[INFO] $1"; }
warn() { echo "[WARN] $1"; }
error() { echo "[ERROR] $1"; return 1; }
success() { echo "✓ $1"; }

# List available profiles
list_profiles() {
    echo "Available Profiles:"
    echo "=================="
    echo ""
    for profile in "${!PROFILES[@]}"; do
        echo "  $profile: ${PROFILES[$profile]}"
        echo "    Packages: ${PROFILE_PACKAGES[$profile]}"
        echo ""
    done
}

# Install profile
install_profile() {
    local profile="$1"
    
    if [[ -z "${PROFILES[$profile]:-}" ]]; then
        error "Unknown profile: $profile"
    fi
    
    log "Installing profile: $profile"
    info "Description: ${PROFILES[$profile]}"
    echo ""
    
    # Get packages for this profile
    local packages=(${PROFILE_PACKAGES[$profile]})
    
    # Install packages with stow
    for package in "${packages[@]}"; do
        if [[ -d "$DOTFILES_ROOT/$package" ]]; then
            log "Installing package: $package"
            cd "$DOTFILES_ROOT"
            stow --target="$HOME" "$package"
            success "$package installed"
        else
            warn "Package directory not found: $package"
        fi
    done
    
    # Run profile-specific npm packages if available
    local npm_script="$DOTFILES_ROOT/profile-$profile/scripts/npm-packages.sh"
    if [[ -f "$npm_script" ]]; then
        log "Installing npm packages for profile: $profile"
        bash "$npm_script" install
        success "npm packages installed for $profile profile"
    fi
    
    # Run profile-specific post-install if available
    local post_install="$DOTFILES_ROOT/profile-$profile/post-install.sh"
    if [[ -f "$post_install" ]]; then
        log "Running post-install script for profile: $profile"
        bash "$post_install"
        success "Post-install completed for $profile profile"
    fi
    
    echo ""
    success "Profile '$profile' installed successfully!"
}

# Uninstall profile
uninstall_profile() {
    local profile="$1"
    
    if [[ -z "${PROFILES[$profile]:-}" ]]; then
        error "Unknown profile: $profile"
    fi
    
    log "Uninstalling profile: $profile"
    
    # Get packages for this profile
    local packages=(${PROFILE_PACKAGES[$profile]})
    
    # Uninstall packages with stow
    for package in "${packages[@]}"; do
        if [[ -d "$DOTFILES_ROOT/$package" ]]; then
            log "Uninstalling package: $package"
            cd "$DOTFILES_ROOT"
            stow --target="$HOME" --delete "$package" 2>/dev/null || warn "Could not uninstall $package"
            success "$package uninstalled"
        fi
    done
    
    success "Profile '$profile' uninstalled"
}

# Show current installation status
show_status() {
    echo "Current Installation Status:"
    echo "==========================="
    echo ""
    
    for profile in "${!PROFILES[@]}"; do
        local packages=(${PROFILE_PACKAGES[$profile]})
        local installed_count=0
        local total_count=${#packages[@]}
        
        for package in "${packages[@]}"; do
            # Check if package is stowed (has symlinks)
            if find "$HOME" -maxdepth 2 -type l 2>/dev/null | grep -q "$DOTFILES_ROOT/$package" 2>/dev/null; then
                ((installed_count++))
            fi
        done
        
        local percentage=$((installed_count * 100 / total_count))
        echo "  $profile: $installed_count/$total_count packages ($percentage%)"
        
        if [[ $percentage -eq 100 ]]; then
            echo "    Status: ✅ Fully installed"
        elif [[ $percentage -gt 0 ]]; then
            echo "    Status: ⚠️  Partially installed"
        else
            echo "    Status: ❌ Not installed"
        fi
        echo ""
    done
}

# Show detailed symlink status for each package
show_detailed_status() {
    echo "Detailed Stow Package Status:"
    echo "============================="
    echo ""
    
    for package in $(ls -d "$DOTFILES_ROOT"/*/ 2>/dev/null | grep -v -E '(tests|docs|scripts|\..*|claudedocs)/' | xargs -n 1 basename); do
        echo "Package: $package"
        
        # Find symlinks for this package
        local symlinks=$(find "$HOME" -maxdepth 3 -type l 2>/dev/null | grep "$DOTFILES_ROOT/$package" | head -10)
        
        if [[ -n "$symlinks" ]]; then
            echo "  Status: ✅ Stowed"
            echo "  Symlinks:"
            while IFS= read -r link; do
                if [[ -n "$link" ]]; then
                    local target=$(readlink "$link" 2>/dev/null || echo "unknown")
                    local rel_source=${link#$HOME/}
                    local rel_target=${target#$DOTFILES_ROOT/}
                    echo "    ~/$rel_source -> $rel_target"
                fi
            done <<< "$symlinks"
            
            # Check for broken links
            local broken_links=$(find "$HOME" -maxdepth 3 -type l ! -exec test -e {} \; -print 2>/dev/null | grep "$DOTFILES_ROOT/$package" || true)
            if [[ -n "$broken_links" ]]; then
                echo "  ⚠️  Broken symlinks:"
                while IFS= read -r link; do
                    if [[ -n "$link" ]]; then
                        local rel_link=${link#$HOME/}
                        echo "    ~/$rel_link (broken)"
                    fi
                done <<< "$broken_links"
            fi
        else
            echo "  Status: ❌ Not stowed"
        fi
        echo ""
    done
}

# Interactive profile selection
interactive_install() {
    echo "Profile Manager - Interactive Installation"
    echo "========================================"
    echo ""
    
    list_profiles
    
    echo "Select a profile to install:"
    select profile in "${!PROFILES[@]}" "Cancel"; do
        case $profile in
            "Cancel")
                echo "Installation cancelled"
                exit 0
                ;;
            *)
                if [[ -n "$profile" ]]; then
                    install_profile "$profile"
                    break
                else
                    echo "Invalid selection, please try again"
                fi
                ;;
        esac
    done
}

# Show help
show_help() {
    cat << EOF
Profile Manager for Dotfiles

USAGE: $0 [COMMAND] [PROFILE]

COMMANDS:
    list                List available profiles
    install <profile>   Install specific profile
    uninstall <profile> Uninstall specific profile
    status              Show current installation status
    status-detailed     Show detailed symlink status for each package
    interactive         Interactive profile selection
    help                Show this help

PROFILES:
$(for profile in "${!PROFILES[@]}"; do echo "    $profile"; done)

EXAMPLES:
    $0 list                    # List all profiles
    $0 install development     # Install development profile
    $0 status                  # Check what's installed
    $0 status-detailed         # Show detailed symlink status
    $0 interactive             # Interactive selection
EOF
}

# Main function
main() {
    case "${1:-help}" in
        list)
            list_profiles
            ;;
        install)
            if [[ $# -lt 2 ]]; then
                error "Profile name required. Use '$0 list' to see available profiles."
            fi
            install_profile "$2"
            ;;
        uninstall)
            if [[ $# -lt 2 ]]; then
                error "Profile name required. Use '$0 list' to see available profiles."
            fi
            uninstall_profile "$2"
            ;;
        status)
            show_status
            ;;
        status-detailed|detailed)
            show_detailed_status
            ;;
        interactive)
            interactive_install
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $1. Run '$0 help' for usage."
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi