# Docker Test Cases

Individual test cases for Docker testing infrastructure.

## Test Case Structure

Each test case should be a bash script that:
1. Has a clear purpose and scope
2. Returns 0 for success, non-zero for failure
3. Outputs progress and results
4. Cleans up after itself

## Test Categories

### End User Tests
- Installation workflows
- Backup and restore
- Basic commands
- Profile switching

### Configuration Tests
- Package installation
- Symlink creation
- Configuration validation
- API key management

### Developer Tests
- Code quality (lint, format)
- Documentation sync
- Git hooks
- CI/CD workflows

### Security Tests
- Secret detection
- Permission validation
- GPG operations
- Audit checks

## Adding New Tests

### 1. Create Test Script
```bash
# Copy template
cp tests/docker/test-cases/template.sh tests/docker/test-cases/my-new-test.sh

# Edit the test
vim tests/docker/test-cases/my-new-test.sh
```

### 2. Add to Docker Compose
Edit `docker-compose.incremental.yml` to include your test:

```yaml
my-test-service:
  # ... service definition
  command: >
    bash -c "
      cd dotfiles-source &&
      echo '🧪 Running My Test...' &&
      ./tests/docker/test-cases/my-new-test.sh &&
      echo '✅ My test completed!'
    "
```

### 3. Add to Test Runner
Edit `test-runner.sh` to include your test in the appropriate level.

### 4. Add Makefile Target (Optional)
```makefile
test-my-feature: ## Test my specific feature
	./tests/docker/test-runner.sh my-test
```

## Test Development Workflow

1. **Write the test locally** - Test on your machine first
2. **Add to quick tests** - Fast validation
3. **Move to appropriate level** - Based on execution time
4. **Document the test** - Clear purpose and expectations
5. **Add error handling** - Graceful failure and cleanup

## Example Test Execution

```bash
# Run specific test level
make test-quick         # 30 seconds
make test-unit          # 2-3 minutes  
make test-integration   # 5-10 minutes

# Run specific test (if added to Makefile)
make test-my-feature

# Direct execution
./tests/docker/test-runner.sh quick --verbose
```

## Test Output

All tests output to:
- `tests/logs/test-run-TIMESTAMP.log` - Main output
- `tests/logs/test-errors-TIMESTAMP.log` - Error output
- Docker container logs via `docker-compose logs`

## Common Patterns

### Validation Test
```bash
#!/usr/bin/env bash
# Test: Validate configuration files
set -euo pipefail

echo "🔍 Validating configuration files..."

# Test logic here
if [[ -f "Makefile" ]]; then
    echo "✅ Makefile exists"
else
    echo "❌ Makefile missing"
    exit 1
fi

echo "✅ Configuration validation passed"
```

### Installation Test
```bash
#!/usr/bin/env bash
# Test: Package installation
set -euo pipefail

echo "📦 Testing package installation..."

# Install package
make install-git

# Verify installation
if [[ -L "$HOME/.gitconfig" ]]; then
    echo "✅ Git configuration installed"
else
    echo "❌ Git configuration not found"
    exit 1
fi

echo "✅ Package installation test passed"
```

### Cleanup Test
```bash
#!/usr/bin/env bash
# Test: Cleanup operations
set -euo pipefail

echo "🧹 Testing cleanup operations..."

# Create test files
touch /tmp/test-file

# Run cleanup
make clean

# Verify cleanup
if [[ ! -f "/tmp/test-file" ]]; then
    echo "✅ Cleanup successful"
else
    echo "❌ Cleanup failed"
    exit 1
fi

echo "✅ Cleanup test passed"
```