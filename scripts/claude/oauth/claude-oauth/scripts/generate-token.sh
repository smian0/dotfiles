#!/bin/bash

# OAuth Token Generation Utility for Claude Code
# This script provides an interactive way to generate OAuth tokens

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🔐 Claude Code OAuth Token Generator"
echo "===================================="
echo

# Check if bun is installed
if ! command -v bun &> /dev/null; then
    echo "❌ Error: Bun is not installed. Please install Bun first:"
    echo "   curl -fsSL https://bun.sh/install | bash"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    bun install
    echo
fi

echo "🚀 Step 1: Generate OAuth Login URL"
echo "-----------------------------------"
echo "Generating login URL..."
echo

# Generate the login URL
LOGIN_URL=$(bun run index.ts)

echo "✅ OAuth login URL generated!"
echo
echo "📋 Please copy and open this URL in your browser:"
echo "   $LOGIN_URL"
echo
echo "🔗 After logging in, you'll be redirected to a callback URL."
echo "   The URL will contain a 'code' parameter. Copy that code value."
echo
echo "⏳ Waiting for your authorization code..."

# Prompt for authorization code
while true; do
    echo
    read -p "🔑 Enter the authorization code from the callback URL: " auth_code
    
    if [ -z "$auth_code" ]; then
        echo "❌ Please enter a valid authorization code."
        continue
    fi
    
    echo
    echo "🔄 Exchanging authorization code for tokens..."
    
    # Exchange the code for tokens
    if bun run index.ts "$auth_code"; then
        echo
        echo "🎉 Success! OAuth tokens have been generated and saved."
        echo "📁 Check the credentials.json file for your tokens."
        break
    else
        echo
        echo "❌ Token exchange failed. Please try again with a fresh authorization code."
        echo "   You may need to generate a new login URL if the state has expired."
        echo
        read -p "Would you like to generate a new login URL? (y/N): " retry
        
        if [[ $retry =~ ^[Yy]$ ]]; then
            echo
            echo "🚀 Generating new login URL..."
            LOGIN_URL=$(bun run index.ts)
            echo "✅ New login URL generated!"
            echo
            echo "📋 Please copy and open this URL in your browser:"
            echo "   $LOGIN_URL"
        else
            echo "❌ Token generation cancelled."
            exit 1
        fi
    fi
done

echo
echo "🔐 OAuth token generation complete!"
echo "   Your credentials are now saved in credentials.json"
echo "   Keep this file secure and do not commit it to version control."