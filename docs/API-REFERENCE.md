# API and Command Reference

Complete reference for all commands, scripts, and APIs in the dotfiles repository.

## Table of Contents

| Section | Description |
|---------|-------------|
| **[Makefile Commands](#makefile-commands)** | Central command interface |
| **[Installation Scripts](#installation-scripts)** | System setup and configuration |
| **[Utility Scripts](#utility-scripts)** | Management and automation tools |
| **[AI Integration APIs](#ai-integration-apis)** | Claude Code and AI tools |
| **[Security Commands](#security-commands)** | GPG, pass, and security utilities |
| **[Testing Commands](#testing-commands)** | Test execution and validation |

---

## Makefile Commands

The Makefile serves as the central command interface. All commands follow the pattern: `make <command> [VARIABLE=value]`

### 📦 End User Commands

| Command | Description | Runtime | Prerequisites |
|---------|-------------|---------|---------------|
| **`make install`** | Install default development profile | ~5 min | Git, Stow |
| **`make install-minimal`** | Install essential tools only | ~2 min | Git, Stow |
| **`make install-full`** | Install all packages | ~8 min | Git, Stow, GPG |
| **`make bootstrap`** | Complete new machine setup | ~10 min | Internet connection |
| **`make backup`** | Create configuration backup | ~30 sec | Backup directory |
| **`make restore`** | Restore from latest backup | ~1 min | Valid backup |
| **`make status`** | Show installation status | ~5 sec | - |
| **`make update`** | Update repository and tools | ~2 min | Internet connection |
| **`make help`** | Show all available commands | ~1 sec | - |

#### Usage Examples
```bash
# Quick setup
make bootstrap              # New machine setup
make install               # Default installation

# Maintenance
make backup                # Before major changes
make status                # Check current state
make update               # Keep system current

# Profile-specific installation
make install-minimal      # Server/CI setup
make install-full         # Power user setup
```

### ⚙️ Configuration Commands

| Command | Description | Parameters | Output |
|---------|-------------|------------|--------|
| **`make profile-status`** | Show current profile status | - | Installation matrix |
| **`make profile-list`** | List available profiles | - | Profile descriptions |
| **`make api-status`** | Show API key status | - | Key availability |
| **`make api-list`** | List stored API keys | - | Key names |
| **`make api-sync`** | Sync API keys with environment | - | Environment variables |
| **`make install-hooks`** | Install git security hooks | - | Hook files |
| **`make check-secrets`** | Scan for committed secrets | - | Security violations |
| **`make doctor`** | Comprehensive health check | - | System diagnostics |
| **`make audit`** | Security configuration review | - | Security assessment |

#### Configuration Examples
```bash
# Profile management
make profile-status        # Check current installation
make profile-list          # See available options

# API key management  
make api-status            # Check key availability
make api-sync              # Load keys into environment

# Security operations
make check-secrets         # Pre-commit security scan
make doctor               # Full system health check
```

### 🛠️ Developer Commands

| Command | Description | Use Case | Output Location |
|---------|-------------|----------|-----------------|
| **`make test`** | Run E2E test suite | Pre-commit validation | `tests/docker/exports/` |
| **`make test-all`** | Run all test scenarios | Pre-release validation | Test reports |
| **`make test-quick`** | Fast validation tests | Development feedback | Terminal |
| **`make lint`** | ShellCheck validation | Code quality | Terminal |
| **`make format`** | Format shell scripts | Code consistency | In-place |
| **`make demo`** | Dry-run installation | Preview changes | Terminal |
| **`make dev-setup`** | Setup development environment | Contributor onboarding | Development tools |
| **`make docs`** | Update documentation | Documentation maintenance | README.md |
| **`make export-config`** | Export configuration archive | Backup/sharing | `dotfiles-export-*.tar.gz` |

#### Development Examples
```bash
# Testing workflow
make test-quick            # Fast feedback during development
make test                  # Full validation before commit
make lint                  # Code quality check

# Development environment
make dev-setup            # Setup contributor environment
make demo                 # Preview installation changes

# Maintenance
make docs                 # Sync documentation
make export-config        # Create portable archive
```

### 🔧 Package-Specific Commands

| Command | Package | Description | Dependencies |
|---------|---------|-------------|--------------|
| **`make install-git`** | git | Git configuration only | Git |
| **`make install-zsh`** | zsh | Zsh shell setup only | Zsh |
| **`make install-vim`** | vim | Vim editor config only | Vim |
| **`make install-claude`** | claude* | Claude Code configurations | Claude CLI |

#### Package Installation Examples
```bash
# Individual package installation
make install-git          # Just Git configuration
make install-zsh          # Just Zsh setup
make install-claude       # Claude Code integration

# Verify individual packages
stow --no --verbose git   # Preview Git package
stow git                  # Apply Git configuration
```

### 🐳 Docker Testing Commands

| Command | Description | Test Scenario | Runtime |
|---------|-------------|---------------|---------|
| **`make test TEST=basic`** | Basic installation test | Minimal profile | ~2 min |
| **`make test TEST=full`** | Complete installation test | Full profile | ~5 min |
| **`make test TEST=claude`** | AI integration test | Claude setup | ~3 min |
| **`make test TEST=switch`** | Profile switching test | Profile changes | ~4 min |
| **`make test-clean`** | Clean test environment | Infrastructure cleanup | ~30 sec |

#### Docker Testing Examples
```bash
# Run specific test scenarios
make test TEST=basic      # Quick validation
make test TEST=full       # Comprehensive test

# Test environment management
make test-clean           # Clean up containers
./view-test-results.sh    # Analyze results
```

---

## Installation Scripts

### 🚀 Main Installation Script (`install.sh`)

**Purpose**: Primary installation interface with profile support

**Usage**:
```bash
./install.sh [OPTIONS] [PACKAGES...]
```

**Options**:
| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--profile <name>` | Use specific profile | `development` | `--profile minimal` |
| `--all` | Install all packages | false | `--all` |
| `--dry-run` | Preview without installing | false | `--dry-run` |
| `--verbose` | Enable verbose output | false | `--verbose` |
| `--help` | Show help message | - | `--help` |

**Examples**:
```bash
# Profile-based installation
./install.sh --profile minimal
./install.sh --profile development
./install.sh --profile full

# Package-specific installation
./install.sh git zsh claude-default

# Preview mode
./install.sh --dry-run --profile full

# Verbose installation
./install.sh --verbose --all
```

**Environment Variables**:
| Variable | Purpose | Values | Default |
|----------|---------|---------|---------|
| `DOTFILES_PROFILE` | Override profile selection | minimal, development, full, work, personal | development |
| `INSTALL_MODE` | Installation mode | interactive, automatic | interactive |
| `BACKUP_EXISTING` | Backup existing configs | true, false | true |

### 🏗️ Bootstrap Script (`install-master.sh`)

**Purpose**: Complete system setup for new machines

**Usage**:
```bash
./install-master.sh [OPTIONS]
```

**Features**:
- OS detection (macOS/Ubuntu)
- Dependency installation (Homebrew/apt)
- GPG and pass setup
- Profile installation
- Validation and testing

**Examples**:
```bash
# Complete new machine setup
./install-master.sh

# With specific profile
DOTFILES_PROFILE=full ./install-master.sh

# Automated mode (no prompts)
INSTALL_MODE=automatic ./install-master.sh
```

---

## Utility Scripts

### 🔑 API Key Manager (`scripts/api-key-manager.sh`)

**Purpose**: Secure API key management using pass

**Usage**:
```bash
./scripts/api-key-manager.sh <command> [options]
```

**Commands**:
| Command | Description | Arguments | Output |
|---------|-------------|-----------|--------|
| **`add <service>`** | Add API key for service | service name | Interactive prompt |
| **`get <service>`** | Retrieve API key | service name | API key value |
| **`list`** | List stored keys | - | Service names |
| **`test <service>`** | Test API key validity | service name | Validation result |
| **`sync`** | Sync with environment | - | Environment variables |
| **`status`** | Show key status | - | Availability matrix |

**Examples**:
```bash
# Add API keys
./scripts/api-key-manager.sh add openai
./scripts/api-key-manager.sh add anthropic
./scripts/api-key-manager.sh add github

# Retrieve and test keys
./scripts/api-key-manager.sh get openai
./scripts/api-key-manager.sh test anthropic

# Environment management
./scripts/api-key-manager.sh sync
export OPENAI_API_KEY=$(./scripts/api-key-manager.sh get openai)
```

### 💾 Backup Restore (`scripts/backup-restore.sh`)

**Purpose**: Configuration backup and restoration

**Usage**:
```bash
./scripts/backup-restore.sh <command> [options]
```

**Commands**:
| Command | Description | Options | Output Location |
|---------|-------------|---------|-----------------|
| **`backup`** | Create backup | `--include-brew`, `--exclude-secrets` | `~/.dotfiles-backups/` |
| **`restore [timestamp]`** | Restore from backup | timestamp | Home directory |
| **`list`** | List available backups | - | Backup listing |
| **`verify [timestamp]`** | Verify backup integrity | timestamp | Validation report |
| **`clean`** | Remove old backups | `--keep <n>` | Cleanup report |

**Examples**:
```bash
# Create backups
./scripts/backup-restore.sh backup                    # Standard backup
./scripts/backup-restore.sh backup --include-brew     # Include Homebrew
./scripts/backup-restore.sh backup --exclude-secrets  # Exclude pass store

# Restore operations
./scripts/backup-restore.sh list                      # Show available backups
./scripts/backup-restore.sh restore                   # Restore latest
./scripts/backup-restore.sh restore 20240315_142000   # Restore specific

# Maintenance
./scripts/backup-restore.sh verify                    # Check integrity
./scripts/backup-restore.sh clean --keep 5           # Keep 5 newest
```

### 📋 Profile Manager (`scripts/profile-manager.sh`)

**Purpose**: Installation profile management

**Usage**:
```bash
./scripts/profile-manager.sh <command> [options]
```

**Commands**:
| Command | Description | Parameters | Output |
|---------|-------------|------------|--------|
| **`list`** | Show available profiles | - | Profile descriptions |
| **`status`** | Show installation status | - | Status matrix |
| **`install <profile>`** | Install specific profile | profile name | Installation log |
| **`uninstall <profile>`** | Remove profile packages | profile name | Removal log |
| **`check`** | Validate profile configs | - | Validation report |
| **`interactive`** | Interactive profile selection | - | Installation wizard |

**Examples**:
```bash
# Profile information
./scripts/profile-manager.sh list     # Available profiles
./scripts/profile-manager.sh status   # Current installation

# Profile operations
./scripts/profile-manager.sh install development
./scripts/profile-manager.sh uninstall full
./scripts/profile-manager.sh interactive
```

### 🔧 Validation Script (`scripts/validate-config.sh`)

**Purpose**: Configuration validation and security audit

**Usage**:
```bash
./scripts/validate-config.sh [options]
```

**Options**:
| Option | Description | Scope | Output |
|--------|-------------|-------|--------|
| `--audit` | Security audit | Full system | Security report |
| `--permissions` | Check file permissions | File system | Permission report |
| `--symlinks` | Validate symlinks | Stow packages | Link status |
| `--all` | Complete validation | Everything | Comprehensive report |

**Examples**:
```bash
# Validation operations
./scripts/validate-config.sh               # Basic validation
./scripts/validate-config.sh --audit       # Security audit
./scripts/validate-config.sh --permissions # Permission check
./scripts/validate-config.sh --all        # Complete check
```

### 🚀 Deployment Scripts

#### Claude Project Deployment (`scripts/deploy-claude-project.sh`)

**Purpose**: Deploy Claude configurations to projects

**Usage**:
```bash
./scripts/deploy-claude-project.sh <project_path> [options]
```

**Options**:
| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--backup` | Create backup before deployment | true | `--no-backup` |
| `--profile <name>` | Claude profile to deploy | default | `--profile experimental` |
| `--force` | Overwrite existing config | false | `--force` |

**Examples**:
```bash
# Deploy to current project
./scripts/deploy-claude-project.sh .

# Deploy to specific project
./scripts/deploy-claude-project.sh ~/projects/myapp

# Deploy experimental profile
./scripts/deploy-claude-project.sh . --profile experimental
```

#### Claude User Deployment (`scripts/deploy-claude-user.sh`)

**Purpose**: Deploy user-level Claude configurations

**Usage**:
```bash
./scripts/deploy-claude-user.sh [options]
```

**Examples**:
```bash
# Deploy user settings
./scripts/deploy-claude-user.sh

# Force deployment (overwrite existing)
./scripts/deploy-claude-user.sh --force
```

---

## AI Integration APIs

### 🤖 Claude Code Integration

#### Shell Functions (from `zsh/llm-tools.zsh`)

**AI Command Functions**:
| Function | Purpose | Usage | Requirements |
|----------|---------|-------|--------------|
| **`claude <prompt>`** | Claude API access | `claude "Explain this code"` | `ANTHROPIC_API_KEY` |
| **`claude-code`** | Claude Code CLI | `claude-code` | `@anthropic-ai/claude-cli` |
| **`gpt <prompt>`** | OpenAI GPT access | `gpt "Generate function"` | `OPENAI_API_KEY` |
| **`load-api-keys`** | Load keys from pass | `load-api-keys` | pass, GPG |
| **`check-api-status`** | Verify key availability | `check-api-status` | - |

**Examples**:
```bash
# Claude integration
claude "Review this shell script for security issues"
claude "Explain the git workflow in this repository"

# Environment management
load-api-keys              # Load all keys from pass
check-api-status           # Verify key availability

# OpenAI integration
gpt "Generate a bash function to backup files"
gpt4 "Complex reasoning task requiring advanced model"
```

#### Agent Framework (from `zsh/agents-md.zsh`)

**Agent Functions**:
| Function | Purpose | Context Source | Activation |
|----------|---------|----------------|------------|
| **`load-agents`** | Load directory agents | `.claude/AGENTS.md` | Automatic on `cd` |
| **`show-agent-context`** | Display current context | Active agent | Manual |
| **`reload-agents`** | Refresh agent configuration | Agent files | Manual |

**Agent File Format** (`.claude/AGENTS.md`):
```markdown
# Project Agents

## Development Agent
**Role**: Code development assistance
**Context**: React TypeScript project with testing
**Commands**: npm test, npm build, npm start

## Documentation Agent  
**Role**: Documentation maintenance
**Context**: Technical writing and API documentation
**Commands**: make docs, markdown-toc, spell-check
```

### 📊 Status Line Integration (`ccstatusline`)

**Purpose**: Claude Code status line enhancement

**Installation**:
```bash
npm install -g ccstatusline
```

**Configuration** (automatically set up):
```bash
# Enable status line
export CLAUDE_STATUS_LINE=true
export CLAUDE_STATUS_FORMAT="compact"
```

---

## Security Commands

### 🔐 GPG Operations

#### GPG Manager (`scripts/gpg-manager.sh`)

**Usage**:
```bash
./scripts/gpg-manager.sh <command> [options]
```

**Commands**:
| Command | Description | Parameters | Output |
|---------|-------------|------------|--------|
| **`export --key-id <id>`** | Export GPG keys | Key ID | Key files |
| **`backup`** | Backup entire keyring | - | Backup archive |
| **`restore --backup-file <file>`** | Restore from backup | Backup file | Keyring |
| **`list`** | List available keys | - | Key listing |
| **`generate`** | Generate new key pair | Interactive | New key |

**Examples**:
```bash
# Key management
./scripts/gpg-manager.sh list                      # Show available keys
./scripts/gpg-manager.sh export --key-id ABC123    # Export specific key
./scripts/gpg-manager.sh backup                    # Backup all keys

# Recovery operations
./scripts/gpg-manager.sh restore --backup-file gpg-backup.tar.gz
```

### 🔑 Pass Operations

#### Pass Manager (`scripts/pass-manager.sh`)

**Usage**:
```bash
./scripts/pass-manager.sh <command> [options]
```

**Commands**:
| Command | Description | Parameters | Sync Required |
|---------|-------------|------------|---------------|
| **`sync`** | Synchronize with remote | - | Git remote |
| **`status`** | Show sync status | - | - |
| **`init <gpg-id>`** | Initialize password store | GPG key ID | - |
| **`backup`** | Create encrypted backup | - | - |
| **`restore <backup>`** | Restore from backup | Backup file | - |

**Examples**:
```bash
# Pass management
./scripts/pass-manager.sh init "Your Name <email@example.com>"
./scripts/pass-manager.sh sync         # Sync with git remote
./scripts/pass-manager.sh status       # Check sync status

# Backup operations
./scripts/pass-manager.sh backup       # Create backup
./scripts/pass-manager.sh restore pass-backup-20240315.tar.gz
```

### 🛡️ Security Scanning

#### Pre-commit Hooks (`git/hooks/pre-commit`)

**Detected Patterns**:
| Pattern Type | Regex | Description |
|--------------|-------|-------------|
| **API Keys** | `[A-Za-z0-9]{20,}` | Generic API keys |
| **OpenAI Keys** | `sk-[A-Za-z0-9]{48}` | OpenAI API keys |
| **GitHub Tokens** | `ghp_[A-Za-z0-9]{36}` | GitHub personal tokens |
| **AWS Keys** | `AKIA[A-Z0-9]{16}` | AWS access keys |
| **Private Keys** | `-----BEGIN.*PRIVATE KEY-----` | PEM format keys |

**Usage**:
```bash
# Install hooks
make install-hooks

# Manual scan
./git/hooks/pre-commit

# Bypass (emergency only)
git commit --no-verify
```

#### Security Validation

**Repository Scanning**:
```bash
# Comprehensive security scan
make check-secrets              # Repository-wide scan
make audit                      # Configuration audit
./scripts/validate-config.sh --audit  # Detailed security review

# Manual patterns
grep -r "sk-[A-Za-z0-9]\{48\}" .      # OpenAI keys
grep -r "ghp_[A-Za-z0-9]\{36\}" .     # GitHub tokens
```

---

## Testing Commands

### 🧪 Test Execution

#### ShellSpec Tests

**Test Categories**:
| Test Type | Location | Purpose | Runtime |
|-----------|----------|---------|---------|
| **Unit Tests** | `tests/unit/` | Individual function testing | ~15s |
| **Integration Tests** | `tests/integration/` | Component interaction | ~90s |
| **Security Tests** | `tests/security/` | Security validation | ~30s |
| **E2E Tests** | `tests/docker/` | Full workflow testing | ~300s |

**Commands**:
```bash
# Individual test types
./tests/run-tests.sh tests/unit/             # Unit tests only
./tests/run-tests.sh tests/integration/      # Integration tests
./tests/run-tests.sh --format documentation  # Detailed output

# Specific test files
./tests/run-tests.sh tests/integration/install_spec.sh
./tests/run-tests.sh tests/unit/api_manager_spec.sh
```

#### Docker E2E Tests

**Test Scenarios**:
| Scenario | Configuration | Purpose | Runtime |
|----------|---------------|---------|---------|
| **basic** | Minimal profile | Essential functionality | ~2 min |
| **full** | Full profile | Complete installation | ~5 min |
| **claude** | AI integration | Claude Code setup | ~3 min |
| **switch** | Profile switching | Dynamic configuration | ~4 min |

**Docker Compose Usage**:
```bash
# Run specific scenarios
docker-compose -f tests/docker/docker-compose.e2e.yml run dotfiles-basic
docker-compose -f tests/docker/docker-compose.e2e.yml run dotfiles-full

# Interactive debugging
docker-compose -f tests/docker/docker-compose.e2e.yml run -it dotfiles-basic bash

# Cleanup
docker-compose -f tests/docker/docker-compose.e2e.yml down --volumes
```

### 📊 Test Analysis

#### Test Results Viewer (`view-test-results.sh`)

**Usage**:
```bash
./view-test-results.sh [options]
```

**Features**:
- Interactive test result browser
- Performance analysis
- Error categorization
- Test coverage reporting

**Examples**:
```bash
# View latest results
./view-test-results.sh

# Filter by test type
./view-test-results.sh --type integration

# Performance analysis
./view-test-results.sh --analyze performance
```

#### Test Infrastructure

**Container Inspection** (`tests/docker/inspect-container.sh`):
```bash
./tests/docker/inspect-container.sh logs basic     # View container logs
./tests/docker/inspect-container.sh status         # Container status
./tests/docker/inspect-container.sh clean          # Clean up containers
```

**Coverage Generation** (`tests/generate-coverage.sh`):
```bash
./tests/generate-coverage.sh                       # Generate coverage report
./tests/generate-coverage.sh --output html         # HTML coverage report
```

---

## Environment Variables

### 🌍 Global Variables

| Variable | Purpose | Values | Default | Usage |
|----------|---------|--------|---------|--------|
| **`DOTFILES_PROFILE`** | Installation profile | minimal, development, full, work, personal | development | `DOTFILES_PROFILE=minimal make install` |
| **`INSTALL_MODE`** | Installation behavior | interactive, automatic | interactive | `INSTALL_MODE=automatic ./install.sh` |
| **`BACKUP_EXISTING`** | Backup before install | true, false | true | `BACKUP_EXISTING=false make install` |
| **`CLAUDE_PROFILE`** | Claude configuration | default, experimental | default | `CLAUDE_PROFILE=experimental make install-claude` |

### 🔑 API Keys (Auto-loaded from pass)

| Variable | Service | Format | Source |
|----------|---------|--------|--------|
| **`OPENAI_API_KEY`** | OpenAI GPT | `sk-...` | `pass api/openai` |
| **`ANTHROPIC_API_KEY`** | Claude | `sk-ant-...` | `pass api/anthropic` |
| **`GITHUB_TOKEN`** | GitHub API | `ghp_...` | `pass services/github/token` |
| **`CLAUDE_API_KEY`** | Claude API | `sk-ant-...` | `pass api/claude` |

### 🧪 Testing Variables

| Variable | Purpose | Values | Usage |
|----------|---------|--------|--------|
| **`E2E_TEST`** | Enable E2E mode | true, false | `E2E_TEST=true ./tests/run-tests.sh` |
| **`TEST_VERBOSE`** | Verbose test output | true, false | `TEST_VERBOSE=true make test` |
| **`DOCKER_TEST_CLEAN`** | Clean containers after test | true, false | `DOCKER_TEST_CLEAN=false make test` |

---

## Return Codes

### 📊 Standard Exit Codes

| Code | Meaning | Common Causes | Recovery Action |
|------|---------|---------------|-----------------|
| **0** | Success | Command completed successfully | - |
| **1** | General error | Various failures | Check error message |
| **2** | Misuse | Invalid arguments or options | Review command usage |
| **126** | Command not executable | Permission or path issues | Check permissions |
| **127** | Command not found | Missing dependencies | Install required tools |
| **130** | Script terminated by Ctrl+C | User interruption | Restart if needed |

### 🔧 Script-Specific Codes

#### Installation Scripts
| Code | Meaning | Context |
|------|---------|---------|
| **10** | Missing dependencies | Required tools not available |
| **11** | Permission denied | Insufficient privileges |
| **12** | Configuration conflict | Existing config conflicts |
| **13** | Profile not found | Invalid profile specified |

#### Security Scripts
| Code | Meaning | Context |
|------|---------|---------|
| **20** | Security violation | Secrets detected |
| **21** | GPG error | Key management failure |
| **22** | Pass error | Password store issue |
| **23** | Permission error | File access denied |

---

*This API reference is comprehensive but evolving. For the most current information, run `make help` or check individual script help messages with `--help`.*