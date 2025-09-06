# Package Configuration Guide

This guide provides detailed information about each configuration package in the dotfiles repository.

## Table of Contents

| Package Category | Packages | Purpose |
|------------------|----------|---------|
| **[Core System](#core-system-packages)** | git, zsh, vim, ssh | Essential system configuration |
| **[AI Integration](#ai-integration-packages)** | claude, claude-project, cursor | AI-powered development |
| **[Security](#security-packages)** | pass, pass-store | Encrypted credential management |
| **[Development](#development-packages)** | npm-configs, direnv | Development environment |
| **[Automation](#automation-packages)** | chrome-automation, scripts | Workflow automation |

---

## Core System Packages

### 📝 Git Package (`git/`)

**Installation**: `make install-git` or included in all profiles

#### Configuration Structure
```
git/
├── .gitconfig              # Global Git configuration
├── .gitignore_global       # Global ignore patterns
└── hooks/
    ├── pre-commit          # Secret detection hook
    └── commit-msg          # Commit message validation
```

#### Key Features

| Feature | Implementation | Benefit |
|---------|----------------|---------|
| **GPG Signing** | Automatic commit signing | Cryptographic verification |
| **Secret Detection** | Pre-commit hooks | Prevents credential leaks |
| **Global Ignores** | Cross-project ignore patterns | Consistent exclusions |
| **Custom Aliases** | Productivity shortcuts | Faster workflows |

#### Configuration Details

**Core Settings**:
```bash
# Essential git configuration
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global commit.gpgsign true
git config --global core.excludesfile ~/.gitignore_global
```

**Security Hooks**:
- **pre-commit**: Scans for API keys, private keys, passwords
- **commit-msg**: Validates commit message format
- **post-commit**: Optional security logging

**Custom Aliases**:
```bash
git st          # status
git co          # checkout  
git br          # branch
git unstage     # reset HEAD
git last        # log -1 HEAD
git visual      # gitk
```

#### Integration Points
- **Pass Integration**: Uses pass for GitHub tokens
- **SSH Integration**: Coordinates with SSH package for key management
- **Claude Integration**: Git context for AI assistance

---

### 🐚 Zsh Package (`zsh/`)

**Installation**: `make install-zsh` or included in all profiles

#### Configuration Structure
```
zsh/
├── .zshrc                  # Main shell configuration
├── llm-tools.zsh          # AI tool integrations
├── agents-md.zsh          # Agent framework support
├── ssh-agent.zsh          # SSH key management
├── completions/           # Custom completions
└── functions/             # Custom shell functions
```

#### Key Features

| Component | Purpose | Integration |
|-----------|---------|-------------|
| **AI Tools** | Claude, ChatGPT, API access | Environment variables from pass |
| **SSH Agent** | Automatic key loading | GitHub, server authentication |
| **Agents Framework** | Directory-based agents | AGENTS.md file processing |
| **Custom Functions** | Productivity utilities | Project management shortcuts |

#### AI Tools Integration (`llm-tools.zsh`)

**Available Commands**:
```bash
# Claude API access
claude "Your question here"
claude-code                 # Claude Code CLI

# OpenAI integration  
gpt "Your prompt"
gpt4 "Complex reasoning task"

# API key management
load-api-keys              # Load from pass
check-api-status           # Verify key availability
```

**Environment Setup**:
```bash
# Automatic API key loading
export OPENAI_API_KEY=$(pass api/openai 2>/dev/null)
export ANTHROPIC_API_KEY=$(pass api/anthropic 2>/dev/null)
export CLAUDE_API_KEY=$(pass api/claude 2>/dev/null)
```

#### SSH Agent Management (`ssh-agent.zsh`)

**Features**:
- Automatic SSH agent startup
- GitHub key auto-loading
- Cross-session agent persistence
- Key availability verification

**Implementation**:
```bash
# Auto-start SSH agent
if [ -z "$SSH_AGENT_PID" ]; then
    eval $(ssh-agent -s)
    ssh-add ~/.ssh/id_ed25519 2>/dev/null
    ssh-add ~/.ssh/id_rsa 2>/dev/null
fi
```

#### Agents Framework (`agents-md.zsh`)

**Purpose**: Directory-specific AI agent configuration

**Usage**:
```bash
cd /path/to/project
# Automatically loads .claude/AGENTS.md if present
# Provides context-aware AI assistance
```

**File Structure**:
```markdown
# AGENTS.md
## Project Context
Brief description of the project...

## Key Commands
- make build
- make test
- make deploy

## Development Notes
Important patterns and conventions...
```

---

### 📄 Vim Package (`vim/`)

**Installation**: `make install-vim` or included in full/personal profiles

#### Configuration Structure
```
vim/
├── .vimrc                 # Main Vim configuration
├── .vim/
│   ├── colors/           # Color schemes
│   ├── plugin/           # Plugin configurations
│   └── ftplugin/         # File-type specific settings
└── README.md             # Vim-specific documentation
```

#### Key Features

| Feature | Description | Keybinding |
|---------|-------------|------------|
| **Syntax Highlighting** | Multi-language support | Automatic |
| **Line Numbers** | Relative and absolute | `set number relativenumber` |
| **Search Enhancement** | Incremental, highlighted | `/pattern` |
| **Split Navigation** | Easy window movement | `Ctrl+w` + direction |
| **Plugin Support** | Extensible architecture | Via `.vimrc` |

#### Configuration Highlights

**Core Settings**:
```vim
" Essential Vim improvements
set number relativenumber    " Line numbers
set tabstop=4 shiftwidth=4  " 4-space indentation
set expandtab               " Use spaces instead of tabs
set hlsearch incsearch      " Enhanced search
set wildmenu                # Command completion
```

**File Type Support**:
- **Shell scripts**: Enhanced highlighting and formatting
- **Markdown**: Improved editing experience
- **JSON/YAML**: Syntax validation and formatting
- **Git commits**: Specialized editing mode

---

### 🔐 SSH Package (`ssh/`)

**Installation**: `make install-ssh` or included in specific profiles

#### Configuration Structure
```
ssh/
├── .ssh/
│   ├── config            # SSH client configuration
│   ├── known_hosts       # Verified host keys
│   └── authorized_keys   # Public key authentication
└── README.md             # SSH-specific documentation
```

#### Key Features

| Feature | Implementation | Security Benefit |
|---------|----------------|------------------|
| **Host Configurations** | Per-host settings | Tailored security levels |
| **Key Management** | Automated key selection | Proper key usage |
| **Security Hardening** | Modern cipher selection | Enhanced protection |
| **Connection Optimization** | Multiplexing, compression | Improved performance |

#### Sample Configuration
```bash
# GitHub configuration
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    
# Server configuration
Host myserver
    HostName server.example.com
    User myuser
    Port 2222
    IdentityFile ~/.ssh/id_rsa_server
    ServerAliveInterval 60
```

---

## AI Integration Packages

### 🤖 Claude Package (`claude/`)

**Installation**: `make install-claude` or included in most profiles

#### Configuration Structure
```
claude/
├── .claude/
│   ├── settings.json         # Global Claude preferences
│   ├── commands/            # Custom AI commands
│   ├── output-styles/       # Response formatting
│   └── CLAUDE_BEST_PRACTICES.md
└── README.md
```

#### Global Settings (`settings.json`)

```json
{
  "model": "claude-3-5-sonnet-20241022",
  "temperature": 0.1,
  "maxTokens": 4096,
  "allowedTools": [
    "Edit",
    "Read", 
    "Bash(git *)",
    "Bash(npm *)",
    "WebFetch",
    "WebSearch"
  ],
  "environmentVariables": {
    "EDITOR": "vim",
    "PAGER": "less"
  }
}
```

#### Output Styles

| Style | Purpose | Use Case |
|-------|---------|----------|
| **table-based** | Structured data presentation | Analysis reports |
| **bullet-points** | Concise information | Quick references |
| **markdown-focused** | Documentation generation | README files |
| **ultra-concise** | Minimal output | Code reviews |
| **yaml-structured** | Configuration files | System configs |

#### Custom Commands

**Development Commands**:
```markdown
# /debug
Analyze and debug the current codebase issue.

Steps:
1. Examine error logs
2. Check recent changes
3. Identify root cause
4. Suggest solutions
```

**Project Commands**:
```markdown
# /deploy
Deploy the current project to staging.

Requirements:
- Run tests first
- Build optimized version
- Deploy with health checks
```

---

### 🎯 Claude Project Package (`claude-project/`)

**Installation**: `./scripts/deploy-claude-project.sh <project_path>`

#### Configuration Structure
```
claude-project/
├── .claude/
│   ├── settings.json         # Project-specific settings
│   ├── settings.local.json   # Personal project preferences
│   ├── commands/            # Project commands
│   ├── agents/              # Project agents
│   └── output-styles/       # Custom styles
├── CLAUDE.md                # Project guidance
└── AGENTS.md                # Agent configurations
```

#### Project Settings Example
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "allowedTools": [
    "Edit",
    "Read",
    "Bash(npm run *)",
    "Bash(docker *)",
    "mcp__task_master_ai__*"
  ],
  "environmentVariables": {
    "NODE_ENV": "development",
    "PROJECT_ROOT": "."
  }
}
```

#### Project Guidance (CLAUDE.md)
- Project architecture and patterns
- Coding conventions and standards  
- Common commands and workflows
- Integration points and dependencies

---

## Security Packages

### 🔒 Pass Package (`pass/`)

**Installation**: `make install-pass` or included in full/personal profiles

#### Features

| Component | Purpose | Security Level |
|-----------|---------|----------------|
| **GPG Integration** | Password encryption | Military-grade |
| **Git Sync** | Cross-device synchronization | Encrypted transport |
| **API Management** | Development key storage | Secure environment injection |
| **Team Sharing** | Selective secret sharing | Fine-grained access |

#### Configuration Structure
```
pass/
├── .password-store/         # Encrypted password database
│   ├── api/                # API keys
│   ├── services/           # Service credentials  
│   ├── personal/           # Personal accounts
│   └── .gpg-id             # GPG key identifier
└── README.md
```

#### Usage Patterns
```bash
# API key management
pass insert api/openai       # Store OpenAI API key
pass insert api/github       # Store GitHub token
pass api/openai             # Retrieve for use

# Environment integration
export OPENAI_API_KEY=$(pass api/openai)

# Git synchronization
pass git push               # Sync to remote
pass git pull               # Get updates
```

---

## Development Packages

### 📦 NPM Configs Package (`npm-configs/`)

**Installation**: Included in development-focused profiles

#### Configuration Files
```
npm-configs/
├── .npmrc                  # NPM client configuration
├── package.json           # Global packages
└── scripts/
    └── npm-packages.sh    # Installation automation
```

#### Global Packages by Profile

| Package | Minimal | Development | Full | Purpose |
|---------|---------|-------------|------|---------|
| **@anthropic-ai/claude-cli** | ✅ | ✅ | ✅ | Claude Code CLI |
| **typescript** | ❌ | ✅ | ✅ | TypeScript support |
| **nodemon** | ❌ | ✅ | ✅ | Development server |
| **http-server** | ❌ | ✅ | ✅ | Simple HTTP server |
| **npm-check-updates** | ❌ | ✅ | ✅ | Dependency updates |

---

### 🌍 Direnv Package (`direnv/`)

**Installation**: `make install-direnv`

#### Purpose
Automatic environment variable loading per directory.

#### Configuration
```bash
# .envrc example
export PROJECT_NAME="myproject"
export NODE_ENV="development"
export DATABASE_URL="postgresql://localhost/myproject_dev"

# Load API keys from pass
export OPENAI_API_KEY=$(pass api/openai)
```

#### Integration
- **Automatic activation**: Changes directory → loads environment
- **Security**: Prevents accidental environment leaks
- **Development**: Project-specific configurations

---

## Automation Packages

### 🌐 Chrome Automation Package (`chrome-automation/`)

**Installation**: Included in full profile only

#### Features
- **Chrome Keeper Service**: Maintains browser state
- **LaunchDaemon**: macOS service management
- **Automation Scripts**: Browser control utilities

#### Configuration Structure
```
chrome-automation/
├── Library/LaunchDaemons/   # macOS service configuration
├── scripts/                # Automation utilities
├── chrome-keeper.sh        # Main service script
└── README.md
```

#### Use Cases
- **Development**: Automated testing and debugging
- **Productivity**: Browser state management
- **Integration**: CI/CD browser automation

---

### 📋 Scripts Package (`scripts/`)

**Core Utility Scripts**

| Script | Purpose | Usage |
|--------|---------|-------|
| **api-key-manager.sh** | API key management | `./scripts/api-key-manager.sh add openai` |
| **backup-restore.sh** | Configuration backup | `./scripts/backup-restore.sh backup` |
| **deploy-claude-project.sh** | Claude deployment | `./scripts/deploy-claude-project.sh .` |
| **profile-manager.sh** | Profile management | `./scripts/profile-manager.sh status` |
| **validate-config.sh** | Configuration validation | `./scripts/validate-config.sh --audit` |

#### MCP Environment Management
```
scripts/mcp-env/
├── README.md              # Quick start guide
├── setup-mcp-env.sh      # Environment setup
├── sync-api-keys.sh      # Key synchronization
└── validate-mcp.sh       # MCP validation
```

**Purpose**: Streamlined MCP server setup with secure credential management.

---

## Package Dependencies

### 🔗 Dependency Matrix

| Package | Dependencies | Optional Dependencies |
|---------|--------------|----------------------|
| **git** | GPG (for signing) | pass (for tokens) |
| **zsh** | - | pass (for API keys) |
| **claude** | - | git (for project context) |
| **pass** | GPG | git (for sync) |
| **ssh** | - | pass (for key passphrases) |

### 🚀 Installation Order

1. **System Dependencies**: GPG, Git, Stow
2. **Security Foundation**: pass, GPG setup
3. **Core Packages**: git, zsh
4. **AI Integration**: claude packages
5. **Development Tools**: npm-configs, direnv
6. **Optional Features**: vim, chrome-automation

---

## Customization Guide

### 📝 Adding New Packages

1. **Create Package Directory**
   ```bash
   mkdir new-package
   cd new-package
   ```

2. **Add Configuration Files**
   ```bash
   # Follow home directory structure
   mkdir -p .config/newapp
   cp config-file .config/newapp/
   ```

3. **Update Installation**
   ```bash
   # Add to Makefile
   install-newpackage:
       stow new-package
   
   # Add to profile
   echo "new-package" >> profiles/development.txt
   ```

4. **Test Installation**
   ```bash
   make install-newpackage
   make test
   ```

### 🔧 Modifying Existing Packages

1. **Backup Current Config**
   ```bash
   make backup
   ```

2. **Edit Package Files**
   ```bash
   # Edit configuration
   vim package-name/.config/app/config
   ```

3. **Test Changes**
   ```bash
   # Dry run
   stow --no --verbose package-name
   
   # Apply changes
   stow --restow package-name
   ```

4. **Validate**
   ```bash
   make test-quick
   make status
   ```

---

*This package guide is part of the comprehensive dotfiles documentation. For setup instructions, see [SETUP.md](SETUP.md). For security configuration, see [SECURITY.md](SECURITY.md).*