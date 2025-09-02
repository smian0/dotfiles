# Developer Workflow Guide

Complete guide for developing, testing, and maintaining the dotfiles repository.

## Table of Contents

| Section | Description |
|---------|-------------|
| **[Development Setup](#development-setup)** | Environment preparation and tooling |
| **[Daily Workflow](#daily-workflow)** | Common development tasks and patterns |
| **[Testing Strategy](#testing-strategy)** | Comprehensive testing approach |
| **[Release Process](#release-process)** | Version management and deployment |
| **[Contribution Guidelines](#contribution-guidelines)** | Standards and best practices |
| **[Advanced Topics](#advanced-topics)** | Complex scenarios and troubleshooting |

---

## Development Setup

### 🚀 Quick Start for Contributors

```bash
# 1. Fork and clone repository
git clone git@github.com:yourusername/dotfiles.git ~/.dotfiles
cd ~/.dotfiles

# 2. Setup development environment
make dev-setup

# 3. Create feature branch
git checkout -b feature/your-enhancement

# 4. Verify setup
make status
make test-quick
```

### 🛠️ Development Environment Requirements

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Git** | ≥2.30 | Version control | `brew install git` |
| **GNU Stow** | ≥2.3 | Symlink management | `brew install stow` |
| **ShellCheck** | Latest | Script linting | `brew install shellcheck` |
| **shfmt** | Latest | Shell formatting | `brew install shfmt` |
| **Docker** | ≥20.10 | E2E testing | `brew install docker` |
| **Pass** | ≥1.7 | Password management | `brew install pass` |
| **GPG** | ≥2.3 | Encryption | `brew install gnupg` |

### 🔧 Development Tools Setup

```bash
# Install all development dependencies
make dev-setup

# Individual tool installation
brew install shellcheck shfmt
brew install --cask docker

# Verify tool availability
make doctor
```

### 📁 Repository Structure for Developers

```
~/.dotfiles/
├── 🔧 Development Tools
│   ├── Makefile              # Central command interface
│   ├── .github/workflows/    # CI/CD automation
│   ├── tests/               # Test infrastructure
│   └── scripts/             # Utility and automation scripts
├── 📦 Configuration Packages
│   ├── git/                 # Git configuration
│   ├── zsh/                 # Shell environment
│   ├── claude*/             # AI integration
│   └── [other-packages]/    # Modular configurations
├── 📚 Documentation
│   ├── docs/                # Comprehensive guides
│   ├── README.md            # Project overview
│   └── *.md                 # Specialized documentation
└── 🏗️ Infrastructure
    ├── profiles/            # Installation profiles
    ├── .stow-global-ignore  # Stow exclusions
    └── install*.sh          # Installation scripts
```

---

## Daily Workflow

### 🔄 Standard Development Cycle

| Phase | Duration | Commands | Success Criteria |
|-------|----------|----------|------------------|
| **1. Setup** | 2 min | `git checkout -b feature/name` | Clean branch created |
| **2. Development** | Variable | Edit → `make test-quick` | Quick tests pass |
| **3. Validation** | 5 min | `make test && make lint` | Full validation passes |
| **4. Review** | Variable | Create PR, address feedback | PR approved |
| **5. Integration** | 2 min | Merge → deploy | Feature integrated |

### 📝 Common Development Tasks

#### Adding a New Configuration Package

```bash
# 1. Create package structure
mkdir new-package
cd new-package

# 2. Add configuration files (following home structure)
mkdir -p .config/appname
cp source-config .config/appname/config

# 3. Test package installation
cd ../
stow --no --verbose new-package  # Dry run
stow new-package                 # Apply changes

# 4. Add to profile system
echo "new-package" >> profiles/development.txt

# 5. Create installation target
cat >> Makefile << 'EOF'
install-newpackage: ## Install new package configuration
	@echo -e "$(GREEN)[INFO]$(NC) Installing new package..."
	stow new-package
EOF

# 6. Test and validate
make test-quick
make install-newpackage
```

#### Modifying Existing Configurations

```bash
# 1. Backup current state
make backup

# 2. Edit configuration files
vim package-name/.config/app/config

# 3. Test changes incrementally
make test-quick    # Fast validation
make lint         # Code quality

# 4. Dry run installation
stow --no --verbose --restow package-name

# 5. Apply and test
stow --restow package-name
make test-integration
```

#### Adding New Scripts

```bash
# 1. Create script with proper structure
cat > scripts/new-utility.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Script purpose and usage
usage() {
    cat << USAGE
Usage: $0 [options]
    
Description of script functionality.

Options:
    -h, --help     Show this help message
    -v, --verbose  Enable verbose output
USAGE
}

# Main functionality here...
EOF

# 2. Make executable and test
chmod +x scripts/new-utility.sh
./scripts/new-utility.sh --help

# 3. Add to Makefile if needed
cat >> Makefile << 'EOF'
new-command: ## Description of new command
	./scripts/new-utility.sh
EOF

# 4. Add tests
cat > tests/integration/new_utility_spec.sh << 'EOF'
Describe 'New Utility Script'
  It 'should show help message'
    When call ./scripts/new-utility.sh --help
    The status should equal 0
    The output should include "Usage:"
  End
End
EOF

# 5. Validate
make test-scripts
make lint
```

### 🧪 Continuous Validation

```bash
# During development - run frequently
make test-quick     # 30 seconds - basic validation
make lint          # 15 seconds - code quality

# Before commits
make test          # 5 minutes - comprehensive tests
make check-secrets # 10 seconds - security scan

# Pre-push validation
make test-all      # 10 minutes - all scenarios
make doctor        # 30 seconds - health check
```

---

## Testing Strategy

### 🎯 Testing Pyramid

| Test Level | Coverage | Runtime | Frequency | Tools |
|------------|----------|---------|-----------|-------|
| **Unit** | Individual functions | 15s | Every save | ShellSpec |
| **Integration** | Component interaction | 90s | Every commit | ShellSpec + Docker |
| **E2E** | Full workflows | 300s | Every PR | Docker Compose |
| **Security** | Secret detection | 10s | Every commit | Custom scanners |

### 🏃‍♂️ Test Commands Reference

```bash
# Development Testing (Fast Feedback)
make test-quick         # Essential validations only
make test-unit          # Unit tests only  
make lint              # ShellCheck validation

# Integration Testing
make test-integration   # Component interaction tests
make test-scripts       # Script functionality tests

# Comprehensive Testing
make test              # Default E2E test suite
make test TEST=full    # Full installation scenario
make test-all          # All test scenarios

# Security Testing
make check-secrets     # Repository secret scan
make audit            # Configuration security review

# Test Infrastructure
make test-clean        # Clean test containers
./view-test-results.sh # Interactive test analysis
```

### 🐳 Docker Testing Environment

#### Test Scenarios

| Scenario | Purpose | Runtime | Command |
|----------|---------|---------|---------|
| **basic** | Essential installation | 2 min | `make test TEST=basic` |
| **full** | Complete setup | 5 min | `make test TEST=full` |
| **claude** | AI integration | 3 min | `make test TEST=claude` |
| **switch** | Profile switching | 4 min | `make test TEST=switch` |

#### Test Environment Structure
```
tests/docker/
├── docker-compose.e2e.yml    # Test orchestration
├── Dockerfile.ubuntu         # Ubuntu test image
├── Dockerfile.macos-like     # macOS simulation
├── test-scenarios/           # Scenario definitions
├── fixtures/                 # Test data and configurations
├── helpers/                  # Test utilities
└── exports/                  # Test results and artifacts
```

#### Custom Test Creation

```bash
# 1. Create test scenario
cat > tests/docker/test-scenarios/new-scenario.sh << 'EOF'
#!/bin/bash
# Test scenario description

set -euo pipefail

echo "=== Testing New Scenario ==="

# Test steps
./install.sh --profile development
make status
make test-quick

echo "✅ New scenario test passed"
EOF

# 2. Add to docker-compose.yml
cat >> tests/docker/docker-compose.e2e.yml << 'EOF'
  dotfiles-new-scenario:
    build: .
    volumes:
      - ./test-scenarios:/test-scenarios:ro
    command: /test-scenarios/new-scenario.sh
EOF

# 3. Run test
docker-compose -f tests/docker/docker-compose.e2e.yml run dotfiles-new-scenario
```

### 🔍 Test Debugging

```bash
# Interactive test container
docker-compose -f tests/docker/docker-compose.e2e.yml run --rm -it dotfiles-basic bash

# Inspect test results
./tests/docker/inspect-container.sh logs basic
./tests/docker/inspect-container.sh status

# Test result analysis
./view-test-results.sh
```

---

## Release Process

### 🏷️ Version Management

#### Semantic Versioning Strategy

| Change Type | Version Bump | Examples |
|-------------|--------------|----------|
| **Major** | x.0.0 | Breaking changes, major rewrites |
| **Minor** | x.y.0 | New packages, features, profiles |
| **Patch** | x.y.z | Bug fixes, minor improvements |

#### Release Workflow

```bash
# 1. Prepare release branch
git checkout -b release/v2.1.0
git checkout main

# 2. Update documentation
make docs                    # Sync Makefile commands
git add README.md docs/

# 3. Comprehensive testing
make test-all               # All scenarios
make audit                  # Security review
make doctor                 # Health check

# 4. Version bump
# Update version in relevant files
git add -A
git commit -m "chore: bump version to v2.1.0"

# 5. Create release
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin main --tags

# 6. Deploy documentation
make docs-deploy            # If documentation site exists
```

### 📦 Release Checklist

- [ ] All tests pass (`make test-all`)
- [ ] Documentation updated (`make docs`)
- [ ] Security audit clean (`make audit`)
- [ ] Version bumped in all relevant files
- [ ] Changelog updated with new features
- [ ] Breaking changes documented
- [ ] Release notes prepared
- [ ] Git tag created and pushed

### 🚀 Deployment Process

```bash
# Production deployment steps
make backup                 # Create system backup
make update                 # Update repository
make install               # Apply changes
make status                # Verify installation
make test-quick            # Validate functionality
```

---

## Contribution Guidelines

### 📋 Pull Request Process

#### 1. Pre-Development
```bash
# Check for existing issues
hub issue list

# Create feature branch
git checkout -b feature/descriptive-name
```

#### 2. Development Standards
```bash
# Code quality requirements
make lint                   # Must pass ShellCheck
make format                 # Apply consistent formatting
make check-secrets          # No secrets in commits
```

#### 3. Testing Requirements
```bash
# Minimum testing for PR
make test-quick            # Basic validation
make test-integration      # Component testing

# Recommended for complex changes
make test-all             # Comprehensive validation
```

#### 4. Documentation Requirements
- Update relevant documentation files
- Add inline comments for complex logic
- Update Makefile help text for new commands
- Include usage examples

#### 5. Review Process
- Self-review checklist completion
- Automated CI/CD validation
- Manual code review approval
- Integration testing verification

### 🎨 Code Style Guidelines

#### Shell Scripting Standards
```bash
#!/bin/bash
# Always use bash with strict mode
set -euo pipefail

# Function naming: snake_case
install_package() {
    local package_name="$1"
    echo "Installing $package_name..."
}

# Variable naming: lowercase with underscores
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Error handling
if ! command -v stow >/dev/null 2>&1; then
    echo "Error: GNU Stow is required" >&2
    exit 1
fi
```

#### Configuration File Standards
```bash
# Use consistent indentation (4 spaces)
# Include header comments explaining purpose
# Group related settings logically
# Document complex configurations
```

#### Documentation Standards
- Use clear, descriptive headers
- Include code examples with explanations
- Provide troubleshooting sections
- Cross-reference related documentation

### 🔧 Development Environment Standards

#### Required Tools
- All tools listed in [Development Setup](#development-setup)
- Pre-commit hooks enabled (`make install-hooks`)
- GPG commit signing configured
- SSH key authentication setup

#### File Organization
- Follow existing directory structure
- Use consistent naming conventions
- Place files in appropriate packages
- Update ignore patterns when needed

---

## Advanced Topics

### 🔄 Complex Scenarios

#### Cross-Platform Development
```bash
# Test on multiple platforms
docker run --rm -it ubuntu:latest /bin/bash
# Mount and test dotfiles installation

# macOS-specific testing
make test-macos

# Linux-specific testing  
make test-ubuntu
```

#### Package Dependencies
```bash
# Analyze package dependencies
./scripts/analyze-dependencies.sh

# Test installation order
./scripts/test-install-order.sh

# Validate package isolation
./scripts/test-package-isolation.sh
```

#### Profile Customization
```bash
# Create custom profile
mkdir -p profiles/custom
echo "git zsh claude-default custom-package" > profiles/custom.txt

# Test custom profile
DOTFILES_PROFILE=custom ./install.sh --dry-run
```

### 🐛 Troubleshooting Development Issues

#### Common Issues and Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Stow conflicts** | Symlink errors | `stow -D package && stow package` |
| **Test failures** | CI/CD failures | Check logs: `./view-test-results.sh` |
| **Permission errors** | Install failures | Run: `make doctor` for diagnostics |
| **Docker issues** | Test environment problems | Clean: `make test-clean` |

#### Debug Commands
```bash
# Comprehensive debugging
make debug                 # Show system information
make doctor               # Health check with recommendations

# Specific debugging
stow --verbose package    # Verbose stow operations
make test-integration V=1 # Verbose test output

# Log analysis
tail -f ~/.dotfiles.log   # Installation logs
journalctl -f            # System logs (Linux)
```

#### Performance Optimization
```bash
# Profile installation performance
time make install

# Analyze test performance
make test-coverage        # Generate performance reports

# Optimize Docker builds
docker system prune       # Clean unused images
```

### 🔐 Security Considerations for Developers

#### Secret Management
```bash
# Never commit secrets
make check-secrets        # Pre-commit validation
git secrets --scan        # Additional scanning

# Use pass for development keys
pass insert dev/api-key
export API_KEY=$(pass dev/api-key)
```

#### Code Security
```bash
# Regular security audits
make audit               # Configuration security
./scripts/security-scan.sh # Custom security checks

# Dependency security
npm audit                # Node.js dependencies
brew audit               # Homebrew packages
```

---

## Developer Resources

### 📚 Reference Documentation

| Resource | Purpose | Location |
|----------|---------|----------|
| **Makefile Reference** | All available commands | `make help` |
| **Package Guide** | Configuration details | [PACKAGE-GUIDE.md](PACKAGE-GUIDE.md) |
| **Security Guide** | Security best practices | [SECURITY.md](SECURITY.md) |
| **Troubleshooting** | Problem resolution | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

### 🛠️ Development Utilities

```bash
# Project statistics
find . -name "*.sh" | wc -l        # Count shell scripts
find . -name "*.md" | wc -l        # Count documentation files
git log --oneline | wc -l          # Count commits

# Quality metrics
make lint | grep -c "error:"       # Count linting errors
make test-coverage                 # Test coverage report

# Performance metrics
time make install                  # Installation time
du -sh ~/.dotfiles                 # Repository size
```

### 🤝 Community and Support

- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Ask questions in GitHub Discussions
- **Contributing**: Follow this developer workflow
- **Documentation**: Help improve documentation accuracy

---

*This developer workflow guide is maintained by the dotfiles community. For questions or improvements, please open an issue or submit a pull request.*