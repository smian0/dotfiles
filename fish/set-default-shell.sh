#!/usr/bin/env bash
# Set Fish as Default Shell
# Run this script manually to complete the fish shell setup

set -e

echo "🐟 Setting Fish as Default Shell"
echo "================================="

# Check if fish is in /etc/shells
if ! grep -q "$(which fish)" /etc/shells; then
    echo "📝 Adding fish to /etc/shells (requires password)"
    echo "$(which fish)" | sudo tee -a /etc/shells
    echo "✅ Fish added to /etc/shells"
else
    echo "✅ Fish is already in /etc/shells"
end

# Change default shell
echo ""
echo "🔧 Changing default shell to fish"
chsh -s $(which fish)

if [ $? -eq 0 ]; then
    echo "✅ Default shell changed to fish!"
    echo ""
    echo "🎉 Setup Complete!"
    echo ""
    echo "Please log out and log back in for the changes to take effect."
    echo ""
    echo "Current shell: $SHELL"
    echo "New shell: $(which fish)"
else
    echo "❌ Failed to change shell. Please try manually:"
    echo "   chsh -s $(which fish)"
fi
