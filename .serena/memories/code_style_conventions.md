# Code Style and Conventions

## Shell Script Conventions

### Header Standards
All shell scripts start with:
```bash
#!/bin/bash
# Script Description
# Purpose and usage information

set -euo pipefail
```

### Error Handling
- Always use `set -euo pipefail` for strict error handling
- Use consistent error handling functions:
```bash
log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }  
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
success() { echo -e "${GREEN}✓${NC} $1"; }
```

### Color Coding Standards
Consistent color variables across all scripts:
```bash
GREEN='\033[0;32m'    # Success messages, info
BLUE='\033[0;34m'     # Informational messages
YELLOW='\033[1;33m'   # Warnings
RED='\033[0;31m'      # Errors
BOLD='\033[1m'        # Emphasis
NC='\033[0m'          # No Color (reset)
```

### Variable Naming
- **Environment variables**: ALL_CAPS with underscores (`DOTFILES_PROFILE`)
- **Local variables**: lowercase with underscores (`package_name`)
- **Constants**: ALL_CAPS (`BACKUP_DIR`)
- **Functions**: lowercase with underscores (`detect_os`)

### Function Conventions
```bash
# Function documentation above each function
# Parameters: $1 - description
# Returns: description
function_name() {
    local param1="$1"
    local param2="${2:-default_value}"
    
    # Function body
    return 0
}
```

### File Naming Conventions
- **Scripts**: kebab-case with `.sh` extension (`api-key-manager.sh`)
- **Config files**: lowercase with appropriate extensions (`.gitconfig`)
- **Documentation**: UPPERCASE for important files (`README.md`, `CLAUDE.md`)

## Directory and Package Structure

### Stow Package Organization
Each Stow package follows this pattern:
```
package-name/
├── .config/           # XDG config files
├── bin/              # Executable scripts
└── other-dotfiles    # Files that go to $HOME
```

### Script Organization
```
scripts/
├── category-script.sh    # Main scripts
├── category/            # Script subdirectories for related tools
│   └── helper-script.sh
└── README.md           # Script documentation
```

## Configuration File Conventions

### Git Configuration
- Consistent user configuration
- Sensible defaults for all projects
- Security-focused settings (no credential storage)

### Zsh Configuration
- Modular sourcing of configuration files
- Environment variables at the top
- Platform-specific sections clearly marked
- Performance-conscious loading order

### Environment Variables
Follow XDG Base Directory Specification:
```bash
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_DATA_HOME="$HOME/.local/share" 
export XDG_STATE_HOME="$HOME/.local/state"
export XDG_CACHE_HOME="$HOME/.cache"
```

## Documentation Standards

### README Structure
1. Project title and brief description
2. Quick start section
3. Core commands table
4. Architecture overview
5. Documentation links
6. License

### Code Comments
- Function-level documentation for all public functions
- Inline comments for complex logic only
- Section headers with clear boundaries:
```bash
# =============================================================================
# Section Name
# =============================================================================
```

### Makefile Conventions
- All targets have `## Description` comments for help system
- Consistent variable naming (`PROJECT_ROOT`, `TIMESTAMP`)
- Color-coded output using standard color variables
- Grouped targets by function (installation, testing, maintenance)

## Testing Conventions

### Test File Naming
- E2E tests: `e2e-test.sh`
- Unit tests: `*_spec.sh` (ShellSpec format)
- Test cases: descriptive names in `test-cases/`

### Test Structure
```bash
# Test header with scenario description
# Test setup
# Test execution  
# Test validation
# Test cleanup
```

### Docker Testing
- Each test scenario in separate container
- Test results exported to `tests/docker/exports/`
- Consistent environment setup across all test containers

## Quality Standards

### Linting Requirements
- **shellcheck**: All shell scripts must pass without errors
- **shfmt**: Consistent formatting with 4-space indentation
- **Secret detection**: Pre-commit hooks prevent credential leaks

### Code Quality Checklist
1. `shellcheck` compliance
2. `shfmt` formatting (4-space indent)
3. Error handling with `set -euo pipefail`
4. Consistent logging functions
5. Proper variable quoting
6. Cross-platform compatibility

## Security Conventions

### Credential Management
- Never commit secrets or API keys
- Use `pass` for encrypted storage
- Environment variables for runtime secrets
- GPG encryption for sensitive data

### File Permissions
- Executable scripts: `chmod +x`
- Private keys: `chmod 600`  
- Configuration files: `chmod 644`

### Git Hooks
- Pre-commit: Secret detection, basic validation
- Post-commit: Optional sync operations

## Platform-Specific Considerations

### macOS (Darwin)
- Use Homebrew for package management
- Respect macOS file system conventions
- Handle macOS-specific environment variables
- Use `sw_vers` for version detection

### Linux (Ubuntu)
- Use apt for package management
- Follow FHS (Filesystem Hierarchy Standard)
- Handle different shell environments
- Use `/etc/os-release` for distribution detection

## IDE and Editor Configuration

### Vim Integration
- Consistent indentation settings
- Syntax highlighting for all file types
- Plugin configuration in version control

### VS Code/Cursor Integration  
- Settings synchronized via dotfiles
- Extensions listed in configuration
- Consistent formatting settings

This style guide ensures consistency, maintainability, and cross-platform compatibility across the entire dotfiles repository.