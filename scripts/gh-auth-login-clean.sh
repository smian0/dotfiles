#!/usr/bin/env bash
# Run gh auth login without GITHUB_TOKEN environment variable

set -euo pipefail

echo "🔐 Running gh auth login without GITHUB_TOKEN..."
echo ""

# Run gh auth login in a clean environment without GITHUB_TOKEN
env -u GITHUB_TOKEN gh auth login --git-protocol ssh --web

echo ""
echo "✅ Authentication complete!"
echo ""
echo "Verifying authentication status:"
env -u GITHUB_TOKEN gh auth status
