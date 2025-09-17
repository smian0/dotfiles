# OpenCode Shell Function Wrapper - Maintenance Guide

## Overview

This document provides maintenance instructions for the `opencode` shell function wrapper that enables direct `opencode` command usage with automatic Claude agent transformation.

## Architecture

The shell function wrapper provides universal command coverage:

```bash
# Shell function in ~/.zshrc
opencode() {
    # Run our wrapper which handles transformation and calls real opencode
    "$HOME/.local/bin/opencode" "$@"
}
```

**Flow**: `opencode [args]` → shell function → binary wrapper → transformation → real OpenCode

## Installation

### Initial Setup

1. **Create binary wrapper**:
   ```bash
   mkdir -p ~/.local/bin
   cp /path/to/dotfiles/bin/opencode-wrapper ~/.local/bin/opencode
   chmod +x ~/.local/bin/opencode
   ```

2. **Add shell function to ~/.zshrc**:
   ```bash
   # Add to end of ~/.zshrc
   opencode() {
       "$HOME/.local/bin/opencode" "$@"
   }
   ```

3. **Reload shell**:
   ```bash
   exec zsh
   # or
   source ~/.zshrc
   ```

### Verification

```bash
# Check function is defined
type opencode
# Should output: "opencode is a shell function from /Users/username/.zshrc"

# Check binary wrapper exists
ls -la ~/.local/bin/opencode
# Should show executable file

# Test functionality
opencode --version
# Should show transformation logs and OpenCode version
```

## Maintenance Tasks

### Updating the Binary Wrapper

When updating the transformation logic:

1. **Update the binary wrapper**:
   ```bash
   cp /path/to/updated/wrapper ~/.local/bin/opencode
   chmod +x ~/.local/bin/opencode
   ```

2. **Test both commands**:
   ```bash
   ./bin/oc --version          # Original wrapper
   opencode --version          # Shell function wrapper
   ```

3. **Verify transformation**:
   ```bash
   rm ~/.config/opencode/agent/*.md
   opencode run --agent test-agent "hello"
   ```

### Shell Configuration Management

#### Adding to User's Shell

For new users or systems:

```bash
# Check current shell
echo $SHELL

# For zsh users (add to ~/.zshrc)
cat >> ~/.zshrc << 'EOF'

# =============================================================================
# OpenCode Agent Transformation Support  
# =============================================================================
# Shell function to wrap opencode with agent transformation
opencode() {
    # Run our wrapper which handles transformation and calls real opencode
    "$HOME/.local/bin/opencode" "$@"
}
EOF

# For bash users (add to ~/.bashrc)
cat >> ~/.bashrc << 'EOF'

# OpenCode Agent Transformation Support
opencode() {
    "$HOME/.local/bin/opencode" "$@"
}
EOF
```

#### Removing Shell Function

To remove the wrapper and use native OpenCode:

```bash
# Method 1: Comment out in shell config
sed -i.bak '/# OpenCode Agent Transformation/,/^}/s/^/# /' ~/.zshrc

# Method 2: Use unset in current session
unset -f opencode

# Method 3: Reload shell without function
exec zsh
```

### Troubleshooting

#### Function Not Found

**Symptoms**: `opencode: command not found`

**Solutions**:
1. Check if function is defined: `type opencode`
2. Check shell config: `grep -n "opencode" ~/.zshrc`
3. Reload shell: `exec zsh`
4. Add function manually:
   ```bash
   opencode() { "$HOME/.local/bin/opencode" "$@"; }
   ```

#### Function Not Working

**Symptoms**: `opencode` command runs but doesn't transform agents

**Solutions**:
1. Check binary wrapper exists: `ls -la ~/.local/bin/opencode`
2. Test binary directly: `~/.local/bin/opencode --version`
3. Check permissions: `chmod +x ~/.local/bin/opencode`
4. Verify transformation script: `which node && node ~/.../pre-launch-transform.js`

#### Function Conflicts

**Symptoms**: Wrong `opencode` command is executed

**Solutions**:
1. Check all available commands: `which -a opencode`
2. Check function priority: `type opencode`
3. Expected output: `"opencode is a shell function from ~/.zshrc"`
4. If showing binary path, function is not loaded

#### Script Compatibility

**Issue**: Shell function doesn't work in non-interactive scripts

**Solutions**:
- **For scripts**: Use `./bin/oc` instead of `opencode`
- **For automation**: Use absolute paths to avoid shell functions
- **For CI/CD**: Export function or use binary wrapper directly

```bash
# Good for scripts
./bin/oc run --agent my-agent "task"

# Good for automation
/full/path/to/bin/oc run --agent my-agent "task"

# Won't work in scripts (shell function not available)
opencode run --agent my-agent "task"
```

## Performance Considerations

### Function Overhead

The shell function adds minimal overhead:
- **Function call**: ~0.1ms
- **Binary wrapper execution**: ~10ms  
- **Transformation process**: ~50-100ms (only when needed)
- **Total overhead**: ~10-100ms (negligible for interactive use)

### Optimization Tips

1. **Skip transformation for simple commands**:
   The binary wrapper already optimizes this:
   ```bash
   opencode --version    # No transformation needed
   opencode --help       # No transformation needed  
   opencode run --agent  # Transformation runs
   ```

2. **Cache transformed files**:
   The system automatically caches transformed agents and only re-transforms when source files are newer.

## Backup and Recovery

### Backup Current Setup

```bash
# Backup shell configuration
cp ~/.zshrc ~/.zshrc.backup

# Backup binary wrapper
cp ~/.local/bin/opencode ~/.local/bin/opencode.backup

# Create restore script
cat > ~/restore-opencode-wrapper.sh << 'EOF'
#!/bin/bash
echo "Restoring OpenCode wrapper..."
cp ~/.zshrc.backup ~/.zshrc
cp ~/.local/bin/opencode.backup ~/.local/bin/opencode
chmod +x ~/.local/bin/opencode
exec zsh
EOF
chmod +x ~/restore-opencode-wrapper.sh
```

### Recovery Procedures

#### If Shell Function Breaks

```bash
# Quick fix - redefine function
opencode() { "$HOME/.local/bin/opencode" "$@"; }

# Permanent fix - restore from backup
cp ~/.zshrc.backup ~/.zshrc
exec zsh
```

#### If Binary Wrapper Breaks

```bash
# Use original oc wrapper as fallback
alias opencode='./bin/oc'

# Restore binary wrapper
cp ~/.local/bin/opencode.backup ~/.local/bin/opencode
chmod +x ~/.local/bin/opencode
```

#### Complete System Reset

```bash
# Remove shell function
sed -i '/opencode()/,/^}/d' ~/.zshrc

# Remove binary wrapper
rm ~/.local/bin/opencode

# Use only original oc wrapper
# (System falls back to ./bin/oc only)
```

## Testing Procedures

### Automated Testing

```bash
#!/bin/bash
# test-shell-function.sh

echo "Testing OpenCode shell function wrapper..."

# Test 1: Function exists
if type opencode | grep -q "shell function"; then
    echo "✅ Shell function defined"
else
    echo "❌ Shell function not found"
    exit 1
fi

# Test 2: Binary wrapper exists
if [[ -x "$HOME/.local/bin/opencode" ]]; then
    echo "✅ Binary wrapper exists and executable"
else
    echo "❌ Binary wrapper missing or not executable"
    exit 1
fi

# Test 3: Function calls wrapper
if opencode --version 2>&1 | grep -q "OpenCode Wrapper"; then
    echo "✅ Function successfully calls wrapper"
else
    echo "❌ Function not calling wrapper"
    exit 1
fi

# Test 4: Transformation works
rm -f ~/.config/opencode/agent/test-agent.md
if opencode run --agent claude-test-agent "test" 2>&1 | grep -q "Pre-Launch Transform"; then
    echo "✅ Transformation pipeline works"
else
    echo "❌ Transformation pipeline failed"
    exit 1
fi

echo "🎉 All tests passed!"
```

### Manual Testing Checklist

- [ ] `type opencode` shows shell function
- [ ] `opencode --version` shows wrapper logs and version
- [ ] `opencode run --agent test-agent "hello"` works
- [ ] Both `oc` and `opencode` produce identical results
- [ ] Function works after shell reload (`exec zsh`)
- [ ] Binary wrapper can be called directly: `~/.local/bin/opencode --version`

## Distribution

### Package for Other Users

```bash
#!/bin/bash
# install-opencode-wrapper.sh

echo "Installing OpenCode shell function wrapper..."

# Create local bin directory
mkdir -p ~/.local/bin

# Copy binary wrapper
cp /path/to/wrapper ~/.local/bin/opencode
chmod +x ~/.local/bin/opencode

# Add shell function to appropriate config
if [[ "$SHELL" == */zsh ]]; then
    CONFIG_FILE="$HOME/.zshrc"
elif [[ "$SHELL" == */bash ]]; then
    CONFIG_FILE="$HOME/.bashrc"
else
    echo "Warning: Unsupported shell $SHELL"
    CONFIG_FILE="$HOME/.profile"
fi

# Add function if not already present
if ! grep -q "opencode()" "$CONFIG_FILE"; then
    cat >> "$CONFIG_FILE" << 'EOF'

# OpenCode Agent Transformation Support
opencode() {
    "$HOME/.local/bin/opencode" "$@"
}
EOF
    echo "✅ Shell function added to $CONFIG_FILE"
else
    echo "✅ Shell function already exists in $CONFIG_FILE"
fi

echo "🎉 Installation complete!"
echo "Run 'exec $(basename $SHELL)' to reload your shell"
```

## Migration

### From oc-only to Universal Coverage

Existing users with only `./bin/oc` can add shell function support:

```bash
# Install binary wrapper
mkdir -p ~/.local/bin
cp ./bin/oc ~/.local/bin/opencode
chmod +x ~/.local/bin/opencode

# Add shell function
echo 'opencode() { "$HOME/.local/bin/opencode" "$@"; }' >> ~/.zshrc
exec zsh

# Test both commands work
./bin/oc --version     # Original
opencode --version     # New shell function
```

### From Shell Function to oc-only

To remove shell function and use only `./bin/oc`:

```bash
# Remove shell function
sed -i '/opencode()/,/^}/d' ~/.zshrc

# Remove binary wrapper
rm ~/.local/bin/opencode

# Reload shell
exec zsh

# Use only original wrapper
./bin/oc --version
```

## Security Considerations

### Shell Function Safety

- **Path injection**: Shell function uses absolute path to prevent PATH manipulation
- **Argument passing**: All arguments passed safely with `"$@"`
- **Execution safety**: No eval or dynamic code execution in function

### Binary Wrapper Security

- **Location security**: Wrapper stored in user's local bin, not system-wide
- **Permission model**: Only user can modify their own wrapper
- **Execution chain**: Clear chain of execution without privilege escalation

### Recommendations

1. **Verify wrapper integrity**: Check binary wrapper hasn't been modified
2. **Monitor function definition**: Ensure shell function hasn't been altered
3. **Use version control**: Keep wrapper and shell config in version control
4. **Regular testing**: Test functionality periodically to detect issues

---

This maintenance guide ensures reliable operation and easy troubleshooting of the OpenCode shell function wrapper system.