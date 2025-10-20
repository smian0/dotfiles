# Scripts Directory

Utility scripts for dotfiles management and system configuration.

## Core Management Scripts

### **profile-manager.sh**
Profile-based installation management with support for minimal, development, work, and personal configurations.

### **os-detect.sh**
Operating system detection and environment setup utilities for macOS and Ubuntu.

### **validate-config.sh**
Configuration validation and integrity checking for symlinks and dependencies.

### **backup-restore.sh**
Complete backup and restoration system for dotfiles and configurations.

## Security & API Management

### **api-key-manager.sh**
Secure API key management using GPG-encrypted `pass` password store.

### **gpg-manager.sh**
GPG key management, backup, and multi-machine synchronization.

### **pass-manager.sh**
Password store management with Git synchronization support.

## Deployment Scripts

### **deploy-claude-project.sh**
Deploy Claude project-level configuration to specific projects.

### **deploy-claude-user.sh**
Deploy Claude user-level configuration to home directory.

### **install-by-environment.sh**
Environment-based installation with automatic profile detection.

### **fix-claude-ssh-auth.sh**
Claude Code SSH authentication issue resolution.

## MCP Configuration Tools

### **zsh/mcp-config.zsh** (Primary)
Shell functions for MCP server configuration management:
- `mcpg` - Extract global servers
- `mcpp` - Extract project servers  
- `mcpa` - Extract all servers
- `mcpls` - List available servers

### **extract-mcp-config.py** (Legacy)
Python-based MCP configuration extraction from Claude Code settings.

### **claude-mcp-extract.sh** (Legacy)
Shell wrapper for Python MCP extraction script.

## Network & Remote Access

### **configure-mosh-firewall.sh**
Configure macOS firewall to allow Mosh (Mobile Shell) connections.

**Usage:** `./configure-mosh-firewall.sh`

Features:
- Adds mosh-server to firewall allowed applications
- Configures incoming connections (UDP 60000-61000)
- Reloads firewall rules
- Verifies configuration

For detailed Mosh setup and troubleshooting, see [../docs/REMOTE-ACCESS.md](../docs/REMOTE-ACCESS.md)

## Chrome Automation Scripts

### **launch-chrome-debug.sh**
Launch Chrome with remote debugging enabled for automation via Chrome DevTools Protocol.

**Usage:** `./launch-chrome-debug.sh [PROFILE_NAME] [DEBUG_PORT] [USER_DATA_DIR]`

Features:
- Launches Chrome with CDP enabled on specified port (default 9222)
- Copies profile data to temporary directory
- Configures security flags for WebSocket connections
- Verifies successful startup and provides connection details

### **perplexity-search.sh**
Automated search on Perplexity AI using Chrome DevTools Protocol.

**Usage:** `./perplexity-search.sh "search query" [debug_port]`

Process:
1. Connects to Chrome via CDP WebSocket
2. Navigates to Perplexity.ai
3. Fills and submits search query
4. Extracts and displays results

**Prerequisites:** Chrome with remote debugging, Python 3, websocket-client package

For detailed Chrome automation documentation, see [../docs/CHROME_AUTOMATION.md](../docs/CHROME_AUTOMATION.md)

## Subdirectories

### **claude-oauth/**
OAuth 2.0 + PKCE authentication tool for Claude Code with TypeScript implementation.

## Architecture

All scripts follow standardized conventions:
- Bash shebang with error handling
- Help documentation via `--help`
- Dependency validation
- Integration with main Makefile
