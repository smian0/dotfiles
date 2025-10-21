# Bundled Resources Guide

This guide explains the three types of bundled resources you can include with skills: scripts, references, and assets.

## Overview

Bundled resources extend skills beyond just SKILL.md instructions. They provide:
- **Scripts** - Executable code for deterministic operations
- **References** - Documentation loaded on-demand for specialized knowledge
- **Assets** - Output templates, boilerplate code, or starter files

## Scripts Directory

**Purpose**: Code that gets rewritten repeatedly or needs deterministic reliability

**When to use scripts**:
- ✅ Complex calculations or data transformations
- ✅ Multi-step processes requiring exact execution
- ✅ Operations that fail when done manually
- ✅ Code that users frequently request

**Examples**:
- PDF manipulation scripts
- File format converters
- Data validation scripts
- Build automation
- Testing harnesses

**Best practices**:
```bash
scripts/
├── README.md              # What each script does
├── setup.sh              # Installation/dependencies
├── process_data.py       # Main functionality
└── validate_output.sh    # Verification
```

**Script requirements**:
- Include shebang line (`#!/usr/bin/env python3`)
- Make executable (`chmod +x`)
- Accept command-line arguments
- Return meaningful exit codes
- Include basic error handling
- Document usage in comments

## References Directory

**Purpose**: Documentation loaded as needed to provide specialized knowledge

**When to use references**:
- ✅ API documentation or specifications
- ✅ Configuration schemas
- ✅ Domain-specific knowledge
- ✅ Decision trees or flowcharts
- ✅ Long examples or templates
- ✅ Policy documents or standards

**Examples**:
- API reference documentation
- Configuration file schemas
- Domain glossaries
- Architecture decision records
- Best practices guides
- Troubleshooting guides

**Best practices**:
```bash
references/
├── api-reference.md       # External API docs
├── config-schema.json     # Configuration format
├── troubleshooting.md     # Common issues
└── examples/              # Code examples
    ├── basic-usage.py
    └── advanced-usage.py
```

**Reference requirements**:
- Keep under 5000 words per file
- Use clear section headings
- Include table of contents for long docs
- Provide code examples inline
- Link to official sources when possible
- Update with version information

**Progressive disclosure pattern**:
- SKILL.md: Brief overview + reference link
- Reference file: Detailed documentation
- Example: "For API details, see [API Reference](./references/api-reference.md)"

## Assets Directory

**Purpose**: Output resources like templates, boilerplate code, or starter files

**When to use assets**:
- ✅ File templates users frequently request
- ✅ Boilerplate code for common patterns
- ✅ Configuration file starters
- ✅ Images, diagrams, or visual resources
- ✅ Sample data or fixtures

**Examples**:
- Project templates
- Configuration file templates
- README templates
- Docker compose files
- CI/CD pipeline templates
- Test fixtures

**Best practices**:
```bash
assets/
├── templates/
│   ├── README.template.md
│   ├── package.json.template
│   └── .gitignore.template
├── boilerplate/
│   ├── basic-app/
│   └── advanced-app/
└── images/
    └── architecture-diagram.png
```

**Asset requirements**:
- Use clear naming conventions
- Include placeholder comments
- Document how to customize
- Keep templates minimal
- Provide multiple variants if needed
- Test templates regularly

## Organization Tips

### File Naming
- Use lowercase with hyphens: `api-reference.md`
- Include version if applicable: `v2-migration-guide.md`
- Group related files: `troubleshooting-*.md`

### Documentation
Each resource directory should have a README.md:

```markdown
# Scripts

- `process_data.py` - Main data processing pipeline
- `validate_output.sh` - Validates processed data format
- `setup.sh` - Installs dependencies

## Usage

See individual scripts for detailed usage.
```

### Size Guidelines
- **Scripts**: < 500 lines (split if larger)
- **References**: < 5000 words (split into multiple files)
- **Assets**: Keep templates minimal, expand as needed

### Version Control
- Track all bundled resources in git
- Document breaking changes
- Use semantic versioning for major changes
- Maintain backward compatibility when possible

## Loading Resources in SKILL.md

**Script reference pattern**:
```markdown
## Data Processing

Use the bundled script:

```bash
./scripts/process_data.py --input data.csv --output results.json
```

See `scripts/README.md` for all options.
```

**Reference loading pattern**:
```markdown
## API Integration

For complete API documentation, see [API Reference](./references/api-reference.md).

Quick example:
```python
# Code example inline
```
```

**Asset usage pattern**:
```markdown
## Project Setup

Start with the template:

```bash
cp assets/templates/package.json.template package.json
# Customize as needed
```
```

## Testing Resources

**Scripts**:
- Run manually with test inputs
- Verify exit codes
- Check error messages
- Test edge cases

**References**:
- Verify accuracy against official sources
- Check for broken links
- Update with new versions
- Test code examples

**Assets**:
- Test templates create valid files
- Verify placeholders are clear
- Ensure boilerplate works as-is
- Check for outdated patterns

## Common Patterns

### API Integration Skill
```
skill-name/
├── SKILL.md
├── scripts/
│   └── test_connection.py
├── references/
│   ├── api-reference.md
│   └── authentication-guide.md
└── assets/
    └── templates/
        └── config.json.template
```

### Code Generator Skill
```
skill-name/
├── SKILL.md
├── scripts/
│   └── generate_code.py
├── references/
│   └── code-patterns.md
└── assets/
    ├── boilerplate/
    │   ├── basic/
    │   └── advanced/
    └── templates/
        └── README.template.md
```

### Configuration Management Skill
```
skill-name/
├── SKILL.md
├── scripts/
│   ├── validate_config.py
│   └── migrate_config.py
├── references/
│   ├── schema.json
│   └── migration-guide.md
└── assets/
    └── templates/
        ├── dev-config.yaml
        └── prod-config.yaml
```

## Maintenance

**Regular updates**:
- Review scripts for deprecated dependencies
- Update references when APIs change
- Refresh templates with modern patterns
- Remove unused resources
- Document breaking changes

**User feedback**:
- Track which resources are most used
- Identify gaps in documentation
- Collect enhancement requests
- Monitor for common issues

---

**Remember**: Bundled resources should solve repeated problems. If Claude keeps rewriting the same code or explaining the same concepts, consider bundling them as scripts or references.
