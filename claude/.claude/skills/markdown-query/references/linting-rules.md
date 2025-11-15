# Linting Rules Reference

Automated markdown issue detection and fixing.

## Issue Detection

```python
lint_document("file.md")
```

Returns categorized issues:

### Auto-Fixable Issues
Can be automatically corrected:

**Header Consistency**
- Missing space after `#`
- Incorrect header incrementing (H1 → H3 skips H2)
- Multiple H1 headers

**Whitespace**
- Trailing whitespace on lines
- Multiple consecutive blank lines
- Missing blank line before/after code blocks

**Task Formatting**
- Inconsistent checkbox syntax
- Missing space after checkbox

### Review-Required Issues
Need manual review:

**Code Blocks**
- Missing language identifier
- Empty code blocks

**Links**
- Broken wiki links (target doesn't exist)
- Broken external links (404s)
- Relative paths that don't resolve

**Frontmatter**
- Invalid YAML syntax
- Missing required fields
- Type mismatches

**Structure**
- No headers in document
- Headers at unexpected levels

## Auto-Fixing

```python
# Fix all auto-fixable issues
auto_fix("file.md")

# Fix specific categories
auto_fix("file.md", ["headers", "whitespace"])
auto_fix("file.md", ["tasks"])
```

### Fix Types

**`"headers"`**
- Add space after `#`
- Normalize header levels
- Consolidate to single H1

**`"whitespace"`**
- Remove trailing spaces
- Collapse multiple blank lines
- Add blank lines around code blocks

**`"tasks"`**
- Standardize checkbox format: `- [ ]` or `- [x]`
- Add space after checkbox

## Linting Output

```json
{
  "file": "file.md",
  "issues": {
    "auto_fixable": [
      {
        "type": "header_spacing",
        "line": 5,
        "message": "Missing space after #",
        "fix": "headers"
      },
      {
        "type": "trailing_whitespace",
        "line": 10,
        "message": "Trailing whitespace",
        "fix": "whitespace"
      }
    ],
    "review_required": [
      {
        "type": "missing_code_language",
        "line": 15,
        "message": "Code block without language identifier"
      },
      {
        "type": "broken_wiki_link",
        "line": 20,
        "message": "Link target 'NonExistent' not found"
      }
    ]
  },
  "counts": {
    "auto_fixable": 2,
    "review_required": 2,
    "total": 4
  }
}
```

## Validation Workflows

### Pre-commit Checks
```python
issues = lint_document("README.md")
if issues["counts"]["total"] > 0:
    print(f"Found {issues['counts']['total']} issues")
    auto_fix("README.md")  # Fix what's possible
```

### Vault-wide Linting
```python
from pathlib import Path

for md_file in Path("vault").rglob("*.md"):
    issues = lint_document(str(md_file))
    if issues["counts"]["auto_fixable"] > 0:
        auto_fix(str(md_file))
```

### CI/CD Integration
```python
# Fail build if review-required issues found
issues = lint_document("docs/spec.md")
assert issues["counts"]["review_required"] == 0, "Manual review needed"
```

## Common Patterns

**Clean up documentation**:
```python
auto_fix("README.md", ["headers", "whitespace", "tasks"])
```

**Validate spec completeness**:
```python
validate_spec("SPEC.md", "completeness")
```

**Check all markdown files**:
```python
for file in Path(".").rglob("*.md"):
    issues = lint_document(str(file))
    if issues["counts"]["auto_fixable"] > 10:
        auto_fix(str(file))
```

## Deterministic Guarantees

Auto-fixes are:
- ✅ **Deterministic**: Same result every time
- ✅ **Safe**: Never delete content
- ✅ **Reversible**: Git history preserves original
- ✅ **Fast**: Processes large files in milliseconds

Review-required issues indicate:
- ⚠️ Potential content problems
- ⚠️ Broken links or references
- ⚠️ Structural inconsistencies

