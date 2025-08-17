# Claude Code Configuration Guide

This guide explains the multi-level Claude Code configuration system and how to manage different profiles.

## Configuration Architecture

### Two-Tier System

1. **User-Level Settings** (`claude-user/`)
   - Deploys to `~/.claude/`
   - Global preferences for all Claude Code sessions
   - Personal commands available everywhere

2. **Project-Level Settings** (`claude-project/`)
   - Deploys to project `.claude/` directories
   - Project-specific configurations and overrides
   - CLAUDE.md guidance files

### Configuration Hierarchy

Claude Code applies settings in order of precedence:
1. Command line arguments (highest)
2. Local project settings (`.claude/settings.local.json`)
3. Shared project settings (`.claude/settings.json`)
4. User settings (`~/.claude/settings.json`) (lowest)

## Installation Commands

### Install All Claude Configurations
```bash
make install-claude      # Install both user and experimental profiles
```

### Install Specific Profiles
```bash
make install-git         # Git configuration only
./install.sh claude-default      # Default Claude profile
./install.sh claude-experimental # Experimental Claude profile
```

## Profile Management

### Deploy User Settings Globally
```bash
# Method 1: Using helper script (recommended)
./scripts/deploy-claude-user.sh

# Method 2: Using stow directly
stow -t ~ claude-user
```

### Deploy Project Settings
```bash
# To specific project
./scripts/deploy-claude-project.sh /path/to/project

# To current directory
./scripts/deploy-claude-project.sh .

# Using stow directly
stow -t /path/to/project claude-project
```

## Configuration Files

### User-Level Files (`~/.claude/`)
- `settings.json` - Global user preferences
- `commands/` - Personal commands available everywhere
- `agents/` - User-specific agents

### Project-Level Files (`.claude/`)
- `settings.json` - Shared project settings (committed to git)
- `settings.local.json` - Personal project preferences (not committed)
- `commands/` - Project-specific commands
- `agents/` - Project agents
- `CLAUDE.md` - Project guidance and context

## Example Configurations

### User Settings (`~/.claude/settings.json`)
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "allowedTools": [
    "Edit",
    "Read", 
    "Bash(git *)",
    "Bash(npm *)"
  ],
  "environmentVariables": {
    "EDITOR": "vim"
  }
}
```

### Project Settings (`.claude/settings.json`)
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "allowedTools": [
    "Edit",
    "Read",
    "Bash(npm run *)",
    "Bash(docker *)",
    "mcp__*"
  ],
  "environmentVariables": {
    "NODE_ENV": "development"
  }
}
```

### Local Project Settings (`.claude/settings.local.json`)
```json
{
  "model": "claude-3-opus-20240229",
  "temperature": 0.1,
  "environmentVariables": {
    "DEBUG": "true"
  }
}
```

## Commands and Agents

### Creating Project Commands
1. Add to `.claude/commands/`
2. Use markdown format with clear instructions
3. Example command file:

```markdown
# Deploy Application

Deploy the application to staging environment.

Steps:
1. Run tests: `npm test`
2. Build application: `npm run build`
3. Deploy: `npm run deploy:staging`
4. Verify deployment with health check
```

### Creating Project Agents
1. Add to `.claude/agents/`
2. Define specific roles and capabilities
3. Include tool permissions and context

## Profile Switching

### Switch Between Profiles
```bash
# Switch to experimental profile
stow -D claude-default
stow claude-experimental

# Switch back to default
stow -D claude-experimental  
stow claude-default
```

### Check Current Profile
```bash
make profile-status         # Show installation status
ls -la ~/.claude           # Check symlink targets
```

## Backup and Restore

### Automatic Backups
Deployment scripts create automatic backups:
- User: `~/.claude.backup.YYYYMMDD_HHMMSS`
- Project: `<project>/.claude.backup.YYYYMMDD_HHMMSS`

### Manual Backup
```bash
# Backup current configuration
cp -r ~/.claude ~/.claude.backup.$(date +%Y%m%d_%H%M%S)

# Backup project configuration
cp -r .claude .claude.backup.$(date +%Y%m%d_%H%M%S)
```

### Restore from Backup
```bash
# Restore user settings
rm -rf ~/.claude
mv ~/.claude.backup.YYYYMMDD_HHMMSS ~/.claude

# Restore project settings
rm -rf .claude
mv .claude.backup.YYYYMMDD_HHMMSS .claude
```

## Setting Up New Projects

### 1. Navigate to Project
```bash
cd /path/to/your/project
```

### 2. Deploy Claude Settings
```bash
~/.dotfiles/scripts/deploy-claude-project.sh .
```

### 3. Customize for Project
```bash
# Edit project guidance
vim CLAUDE.md

# Adjust project settings
vim .claude/settings.json

# Add personal preferences (not committed)
vim .claude/settings.local.json
```

### 4. Add to Git (Optional)
```bash
git add .claude/settings.json CLAUDE.md
git add .claude/commands/ .claude/agents/
git commit -m "Add Claude Code configuration"
```

## Use Cases

### User-Level Configuration
- Set preferred AI model globally
- Configure default tool permissions
- Add personal productivity commands
- Set environment variables for all projects

### Project-Level Configuration  
- Project-specific tool permissions
- Custom commands for project workflows
- Project architecture and coding patterns
- Team-shared agents and workflows

### Local Project Configuration
- Personal model preferences for specific projects
- Debug settings and development flags
- Individual developer customizations
- Temporary experimental settings

## Troubleshooting

### Configuration Not Loading
1. Check file permissions: `ls -la ~/.claude`
2. Validate JSON syntax: `cat ~/.claude/settings.json | python -m json.tool`
3. Review Claude Code logs

### Symlink Issues
```bash
# Check symlink status
ls -la ~/.claude

# Restow if needed
stow --restow claude-user
```

### Command Conflicts
1. Check command precedence (local > project > user)
2. Rename conflicting commands
3. Use unique command names

### Missing Tools
1. Review `allowedTools` configuration
2. Check tool availability: `which tool-name`
3. Update tool permissions in settings

## Advanced Configuration

### MCP Integration
Configure MCP servers in project settings:
```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "--package=task-master-ai", "task-master-ai"]
    }
  }
}
```

### Custom Tool Permissions
```json
{
  "allowedTools": [
    "Edit",
    "Read",
    "Bash(make *)",
    "Bash(docker compose *)",
    "mcp__task_master_ai__*"
  ]
}
```

For more examples, see the configuration files in `claude-user/` and `claude-project/` directories.