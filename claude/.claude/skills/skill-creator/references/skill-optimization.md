# Skill Optimization Guide

## Core Principle

**Every file must serve a purpose and be referenced in SKILL.md.**

If a file exists but SKILL.md doesn't load or reference it, the file is orphaned and should be deleted.

## Verification Checklist

### 1. Every File Must Be Referenced

**Check each file type:**

```bash
# In skill directory
cd .claude/skills/<skill-name>

# Check markdown files
for f in $(find . -name "*.md" ! -name "SKILL.md"); do
  grep -q "$(basename $f)" SKILL.md || echo "❌ DELETE: $f (not referenced)"
done

# Check scripts
for f in $(find scripts -type f 2>/dev/null); do
  grep -q "$(basename $f)" SKILL.md || echo "❌ DELETE: $f (not referenced)"
done

# Check assets
for f in $(find assets -type f 2>/dev/null); do
  grep -q "$(basename $f)" SKILL.md || echo "❌ DELETE: $f (not referenced)"
done
```

**Exceptions (files that don't need references):**
- `SKILL.md` itself
- `LICENSE.txt`
- `.gitignore` or similar meta files

### 2. No Redundant Content

**Common violations:**

❌ **Don't duplicate script content in SKILL.md:**
```markdown
<!-- SKILL.md - WRONG -->
## How It Works

The script does this:
1. Validates input
2. Processes data
3. Generates output

[Copies 50 lines of script explanation]
```

✅ **Reference the script instead:**
```markdown
<!-- SKILL.md - CORRECT -->
## Usage

```bash
scripts/process.py --input data.json --output result.json
```

See `scripts/process.py --help` for all options.
```

❌ **Don't duplicate reference file content:**
```markdown
<!-- SKILL.md - WRONG -->
## Architecture Patterns

[Copies entire architecture-patterns.md content]
```

✅ **Load the reference:**
```markdown
<!-- SKILL.md - CORRECT -->
See [Architecture Patterns](./references/architecture-patterns.md) for detailed guidance.
```

### 3. Clear Documentation Purpose

**"For Claude" documentation must be loaded:**

❌ **Creating orphaned context files:**
- You create `context.md` with "background info for Claude"
- SKILL.md never references or loads it
- Result: Wasted file, never read

✅ **Loaded references:**
- Create `references/background.md`
- SKILL.md includes: "See [Background](./references/background.md)"
- Result: Loaded when needed, serves purpose

### 4. Reference File Updates

**Update reference list in SKILL.md:**

```markdown
## Reference Files

Load these for detailed guidance:

- [📊 Pattern Guide](./references/pattern-guide.md) - Detailed patterns
- [🔗 Examples](./references/examples.md) - Usage examples
```

**Every file in `references/` MUST appear in this list.**

## Common Bloat Patterns

### Pattern 1: Implementation Details in SKILL.md

**Problem:** Script exists but SKILL.md explains implementation

```markdown
<!-- SKILL.md - BLOAT -->
### How Validation Works

The validation process:
1. Checks file exists
2. Parses JSON schema
3. Validates each field
4. Returns error list

[30 more lines of implementation details]
```

**Solution:** Reference the script

```markdown
<!-- SKILL.md - LEAN -->
### Validation

```bash
scripts/validate.py config.json
```

Returns exit code 0 if valid, non-zero with error details if invalid.
```

**Delete from SKILL.md:** 30 lines
**Keep:** 5 lines + script

### Pattern 2: Unused Architecture Documents

**Problem:** Creating design docs that SKILL.md never loads

```
skill-folder/
├── SKILL.md
├── architecture.md          ❌ Not referenced
├── design-decisions.md      ❌ Not referenced
└── references/
    └── patterns.md          ✅ Referenced in SKILL.md
```

**Solution:** Delete unreferenced files or add references

Either:
1. Delete `architecture.md` and `design-decisions.md`
2. OR move to `references/` and add to SKILL.md reference list

### Pattern 3: Duplicate Content Across Files

**Problem:** Same information in multiple places

```
SKILL.md: "To use feature X, do Y"
references/usage-guide.md: "To use feature X, do Y"
README.md: "To use feature X, do Y"
```

**Solution:** Single source of truth

```
SKILL.md: "See [Usage Guide](./references/usage-guide.md)"
references/usage-guide.md: [Complete usage information]
README.md: "See SKILL.md for AI assistant usage"
```

### Pattern 4: "For Claude" Comments Without Purpose

**Problem:** Comments intended for Claude that aren't loaded

```python
# scripts/process.py

# NOTE FOR CLAUDE: This script uses the XYZ algorithm
# because ABC was too slow. Remember to explain this
# when users ask about performance.

def process():
    # implementation
```

**Solution:** Either load the context or remove it

Option 1 - Load it:
```markdown
<!-- SKILL.md -->
See [Implementation Notes](./references/implementation-notes.md)
```

Option 2 - Remove it (if not loaded):
```python
# scripts/process.py
def process():
    # implementation (Claude never sees the comment)
```

## Optimization Commands

### Full Skill Audit

```bash
#!/bin/bash
# Run from skill directory

echo "=== Unreferenced Markdown Files ==="
for f in $(find . -name "*.md" ! -name "SKILL.md"); do
  grep -q "$(basename $f)" SKILL.md || echo "DELETE: $f"
done

echo ""
echo "=== Unreferenced Scripts ==="
for f in $(find scripts -type f 2>/dev/null); do
  grep -q "$(basename $f)" SKILL.md || echo "DELETE: $f"
done

echo ""
echo "=== Unreferenced Assets ==="
for f in $(find assets -type f 2>/dev/null); do
  grep -q "$(basename $f)" SKILL.md || echo "DELETE: $f"
done

echo ""
echo "=== Reference Files Not in SKILL.md List ==="
for f in $(find references -name "*.md" 2>/dev/null); do
  grep -q "$(basename $f)" SKILL.md || echo "MISSING FROM LIST: $f"
done
```

### File Size Analysis

```bash
# Find large files that might have duplication
find . -name "*.md" -exec wc -l {} + | sort -rn
```

If SKILL.md is >300 lines with scripts, likely has duplication.

## Before/After Examples

### Before: Bloated Skill (184 files, 8 unreferenced)

```
.claude/skills/data-processor/
├── SKILL.md (324 lines)
├── architecture.md          ❌ Unreferenced
├── design-notes.md          ❌ Unreferenced
├── scripts/
│   ├── process.py          ✅ Used
│   ├── validate.py         ✅ Used
│   └── old-backup.py       ❌ Unreferenced
├── references/
│   ├── api-guide.md        ✅ Referenced
│   ├── examples.md         ✅ Referenced
│   └── draft-ideas.md      ❌ Unreferenced
└── assets/
    └── template.json       ✅ Used
```

**SKILL.md issues:**
- 324 lines (should be ~100 with scripts)
- Duplicates script documentation
- Copies reference content inline

### After: Optimized Skill (8 files, 0 unreferenced)

```
.claude/skills/data-processor/
├── SKILL.md (103 lines)
├── scripts/
│   ├── process.py          ✅ Referenced
│   └── validate.py         ✅ Referenced
├── references/
│   ├── api-guide.md        ✅ Referenced
│   └── examples.md         ✅ Referenced
└── assets/
    └── template.json       ✅ Referenced
```

**Changes:**
- Deleted 3 unreferenced files
- Reduced SKILL.md by 221 lines (removed duplication)
- Added references to all bundled resources

## The Golden Rule

**If you can't explain why a file exists and where SKILL.md references it, delete the file.**

Every file costs:
- Disk space
- Mental overhead
- Maintenance burden
- Confusion for users

Keep only what serves a clear, documented purpose.
