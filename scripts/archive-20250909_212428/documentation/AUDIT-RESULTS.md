# Scripts Audit Results

## 🔍 Outdated Scripts Found

### ❌ Explicitly Deprecated

1. **`scripts/mcp/extract.sh`** - Contains deprecation warning
   - **Status**: Marked as deprecated in header comment
   - **Replacement**: Use `zsh/mcp-config.zsh` functions (`mcpg`, `mcpls`, etc.)
   - **Action**: Consider removing

2. **`scripts/mcp/extract-config.py`** - Legacy tool
   - **Status**: Marked as "Legacy" in README.md
   - **Replacement**: zsh functions provide same functionality
   - **Action**: Consider removing if no longer needed

### ⚠️ Broken Paths After Reorganization

The following scripts calculate `DOTFILES_DIR` incorrectly after moving to subdirectories:

1. **`scripts/claude/deploy-project.sh`**
   - **Issue**: `DOTFILES_DIR="$(dirname "$SCRIPT_DIR")"` now points to `/scripts/` instead of root
   - **Fix**: Change to `DOTFILES_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"`

2. **`scripts/claude/deploy-user.sh`**
   - **Issue**: Same path calculation problem
   - **Fix**: Same as above

3. **`scripts/mcp/sync.sh`**
   - **Issue**: Path calculation broken
   - **Fix**: Update path calculation

4. **`scripts/mcp/sync-config.sh`**
   - **Issue**: Path calculation broken
   - **Fix**: Update path calculation

5. **`scripts/mcp/check.sh`**
   - **Issue**: Path calculation broken
   - **Fix**: Update path calculation

### 🔗 Outdated References

1. **`scripts/security/pass-manager.sh`**
   - **Issue**: References `git@github.com:smian0/pass-store.git`
   - **Note**: May need updating if repo was renamed to match new `pass/` directory

### 💡 Redundant/Tiny Wrappers

1. **`scripts/mcp/sync.sh`** (10 lines)
   - **Purpose**: Just calls `sync-config.sh`
   - **Consider**: Whether this wrapper adds value

## ✅ Scripts That Look Good

### Security Scripts
- **api-key-manager.sh** - Core functionality, actively used
- **env-debug.sh** - Recently created, highly useful
- **gpg-manager.sh** - Essential GPG management
- **pass-manager.sh** - Core pass functionality (just needs repo URL update)

### System Scripts
- **backup-restore.sh** - Essential backup functionality
- **install-by-environment.sh** - Smart environment detection
- **npm-packages.sh** - Recent, package management
- **os-detect.sh** - Cross-platform compatibility
- **profile-manager.sh** - Recent, profile system
- **validate-config.sh** - Configuration validation

### Claude Scripts
- **fix-ssh-auth.sh** - Specific Claude issue resolution
- **OAuth tools** - Complete authentication system

### MCP Scripts
- **sync-config.sh** - Core MCP synchronization (after path fix)
- **check.sh** - Configuration validation (after path fix)

## 📋 Recommended Actions

### Immediate (High Priority)
1. **Fix broken paths** in 5 scripts due to reorganization
2. **Remove deprecated** `mcp/extract.sh` 
3. **Update pass-manager.sh** repo URL if needed

### Consider (Medium Priority)
1. **Remove legacy** `mcp/extract-config.py` if zsh functions fully replace it
2. **Simplify** `mcp/sync.sh` or remove wrapper

### Later (Low Priority)
1. **Standardize** error handling across all scripts
2. **Add** `--help` support to scripts missing it
3. **Document** which scripts are user-facing vs internal

## 🎯 Summary

**Scripts Status:**
- ✅ **20 scripts** are current and useful
- ⚠️ **5 scripts** need path fixes (broken by reorganization)
- ❌ **2 scripts** are deprecated/legacy
- 🔗 **1 script** has outdated reference

**Overall Assessment:** Most scripts are in good shape, but the reorganization broke some path calculations that need immediate fixing.