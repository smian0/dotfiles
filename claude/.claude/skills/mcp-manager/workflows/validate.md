# Workflow: Validate MCP Configuration

**Purpose**: Comprehensive validation of MCP server configurations for consistency and correctness

**Pattern**: User wants to check MCP configuration health before committing or after manual edits

## Trigger Conditions

✅ This workflow activates when:
- After manual edits to `.mcp.json` or `settings.json`
- Before committing configuration changes
- During CI/CD pipeline
- Debugging MCP server loading issues
- After pulling changes from team

## Execution Steps

**Step 1: Run full validation**

```bash
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
```

Expected: Pass all validation checks or report specific errors.

**Step 2: Review validation results**

**If validation passes:**
```
✅ JSON syntax: Valid
✅ Required fields: Present
✅ Server-permission consistency: OK
✅ No duplicate server names
✅ Command paths: Valid
✅ Environment variable format: OK

Configuration is valid!
```

**If validation fails:**
```
❌ JSON syntax error in ~/.claude/.mcp.json (line 15)
❌ Orphaned permissions: mcp__old-server__*
⚠️ Server 'my-server' missing permissions in settings.json

Fix these issues and re-run validation.
```

**Step 3: Fix identified issues**

**JSON syntax errors:**
```bash
# Check syntax
jq . ~/.claude/.mcp.json

# Common issues:
# - Missing/extra commas
# - Unquoted keys
# - Trailing commas in objects/arrays
```

**Orphaned permissions:**
```bash
# Remove permissions for non-existent servers
vim ~/.claude/settings.json
# Delete lines starting with "mcp__removed-server__"
```

**Missing permissions:**
```bash
# Add permissions for server tools
vim ~/.claude/settings.json
# Add: "mcp__server-name__tool-name"
```

**Step 4: Re-run validation**

```bash
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
```

Expected: All checks pass.

**Step 5: Commit validated configuration**

```bash
cd ~/dotfiles  # or project directory
git add claude/.claude/.mcp.json claude/.claude/settings.json
git commit -m "fix: validate and correct MCP configuration"
```

## Validation Modes

### Syntax-Only Mode

Check only JSON syntax:

```bash
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh --syntax-only
```

**Checks:**
- Valid JSON in `.mcp.json`
- Valid JSON in `settings.json`
- No parse errors

**Use when:** Quick check before committing.

### Consistency-Only Mode

Check only server-permission consistency:

```bash
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh --consistency-only
```

**Checks:**
- All servers have matching permissions
- No orphaned permissions
- Permission naming follows convention

**Use when:** After adding/removing servers.

### Auto-Fix Mode

Attempt automatic fixes for common issues:

```bash
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh --fix
```

**Can auto-fix:**
- Remove orphaned permissions
- Add missing permission placeholders
- Fix permission naming format

**Cannot auto-fix:**
- JSON syntax errors (manual fix required)
- Invalid command paths
- Malformed environment variables

**Use when:** Quick cleanup of minor issues.

### Report Mode

Generate detailed validation report:

```bash
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh --report
```

Output saved to: `~/.claude/mcp-validation-report.txt`

**Use when:** Debugging complex configuration issues or for documentation.

## What Gets Validated

### JSON Syntax

- ✅ `.mcp.json` parses without errors
- ✅ `settings.json` parses without errors
- ✅ All values properly quoted
- ✅ No trailing commas
- ✅ Proper nesting

### Required Fields

For each server in `.mcp.json`:
- ✅ `command` field present
- ✅ `args` array present (can be empty)
- ✅ `type` field present ("stdio", "sse", or "http")

Optional but validated if present:
- `description` (string)
- `env` (object with string values)

### Server-Permission Consistency

- ✅ Each server has at least one permission in `settings.json`
- ✅ No permissions for non-existent servers (orphaned)
- ✅ Permission format: `mcp__<server>__<tool>` or `mcp__<server>__*`

### Server Names

- ✅ No duplicate server names
- ✅ Names follow convention (lowercase, hyphens, no spaces)

### Command Paths

- ✅ Commands exist in PATH: `which <command>`
- ⚠️ Warning if command not found (may be installed later)

### Environment Variables

- ✅ Format: `${VAR_NAME}` for variable substitution
- ✅ Or literal strings for static values
- ✅ No malformed placeholders

## Integration with Main Skill

**Before validation (see main skill):**
- Core Concepts: Understanding configuration structure
- Configuration Files: What `.mcp.json` and `settings.json` contain

**After validation (see main skill):**
- Add workflow: How to add servers correctly
- Remove workflow: How to clean up servers
- Best Practices: When to validate

## Error Handling

**Validation script not found:**
```bash
# Check script exists
ls -la ~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh

# Ensure execute permissions
chmod +x ~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
```

**jq command not found:**
```bash
# Install jq
brew install jq  # macOS
sudo apt install jq  # Linux
```

**Validation reports errors but config looks correct:**
- Check for hidden characters in JSON files
- Verify Stow symlinks not broken: `ls -la ~/.claude/.mcp.json`
- Try: `cat ~/.claude/.mcp.json | jq .` for clean reformat

## Example: Full Validation Workflow

```bash
# 1. After editing MCP config
vim ~/.claude/.mcp.json
# (make changes)

# 2. Quick syntax check
jq . ~/.claude/.mcp.json
# Expected: Reformatted JSON output (no errors)

# 3. Run full validation
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh

# 4. If errors found, fix them
# Example: Orphaned permission detected
vim ~/.claude/settings.json
# Remove: "mcp__old-server__*"

# 5. Re-validate
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
# Expected: ✅ All checks pass

# 6. Check consistency
~/.claude/skills/mcp-manager/scripts/check-mcp-consistency.sh
# Expected: Consistent

# 7. Commit
cd ~/dotfiles
git add claude/.claude/.mcp.json claude/.claude/settings.json
git commit -m "feat: add new MCP server (validated)"
```

## Best Practices

### When to Validate

**Always validate before:**
- Committing configuration changes
- Pushing to shared repository
- Restarting Claude Code
- Deploying to production

**Validate after:**
- Any manual edits to `.mcp.json` or `settings.json`
- Pulling changes from team
- Adding/removing servers
- Modifying permissions

### Validation in CI/CD

Add to CI pipeline:

```yaml
# .github/workflows/validate-mcp.yml
steps:
  - name: Validate MCP Configuration
    run: |
      ./claude/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
      if [ $? -ne 0 ]; then
        echo "❌ MCP configuration invalid"
        exit 1
      fi
```

### Pre-Commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
if git diff --cached --name-only | grep -q ".mcp.json\|settings.json"; then
  echo "Validating MCP configuration..."
  ~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
  if [ $? -ne 0 ]; then
    echo "❌ MCP validation failed. Fix errors before committing."
    exit 1
  fi
fi
```

## Checklist

**Pre-validation:**
- [ ] All edits completed
- [ ] JSON files saved
- [ ] No unsaved changes

**Running validation:**
- [ ] Full validation passes
- [ ] No syntax errors
- [ ] No consistency issues
- [ ] All warnings reviewed

**Post-validation:**
- [ ] Errors fixed (if any)
- [ ] Re-validated successfully
- [ ] Ready to commit
- [ ] Documentation updated (if needed)
