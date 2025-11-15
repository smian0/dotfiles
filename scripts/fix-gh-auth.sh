#!/usr/bin/env bash
# Fix GitHub CLI authentication by removing GITHUB_TOKEN and using gh native auth

set -euo pipefail

echo "🔧 Fixing GitHub CLI authentication..."
echo ""

# Step 1: Clear GITHUB_TOKEN from all locations
echo "1️⃣ Clearing GITHUB_TOKEN from environment..."
unset GITHUB_TOKEN 2>/dev/null || true
launchctl unsetenv GITHUB_TOKEN 2>/dev/null || true
echo "   ✓ GITHUB_TOKEN cleared"
echo ""

# Step 2: Logout of gh to clear any cached credentials
echo "2️⃣ Logging out of GitHub CLI..."
gh auth logout --hostname github.com 2>/dev/null || echo "   (no existing session)"
echo ""

# Step 3: Check for SSH keys
echo "3️⃣ Checking for SSH keys..."
if [[ -f ~/.ssh/id_ed25519.pub ]] || [[ -f ~/.ssh/id_rsa.pub ]]; then
    echo "   ✓ SSH keys found"
    USE_SSH=true
else
    echo "   ⚠️  No SSH keys found - will use HTTPS"
    USE_SSH=false
fi
echo ""

# Step 4: Guide user through gh auth login
echo "4️⃣ Ready to authenticate with GitHub CLI"
echo ""
echo "Please run the following command in your terminal:"
echo ""
if [[ "$USE_SSH" == "true" ]]; then
    echo "   gh auth login --git-protocol ssh --web"
else
    echo "   gh auth login --git-protocol https --web"
fi
echo ""
echo "This will:"
echo "  • Use your existing SSH keys (if available)"
echo "  • Store credentials securely in gh's keychain"
echo "  • Remove dependency on GITHUB_TOKEN environment variable"
echo ""
echo "After logging in, verify with:"
echo "   gh auth status"
echo ""
