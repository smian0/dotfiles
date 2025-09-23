# Claude Package Maintenance Instructions

This file provides instructions for Claude Code to maintain the `claude` package stow configuration.

## Automatic Verification Requirements

### When to Check Stow Status
You should automatically verify the stow status when:
1. **Any file is modified** in `/Users/smian/dotfiles/claude/`
2. **New files are added** to the claude package
3. **Files are deleted** from the claude package
4. **User reports issues** with Claude configuration not working
5. **After running** `stow claude` or any stow-related commands

### Verification Steps
When changes are detected, automatically:

1. **Run the verification script:**
   ```bash
   bash ~/dotfiles/scripts/verify-claude-stow.sh
   ```

2. **Check for conflicts:**
   ```bash
   cd ~/dotfiles && stow --no --verbose claude 2>&1 | grep -v "simulation mode"
   ```

3. **If issues are found**, alert the user and suggest:
   ```bash
   cd ~/dotfiles && stow -R claude  # Restow the package
   ```

## Documentation Maintenance

### README.md Updates
The `/Users/smian/dotfiles/claude/README.md` should be kept current with:

1. **Package Status** - Update the "Current Status" section when:
   - New files/directories are added
   - Configuration structure changes
   - Stow behavior changes

2. **File Inventory** - Maintain an accurate list of:
   - All configuration files
   - Their purposes
   - Symlink status (direct vs tree-folded)

3. **Last Verified** timestamp - Update after each verification

### Update Template for README.md
When updating, include:
```markdown
## Current Status
- **Last Verified:** [DATE TIME]
- **Verification Method:** verify-claude-stow.sh
- **Status:** ✅ Fully Stowed / ⚠️ Issues Found
- **Total Items:** [COUNT]
- **Symlinked Items:** [COUNT]
- **Tree-folded Directories:** [COUNT]
```

## Proactive Monitoring

### File Change Detection
When working in the claude package, monitor for:
- New files without corresponding symlinks
- Broken symlinks in `~/.claude/`
- Files that should be symlinks but aren't
- Conflicts between stowed and non-stowed files

### Automatic Fixes
When safe, automatically fix issues:
1. **Missing symlinks** - Run `stow claude`
2. **Stale symlinks** - Remove and restow
3. **Regular files blocking symlinks** - Alert user, backup, then fix

## Critical Files to Monitor

Priority files that MUST always be properly symlinked:
1. `settings.json` - Main configuration
2. `scripts/statusline.sh` - Status bar functionality
3. `hooks/` - Event handlers
4. `.mcp.json` - MCP server configuration
5. `profiles/` - Configuration profiles

## Reporting Format

When reporting stow status to the user, use this format:
```
Claude Package Stow Status:
✅ All systems operational
- 19/19 items properly symlinked
- No conflicts detected
- Statusline: Active
- Last check: [timestamp]
```

Or for issues:
```
⚠️ Claude Package Issues Detected:
- settings.json is not symlinked (critical)
- 2 conflicts found
- Run: cd ~/dotfiles && stow -R claude
```

## Integration with Other Tools

### Makefile Integration
Suggest adding to ~/dotfiles/Makefile:
```makefile
verify-claude:
	@bash scripts/verify-claude-stow.sh

.PHONY: verify-claude
```

### Git Hook Integration
Check stow status before commits affecting claude package.

## Auto-Recovery Procedures

If verification fails:
1. First attempt: `stow -R claude` (restow)
2. If conflicts exist: Backup conflicts, remove, restow
3. If still failing: Alert user with specific conflict details

## Code and Configuration Principles

### DRY (Don't Repeat Yourself) & YAGNI (You Aren't Gonna Need It)
When maintaining configurations and scripts:
- **DRY**: Avoid duplicating configuration patterns - use references, templates, or shared configs instead
- **YAGNI**: Only add features/configurations when actually needed, not "just in case"
- Examples:
  - Use symlinks rather than copying identical configs
  - Reference existing scripts instead of reimplementing functionality
  - Add new hooks/profiles only when there's an immediate use case

## Documentation Standards

When updating documentation:
1. Use consistent formatting
2. Include timestamps
3. Provide actionable solutions
4. Keep technical details in STOW-SETUP.md
5. Keep user-facing info in README.md

---
**Remember:** Always verify changes don't break existing functionality.
**Priority:** Statusline functionality is critical - always verify it works.