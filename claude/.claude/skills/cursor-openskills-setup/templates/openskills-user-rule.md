# OpenSkills User Rule (Global)

This is a global Cursor User Rule that enables OpenSkills awareness across ALL projects.

---

## OpenSkills Integration

You have access to specialized skills via the OpenSkills system when projects contain an `AGENTS.md` file.

### How to Check for Skills

1. **Look for AGENTS.md** in the project root
2. **If found**, check the `<available_skills>` section
3. **Invoke skills** via: `Bash("openskills read <skill-name>")`

### Skill Invocation Format

When you see `<skill>` entries in AGENTS.md:
```bash
openskills read <skill-name>
```

This loads the skill's SKILL.md file with detailed workflow instructions.

### Progressive Disclosure

- Skills load ONLY when explicitly invoked
- Check AGENTS.md to see what's available before loading
- Don't load skills that are already in your context

### Example

If AGENTS.md shows:
```xml
<skill>
<name>research</name>
<description>Comprehensive multi-source research...</description>
</skill>
```

Invoke it with: `Bash("openskills read research")`

---

**Source**: This rule is managed via dotfiles at `~/dotfiles/cursor/user-rules/openskills.md`
