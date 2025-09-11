# OpenCode AI Integration

This repository uses OpenCode to provide AI-powered assistance directly in GitHub issues and pull requests.

## Usage

Comment on any issue or PR with:
- `/oc <your request>` - Short command
- `/opencode <your request>` - Full command

## Examples

### Code Analysis
- `/oc explain this issue`
- `/opencode review this PR`
- `/oc analyze the security implications`

### Code Fixes
- `/oc fix this bug`
- `/opencode improve error handling`
- `/oc add tests for this function`

### Documentation
- `/oc explain how this works`
- `/opencode document this function`
- `/oc summarize the changes`

## Configuration

The workflow is configured in `.github/workflows/opencode.yml` with:
- **Model**: `ollamat/gpt-oss:120b` (Ollama Turbo)
- **Permissions**: Full write access for automatic fixes
- **Trigger**: Issue comments containing `/oc` or `/opencode`

## Secrets Required

- `OLLAMA_API_KEY` - API key for Ollama service

## Alternative Models

See `.github/workflows/opencode-examples.yml` for configurations with:
- Anthropic Claude
- OpenAI GPT
- Groq
- Fireworks AI
- Local Ollama models

## Testing

1. Create a new issue
2. Comment with `/oc explain this repository`
3. OpenCode will analyze and respond

## Security

- API keys are stored as GitHub secrets
- OpenCode runs in isolated GitHub Actions environment
- All changes create PRs for review (unless configured otherwise)