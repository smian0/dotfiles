#!/bin/bash

# Claude OAuth Quick Reference Script
# Provides quick access to common Claude credential operations

show_help() {
    echo "🔐 Claude OAuth Quick Reference"
    echo "=============================="
    echo
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  keychain         Show Claude keychain entry details"
    echo "  password         Copy Claude password to clipboard (prompts for Mac password)"
    echo "  show-password    Display Claude password in terminal (prompts for Mac password)"
    echo "  find-keychain    Search for Claude entries in keychain"
    echo "  open-keychain    Open Keychain Access app"
    echo "  env-tokens       Show current environment OAuth tokens"
    echo "  generate         Generate new OAuth token"
    echo "  test-oauth       Test OAuth authentication bug"
    echo "  help             Show this help message"
    echo
    echo "Files:"
    echo "  KEYCHAIN_ACCESS.md  - Detailed keychain access guide"
    echo "  KNOWN_ISSUES.md     - OAuth bug tracking"
    echo "  USAGE.md           - General usage instructions"
}

case "${1:-help}" in
    "keychain"|"info")
        echo "🔍 Claude Keychain Entry Information:"
        echo "====================================="
        security find-generic-password -s "Claude Code-credentials" -a "smian" 2>/dev/null || {
            echo "❌ Claude keychain entry not found"
            echo "💡 Try: $0 find-keychain"
        }
        ;;
    
    "password"|"copy")
        echo "🔐 Copying Claude password to clipboard..."
        echo "   (You'll be prompted for your Mac password)"
        security find-generic-password -s "Claude Code-credentials" -a "smian" -w | pbcopy 2>/dev/null && {
            echo "✅ Password copied to clipboard!"
        } || {
            echo "❌ Failed to copy password"
            echo "💡 Make sure the keychain entry exists: $0 keychain"
        }
        ;;
    
    "show-password"|"show")
        echo "🔐 Claude Password:"
        echo "=================="
        echo "   (You'll be prompted for your Mac password)"
        security find-generic-password -s "Claude Code-credentials" -a "smian" -g 2>/dev/null || {
            echo "❌ Failed to retrieve password"
            echo "💡 Check keychain entry: $0 keychain"
        }
        ;;
    
    "find-keychain"|"search")
        echo "🔍 Searching for Claude entries in keychain..."
        echo "============================================="
        security dump-keychain 2>/dev/null | grep -i "claude" -A 3 -B 1 || {
            echo "❌ No Claude entries found in keychain"
        }
        ;;
    
    "open-keychain"|"open")
        echo "🔑 Opening Keychain Access..."
        open -a "Keychain Access"
        echo "💡 Look in 'login' keychain → 'All Items' → search 'Claude'"
        ;;
    
    "env-tokens"|"env")
        echo "🌍 Current Environment OAuth Tokens:"
        echo "==================================="
        echo "CLAUDE_CODE_OAUTH_TOKEN: $([ -n "$CLAUDE_CODE_OAUTH_TOKEN" ] && echo "${CLAUDE_CODE_OAUTH_TOKEN:0:20}..." || echo "Not set")"
        echo "ANTHROPIC_API_KEY: $([ -n "$ANTHROPIC_API_KEY" ] && echo "${ANTHROPIC_API_KEY:0:20}..." || echo "Not set")"
        ;;
    
    "generate"|"oauth")
        echo "🚀 Launching OAuth token generator..."
        bun run oauth
        ;;
    
    "test-oauth"|"test")
        echo "🧪 Running OAuth authentication test..."
        ./test_oauth_model_access.sh
        ;;
    
    "help"|"-h"|"--help")
        show_help
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac