# Password Store Workflow Quick Reference

## 🎯 The Setup

You have **one GitHub repository** (`smian0/pass-store`) with **two local locations**:

- **`~/.password-store/`** - Your daily workspace 📝
- **`pass-store/`** - Submodule for new machines 🚀

## 📅 Daily Workflow

### Adding Passwords (90% of your usage)

```bash
# Add any new password/API key
pass insert api/service-name

# This automatically:
# ✅ Creates encrypted .gpg file
# ✅ Commits to Git with message
# ✅ Ready to sync

# Sync to GitHub
cd ~/.password-store && git push origin main
```

### Viewing Passwords

```bash
# Command line
pass show api/service-name

# GUI (QtPass)
# Just click on the password in the tree view
```

## 🔄 Periodic Maintenance

### Update Your Dotfiles with Latest Passwords

**When:** After adding several new passwords  
**Why:** So new machine setups get your latest encrypted passwords

```bash
# Go to dotfiles repo
cd /Users/smian/workspaces/mac-dotfiles-secrets

# Pull latest encrypted passwords into submodule
git submodule update --remote pass-store

# Commit the submodule update
git add pass-store
git commit -m "Update pass-store with latest encrypted passwords"
git push origin main
```

## 🆕 New Machine Setup

When you get a new laptop:

```bash
# Clone with submodules
git clone --recursive https://github.com/smian0/mac-dotfiles-secrets.git

# Run master installer
cd mac-dotfiles-secrets
./install-master.sh

# Your encrypted passwords will be available in pass-store/
# Installation script handles setting up ~/.password-store
```

## 🔍 Checking Status

```bash
# Check your working password store
cd ~/.password-store
git status
pass  # List all passwords

# Check submodule status
cd /Users/smian/workspaces/mac-dotfiles-secrets
git submodule status
```

## 🚨 Important Notes

- **Never edit files in `pass-store/` directly** - it's just a deployment copy
- **Always work in `~/.password-store/`** for daily password management
- **Use `pass` commands** - they handle Git commits automatically
- **Both locations contain the same encrypted data** - just different purposes

## 🎯 Memory Aid

| Task | Where | Command |
|------|-------|---------|
| Add password | `~/.password-store` | `pass insert api/service` |
| View password | Anywhere | `pass show api/service` |
| Sync to GitHub | `~/.password-store` | `git push origin main` |
| Update dotfiles | `mac-dotfiles-secrets/` | `git submodule update --remote` |

**Golden Rule**: Daily work happens in `~/.password-store`, everything else is automatic! 🎉