#!/bin/bash

# Claude Code SSH Authentication Fix
# 
# Problem: Claude Code works locally but fails with "Invalid API key" over SSH
# Root Cause: Empty ANTHROPIC_API_KEY="" variables interfere with OAuth authentication
# Solution: Remove conflicting empty API key environment variables
#
# Usage: ./fix-claude-ssh-auth.sh
# 
# This script will:
# 1. Remove empty ANTHROPIC_API_KEY exports from shell configs
# 2. Remove empty CLAUDE_OAUTH_TOKEN exports from shell configs  
# 3. Clean up any conflicting authentication scripts

set -e

echo "🔧 Fixing Claude Code SSH Authentication Issue..."
echo ""

# Function to backup file before modification
backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "📋 Backed up: $file"
    fi
}

# Function to remove conflicting environment variables
remove_conflicting_vars() {
    local file="$1"
    local changes_made=false
    
    if [ -f "$file" ]; then
        echo "🔍 Checking: $file"
        
        # Remove empty ANTHROPIC_API_KEY exports
        if grep -q 'export ANTHROPIC_API_KEY=""' "$file"; then
            backup_file "$file"
            sed -i.tmp '/export ANTHROPIC_API_KEY=""/d' "$file"
            rm -f "${file}.tmp"
            echo "  ✅ Removed empty ANTHROPIC_API_KEY"
            changes_made=true
        fi
        
        # Remove empty CLAUDE_OAUTH_TOKEN exports  
        if grep -q 'export CLAUDE_OAUTH_TOKEN=""' "$file"; then
            backup_file "$file"
            sed -i.tmp '/export CLAUDE_OAUTH_TOKEN=""/d' "$file"
            rm -f "${file}.tmp"
            echo "  ✅ Removed empty CLAUDE_OAUTH_TOKEN"
            changes_made=true
        fi
        
        # Remove lines that just set empty values
        if grep -q 'ANTHROPIC_API_KEY=$' "$file"; then
            backup_file "$file"
            sed -i.tmp '/ANTHROPIC_API_KEY=$/d' "$file"
            rm -f "${file}.tmp"
            echo "  ✅ Removed empty ANTHROPIC_API_KEY assignment"
            changes_made=true
        fi
        
        if ! $changes_made; then
            echo "  ✓ No conflicting variables found"
        fi
    else
        echo "  ⚠️  File not found: $file"
    fi
    echo ""
}

# Check common shell configuration files
echo "🧹 Cleaning shell configuration files..."
echo ""

remove_conflicting_vars "$HOME/.zshrc"
remove_conflicting_vars "$HOME/.zshenv"  
remove_conflicting_vars "$HOME/.bashrc"
remove_conflicting_vars "$HOME/.profile"
remove_conflicting_vars "$HOME/.bash_profile"

# Remove any custom OAuth setup scripts that might be interfering
echo "🗑️  Cleaning up conflicting scripts..."
if [ -f "$HOME/.claude_oauth_setup.sh" ]; then
    backup_file "$HOME/.claude_oauth_setup.sh"
    rm "$HOME/.claude_oauth_setup.sh"
    echo "✅ Removed conflicting OAuth setup script"
else
    echo "✓ No conflicting OAuth setup scripts found"
fi
echo ""

# Verify current environment
echo "🔍 Checking current environment..."
if [ -n "$ANTHROPIC_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY is currently set to empty value"
    echo "💡 You may need to restart your shell or run: unset ANTHROPIC_API_KEY"
elif [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "ℹ️  ANTHROPIC_API_KEY is currently set to: ${ANTHROPIC_API_KEY:0:10}..."
else
    echo "✅ ANTHROPIC_API_KEY is not set (good!)"
fi

if [ -n "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
    echo "✅ CLAUDE_CODE_OAUTH_TOKEN is present: ${CLAUDE_CODE_OAUTH_TOKEN:0:20}..."
else
    echo "⚠️  CLAUDE_CODE_OAUTH_TOKEN not found"
    echo "💡 You may need to run 'claude /login' or restart your shell"
fi
echo ""

echo "🎉 Claude Code SSH authentication fix completed!"
echo ""
echo "📝 Next steps:"
echo "   1. Restart your shell or run: source ~/.zshrc"
echo "   2. Test Claude Code over SSH: ssh your-remote-host"
echo "   3. If still not working, run: claude /login"
echo ""
echo "🔧 What this fixed:"
echo "   • Removed empty ANTHROPIC_API_KEY variables that blocked OAuth"
echo "   • Claude Code can now use CLAUDE_CODE_OAUTH_TOKEN properly"
echo "   • SSH sessions should work the same as local terminals"
echo ""
echo "📖 For more details, see: ~/dotfiles/docs/claude-ssh-auth-fix.md"