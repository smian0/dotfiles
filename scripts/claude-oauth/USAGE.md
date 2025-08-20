# Claude OAuth Token Generator

This utility generates OAuth tokens for Claude Code authentication. It's a standalone version that can be run manually to obtain access tokens.

## Quick Start

```bash
cd scripts/claude-oauth
bun install
bun run oauth
```

## Installation

1. Ensure you have [Bun](https://bun.sh) installed
2. Install dependencies:
   ```bash
   cd scripts/claude-oauth
   bun install
   ```

## Usage

### Interactive Token Generation (Recommended)

```bash
# Generate login URL and exchange code interactively
bun run oauth

# Or use the shell script version
./scripts/generate-token.sh
```

### Manual Steps

```bash
# Step 1: Generate login URL
bun run index.ts

# Step 2: Open URL in browser, get authorization code from callback
# Step 3: Exchange code for tokens
bun run index.ts <authorization_code>
```

## Files Generated

- `credentials.json` - Contains your OAuth access/refresh tokens
- `claude_oauth_state.json` - Temporary state file (auto-cleaned)

## Security Notes

- Never commit `credentials.json` to version control
- Tokens expire - use the refresh token to get new access tokens
- Keep your credentials secure and treat them like passwords

## Token Usage

After generating tokens, you'll have a `credentials.json` file with:
```json
{
  "claudeAiOauth": {
    "accessToken": "...",
    "refreshToken": "...",
    "expiresAt": 1234567890000,
    "scopes": ["user:inference", "user:profile"],
    "isMax": true
  }
}
```

Use these tokens for Claude API authentication or with Claude Code's OAuth mode.

## ⚠️ Known Issues

**OAuth + Max Plan Bug**: Currently there's a bug where OAuth tokens don't properly recognize Max plan subscriptions, causing Opus model access to be denied. See `KNOWN_ISSUES.md` for details and workarounds.

To test if this bug is fixed, run:
```bash
./test_oauth_model_access.sh
```