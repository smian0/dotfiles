# Claude Code System Prompt Configuration

Documentation for configuring system prompts and behavioral modifications in Claude Code (2025).

## Configuration Hierarchy

Claude Code uses multiple layers for system prompt configuration:

1. **Core System Prompt** (internal, not directly modifiable)
2. **Output Styles** (modify system prompt directly)
3. **CLAUDE.md Files** (add as user messages)
4. **Command-line Flags** (session-specific modifications)

## Current Setup Status

✅ **Global CLAUDE.md**: `/Users/smian/.claude/CLAUDE.md` (SuperClaude + CCPM integration)  
✅ **Project CLAUDE.md**: `/Users/smian/dotfiles/CLAUDE.md` (dotfiles-specific instructions)  
✅ **Settings Configuration**: `claude/.claude/settings.json` (timeout settings configured)

## System Prompt Modification Methods

### 1. Output Styles (Recommended)

**Purpose**: Directly modify Claude's system prompt for different behavioral modes.

**Configuration**:
```json
{
  "outputStyle": {
    "name": "custom-style-name"
  }
}
```

**Implementation Options**:

#### Option A: Command-Based Creation
```bash
# Interactive style creation
/output-style:new

# Switch to existing style
/output-style [style-name]

# View available styles
/output-style
```

#### Option B: File-Based Creation
Create files in `~/.claude/output-styles/` or `.claude/output-styles/`:

```markdown
---
name: "Security-First Developer"
description: "Emphasizes security and best practices"
---

# Security-Focused Development Mode

You are a senior security engineer and developer. Always:

## Security Priorities
- Identify potential security vulnerabilities
- Suggest secure coding practices
- Validate input/output sanitization
- Check for authentication/authorization issues

## Development Standards
- Follow OWASP guidelines
- Implement defense in depth
- Use secure dependencies
- Include comprehensive error handling

## Code Review Focus
- Security implications of changes
- Performance impact analysis  
- Maintainability and documentation
- Test coverage requirements
```

### 2. Command-Line Modification

**--append-system-prompt Flag** (v1.0.51+):
```bash
# Session-specific system prompt addition
claude --append-system-prompt "Focus on TypeScript best practices and include comprehensive tests"

# Can be combined with other flags
claude --model claude-opus-4-1-20250805 \
       --append-system-prompt "Working in WSL2 environment. Use 'service' not 'systemctl'" \
       --max-tokens 8192
```

**Limitations**:
- Command-line only (not configurable in settings.json)
- Session-specific (doesn't persist)
- Appends to existing prompt (doesn't replace)

### 3. CLAUDE.md Files (Current Method)

**How it works**:
- Adds content as user message (not system prompt modification)
- Hierarchical: Global → Project → Directory specific
- Persistent across sessions

**Current Hierarchy**:
```
~/.claude/CLAUDE.md               # Global (SuperClaude + CCPM)
/Users/smian/dotfiles/CLAUDE.md   # Project-specific
```

## Configuration Strategies

### Strategy 1: Output Style Profiles

Create different output styles for different work contexts:

```bash
# Development styles
~/.claude/output-styles/security-focused.md
~/.claude/output-styles/performance-optimized.md
~/.claude/output-styles/documentation-heavy.md

# Project-specific styles
.claude/output-styles/dotfiles-maintenance.md
.claude/output-styles/system-administration.md
```

### Strategy 2: Command Aliases

For frequently used system prompt modifications:

```bash
# Add to ~/.zshrc
alias claude-sec='claude --append-system-prompt "Prioritize security in all recommendations"'
alias claude-perf='claude --append-system-prompt "Focus on performance optimization"'
alias claude-docs='claude --append-system-prompt "Include comprehensive documentation"'
```

### Strategy 3: Hybrid Approach

Combine methods for maximum flexibility:

1. **Base configuration**: CLAUDE.md for persistent project context
2. **Role-specific**: Output styles for different developer personas
3. **Session-specific**: Command flags for temporary modifications

## Implementation Examples

### Example 1: Security-Focused Output Style

File: `~/.claude/output-styles/security-first.md`
```markdown
---
name: "Security-First Developer"
description: "Emphasizes security and compliance"
---

You are a security-conscious senior developer. For every task:

1. **Security Assessment**: Identify potential vulnerabilities
2. **Compliance Check**: Ensure adherence to security standards
3. **Risk Evaluation**: Assess impact of proposed changes
4. **Mitigation Strategies**: Suggest security improvements
5. **Best Practices**: Apply OWASP, NIST guidelines
```

### Example 2: Documentation-Heavy Style

File: `~/.claude/output-styles/documentation-focused.md`
```markdown
---
name: "Documentation Expert"
description: "Prioritizes clear, comprehensive documentation"
---

You are a technical writer and developer. Always include:

- **Comprehensive docstrings**: For all functions/classes
- **README updates**: When adding new features
- **Inline comments**: For complex logic
- **Usage examples**: Practical implementation examples
- **Architecture notes**: High-level design decisions
```

## Advanced Configuration

### Conditional System Prompts

Using hooks to modify behavior based on context:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*.py",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Python development session - focus on type hints and testing'"
          }
        ]
      }
    ]
  }
}
```

### Profile-Based System Prompts

Integrate with the existing profile system:

```bash
# Different prompts for different profiles
claude-profile switch minimal && claude --append-system-prompt "Focus on essential tasks only"
claude-profile switch full && claude --append-system-prompt "Comprehensive analysis mode"
```

## Best Practices

### 1. Layered Approach
- **Global CLAUDE.md**: Persistent behavioral guidelines
- **Output Styles**: Role-specific system prompt modifications  
- **Command Flags**: Session-specific adjustments

### 2. Context Awareness
- Use different styles for different types of work
- Consider token efficiency (align with MODE_Token_Efficiency)
- Match complexity to task requirements

### 3. Maintainability
- Keep styles focused and specific
- Document style purposes clearly
- Version control custom styles
- Regular review and updates

## Troubleshooting

### Common Issues

1. **Output style not taking effect**: Ensure style file exists and has correct metadata
2. **Command flag ignored**: Verify Claude Code version (--append-system-prompt requires v1.0.51+)
3. **Conflicts between methods**: Output styles override system prompt; CLAUDE.md adds user context

### Verification

Test system prompt modifications:
```bash
# Ask Claude to describe its current instructions
echo "What are your current behavioral guidelines?" | claude
```

## Migration Path

### From CLAUDE.md to Output Styles

1. **Identify behavioral instructions** in current CLAUDE.md
2. **Extract system-level guidelines** (not project context)
3. **Create output style** with extracted content
4. **Test behavior changes**
5. **Update project CLAUDE.md** to remove duplicated content

---

*Last Updated: September 2025*  
*Status: Research completed - implementation pending*