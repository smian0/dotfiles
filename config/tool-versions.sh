#!/usr/bin/env bash
# Tool Version Definitions
# Centralized version management for critical tools
# These versions are used by installation scripts to ensure consistency

# Core Tools
export STOW_VERSION="2.4.0"
export SHELLSPEC_VERSION="0.28.1"
export PASS_VERSION="1.7.4"

# Development Tools
export NODE_VERSION="20.11.0"  # LTS version
export PYTHON_VERSION="3.12.1"
export RUBY_VERSION="3.3.0"
export GO_VERSION="1.21.6"
export RUST_VERSION="1.75.0"

# Shell Tools
export ZSH_VERSION="5.9"
export BASH_VERSION="5.2"
export FISH_VERSION="3.7.0"

# CLI Tools
export FZF_VERSION="0.45.0"
export RIPGREP_VERSION="14.1.0"
export BAT_VERSION="0.24.0"
export EZA_VERSION="0.17.3"
export DELTA_VERSION="0.16.5"
export DIRENV_VERSION="2.34.0"
export STARSHIP_VERSION="1.17.1"

# Container Tools
export DOCKER_VERSION="24.0.7"
export DOCKER_COMPOSE_VERSION="2.24.1"
export PODMAN_VERSION="4.8.3"

# Cloud Tools
export AWSCLI_VERSION="2.15.10"
export AZURE_CLI_VERSION="2.56.0"
export GCLOUD_VERSION="460.0.0"
export TERRAFORM_VERSION="1.7.0"
export KUBECTL_VERSION="1.29.1"
export HELM_VERSION="3.14.0"

# Database Tools
export POSTGRESQL_VERSION="16"
export MYSQL_VERSION="8.2"
export REDIS_VERSION="7.2"
export MONGODB_VERSION="7.0"

# Editor Tools
export NEOVIM_VERSION="0.9.5"
export EMACS_VERSION="29.2"
export VSCODE_VERSION="latest"  # Uses latest stable

# Git Tools
export GIT_VERSION="2.43.0"
export GH_CLI_VERSION="2.42.1"
export GITUI_VERSION="0.25.1"
export LAZYGIT_VERSION="0.40.2"

# Monitoring Tools
export HTOP_VERSION="3.3.0"
export BTOP_VERSION="1.3.0"
export NCDU_VERSION="2.3"

# Network Tools
export CURL_VERSION="8.5.0"
export WGET_VERSION="1.21.4"
export HTTPIE_VERSION="3.2.2"

# Build Tools
export CMAKE_VERSION="3.28.1"
export MAKE_VERSION="4.4.1"
export NINJA_VERSION="1.11.1"

# Package Managers
export HOMEBREW_VERSION="4.2.5"
export NPM_VERSION="10.3.0"
export YARN_VERSION="1.22.21"
export PNPM_VERSION="8.14.3"
export CARGO_VERSION="1.75.0"
export COMPOSER_VERSION="2.6.6"

# Testing Tools
export JEST_VERSION="29.7.0"
export PYTEST_VERSION="7.4.4"
export RSPEC_VERSION="3.13.0"

# Functions to check and install specific versions

# Check if a tool version matches the expected version
check_version() {
    local tool="$1"
    local expected="$2"
    local current="$3"
    
    if [[ "$current" == "$expected"* ]]; then
        echo "✓ $tool version $current matches expected $expected"
        return 0
    else
        echo "⚠ $tool version mismatch: current=$current, expected=$expected"
        return 1
    fi
}

# Get version variable for a tool
get_tool_version() {
    local tool="$1"
    local var_name="${tool^^}_VERSION"
    var_name="${var_name//-/_}"  # Replace hyphens with underscores
    echo "${!var_name}"
}

# Install tool with specific version using Homebrew
install_with_version_brew() {
    local formula="$1"
    local version="$2"
    
    if [[ -z "$version" ]] || [[ "$version" == "latest" ]]; then
        brew install "$formula"
    else
        # Try to install specific version if available
        if brew list --versions "$formula" | grep -q "$version"; then
            brew install "${formula}@${version}"
        else
            # Fall back to latest with warning
            echo "Warning: Specific version $version not available for $formula, installing latest"
            brew install "$formula"
        fi
    fi
}

# Install tool with specific version using apt
install_with_version_apt() {
    local package="$1"
    local version="$2"
    
    if [[ -z "$version" ]] || [[ "$version" == "latest" ]]; then
        sudo apt-get install -y "$package"
    else
        # Try to install specific version if available
        if apt-cache show "${package}=${version}*" &>/dev/null; then
            sudo apt-get install -y "${package}=${version}*"
        else
            # Fall back to latest with warning
            echo "Warning: Specific version $version not available for $package, installing latest"
            sudo apt-get install -y "$package"
        fi
    fi
}

# Install Node.js with specific version using nvm
install_node_version() {
    local version="${NODE_VERSION}"
    
    if command -v nvm &>/dev/null; then
        nvm install "$version"
        nvm use "$version"
        nvm alias default "$version"
    elif command -v n &>/dev/null; then
        n "$version"
    else
        echo "Warning: Neither nvm nor n found, cannot install specific Node.js version"
    fi
}

# Install Python with specific version using pyenv
install_python_version() {
    local version="${PYTHON_VERSION}"
    
    if command -v pyenv &>/dev/null; then
        pyenv install -s "$version"
        pyenv global "$version"
    else
        echo "Warning: pyenv not found, cannot install specific Python version"
    fi
}

# Install Ruby with specific version using rbenv
install_ruby_version() {
    local version="${RUBY_VERSION}"
    
    if command -v rbenv &>/dev/null; then
        rbenv install -s "$version"
        rbenv global "$version"
    elif command -v rvm &>/dev/null; then
        rvm install "$version"
        rvm use "$version" --default
    else
        echo "Warning: Neither rbenv nor rvm found, cannot install specific Ruby version"
    fi
}

# Export function to be used by other scripts
export -f check_version
export -f get_tool_version
export -f install_with_version_brew
export -f install_with_version_apt
export -f install_node_version
export -f install_python_version
export -f install_ruby_version