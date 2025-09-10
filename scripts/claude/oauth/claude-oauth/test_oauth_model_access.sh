#!/bin/bash

# OAuth Model Access Test Script
# Tests whether the OAuth authentication bug has been fixed
# Bug: OAuth tokens don't recognize Max plan subscription (GitHub Issue #5625)

set -e

echo "🔍 Claude OAuth Model Access Test"
echo "================================="
echo
echo "Testing for GitHub Issue #5625: OAuth tokens not recognizing Max subscription"
echo

# Check if we have OAuth token
if [ -z "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
    echo "❌ No OAuth token found in environment"
    echo "💡 Generate one first with: bun run oauth"
    echo
    read -p "Would you like to generate an OAuth token now? (y/N): " generate
    
    if [[ $generate =~ ^[Yy]$ ]]; then
        echo "🚀 Launching OAuth token generator..."
        bun run oauth
        echo
        echo "⚠️  After generating token, restart this script to test"
    fi
    exit 1
fi

echo "✅ OAuth token found in environment"
echo "🔑 Token prefix: ${CLAUDE_CODE_OAUTH_TOKEN:0:20}..."
echo

# Check subscription info if possible
echo "🔍 Current Authentication Status:"
echo "   OAuth Token: ✅ Set"
echo "   API Key: $([ -n "$ANTHROPIC_API_KEY" ] && echo "✅ Set" || echo "❌ Not set")"
echo

echo "📋 Manual Test Instructions:"
echo "=============================="
echo
echo "1️⃣  Start Claude Code:"
echo "    claude"
echo
echo "2️⃣  Try to switch to Opus model:"
echo "    /model opus"
echo
echo "3️⃣  Check the result:"
echo
echo "   🔴 BUG STILL EXISTS if you see:"
echo "      'Claude Pro users are not currently able to use Opus in Claude Code'"
echo "      'The current model is now Sonnet'"
echo
echo "   🟢 BUG IS FIXED if you see:"
echo "      'Model switched to Opus' or similar success message"
echo "      No Pro user restriction warnings"
echo
echo "4️⃣  Comparison Test (Optional):"
echo "    - Exit Claude Code"
echo "    - Run: unset CLAUDE_CODE_OAUTH_TOKEN"
echo "    - Restart Claude Code and try /model opus again"
echo "    - If Opus works without token but not with token, bug still exists"
echo

echo "📊 Expected Results:"
echo "==================="
echo "• With Max Plan + Working OAuth: Opus should be available"
echo "• Current Bug: OAuth makes Max users appear as Pro users"
echo "• Workaround: Remove OAuth token to access Opus"
echo

echo "📝 Please report results by updating KNOWN_ISSUES.md"
echo "   - If FIXED: Update status to 🟢 and add fix date"
echo "   - If BROKEN: Confirm bug still exists with current date"
echo

# Check for updates
echo "🔄 Checking for Claude Code updates..."
if command -v claude &> /dev/null; then
    claude --version 2>/dev/null || echo "   Could not get Claude Code version"
else
    echo "   Claude Code not found in PATH"
fi

echo
echo "🔗 Related Links:"
echo "   • GitHub Issue: https://github.com/anthropics/claude-code/issues/5625"
echo "   • Issue #2207: https://github.com/anthropics/claude-code/issues/2207"
echo
echo "📅 Test Date: $(date)"
echo "🏁 Test completed. Please run manual verification steps above."