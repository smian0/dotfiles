# Migration Guide

## Overview

This guide helps migrate from existing SuperClaude commands to the unified SuperClaudeExt skill framework.

## Command Mapping

### Business Commands

| Legacy Command | New Command | Direct Agent Access |
|---------------|-------------|-------------------|
| `/biz:panel` | `/biz:panel` (preserved) | `@superclaude-ext/business-panel` |
| `/biz:prd` | `/biz:prd` (preserved) | `@superclaude-ext/prd-manager` |
| `/biz:review` | `/biz:review` (preserved) | `@superclaude-ext/product-reviewer` |
| `/biz:research` | `/biz:research` (preserved) | `@superclaude-ext/market-intel` |

### Macro Commands

| Legacy Command | New Command | Direct Agent Access |
|---------------|-------------|-------------------|
| `/macro:brief` | `/macro:brief` (preserved) | `@superclaude-ext/macro-analyst` |
| `/macro:analyze` | `/macro:analyze` (preserved) | `@superclaude-ext/market-analyzer` |
| `/macro:research` | `/macro:research` (preserved) | `@superclaude-ext/research-assistant` |

### System Commands

| Legacy Command | New Command | Direct Agent Access |
|---------------|-------------|-------------------|
| `/sys:generate` | `/sys:generate` (preserved) | `@superclaude-ext/meta-builder` |
| `/sys:validate` | `/sys:validate` (preserved) | `@superclaude-ext/framework-validator` |

## Key Differences

### Automatic Activation
**Old Way**: Required explicit slash commands
```
/biz:panel analyze our market position
```

**New Way**: Natural language triggers
```
I need a business analysis of our market position
→ Automatically routes to business-panel
```

### Unified Entry Point
**Old Way**: Multiple separate commands
```
/biz:panel for business
/macro:brief for macro
/sys:generate for systems
```

**New Way**: Single skill with intelligent routing
```
Any business, macro, or system request
→ domain-router automatically handles
```

### Direct Agent Access
**Old Way**: Only through slash commands
```
/biz:panel [request]
```

**New Way**: Direct agent invocation
```
@superclaude-ext/business-panel [request]
```

## Migration Steps

### Step 1: Install SuperClaudeExt Skill
Place the skill in:
```
~/.claude/skills/superclaude-ext/
```

### Step 2: Test Backward Compatibility
Verify existing commands still work:
```bash
/biz:panel test
/macro:brief test
/sys:generate test
```

### Step 3: Try Natural Language
Test automatic activation:
```
"Analyze our business strategy"
"What's the Fed's impact today?"
"Create a multi-agent system"
```

### Step 4: Update Workflows
Gradually transition to new patterns:
- Use natural language for ad-hoc requests
- Use direct agents for specific needs
- Keep slash commands for muscle memory

## Feature Enhancements

### Better Context Detection
**Old**: Required exact command format
**New**: Understands context and intent

### Multi-Domain Workflows
**Old**: Separate command chains
**New**: Seamless cross-domain integration

### Intelligent Fallbacks
**Old**: Command not found errors
**New**: Helpful clarification prompts

## Compatibility Matrix

| Feature | Legacy | SuperClaudeExt | Status |
|---------|---------|----------------|---------|
| Slash commands | ✅ | ✅ | Fully compatible |
| Natural language | ❌ | ✅ | New feature |
| Direct agents | ❌ | ✅ | New feature |
| Cross-domain | Limited | ✅ | Enhanced |
| Auto-routing | ❌ | ✅ | New feature |

## Common Scenarios

### Scenario 1: Business Analysis
**Legacy Approach**:
```bash
/biz:panel analyze market
/biz:research competitors
# Manual correlation of results
```

**New Approach**:
```
"I need a comprehensive business analysis with market research"
→ Router coordinates both agents automatically
```

### Scenario 2: Macro + Trading
**Legacy Approach**:
```bash
/macro:brief
/macro:analyze SPY
# Manually combine insights
```

**New Approach**:
```
"Macro briefing with SPY trading opportunities"
→ Integrated analysis with trade ideas
```

### Scenario 3: System Generation
**Legacy Approach**:
```bash
/sys:generate customer-support
# Then manually validate
```

**New Approach**:
```
"Create and validate a customer support system"
→ Meta-builder + framework-validator automatically
```

## Troubleshooting

### Issue: Commands Not Working
**Solution**: Check skill installation path
```bash
ls ~/.claude/skills/superclaude-ext/
```

### Issue: Wrong Agent Selected
**Solution**: Use direct agent syntax
```
@superclaude-ext/specific-agent
```

### Issue: Natural Language Not Triggering
**Solution**: Add more context or use slash command
```
"business analysis" → "I need business panel analysis"
```

## Best Practices

### During Transition
1. Keep using what works
2. Experiment with new features
3. Provide feedback on routing
4. Document custom workflows
5. Share successful patterns

### After Migration
1. Prefer natural language for flexibility
2. Use direct agents for precision
3. Leverage cross-domain capabilities
4. Create workflow shortcuts
5. Optimize token usage

## Rollback Plan

If issues arise, you can:
1. Disable skill temporarily
2. Use legacy commands (still work)
3. Access agents directly
4. Report issues for fixing

## Advanced Migration

### Custom Commands
Transform custom commands into skill patterns:

**Old Custom Command**:
```bash
/my-analysis
```

**New Skill Integration**:
1. Add trigger to SKILL.md
2. Update domain-router.md
3. Route to appropriate agents

### Workflow Automation
Convert multi-step workflows:

**Old Workflow**:
```bash
/biz:research
/biz:panel
/biz:prd
```

**New Integrated Flow**:
```
"Complete business analysis with PRD"
→ Router orchestrates all three
```

## Support and Feedback

### Getting Help
- Check this migration guide
- Review SKILL.md documentation
- Test with simple requests first
- Use explicit commands if unclear

### Reporting Issues
When reporting issues, include:
- Exact command/request used
- Expected behavior
- Actual behavior
- Any error messages

## Future Enhancements

### Planned Features
- More intelligent routing
- Custom domain addition
- Workflow templates
- Performance optimization
- Extended agent library

### Deprecation Timeline
- Legacy commands: Supported indefinitely
- Recommendation: Adopt new patterns gradually
- No forced migration required