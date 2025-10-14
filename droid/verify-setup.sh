#!/usr/bin/env bash

# Droid Configuration Verification Script
# This script verifies your droid configuration setup

echo "🔍 Verifying Droid Configuration Setup"
echo "======================================"

# Check if stow package exists
if [[ -d "$HOME/dotfiles/droid" ]]; then
    echo "✅ Droid stow package found"
else
    echo "❌ Droid stow package not found"
    exit 1
fi

# Check if config.json exists
if [[ -f "$HOME/dotfiles/droid/.factory/config.json" ]]; then
    echo "✅ Config file exists in stow package"
    
    # Test JSON syntax
    if python3 -m json.tool "$HOME/dotfiles/droid/.factory/config.json" > /dev/null 2>&1; then
        echo "✅ Config JSON is valid"
    else
        echo "❌ Config JSON has syntax errors"
        exit 1
    fi
else
    echo "❌ Config file not found"
    exit 1
fi

# Check if ~/.factory/config.json exists
if [[ -f "$HOME/.factory/config.json" ]]; then
    echo "✅ Active config file exists (~/.factory/config.json)"
else
    echo "⚠️  Active config file not linked (~/.factory/config.json)"
    echo "   Run: stow droid"
fi

# Check if stowed config matches package config
if diff -q "$HOME/dotfiles/droid/.factory/config.json" "$HOME/.factory/config.json" > /dev/null 2>&1; then
    echo "✅ Stowed config matches package config"
else
    echo "⚠️  Config file mismatch detected"
fi

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama server is running"
    
    # Check if models are available
    models_available=$(ollama list | grep -c "cloud" 2>/dev/null || echo "0")
    if [[ $models_available -gt 0 ]]; then
        echo "✅ Cloud models available: $models_available"
        echo ""
        echo "Available Ollama Cloud Models:"
        ollama list | grep "cloud" | sed 's/^/  • /'
    else
        echo "⚠️  No cloud models found in Ollama"
    fi
else
    echo "⚠️  Ollama server not running or not accessible"
fi

echo ""
echo "📋 Configuration Content:"
echo "========================"
cat "$HOME/dotfiles/droid/.factory/config.json" | python3 -m json.tool 2>/dev/null || cat "$HOME/dotfiles/droid/.factory/config.json"

echo ""
echo "🔧 Quick Fixes (if needed):"
echo "==========================="
echo "1. Stow package:     stow droid"
echo "2. Start Ollama:     ollama serve"
echo "3. Pull models:      ollama pull qwen3-coder:480b-cloud kimi-k2:1t-cloud deepseek-v3.1:671b-cloud"
echo "4. Test connection:  curl http://localhost:11434/api/tags"
echo ""
echo "Setup verification complete! Setup droid and use /model to see your custom models."
