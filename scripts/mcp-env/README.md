# MCP Environment Management

**🚀 Shell-independent credential management for MCP servers using GPG-encrypted pass store.**

> **All-in-one solution**: Automatic system-wide environment variables that MCP servers read directly, without shell dependencies or manual configuration.

## 🎯 **What This Does**

- **🔐 Secure**: GPG-encrypted credential storage via `pass`
- **🖥️ System-wide**: Environment variables available to all processes
- **⚡ Automatic**: Runs on login, refreshes credentials periodically
- **🚫 No shell required**: Works across terminals, apps, and processes
- **✨ Zero MCP changes**: Keep your configuration files exactly as they are

## 🚀 **Quick Setup (3 Steps)**

### **1. Install System Service**
```bash
# Copy LaunchAgent to system location
cp scripts/mcp-env/com.mcp.env.agent.plist ~/Library/LaunchAgents/

# Load the agent (runs automatically on login)
launchctl load ~/Library/LaunchAgents/com.mcp.env.agent.plist
```

### **2. Add Your API Keys**
```bash
# Store credentials in encrypted pass store
pass insert api/openai        # OpenAI API key
pass insert api/brave         # Brave Search API key
pass insert api/github-demo   # GitHub Personal Access Token
pass insert llm/ollama_turbo_key  # Ollama API key

# Add more as needed...
```

### **3. Test & Verify**
```bash
# Run setup script manually (first time)
./scripts/mcp-env/set-mcp-env-system.sh

# Verify credentials are available system-wide
launchctl getenv OPENAI_API_KEY
launchctl getenv BRAVE_API_KEY

# Your MCP servers now have automatic access!
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

## 🏗️ **Architecture**

```
env-mapping.conf → Pass Store (GPG) → LaunchAgent → System Environment → MCP Servers
       ↓               ↓                ↓              ↓                ↓
   Simple Config   Encrypted        Auto-runs      Variables Set    Direct Access
   (You Edit)      Credentials      on Login      System-wide      No Changes
```

## 📋 **Supported Credentials**

| Environment Variable | Pass Path | Service |
|---------------------|-----------|---------|
| `OPENAI_API_KEY` | `api/openai` | OpenAI |
| `ANTHROPIC_API_KEY` | `api/anthropic` | Anthropic |
| `BRAVE_API_KEY` | `api/brave` | Brave Search |
| `GITHUB_TOKEN` | `api/github-demo` | GitHub |
| `OLLAMA_API_KEY` | `llm/ollama_turbo_key` | Ollama |
| `DEEPSEEK_API_KEY` | `llm/deepseek_api_key` | DeepSeek |
| `GLM_API_KEY` | `llm/glm_api_key` | ChatGLM |
| `KIMI_API_KEY` | `llm/kimi_api_key` | Kimi |
| `SUPABASE_ACCESS_TOKEN` | `api/supabase` | Supabase |
| `JIRA_API_TOKEN` | `services/jira` | Jira |
| `N8N_API_KEY` | `services/n8n` | N8N |
| `MAGIC_API_KEY` | `api/magic` | Magic MCP |
| `AGENTQL_API_KEY` | `api/agentql` | AgentQL |

## 🛠️ **MCP Configuration**

Your MCP servers reference environment variables (no hardcoded secrets):

```json
{
  "mcpServers": {
    "Brave Search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

## 📁 **Package Contents**

```
scripts/mcp-env/
├── README.md                   # 📖 This quick-start guide
├── MCP-SETUP.md               # 📚 Complete setup & troubleshooting guide
├── env-mapping.conf           # ⚙️ Simple credential mappings (EDIT THIS!)
├── set-mcp-env-system.sh      # 🚀 Main environment script  
├── status.sh                  # 📊 Environment status checker
└── com.mcp.env.agent.plist    # ⚙️ macOS LaunchAgent config
```

## 🧪 **Testing Your Setup**

```bash
# Check system-wide environment variables
launchctl getenv OPENAI_API_KEY
launchctl getenv GITHUB_TOKEN

# Test in current shell
env | grep -E "(OPENAI|BRAVE|GITHUB)_API_KEY"

# Test MCP server directly
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "brave_web_search", "arguments": {"query": "test", "count": 1}}}' | npx -y @modelcontextprotocol/server-brave-search
```

## 🔒 **Security Features**

- **🔐 GPG Encryption**: All credentials encrypted with your GPG key
- **👤 User Isolation**: Variables only available to your user account  
- **🧹 Auto Cleanup**: Credentials cleared on logout
- **⏰ 30-day Caching**: GPG agent caches master password securely
- **📝 No Plain Text**: Zero persistent plain text credential storage

## 🔄 **Management Commands**

```bash
# Configuration management
vim scripts/mcp-env/env-mapping.conf   # Edit credential mappings
bash scripts/mcp-env/status.sh         # Check environment status

# LaunchAgent control
launchctl list | grep mcp              # Check status
launchctl unload ~/Library/LaunchAgents/com.mcp.env.agent.plist  # Stop
launchctl load ~/Library/LaunchAgents/com.mcp.env.agent.plist    # Start

# Environment variables
launchctl getenv VARIABLE_NAME         # Get variable
launchctl setenv VARIABLE_NAME "value" # Set variable
launchctl unsetenv VARIABLE_NAME       # Remove variable

# Pass store management
pass ls                                 # List all credentials
pass show api/openai                   # View specific credential
pass insert api/newservice             # Add new credential
pass edit api/existing                 # Edit existing credential
```

## 🚨 **Troubleshooting**

**Environment variables not set?**
```bash
# Check LaunchAgent status
launchctl list | grep mcp

# Check logs for errors
cat /tmp/mcp-env-agent.log
cat /tmp/mcp-env-agent.error.log

# Run script manually to debug
./scripts/mcp-env/set-mcp-env-system.sh
```

**Pass not working?**
```bash
# Test pass functionality
pass ls
pass show api/github-demo

# Check GPG setup
gpg --list-secret-keys
```

## 📚 **Complete Documentation**

- **[MCP-SETUP.md](MCP-SETUP.md)** - Comprehensive setup, configuration, and troubleshooting guide
- **[Pass Workflow](../../PASSWORD-STORE-WORKFLOW.md)** - GPG & pass setup guide

---

**✨ That's it!** Your MCP servers now have secure, automatic access to all the credentials they need, without any shell dependencies or configuration changes.
