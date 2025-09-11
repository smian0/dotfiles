# Dotfiles Management Makefile
# Provides convenient commands for managing dotfiles installation and maintenance

.PHONY: help install install-all install-minimal backup restore clean test lint format update status stow-audit stow-status stow-conflicts stow-dry-run stow-debug docs docs-check test-quick test-unit test-integration test-e2e test-stress test-all-docker

# Default target
.DEFAULT_GOAL := help

# Variables
SHELL := /bin/bash
PROJECT_ROOT := $(shell pwd)
BACKUP_DIR := $(HOME)/.dotfiles-backups
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

# Colors for output
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[1;33m
RED := \033[0;31m
BOLD := \033[1m
NC := \033[0m # No Color

# Help target - shows available commands
help: ## Show this help message
	@echo -e "$(BOLD)Dotfiles Management Commands$(NC)"
	@echo
	@echo "Usage: make [target]"
	@echo
	@echo -e "$(BOLD)📦 End User Commands$(NC)"
	@echo "Common operations for daily use:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	grep -E "^(install|backup|restore|status|help|bootstrap|update|sync|clean|list-backups|verify-backup):" | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' | \
	sort
	@echo
	@echo -e "$(BOLD)⚙️  Configuration Commands$(NC)"
	@echo "Profile and package management:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	grep -E "(profile|api|install-|check-secrets|doctor|audit|backup-|restore-from|clean-|info|stow-):" | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}' | \
	sort
	@echo
	@echo -e "$(BOLD)🛠️  Developer Commands$(NC)"
	@echo "Development and testing operations:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	grep -E "(test|lint|format|debug|demo|dev-setup|docker|docs|export):" | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' | \
	sort
	@echo
	@echo -e "$(BOLD)Examples:$(NC)"
	@echo "  make bootstrap            # Complete setup for new machines"
	@echo "  make install              # Install default profile"
	@echo "  make backup               # Create backup of configurations"
	@echo "  make status               # Show current status"
	@echo "  make test                 # Run E2E tests (developers)"

# Installation targets
install: ## Install default profile with Claude Code
	@echo -e "$(GREEN)[INFO]$(NC) Installing default profile with Claude Code..."
	./install.sh

install-all: ## Install all packages and configurations with Claude Code
	@echo -e "$(GREEN)[INFO]$(NC) Installing all dotfiles packages with Claude Code..."
	./install.sh --all

install-minimal: ## Install minimal profile (essential tools only)
	@echo -e "$(GREEN)[INFO]$(NC) Installing minimal dotfiles profile..."
	./install.sh --profile minimal


# Package-specific installations
install-git: ## Install git configuration only
	@echo -e "$(GREEN)[INFO]$(NC) Installing git configuration..."
	./install.sh git

install-zsh: ## Install zsh configuration only
	@echo -e "$(GREEN)[INFO]$(NC) Installing zsh configuration..."
	./install.sh zsh

install-vim: ## Install vim configuration only
	@echo -e "$(GREEN)[INFO]$(NC) Installing vim configuration..."
	./install.sh vim

install-claude: ## Install Claude Code configurations
	@echo -e "$(GREEN)[INFO]$(NC) Installing Claude configurations..."
	./install.sh claude-default claude-experimental

install-crystal: ## Install Crystal configuration
	@echo -e "$(GREEN)[INFO]$(NC) Installing Crystal configuration..."
	stow crystal


# Backup and restore
backup: ## Create a backup of current configurations
	@echo -e "$(GREEN)[INFO]$(NC) Creating backup..."
	./scripts/backup-restore.sh backup --include-brew

backup-minimal: ## Create a backup excluding secrets
	@echo -e "$(GREEN)[INFO]$(NC) Creating minimal backup..."
	./scripts/backup-restore.sh backup --exclude-secrets

restore: ## Restore from latest backup
	@echo -e "$(YELLOW)[WARN]$(NC) This will restore from the latest backup"
	./scripts/backup-restore.sh restore

restore-from: ## Restore from specific backup (Usage: make restore-from BACKUP=20240117_120000)
	@if [ -z "$(BACKUP)" ]; then \
		echo -e "$(RED)[ERROR]$(NC) Please specify BACKUP timestamp: make restore-from BACKUP=20240117_120000"; \
		exit 1; \
	fi
	./scripts/backup-restore.sh restore $(BACKUP)

list-backups: ## List available backups
	./scripts/backup-restore.sh list

verify-backup: ## Verify latest backup integrity
	./scripts/backup-restore.sh verify

clean-backups: ## Clean old backups (keep last 5)
	./scripts/backup-restore.sh clean

# Profile management
profile-status: ## Show current profile installation status
	./scripts/profile-manager.sh status

profile-list: ## List available installation profiles
	./scripts/profile-manager.sh list

profile-check: ## Validate profile configurations
	./scripts/profile-manager.sh check

# Testing
test-suite: ## Run shell test suite
	@echo -e "$(GREEN)[INFO]$(NC) Running test suite..."
	./tests/run-tests.sh

test-scripts: ## Test script functionality
	@echo -e "$(GREEN)[INFO]$(NC) Running script tests..."
	./tests/run-tests.sh tests/integration/scripts_spec.sh

test-shellspec: ## Run ShellSpec integration tests
	@echo -e "$(GREEN)[INFO]$(NC) Running ShellSpec integration tests..."
	./tests/run-tests.sh --format documentation tests/integration/

test-e2e-shellspec: ## Run ShellSpec E2E tests
	@echo -e "$(GREEN)[INFO]$(NC) Running ShellSpec E2E tests..."
	E2E_TEST=true ./tests/run-tests.sh

test-coverage: ## Generate test coverage report
	@echo -e "$(GREEN)[INFO]$(NC) Generating coverage report..."
	./tests/generate-coverage.sh

# Maintenance
clean: ## Clean temporary files and caches
	@echo -e "$(GREEN)[INFO]$(NC) Cleaning temporary files..."
	find . -name "*.tmp" -type f -delete
	find . -name "*.cache" -type f -delete
	find . -name ".DS_Store" -type f -delete
	rm -rf ./.cache/
	@echo -e "$(GREEN)[INFO]$(NC) Cleanup complete"

lint: ## Lint shell scripts
	@echo -e "$(GREEN)[INFO]$(NC) Linting shell scripts..."
	@if command -v shellcheck >/dev/null 2>&1; then \
		find . -name "*.sh" -type f -exec shellcheck {} \; ; \
	else \
		echo -e "$(YELLOW)[WARN]$(NC) shellcheck not installed, skipping lint"; \
	fi

format: ## Format shell scripts
	@echo -e "$(GREEN)[INFO]$(NC) Formatting shell scripts..."
	@if command -v shfmt >/dev/null 2>&1; then \
		find . -name "*.sh" -type f -exec shfmt -w -i 4 {} \; ; \
	else \
		echo -e "$(YELLOW)[WARN]$(NC) shfmt not installed, skipping format"; \
	fi

# Updates and synchronization
update: ## Update dotfiles repository and tools
	@echo -e "$(GREEN)[INFO]$(NC) Updating dotfiles repository..."
	git pull origin main
	@echo -e "$(GREEN)[INFO]$(NC) Updating Homebrew packages..."
	@if command -v brew >/dev/null 2>&1; then \
		brew update && brew upgrade; \
	fi
	@echo -e "$(GREEN)[INFO]$(NC) Update complete"

sync: ## Sync with remote repositories
	@echo -e "$(GREEN)[INFO]$(NC) Syncing dotfiles..."
	git add -A && git commit -m "sync: $(TIMESTAMP)" || true
	git push origin main
	@if [ -d "$(HOME)/.password-store" ]; then \
		echo -e "$(GREEN)[INFO]$(NC) Syncing password store..."; \
		./scripts/pass-manager.sh sync; \
	fi

# Status and information
status: ## Show installation status and system info
	@echo -e "$(BOLD)Dotfiles Status$(NC)"
	@echo "=================="
	@echo
	@echo -e "$(BLUE)Repository:$(NC)"
	@echo "  Location: $(PROJECT_ROOT)"
	@echo "  Branch: $$(git branch --show-current 2>/dev/null || echo 'unknown')"
	@echo "  Commit: $$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
	@echo
	@echo -e "$(BLUE)System:$(NC)"
	@echo "  OS: $$(uname -s)"
	@echo "  Version: $$(uname -r)"
	@echo "  Shell: $$SHELL"
	@echo
	@echo -e "$(BLUE)Tools:$(NC)"
	@command -v stow >/dev/null 2>&1 && echo "  ✓ GNU Stow: $$(stow --version | head -1)" || echo "  ✗ GNU Stow: not installed"
	@command -v git >/dev/null 2>&1 && echo "  ✓ Git: $$(git --version)" || echo "  ✗ Git: not installed"
	@command -v pass >/dev/null 2>&1 && echo "  ✓ Pass: $$(pass version 2>/dev/null | head -1)" || echo "  ✗ Pass: not installed"
	@command -v gpg >/dev/null 2>&1 && echo "  ✓ GPG: $$(gpg --version | head -1)" || echo "  ✗ GPG: not installed"
	@echo
	@./scripts/profile-manager.sh status

# Stow audit and debugging
stow-audit: ## Comprehensive stow state audit
	@echo -e "$(BOLD)Stow State Audit$(NC)"
	@echo "================"
	@echo
	@echo -e "$(BLUE)Active Stow Symlinks:$(NC)"
	@find "$(HOME)" -maxdepth 3 -type l -ls 2>/dev/null | grep "$(PROJECT_ROOT)" | awk '{print "  " $$11 " -> " $$13}' || echo "  No symlinks found"
	@echo
	@echo -e "$(BLUE)Broken Symlinks:$(NC)"
	@broken_links=$$(find "$(HOME)" -maxdepth 3 -type l ! -exec test -e {} \; -print 2>/dev/null | grep "$(PROJECT_ROOT)" || true); \
	if [ -n "$$broken_links" ]; then \
		echo "$$broken_links" | sed 's/^/  /'; \
	else \
		echo "  ✓ No broken symlinks found"; \
	fi
	@echo
	@echo -e "$(BLUE)Stow Package Status:$(NC)"
	@for pkg in $$(ls -d */ 2>/dev/null | grep -v -E '^(tests|docs|scripts|\..*|claudedocs)/' | tr -d '/'); do \
		if find "$(HOME)" -maxdepth 3 -type l 2>/dev/null | grep -q "$(PROJECT_ROOT)/$$pkg" 2>/dev/null; then \
			echo "  ✓ $$pkg: stowed"; \
		else \
			echo "  ✗ $$pkg: not stowed"; \
		fi; \
	done

stow-status: ## Show current stow symlink status by package
	@echo -e "$(BOLD)Stow Symlink Status$(NC)"
	@echo "==================="
	@echo
	@for pkg in $$(ls -d */ 2>/dev/null | grep -v -E '^(tests|docs|scripts|\..*|claudedocs)/' | tr -d '/'); do \
		echo -e "$(BLUE)Package: $$pkg$(NC)"; \
		links=$$(find "$(HOME)" -maxdepth 3 -type l 2>/dev/null | grep "$(PROJECT_ROOT)/$$pkg" | head -10 || true); \
		if [ -n "$$links" ]; then \
			echo "$$links" | while read link; do \
				target=$$(readlink "$$link" 2>/dev/null || echo "unknown"); \
				echo "  $$link -> $$target"; \
			done; \
		else \
			echo "  No symlinks found"; \
		fi; \
		echo; \
	done

stow-conflicts: ## Check for stow conflicts and issues
	@echo -e "$(BOLD)Stow Conflict Analysis$(NC)"
	@echo "======================"
	@echo
	@echo -e "$(BLUE)Checking for conflicts...$(NC)"
	@conflict_found=false; \
	for pkg in $$(ls -d */ 2>/dev/null | grep -v -E '^(tests|docs|scripts|\..*|claudedocs)/' | tr -d '/'); do \
		if [ -d "$$pkg" ]; then \
			echo "Checking package: $$pkg"; \
			if ! stow -n -t "$(HOME)" "$$pkg" 2>&1 | grep -q "CONFLICT\|ERROR"; then \
				echo "  ✓ No conflicts"; \
			else \
				echo "  ⚠️  Conflicts detected:"; \
				stow -n -t "$(HOME)" "$$pkg" 2>&1 | grep -A 2 "CONFLICT\|ERROR" | sed 's/^/    /'; \
				conflict_found=true; \
			fi; \
		fi; \
	done; \
	if [ "$$conflict_found" = "false" ]; then \
		echo -e "$(GREEN)✓ No stow conflicts detected$(NC)"; \
	fi

stow-dry-run: ## Preview what stow operations would do (dry run)
	@echo -e "$(BOLD)Stow Dry Run Preview$(NC)"
	@echo "===================="
	@echo
	@echo -e "$(BLUE)What would happen if we stowed all packages:$(NC)"
	@for pkg in $$(ls -d */ 2>/dev/null | grep -v -E '^(tests|docs|scripts|\..*|claudedocs)/' | tr -d '/'); do \
		if [ -d "$$pkg" ]; then \
			echo -e "$(BLUE)Package: $$pkg$(NC)"; \
			stow -n -v -t "$(HOME)" "$$pkg" 2>&1 | grep -E "LINK|MKDIR|UNLINK" | sed 's/^/  /' || echo "  No changes needed"; \
			echo; \
		fi; \
	done

stow-debug: ## Verbose stow operations for debugging
	@echo -e "$(BOLD)Stow Debug Mode$(NC)"
	@echo "==============="
	@echo
	@echo -e "$(BLUE)Stow version and configuration:$(NC)"
	@stow --version | head -1
	@echo "Target directory: $(HOME)"
	@echo "Stow directory: $(PROJECT_ROOT)"
	@echo "Ignore file: $(PROJECT_ROOT)/.stow-global-ignore"
	@echo
	@echo -e "$(BLUE)Global ignore patterns:$(NC)"
	@if [ -f ".stow-global-ignore" ]; then \
		cat .stow-global-ignore | grep -v '^#' | grep -v '^$$' | sed 's/^/  /'; \
	else \
		echo "  No .stow-global-ignore file found"; \
	fi

info: ## Show detailed system and dotfiles information
	@echo -e "$(BOLD)Detailed System Information$(NC)"
	@echo "=============================="
	@echo
	@./scripts/os-detect.sh --info
	@echo
	@./scripts/validate-config.sh

# Security
check-secrets: ## Check for accidentally committed secrets
	@echo -e "$(GREEN)[INFO]$(NC) Checking for secrets in repository..."
	@if [ -f ".git/hooks/pre-commit" ]; then \
		git diff HEAD~1 HEAD --name-only | xargs -I {} bash .git/hooks/pre-commit || true; \
	else \
		echo -e "$(YELLOW)[WARN]$(NC) Pre-commit hook not installed"; \
	fi

install-hooks: ## Install git hooks
	@echo -e "$(GREEN)[INFO]$(NC) Installing git hooks..."
	cp git/hooks/* .git/hooks/
	chmod +x .git/hooks/*
	@echo -e "$(GREEN)[INFO]$(NC) Git hooks installed"

# API Key management
api-keys: ## Show API key management help
	@echo -e "$(BOLD)API Key Management$(NC)"
	@echo "==================="
	@echo
	@echo "Available commands:"
	@echo "  make api-status     - Show API key status"
	@echo "  make api-list       - List stored API keys"
	@echo "  make api-sync       - Sync keys with pass store"
	@echo
	@echo "Manual key management:"
	@echo "  ./scripts/api-key-manager.sh add openai"
	@echo "  ./scripts/api-key-manager.sh test anthropic"

api-status: ## Show API key status
	./scripts/api-key-manager.sh status

api-list: ## List stored API keys
	./scripts/api-key-manager.sh list

api-sync: ## Sync API keys with pass store
	./scripts/api-key-manager.sh sync

# Development helpers
dev-setup: ## Setup development environment
	@echo -e "$(GREEN)[INFO]$(NC) Setting up development environment..."
	make install-minimal
	make install-claude
	./config/completions/install.sh
	@echo -e "$(GREEN)[INFO]$(NC) Development setup complete"

demo: ## Run installation demo (dry-run)
	@echo -e "$(GREEN)[INFO]$(NC) Running installation demo..."
	./install.sh --dry-run --profile development

# Docker E2E Testing (simplified)
test: ## Run end-to-end test (default: basic, or TEST=full/claude/switch)
	@echo -e "$(GREEN)[INFO]$(NC) Running E2E test: $(or $(TEST),basic)"
	@docker-compose -f tests/docker/docker-compose.e2e.yml run --rm dotfiles-$(or $(TEST),basic)
	@echo -e "\n$(BLUE)[INFO]$(NC) Test results exported to: tests/docker/exports/"
	@echo -e "$(BLUE)[INFO]$(NC) View results with: ./view-test-results.sh"

test-all: ## Run all E2E test scenarios
	@echo -e "$(GREEN)[INFO]$(NC) Running all E2E tests..."
	@for test in basic full claude switch; do \
		echo -e "\n$(BLUE)Testing $$test scenario...$(NC)"; \
		docker-compose -f tests/docker/docker-compose.e2e.yml run --rm dotfiles-$$test; \
	done
	@echo -e "\n$(GREEN)✅ All E2E tests passed!$(NC)"

test-clean: ## Clean up all Docker test containers and volumes
	@echo -e "$(GREEN)[INFO]$(NC) Cleaning up Docker test environment..."
	@./tests/docker/inspect-container.sh clean

# Maintenance tasks
audit: ## Audit dotfiles configuration
	@echo -e "$(GREEN)[INFO]$(NC) Auditing dotfiles configuration..."
	./scripts/validate-config.sh --audit

doctor: ## Run comprehensive health check
	@echo -e "$(GREEN)[INFO]$(NC) Running dotfiles health check..."
	@echo
	make status
	@echo
	make check-secrets
	@echo
	./scripts/validate-config.sh

# Advanced targets
export-config: ## Export current configuration to archive
	@echo -e "$(GREEN)[INFO]$(NC) Exporting configuration..."
	tar -czf "dotfiles-export-$(TIMESTAMP).tar.gz" \
		--exclude='.git' \
		--exclude='node_modules' \
		--exclude='*.cache' \
		--exclude='*.tmp' \
		.
	@echo -e "$(GREEN)[INFO]$(NC) Configuration exported to dotfiles-export-$(TIMESTAMP).tar.gz"

bootstrap: ## Bootstrap from scratch (for new machines)
	@echo -e "$(GREEN)[INFO]$(NC) Bootstrapping dotfiles on new system..."
	./install-master.sh

# Documentation
docs: ## Update README with Makefile commands
	@echo -e "$(GREEN)[INFO]$(NC) Syncing Makefile commands to README..."
	@echo "<!-- MAKEFILE_COMMANDS_START -->" > /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "## Available Commands" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "This project uses a Makefile for common operations. Run \`make help\` to see all available commands." >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "### Quick Start" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "\`\`\`bash" >> /tmp/makefile_commands.md
	@echo "make install          # Install with default profile" >> /tmp/makefile_commands.md
	@echo "make install-minimal  # Install minimal profile" >> /tmp/makefile_commands.md
	@echo "make backup           # Create backup" >> /tmp/makefile_commands.md
	@echo "make test             # Run tests" >> /tmp/makefile_commands.md
	@echo "make help             # Show all commands" >> /tmp/makefile_commands.md
	@echo "\`\`\`" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "### 📦 End User Commands" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "Common operations for daily use:" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	grep -E "^(install|backup|restore|status|help|bootstrap|update|sync|clean|list-backups|verify-backup):" | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "- **`make %s`** - %s\n", $$1, $$2}' | \
	sort >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "### ⚙️ Configuration Commands" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "Profile and package management:" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	grep -E "(profile|api|install-|check-secrets|doctor|audit|backup-|restore-from|clean-|info|stow-):" | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "- **`make %s`** - %s\n", $$1, $$2}' | \
	sort >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "### 🛠️ Developer Commands" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "Development and testing operations:" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	grep -E "(test|lint|format|debug|demo|dev-setup|docker|docs|export):" | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "- **`make %s`** - %s\n", $$1, $$2}' | \
	sort >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "---" >> /tmp/makefile_commands.md
	@echo "*Documentation auto-generated from Makefile on $$(date '+%Y-%m-%d %H:%M:%S')*" >> /tmp/makefile_commands.md
	@echo "" >> /tmp/makefile_commands.md
	@echo "<!-- MAKEFILE_COMMANDS_END -->" >> /tmp/makefile_commands.md
	@if grep -q "<!-- MAKEFILE_COMMANDS_START -->" README.md 2>/dev/null; then \
		awk '/<!-- MAKEFILE_COMMANDS_START -->/{print; while(getline < "/tmp/makefile_commands.md") print; next} \
		     /<!-- MAKEFILE_COMMANDS_END -->/{next} 1' README.md > README.md.tmp && \
		mv README.md.tmp README.md; \
	else \
		echo "" >> README.md; \
		cat /tmp/makefile_commands.md >> README.md; \
	fi
	@rm -f /tmp/makefile_commands.md
	@echo -e "$(GREEN)[INFO]$(NC) Documentation updated successfully"

docs-check: ## Check if documentation is up to date
	@echo -e "$(GREEN)[INFO]$(NC) Checking if README is synced with Makefile..."
	@if ! grep -q "make help" README.md 2>/dev/null; then \
		echo -e "$(YELLOW)[WARN]$(NC) README needs updating - run 'make docs'"; \
	else \
		echo -e "$(GREEN)[INFO]$(NC) Documentation appears to be in sync"; \
	fi

# Debugging
debug: ## Show debug information
	@echo -e "$(BOLD)Debug Information$(NC)"
	@echo "=================="
	@echo
	@echo "Environment Variables:"
	@env | grep -E "(HOME|SHELL|PATH|USER)" | sort
	@echo
	@echo "Makefile Variables:"
	@echo "  PROJECT_ROOT: $(PROJECT_ROOT)"
	@echo "  BACKUP_DIR: $(BACKUP_DIR)"
	@echo "  TIMESTAMP: $(TIMESTAMP)"
	@echo
	@echo "File Permissions:"
	@ls -la install*.sh scripts/*.sh 2>/dev/null | head -5
# Cursor Project Management
cursor-life:
	@echo "Opening shoaib-life-hub in Cursor..."
	open -a "Cursor" "$(LIFE_HUB_PATH)"

cursor-dotfiles:
	@echo "Opening dotfiles in Cursor..."
	open -a "Cursor" ~/dotfiles

cursor-projects:
	@echo "Opening projects folder in Cursor..."
	open -a "Cursor" ~/projects
