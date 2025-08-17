# AI Tools Integration Guide

This guide covers the AI assistant tools integrated into the Zsh environment, making Kimi AI and ChatGLM available across all machines through the dotfiles system.

## 🤖 Available AI Assistants

### Kimi AI (Moonshot)
- **Command**: `kimi 'your question'`
- **Provider**: Moonshot AI
- **Model**: moonshot-v1-8k
- **Best for**: General assistance, Chinese language tasks

### ChatGLM
- **Command**: `glm 'your question'`  
- **Provider**: Zhipu AI
- **Model**: glm-4
- **Best for**: Code generation, analysis, Chinese language

### Claude Code CLI
- **Command**: `ai claude 'your question'`
- **Provider**: Anthropic (via Claude Code)
- **Best for**: Code analysis, development tasks

## 🚀 Quick Start

### Setup AI Tools
```bash
# Check AI tools status
ai-status

# Interactive setup (first time only)
ai-setup

# Store API keys securely
pass insert api/kimi    # Enter your Kimi API key
pass insert api/glm     # Enter your GLM API key
```

### Basic Usage
```bash
# Direct AI assistant calls
kimi 'Explain how git rebase works'
glm 'Write a Python function to calculate fibonacci'

# Unified AI interface
ai kimi 'What is the weather today?'
ai glm 'Generate a shell script to backup files'
ai claude 'Review this code for security issues'

# Quick aliases
ask kimi 'your question'
askimi 'your question'
askglm 'your question'
```

## 🔧 Configuration

### API Key Sources (Priority Order)
1. **Pass store** (recommended): `pass show api/kimi`
2. **Environment variables**: `$KIMI_API_KEY`, `$GLM_API_KEY`

### Secure Storage with Pass
```bash
# Store API keys (encrypted with GPG)
pass insert api/kimi
pass insert api/glm

# View stored keys
pass show api/kimi
pass show api/glm

# List all API keys
pass ls api/
```

### Environment Variables (Alternative)
```bash
# Add to ~/.zshrc.local for machine-specific config
export KIMI_API_KEY="your-kimi-api-key"
export GLM_API_KEY="your-glm-api-key"
```

## 📚 Commands Reference

### AI Functions
| Command | Description | Example |
|---------|-------------|---------|
| `kimi 'question'` | Ask Kimi AI directly | `kimi 'Explain Docker containers'` |
| `glm 'question'` | Ask ChatGLM directly | `glm 'Write a Python class'` |
| `ai <service> 'question'` | Unified AI interface | `ai kimi 'Help with Git'` |
| `ai help` | Show available services | `ai help` |

### Setup & Management
| Command | Description | Usage |
|---------|-------------|-------|
| `ai-setup` | Interactive API key setup | `ai-setup` |
| `ai-status` | Check tools and dependencies | `ai-status` |
| `ask` | Alias for `ai` command | `ask kimi 'question'` |
| `askimi` | Alias for `kimi` | `askimi 'question'` |
| `askglm` | Alias for `glm` | `askglm 'question'` |

## 🔐 Security Features

### Encrypted Storage
- API keys stored encrypted in pass password store
- GPG-based encryption with your personal key
- No plain-text secrets in shell history or files

### Secure Transmission
- HTTPS API calls to AI providers
- Bearer token authentication
- No key exposure in process lists

### Multi-Machine Sync
- Pass store synced via Git submodule
- Same encrypted keys available on all machines
- Automatic fallback to environment variables

## 🛠 Installation & Deployment

### Automatic Installation
The AI tools are automatically installed when you deploy the zsh package:

```bash
# Deploy zsh configuration (includes AI tools)
cd ~/workspaces/mac-dotfiles-secrets/dotfiles
stow --target=$HOME zsh

# Or use the master installer
./install-master.sh
```

### Dependencies
Required dependencies are automatically installed:
- **jq** - JSON parsing for API responses
- **curl** - HTTP requests to AI services
- **pass** - Secure password storage

### Manual Installation
```bash
# Install dependencies
brew install jq curl  # macOS
sudo apt install jq curl  # Ubuntu

# Source the configuration
source ~/.zshrc

# Run setup
ai-setup
```

## 🧪 Testing

### Test AI Tools
```bash
# Check status
ai-status

# Test each service
kimi 'Hello, how are you?'
glm 'What is 2+2?'
ai help

# Test with different prompts
kimi 'Explain the difference between git merge and rebase'
glm 'Write a bash function to count files in a directory'
```

### Troubleshooting
```bash
# Check dependencies
command -v jq && echo "jq available" || echo "jq missing"
command -v curl && echo "curl available" || echo "curl missing"

# Check API keys
pass show api/kimi
pass show api/glm

# Test API endpoints manually
curl -s "https://api.moonshot.cn/v1/models" \
  -H "Authorization: Bearer $(pass show api/kimi)"
```

## 🌐 API Provider Information

### Getting API Keys

#### Kimi AI (Moonshot)
1. Visit: https://platform.moonshot.cn/
2. Create account and verify
3. Go to API Keys section
4. Generate new API key
5. Store with: `pass insert api/kimi`

#### ChatGLM (Zhipu AI)
1. Visit: https://open.bigmodel.cn/
2. Create account and verify
3. Go to API Keys section  
4. Generate new API key
5. Store with: `pass insert api/glm`

### Rate Limits & Pricing
- **Kimi AI**: Check platform.moonshot.cn for current rates
- **ChatGLM**: Check open.bigmodel.cn for current rates
- Both services offer free tiers for testing

## 🔄 Updates & Maintenance

### Updating AI Tools
```bash
# Pull latest dotfiles
cd ~/workspaces/mac-dotfiles-secrets
git pull --recurse-submodules

# Re-deploy zsh configuration
cd dotfiles
stow --restow --target=$HOME zsh
```

### Rotating API Keys
```bash
# Update stored keys
pass edit api/kimi
pass edit api/glm

# Or insert new keys
pass insert api/kimi --force
pass insert api/glm --force
```

## 💡 Usage Tips

### Effective Prompting
```bash
# Be specific with requests
kimi 'Explain how to use git stash with specific files'
glm 'Write a Python function that reads CSV and returns pandas DataFrame'

# Use context in conversations
kimi 'I have a React app. How do I add TypeScript?'
glm 'For the TypeScript React app, how do I add routing?'
```

### Combining with Other Tools
```bash
# Use with pipes
echo "def fibonacci(n): pass" | glm 'Complete this Python function'

# Use in scripts
result=$(kimi 'What is the best way to handle errors in bash?')
echo "$result" > error_handling_tips.txt
```

### Shell Integration
```bash
# Add to functions
function explain() {
    kimi "Explain this command: $*"
}

# Use in aliases
alias explainlast='kimi "Explain this command: $(history | tail -1 | cut -d" " -f4-)"'
```

## 🤝 Contributing

### Adding New AI Services
1. Edit `zsh/.zshrc` and add new function
2. Update `ai()` function with new service
3. Add to `ai-setup` and `ai-status` functions
4. Update this documentation
5. Test thoroughly and commit

### Improving Existing Integration
- Enhance error handling
- Add response caching
- Improve prompt templates
- Add conversation context

---

**Happy AI-assisted development! 🤖✨**