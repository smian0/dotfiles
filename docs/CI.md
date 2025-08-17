# Continuous Integration (CI) Setup

## GitHub Actions Configuration

This project uses GitHub Actions for automated testing on every push and pull request.

## Why It's Safe

### 1. **Isolated Test Environment**
- Tests run in `tests/test-environment/` directory
- No system files are modified
- All operations are sandboxed

### 2. **Dry-Run Mode**
- The CI only runs `--dry-run` mode of installation scripts
- No actual installation happens on GitHub runners
- Only simulation and validation

### 3. **Read-Only Operations**
- Tests primarily validate structure and syntax
- No GPG keys are created or imported
- No passwords are stored or accessed

### 4. **macOS Runners**
- GitHub provides clean macOS VMs for each run
- Runners are destroyed after job completion
- No persistent state between runs

## What Gets Tested

### Test Job (Primary)
- ✅ ShellSpec unit tests
- ✅ Script syntax validation
- ✅ Directory structure verification
- ✅ Dry-run installation simulation

### Validate Job
- ✅ ShellCheck linting
- ✅ File permission checks
- ✅ Script executability

### Coverage Job (Optional)
- ✅ Code coverage with bashcov
- ✅ Coverage reports as artifacts
- ✅ Only runs on main branch pushes

## Security Considerations

### Safe Practices
- **No secrets in tests** - Tests don't use real API keys
- **No real passwords** - Pass store tests use mock data
- **No system modifications** - Everything runs in isolation
- **Submodules are public** - No private data in submodules

### What's NOT Tested in CI
- Actual GPG key generation
- Real pass password store operations
- Actual Homebrew package installation
- System-wide configuration changes
- Claude Code API connections

## Workflow Triggers

```yaml
on:
  push:
    branches: [ main ]      # On push to main
  pull_request:
    branches: [ main ]      # On PRs to main
  workflow_dispatch:        # Manual trigger
```

## Test Matrix

Tests run on multiple macOS versions:
- macOS 13 (Ventura)
- macOS 14 (Sonoma)

## Artifacts

The workflow saves:
- Test results
- Test environment contents
- Coverage reports (if generated)

Artifacts are retained for 7-30 days.

## Local vs CI Testing

| Aspect | Local | GitHub Actions |
|--------|-------|----------------|
| Full installation | ✅ Can test | ❌ Dry-run only |
| GPG operations | ✅ Full testing | ❌ Skipped |
| Pass store | ✅ Can initialize | ❌ Mock only |
| Coverage | ✅ Full bashcov | ⚠️ Best effort |
| Performance | ✅ Real timing | ⚠️ Slower runners |

## Monitoring CI

### View Status
- Check badge on README
- Visit Actions tab on GitHub
- Review workflow runs

### Debug Failures
1. Check the workflow logs
2. Download artifacts for test environment
3. Run tests locally with same configuration
4. Fix and push updates

## Cost Considerations

GitHub Actions provides:
- **2,000 minutes/month free** for private repos
- **macOS runners use 10x minutes** (1 min = 10 min counted)
- Effective: ~200 macOS minutes/month free

Our typical run:
- ~3-5 minutes per job
- 3 jobs × 2 OS versions = ~30-50 minutes counted
- Well within free tier for reasonable usage

## Enabling/Disabling

### To Enable
Push the workflow file - it auto-enables

### To Disable
1. Go to Settings → Actions
2. Disable Actions for this repository

### To Modify
Edit `.github/workflows/test.yml` and push changes

## Best Practices

1. **Keep tests fast** - Under 5 minutes total
2. **Use dry-run** - Don't modify runner systems
3. **Cache dependencies** - Speeds up runs
4. **Matrix wisely** - Test key OS versions only
5. **Fail fast** - Stop on first failure