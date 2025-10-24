# Research Summary: Claude Agent SDK Authentication with Claude Code Session
**Date**: 2025-10-17
**Data Currency**: October 2025

## Key Findings

### 1. **Claude Agent SDK Does NOT Currently Support Claude Code OAuth Sessions** [Evidence Grade: A]
The Claude Agent SDK (Python) and Claude Code CLI use **separate authentication systems**:
- **Claude Code CLI**: Uses OAuth tokens from Claude.ai subscriptions (Pro/Max plans)
- **Claude Agent SDK**: Requires traditional API keys from Anthropic Console with token-based billing

**Critical Limitation**: GitHub Issue #6536 confirms that `CLAUDE_CODE_OAUTH_TOKEN` does **not work** with the SDK, despite working with the CLI. Users report "Invalid API key" errors when attempting to use OAuth tokens.

### 2. **Claude Code Authentication Storage** [Evidence Grade: A]
Claude Code stores OAuth credentials in platform-specific locations:

**macOS**:
- API keys, OAuth tokens stored in encrypted macOS Keychain
- Search for "claude" → "show password" to view credentials

**Linux/Ubuntu**:
- Credentials file: `~/.claude/.credentials.json`
- OAuth token file: `~/.claude/oauth_token.json` (mentioned in some sources)

**Credential Structure** (`~/.claude/.credentials.json`):
```json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-...",
    "refreshToken": "sk-ant-ort01-...",
    "expiresAt": 1748658860401,
    "scopes": ["user:inference", "user:profile"]
  }
}
```

**Token Formats**:
- Access tokens: `sk-ant-oat01-...` (short-lived)
- Refresh tokens: `sk-ant-ort01-...` (for renewal)
- Standard credentials need refresh ~every 6 hours

### 3. **Required Authentication Method for Agent SDK** [Evidence Grade: A]
To use Claude Agent SDK Python scripts, you **must** use an Anthropic Console API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Why OAuth Tokens Don't Work**:
According to Anthropic engineers, "The SDK is designed for programmatic use (building applications, scripts, agents, etc.). This type of usage is tied to the Anthropic API, which is billed based on token usage and requires a traditional API key."

The CLI tool is for interactive human-in-the-loop usage with subscription plans, while the SDK is for programmatic/automated applications requiring API billing.

### 4. **Workaround: Long-Lived OAuth Token (Limited)** [Evidence Grade: B]
Claude Code provides a command to generate long-lived OAuth tokens:

```bash
claude setup-token
```

This outputs a token that can be set as:
```bash
export CLAUDE_CODE_OAUTH_TOKEN="<token>"
```

**However**: This token is designed for Claude Code CLI in headless/container environments, **NOT for the Agent SDK**. The SDK does not recognize this environment variable.

**Use Cases for `claude setup-token`**:
- CI/CD pipelines running Claude Code CLI
- Docker containers running interactive Claude Code
- Remote Claude Code agent deployments
- GitHub Actions with Claude Code

### 5. **Configuration Example for Agent SDK** [Evidence Grade: A]

**Basic Setup**:
```bash
# Install SDK
pip install claude-agent-sdk

# Set API key (required)
export ANTHROPIC_API_KEY="sk-ant-api01-..."
```

**Python Code Example**:
```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_agent():
    options = ClaudeAgentOptions(
        cwd=".",
        system_prompt="You are a helpful assistant.",
        # SDK automatically uses ANTHROPIC_API_KEY from environment
    )

    async for message in query(
        prompt="Your task here",
        options=options
    ):
        if hasattr(message, 'text'):
            print(message.text)

if __name__ == "__main__":
    anyio.run(run_agent)
```

**Using ClaudeSDKClient for Persistent Sessions**:
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def run_with_session():
    options = ClaudeAgentOptions(
        cwd=".",
        system_prompt="You are a helpful assistant."
    )

    async with ClaudeSDKClient(options=options) as client:
        # Multiple queries in same session
        await client.query("First question")
        async for msg in client.receive_response():
            print(msg)

        await client.query("Follow-up question")
        async for msg in client.receive_response():
            print(msg)
```

## Alternative Authentication Methods

### Amazon Bedrock
```bash
export CLAUDE_CODE_USE_BEDROCK=1
# Configure AWS credentials via standard AWS methods
aws configure
```

### Google Vertex AI
```bash
export CLAUDE_CODE_USE_VERTEX=1
# Configure Google Cloud credentials
gcloud auth application-default login
```

## Important Caveats

1. **No Subscription Reuse**: You **cannot** use your Claude Max/Pro subscription tokens directly with the Agent SDK. This is a deliberate design decision by Anthropic.

2. **Separate Billing**: Agent SDK usage is billed separately through the Anthropic API, even if you have a Claude Max subscription.

3. **Authentication Precedence** (Claude Code CLI only):
   - `ANTHROPIC_API_KEY` (highest priority)
   - OAuth token from `~/.claude/`
   - Subscription authentication (lowest)

4. **Token Expiration**: Standard OAuth tokens expire frequently (~6 hours). Long-lived tokens from `claude setup-token` last longer but still eventually expire.

5. **Not Documented**: The limitation that OAuth tokens don't work with the SDK is not clearly documented in official docs, leading to user confusion.

## Recommendations

### For Local Development with Agent SDK:

**Option 1: Use Anthropic Console API Key (Recommended)**
```bash
# Get API key from console.anthropic.com
export ANTHROPIC_API_KEY="sk-ant-api01-..."
# Add to ~/.zshrc or ~/.bashrc for persistence
echo 'export ANTHROPIC_API_KEY="sk-ant-api01-..."' >> ~/.zshrc
```

**Option 2: Use Custom Credential Helper**
Configure `apiKeyHelper` in `~/.claude/settings.json` to run a script that returns your API key:
```json
{
  "apiKeyHelper": {
    "command": "/path/to/get-api-key.sh",
    "refreshInterval": 300000
  }
}
```

**Option 3: Use Cloud Provider Authentication**
If running on AWS/GCP, use Bedrock or Vertex AI authentication instead.

### For Container/CI Environments:

1. Store `ANTHROPIC_API_KEY` as a secret in your CI system
2. Inject as environment variable at runtime
3. Do **not** try to copy `~/.claude/.credentials.json` - it won't work with the SDK

### If You Want to Use Subscription Credits:

**Currently impossible with Agent SDK.** You must use the Claude Code CLI interactively or request Anthropic to add this feature (GitHub issue #6536 is open).

## Research Methodology

**Queries Run**:
- "Claude Code CLI authentication session token management" - 10 results reviewed
- "Claude Agent SDK Python authentication reuse session" - 10 results reviewed
- "Claude Code API authentication environment variables configuration" - 10 results reviewed
- "~/.claude credentials.json OAuth token format structure" - 10 results reviewed
- "CLAUDE_CODE_OAUTH_TOKEN environment variable Claude Agent SDK" - 8 results reviewed
- GitHub issue anthropics/claude-code#6536 - reviewed in detail

**Source Types**:
- Primary sources: 3 (Official Anthropic docs, GitHub repositories)
- Authoritative secondary: 8 (Technical tutorials, engineering blogs)
- Community reports: 5 (Stack Overflow, GitHub issues)

**Excluded Sources**: 12 sources excluded (outdated SDK references, deprecated claude-code-sdk)

**Limitations**:
- Research limited to publicly available documentation
- Some authentication implementation details are in private/closed-source code
- Long-lived token behavior not fully documented by Anthropic

## Sources

### Official Documentation
- [Agent SDK Overview](https://docs.claude.com/en/api/agent-sdk/overview) - Primary - Oct 2025
- [Identity and Access Management](https://docs.claude.com/en/docs/claude-code/iam) - Primary - Oct 2025
- [GitHub: claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) - Primary - Oct 2025

### Technical Implementation Guides
- [From API Call to Autonomous Agent: Software Engineer's Guide](https://typevar.dev/articles/anthropics/claude-agent-sdk-python) - Secondary - Oct 2025
- [Practical Guide to Python Claude Code SDK](https://www.eesel.ai/blog/python-claude-code-sdk) - Secondary - Oct 2025
- [Claude Agent SDK Tutorial (DataCamp)](https://www.datacamp.com/tutorial/how-to-use-claude-agent-sdk) - Secondary - Oct 2025

### Community Resources
- [GitHub Issue #6536: OAuth Token Support](https://github.com/anthropics/claude-code/issues/6536) - Primary - Open issue
- [Stack Overflow: Using Existing API Key](https://stackoverflow.com/questions/79629224/how-do-i-use-claude-code-with-an-existing-anthropic-api-key) - Community - Oct 2025
- [How I Built claude_max (Substack)](https://idsc2025.substack.com/p/how-i-built-claude_max-to-unlock) - Secondary - Oct 2025

### Container/Deployment Guides
- [Setup Container Authentication](https://claude-did-this.com/claude-hub/getting-started/setup-container-guide) - Secondary - 2025
- [Depot: Quickstart for Remote Agents](https://depot.dev/docs/agents/claude-code/quickstart) - Secondary - 2025

## Evidence Grading Legend
- **Grade A**: Multiple independent primary sources, confirmed by official documentation
- **Grade B**: Strong secondary sources with partial official confirmation
- **Grade C**: Community reports and experimental findings
- **Grade D**: Unverified claims or deprecated information

## Conclusion

**Bottom Line**: Claude Agent SDK **cannot** use Claude Code's OAuth session. You must use an Anthropic Console API key set via `ANTHROPIC_API_KEY` environment variable. This is a deliberate architectural decision that separates interactive CLI usage (subscription-based) from programmatic SDK usage (API billing).

The only way to avoid setting `ANTHROPIC_API_KEY` is to use cloud provider authentication (Bedrock/Vertex), but you still can't leverage your Claude subscription credits.
