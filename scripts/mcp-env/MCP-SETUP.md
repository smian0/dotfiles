# MCP Environment Management - Complete Guide

**🚀 Secure, shell-independent credential management for MCP servers using GPG-encrypted pass store.**

## 🎯 **Overview**

This comprehensive setup provides automatic, secure credential management for MCP (Model Context Protocol) servers using:

- **🔐 GPG-encrypted pass store** for secure credential storage
- **🖥️ System-wide environment variables** via `launchctl setenv` (truly shell-independent!)
- **⚡ Automatic credential loading** on login via LaunchAgent
- **📋 Configuration-driven** via simple `env-mapping.conf` file
- **🚫 Zero shell dependencies** - works across all processes, terminals, and apps

## 🚀 **Quick Start**

### **1. Install LaunchAgent**
```bash
# Copy LaunchAgent to system location
cp scripts/mcp-env/com.mcp.env.agent.plist ~/Library/LaunchAgents/

# Load the agent
launchctl load ~/Library/LaunchAgents/com.mcp.env.agent.plist
```

### **2. Add Credentials to Pass**
```bash
# Add API keys
pass insert api/openai
pass insert api/anthropic
pass insert api/brave
pass insert api/github-demo

# Add LLM service keys
pass insert llm/ollama_turbo_key
pass insert llm/deepseek_api_key
pass insert llm/glm_api_key
pass insert llm/kimi_api_key
```

### **3. Test Setup**
```bash
# Run script manually to test
./scripts/mcp-env/set-mcp-env-system.sh

# Verify environment variables
launchctl getenv OPENAI_API_KEY
```

## 🏗️ **Architecture & How It Works**

### **Complete Flow**
```
env-mapping.conf → Pass Store (GPG) → LaunchAgent → System Environment → MCP Servers
       ↓               ↓                ↓              ↓                ↓
   Simple Config   Encrypted        Auto-runs      Variables Set    Direct Access
   (You Edit)      Credentials      on Login      System-wide      No Changes
```

### **1. Configuration-Driven Setup**
All environment variable mappings are defined in `env-mapping.conf`:
```bash
# Simple key=value format
OPENAI_API_KEY=api/openai
BRAVE_API_KEY=api/brave
GITHUB_TOKEN=api/github-demo
```

### **2. System-Level Environment Variables**
Uses `launchctl setenv` to set environment variables at the user level that persist across:
- **Terminal sessions** - Available in all shells
- **Application launches** - GUI apps can access them
- **System reboots** - Reloaded automatically on login
- **MCP server processes** - No shell sourcing required

### **3. Automatic Execution via LaunchAgent**
A LaunchAgent (`com.mcp.env.agent.plist`) runs the script:
- **On login** - Sets environment variables when you log in
- **Every hour** - Refreshes credentials (in case they change)
- **Daily at midnight** - Ensures fresh credentials

### **4. MCP Server Access**
MCP servers automatically read these environment variables:
- **Node.js**: `process.env.OPENAI_API_KEY`
- **Python**: `os.environ.get('OPENAI_API_KEY')`
- **Docker**: `-e OPENAI_API_KEY=$OPENAI_API_KEY`
- **Any process**: `getenv("OPENAI_API_KEY")`

### **5. Security Features**
- **GPG encryption** for all credentials
- **User-level isolation** - no credential leakage to other users  
- **Automatic cleanup** on logout
- **30-day caching** via GPG agent
- **No plain text storage** of sensitive data

## 📋 **Available Credentials**

| Environment Variable | Pass Path | Description | Status |
|---------------------|-----------|-------------|---------|
| `OPENAI_API_KEY` | `api/openai` | OpenAI API key | ⚠️ Not set |
| `ANTHROPIC_API_KEY` | `api/anthropic` | Anthropic API key | ⚠️ Not set |
| `GITHUB_TOKEN` | `api/github-demo` | GitHub personal access token | ✅ Set |
| `BRAVE_API_KEY` | `api/brave` | Brave Search API key | ✅ Set |
| `SUPABASE_ACCESS_TOKEN` | `api/supabase` | Supabase access token | ⚠️ Not set |
| `MAGIC_API_KEY` | `api/magic` | Magic MCP API key | ⚠️ Not set |
| `AGENTQL_API_KEY` | `api/agentql` | AgentQL API key | ⚠️ Not set |
| `OLLAMA_API_KEY` | `llm/ollama_turbo_key` | Ollama API key | ✅ Set |
| `DEEPSEEK_API_KEY` | `llm/deepseek_api_key` | DeepSeek API key | ✅ Set |
| `GLM_API_KEY` | `llm/glm_api_key` | ChatGLM API key | ✅ Set |
| `KIMI_API_KEY` | `llm/kimi_api_key` | Kimi API key | ✅ Set |
| `JIRA_API_TOKEN` | `services/jira` | Jira API token | ⚠️ Not set |
| `N8N_API_KEY` | `services/n8n` | N8N API key | ⚠️ Not set |

## 🛠️ **Configuration**

### **MCP Server Setup**
Your MCP servers should reference environment variables in their configuration:

```json
{
  "mcpServers": {
    "Brave Search": {
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "command": "npx",
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

### **Environment Variable Reference**
- **Node.js**: `process.env.VARIABLE_NAME`
- **Python**: `os.environ.get('VARIABLE_NAME')`
- **Docker**: `-e VARIABLE_NAME=$VARIABLE_NAME`
- **Shell**: `$VARIABLE_NAME`

## 🔄 **Management Commands**

### **LaunchAgent Control**
```bash
# Check status
launchctl list | grep mcp

# Reload agent
launchctl unload ~/Library/LaunchAgents/com.mcp.env.agent.plist
launchctl load ~/Library/LaunchAgents/com.mcp.env.agent.plist
```

### **Environment Variables**
```bash
# Set variable
launchctl setenv VARIABLE_NAME "value"

# Get variable
launchctl getenv VARIABLE_NAME

# Unset variable
launchctl unsetenv VARIABLE_NAME
```

### **Pass Store Management**
```bash
# List credentials
pass ls

# Add new credential
pass insert path/to/credential

# Edit credential
pass edit path/to/credential

# Remove credential
pass rm path/to/credential
```

## ➕ **Adding New Credentials**

```bash
# 1. Add credential to pass store
pass insert api/newservice

# 2. Add mapping to configuration file
echo "NEW_SERVICE_API_KEY=api/newservice" >> scripts/mcp-env/env-mapping.conf

# 3. Reload environment variables
./scripts/mcp-env/set-mcp-env-system.sh

# 4. Verify it worked
bash scripts/mcp-env/status.sh
```

## 🧪 **Testing & Verification**

### **1. Test Environment Variables**
```bash
# Check if variables are set system-wide
launchctl getenv OPENAI_API_KEY
launchctl getenv GITHUB_TOKEN

# Verify they're available in new processes
env | grep OPENAI_API_KEY

# Check status of all credentials
bash scripts/mcp-env/status.sh
```

### **2. Test MCP Server Access**
```bash
# Test Brave Search (example)
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "brave_web_search", "arguments": {"query": "test", "count": 1}}}' | npx -y @modelcontextprotocol/server-brave-search

# Or test with a simple command
node -e "console.log('OpenAI Key:', process.env.OPENAI_API_KEY)"
```

### **3. Test Cross-Session Persistence**
```bash
# Open a new terminal
# Environment variables should be available without any sourcing
env | grep OPENAI_API_KEY

# Test that MCP servers work in new processes
npx -y @modelcontextprotocol/server-brave-search
```

## 🚨 **Comprehensive Troubleshooting**

### **Environment Variables Not Set**
```bash
# Check LaunchAgent status
launchctl list | grep mcp

# If agent isn't running, reload it
launchctl unload ~/Library/LaunchAgents/com.mcp.env.agent.plist
launchctl load ~/Library/LaunchAgents/com.mcp.env.agent.plist

# Check logs for errors
cat /tmp/mcp-env-agent.log
cat /tmp/mcp-env-agent.error.log

# Run script manually to test
./scripts/mcp-env/set-mcp-env-system.sh

# Verify specific variables
launchctl getenv OPENAI_API_KEY
launchctl getenv GITHUB_TOKEN
```

### **Credentials Not Loading from Pass**
```bash
# Verify pass is working
pass ls

# Test credential retrieval
pass show api/github-demo

# Check GPG setup
gpg --list-secret-keys

# Test GPG agent
gpg-agent --version

# Check if GPG agent is running
ps aux | grep gpg-agent
```

### **LaunchAgent Issues**
```bash
# Check if LaunchAgent file exists
ls -la ~/Library/LaunchAgents/com.mcp.env.agent.plist

# Verify LaunchAgent syntax
plutil -lint ~/Library/LaunchAgents/com.mcp.env.agent.plist

# Check LaunchAgent status
launchctl list | grep mcp

# Force reload LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.mcp.env.agent.plist
launchctl load ~/Library/LaunchAgents/com.mcp.env.agent.plist
```

### **MCP Server Issues**
```bash
# Verify environment variable is set
launchctl getenv VARIABLE_NAME

# Test if current shell has the variable
env | grep VARIABLE_NAME

# Export variable to current shell if needed
export VARIABLE_NAME=$(launchctl getenv VARIABLE_NAME)

# Test server manually
npx -y server-package-name

# Check server logs for environment variable errors
```

### **Configuration File Issues**
```bash
# Check if config file exists
ls -la scripts/mcp-env/env-mapping.conf

# Verify config file format
cat scripts/mcp-env/env-mapping.conf

# Check for syntax errors (no spaces around =)
grep -E '^\s*[A-Z_]+=\S+' scripts/mcp-env/env-mapping.conf
```

## 📁 **File Structure**

```
dotfiles/
├── scripts/
│   └── mcp-env/                    # MCP environment management
│       ├── env-mapping.conf        # Environment variable mappings (EDIT THIS!)
│       ├── set-mcp-env-system.sh   # Sets environment variables system-wide
│       ├── status.sh               # Environment status checker
│       ├── com.mcp.env.agent.plist # LaunchAgent configuration
│       ├── README.md               # Quick-start guide
│       └── MCP-SETUP.md           # This comprehensive guide
├── ~/Library/LaunchAgents/
│   └── com.mcp.env.agent.plist    # Installed LaunchAgent
└── cursor/.cursor/
    └── mcp.json                   # MCP server configuration
```



## 🔄 **Advanced Management Commands**

### **Environment Variable Management**
```bash
# Set a variable manually
launchctl setenv VARIABLE_NAME "value"

# Get a variable
launchctl getenv VARIABLE_NAME

# Unset a variable
launchctl unsetenv VARIABLE_NAME

# Check all MCP-related variables
launchctl getenv OPENAI_API_KEY
launchctl getenv GITHUB_TOKEN
launchctl getenv OLLAMA_API_KEY
```

### **Configuration Management**
```bash
# Edit credential mappings
vim scripts/mcp-env/env-mapping.conf

# Check environment status
bash scripts/mcp-env/status.sh

# Reload all environment variables
./scripts/mcp-env/set-mcp-env-system.sh
```

### **Pass Store Advanced Commands**
```bash
# List all credentials with tree view
pass ls

# Edit existing credential
pass edit api/openai

# Generate a random password
pass generate api/newservice 32

# Copy credential to clipboard
pass -c api/openai

# Search for credentials
pass find github
```

## 📚 **Best Practices & Security**

### **✅ Recommended Practices**
1. **🔒 Install LaunchAgent once** - It will run automatically on every login
2. **📝 Keep credentials updated** - Use pass to manage and rotate API keys regularly
3. **📊 Monitor system health** - Check `/tmp/mcp-env-agent.log` for issues periodically
4. **🧪 Test thoroughly** - Always verify MCP servers can access credentials after changes
5. **🔐 Secure your pass store** - Keep your GPG keys safe and backed up
6. **💾 Regular backups** - Backup your pass store with `pass git push` if using git backend
7. **📋 Use status checker** - Run `bash scripts/mcp-env/status.sh` to monitor credential health

### **🔒 Security Considerations**
- **GPG encryption** protects all credentials at rest
- **User-level isolation** prevents credential leakage to other system users
- **No plain text storage** of sensitive data anywhere on disk
- **Automatic cleanup** removes environment variables on logout
- **Master password required** - GPG keys protect pass store access
- **30-day GPG caching** - Convenient but secure with automatic expiration

## 🔗 **Related Documentation**

- **[Quick Start Guide](README.md)** - Fast setup and basic usage
- **[Pass Store Workflow](../../PASSWORD-STORE-WORKFLOW.md)** - GPG & pass setup guide  
- **[GPG Setup](../../docs/GPG-SETUP.md)** - Complete GPG configuration
- **[Cursor MCP Configuration](../../cursor/README.md)** - Cursor-specific MCP setup

---

**✨ This is the complete, enterprise-grade solution for MCP server credential management - secure, automatic, and truly shell-independent!**
