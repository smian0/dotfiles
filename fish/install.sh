#!/usr/bin/env bash
# Fish Shell Installation Script
# Installs fish shell and sets up plugins

set -e

echo "🐟 Installing Fish Shell Configuration"
echo "======================================="

# Check if fish is installed
if ! command -v fish >/dev/null 2>&1; then
    echo "❌ Fish shell not found!"
    echo "Installing fish via Homebrew..."
    brew install fish
fi

echo "✅ Fish shell is installed: $(fish --version)"

# Add fish to allowed shells if not already there
if ! grep -q "$(which fish)" /etc/shells; then
    echo "📝 Adding fish to /etc/shells (requires sudo)"
    echo "$(which fish)" | sudo tee -a /etc/shells
    echo "✅ Fish added to allowed shells"
fi

# Start fish to install fisher and plugins
echo "📦 Installing fisher plugin manager and plugins..."
fish -c "
    # Install fisher if not already installed
    if not functions -q fisher
        echo '🔧 Installing fisher plugin manager...'
        curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source
        fisher install jorgebucaran/fisher
    end

    # Install plugins from fish_plugins file
    if test -f ~/.config/fish/fish_plugins
        echo '📦 Installing fish plugins...'
        fisher update
    end

    # Configure tide prompt (minimal setup, similar to robbyrussell)
    if functions -q tide
        echo '🎨 Configuring tide prompt...'
        tide configure --auto --style=Lean --prompt_colors='True color' --show_time='No' --lean_prompt_height='One line' --prompt_connection='Disconnected' --prompt_spacing='Compact' --icons='Many icons' --transient='No'
    end

    echo '✅ Fisher and plugins installed successfully!'
"

# Start SSH agent on shell start (auto-run)
if ! grep -q "start_ssh_agent" ~/.config/fish/config.fish 2>/dev/null; then
    echo ""
    echo "# Auto-start SSH agent" >> ~/.config/fish/config.fish
    echo "start_ssh_agent" >> ~/.config/fish/config.fish
    echo "✅ SSH agent auto-start enabled"
fi

echo ""
echo "🎉 Fish shell configuration installed successfully!"
echo ""
echo "Next steps:"
echo "1. Run: chsh -s \$(which fish)      # Set fish as default shell"
echo "2. Log out and log back in"
echo "3. Enjoy your new fish shell! 🐟"
echo ""
echo "Useful commands:"
echo "  - fish_config      # Open web-based configuration"
echo "  - fisher list      # List installed plugins"
echo "  - tide configure   # Reconfigure prompt"
echo ""
