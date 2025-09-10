# Scripts Directory Reorganization Proposal

## Current Structure Issues
- 20+ files in flat `/scripts/` directory
- Mixed purposes make navigation difficult
- Related functionality scattered
- Inconsistent grouping (some subdirs exist: `claude-oauth/`, `mcp-env/`)

## Proposed New Structure

```
scripts/
├── README.md                    # Overview and index
├── security/                    # 🔐 Credential & Security Management
│   ├── api-key-manager.sh      # API key management via pass
│   ├── env-debug.sh           # Environment variable diagnostics
│   ├── gpg-manager.sh         # GPG key management
│   └── pass-manager.sh        # Password store management
├── system/                     # 🖥️ System & Installation
│   ├── backup-restore.sh      # Backup/restore dotfiles
│   ├── install-by-environment.sh  # Environment-based installation
│   ├── npm-packages.sh        # NPM package management
│   ├── os-detect.sh          # OS detection utilities
│   ├── profile-manager.sh     # Profile management
│   └── validate-config.sh     # Configuration validation
├── claude/                     # 🤖 Claude Code Tools
│   ├── oauth/                 # OAuth authentication (moved from claude-oauth/)
│   ├── deploy-project.sh      # Deploy Claude to projects
│   ├── deploy-user.sh         # Deploy Claude user config
│   └── fix-ssh-auth.sh        # SSH authentication fixes
├── mcp/                       # 🔌 MCP Server Management
│   ├── env/                   # Environment management (moved from mcp-env/)
│   ├── check.sh              # MCP configuration check
│   ├── extract.sh            # Extract MCP configs (claude-mcp-extract.sh)
│   ├── extract-config.py     # Python MCP extraction
│   └── sync-config.sh        # Sync MCP configurations
└── utils/                     # 🛠️ General Utilities
    └── (future utility scripts)
```

## Benefits

### 1. **Logical Grouping**
- **Security**: All credential/key management in one place
- **System**: Installation, backup, OS-specific tools  
- **Claude**: Claude Code specific functionality
- **MCP**: Consolidates scattered MCP tools

### 2. **Improved Navigation**
```bash
# Instead of searching through 20+ files:
scripts/api-key-manager.sh

# Clear functional organization:
scripts/security/api-key-manager.sh
```

### 3. **Scalability**
- Easy to add new tools to appropriate categories
- Clear ownership and responsibility areas
- Consistent naming conventions

### 4. **Consolidation Opportunities**
- Move `mcp-env/` → `mcp/env/`  
- Move `claude-oauth/` → `claude/oauth/`
- Group related MCP scripts: `mcp-*.sh` → `mcp/`

## Migration Strategy

### Phase 1: Create New Structure
```bash
# Create new directories
mkdir -p scripts/{security,system,claude,mcp,utils}
mkdir -p scripts/claude/oauth scripts/mcp/env
```

### Phase 2: Move Files (with symlinks for compatibility)
```bash
# Move and create compatibility symlinks
mv scripts/api-key-manager.sh scripts/security/
ln -s security/api-key-manager.sh scripts/api-key-manager.sh
```

### Phase 3: Update References
- Update Makefile references
- Update documentation  
- Update any hardcoded paths

### Phase 4: Remove Compatibility Layer (after testing)
- Remove old symlinks
- Update all documentation

## Backward Compatibility

**Immediate**: All existing paths continue working via symlinks
**Long-term**: Update references to use new paths
**Documentation**: Reflects new structure with migration notes

## File Mapping

| Current | New Location | Rationale |
|---------|--------------|-----------|
| `api-key-manager.sh` | `security/api-key-manager.sh` | Credential management |
| `env-debug.sh` | `security/env-debug.sh` | Environment security |
| `gpg-manager.sh` | `security/gpg-manager.sh` | Security keys |
| `pass-manager.sh` | `security/pass-manager.sh` | Password management |
| `backup-restore.sh` | `system/backup-restore.sh` | System management |
| `os-detect.sh` | `system/os-detect.sh` | System detection |
| `profile-manager.sh` | `system/profile-manager.sh` | System profiles |
| `validate-config.sh` | `system/validate-config.sh` | System validation |
| `deploy-claude-project.sh` | `claude/deploy-project.sh` | Claude tooling |
| `deploy-claude-user.sh` | `claude/deploy-user.sh` | Claude tooling |
| `fix-claude-ssh-auth.sh` | `claude/fix-ssh-auth.sh` | Claude tooling |
| `claude-oauth/` | `claude/oauth/` | Move existing directory |
| `claude-mcp-extract.sh` | `mcp/extract.sh` | MCP management |
| `extract-mcp-config.py` | `mcp/extract-config.py` | MCP management |
| `mcp-check.sh` | `mcp/check.sh` | MCP management |
| `mcp-sync.sh` | `mcp/sync.sh` | MCP management |
| `sync-mcp-config.sh` | `mcp/sync-config.sh` | MCP management |
| `mcp-env/` | `mcp/env/` | Move existing directory |

## Updated Documentation

The reorganization includes:
- Updated `scripts/README.md` with new structure
- Category-specific README files in each subdirectory
- Clear navigation and discovery
- Migration guide for users

This structure makes the scripts directory much more maintainable and easier to navigate as the project grows.