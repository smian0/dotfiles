# Advanced Skill Structure Patterns

This guide covers additional directory patterns for complex skills beyond the basic structure (scripts, references, assets, workflows, agents, commands).

## When to Use Advanced Patterns

**Basic structure handles:** Simple tools, API integrations, document generators

**Advanced patterns needed for:**
- Multi-phase sequential workflows
- Stateful operations with persistent data
- Complex dependency management
- External service integrations
- File generation and output organization
- Testing infrastructure
- Multi-language script support

## Pattern 1: Multi-Phase Workflows

**Directory:** `phases/`

### When to Use

**Use `phases/` when:**
- ✅ Single operation has 3+ sequential stages
- ✅ Each stage has distinct procedures and state
- ✅ Stages must execute in order (can't parallelize)
- ✅ Need to resume from specific stage on failure

**Don't use `phases/` when:**
- ❌ Different operations (use `workflows/` instead)
- ❌ Stages are trivial (2-3 lines each)
- ❌ Process is linear with no stage boundaries

### Structure

```
skill-name/
└── phases/
    ├── 0-initialization/
    │   ├── README.md         # Stage purpose and triggers
    │   ├── setup.md          # Detailed instructions
    │   └── validation.md     # Stage completion criteria
    ├── 1-discovery/
    │   ├── README.md
    │   └── search-strategy.md
    ├── 2-validation/
    │   └── README.md
    └── 3-synthesis/
        └── README.md
```

### SKILL.md Integration

```markdown
## Phase-Based Execution

This skill uses a multi-phase approach:

1. **Initialization** - See [Phase 0](./phases/0-initialization/README.md)
2. **Discovery** - See [Phase 1](./phases/1-discovery/README.md)
3. **Validation** - See [Phase 2](./phases/2-validation/README.md)
4. **Synthesis** - See [Phase 3](./phases/3-synthesis/README.md)

**Execution:** Follow phases sequentially. Each phase completes before next begins.

**Recovery:** If phase fails, resume from that phase after fixing issues.
```

### Example: Research Workflow

```
research/
└── phases/
    ├── 0-initialization/     # Plan research, define scope
    ├── 1-discovery/          # Execute searches, gather sources
    ├── 2-validation/         # Verify sources, check citations
    ├── 3-analysis/           # Deep analysis, pattern recognition
    └── 4-synthesis/          # Generate final report
```

### Difference: phases/ vs workflows/

| Aspect | phases/ | workflows/ |
|--------|---------|------------|
| Purpose | Sequential stages of ONE operation | Different specialized operations |
| Order | Must execute in sequence | Independent, any order |
| Example | Research: init → search → validate → analyze | Xero: invoice-copy OR contact-merge OR payment-batch |
| Resumable | Yes, from any phase | N/A (independent operations) |

## Pattern 2: Output Directory Organization

**Directory:** `output/` or `<skill-name>-output/`

### When to Use

**Use output directory when:**
- ✅ Skill generates files (reports, configs, code)
- ✅ Need organized storage for generated content
- ✅ Multiple output types produced
- ✅ Outputs should persist across sessions

### Structure

```
skill-name/
├── output/                   # ALWAYS gitignore this
│   ├── reports/
│   │   └── report-2025-01-15.md
│   ├── generated/
│   │   └── config.json
│   ├── logs/
│   │   └── execution.log
│   └── archives/
│       └── old-reports/
└── .gitignore               # Add: output/
```

### .gitignore Pattern

```
# .gitignore
output/
*.log
.state/
cache/
```

### SKILL.md Integration

```markdown
## Output Files

Generated files are saved to `output/`:
- **Reports:** `output/reports/`
- **Generated code:** `output/generated/`
- **Logs:** `output/logs/`

Check these directories after execution.
```

### Example: Research Skill

```
research/
└── research-output/          # Descriptive naming
    ├── sources/              # Source validation results
    ├── analysis/             # Analysis artifacts
    ├── progress/             # Progress tracking
    └── report/               # Final deliverables
```

## Pattern 3: Configuration Management

**Directory:** `config/`

### When to Use

**Use config/ when:**
- ✅ Environment-specific settings (dev/staging/prod)
- ✅ API keys or credentials needed
- ✅ Feature flags or toggles
- ✅ User-customizable preferences
- ✅ Schema definitions for validation

### Structure

```
skill-name/
├── config/
│   ├── default.json          # Default settings
│   ├── dev.json              # Development overrides
│   ├── prod.json             # Production overrides
│   ├── .env.template         # Environment variables template
│   └── schemas/
│       └── config-schema.json
└── .gitignore               # Add: config/.env, config/local.*
```

### .env.template Pattern

```bash
# config/.env.template
# Copy to config/.env and fill in values

API_KEY=your_api_key_here
API_URL=https://api.example.com
DEBUG=false
```

### SKILL.md Integration

```markdown
## Configuration

1. Copy template: `cp config/.env.template config/.env`
2. Edit `config/.env` with your API credentials
3. Customize settings in `config/default.json` if needed

See [Configuration Guide](./references/config-guide.md) for details.
```

### Security Best Practices

```
# .gitignore - CRITICAL
config/.env
config/local.*
config/*secret*
config/*credentials*
*.key
*.pem
```

## Pattern 4: Data Files & Fixtures

**Directory:** `data/`

### When to Use

**Use data/ when:**
- ✅ Reference data needed (schemas, taxonomies)
- ✅ Sample datasets for testing
- ✅ Validation fixtures
- ✅ Static lookup tables

### Structure

```
skill-name/
└── data/
    ├── schemas/              # Data structure definitions
    │   ├── api-schema.json
    │   └── config-schema.json
    ├── samples/              # Example data for testing
    │   ├── sample-input.json
    │   └── sample-output.json
    ├── fixtures/             # Test fixtures
    │   └── test-data.json
    └── reference/            # Static reference data
        ├── country-codes.json
        └── currency-rates.json
```

### SKILL.md Integration

```markdown
## Data Files

Reference data in `data/`:
- **Schemas:** `data/schemas/` - Validation schemas
- **Samples:** `data/samples/` - Example datasets
- **Reference:** `data/reference/` - Lookup tables

Scripts load data from these directories automatically.
```

## Pattern 5: Testing Infrastructure

**Directory:** `tests/`

### When to Use

**Use tests/ when:**
- ✅ Complex scripts requiring validation
- ✅ Critical operations needing reliability
- ✅ Shared skills requiring quality assurance
- ✅ Regression prevention needed

### Structure

```
skill-name/
├── tests/
│   ├── unit/                 # Unit tests for individual functions
│   │   ├── test_processor.py
│   │   └── test_validator.py
│   ├── integration/          # Integration tests
│   │   └── test_workflow.py
│   ├── fixtures/             # Test data
│   │   └── sample-data.json
│   └── conftest.py          # Test configuration (pytest)
└── scripts/
    └── run-tests.sh         # Test runner
```

### SKILL.md Integration

```markdown
## Testing

Run tests before using skill:

```bash
./scripts/run-tests.sh
```

Tests validate:
- Script functionality
- Data processing logic
- API integrations
- Error handling
```

### Test Script Pattern

```bash
#!/bin/bash
# scripts/run-tests.sh

cd "$(dirname "$0")/.."

echo "Running unit tests..."
pytest tests/unit/

echo "Running integration tests..."
pytest tests/integration/

echo "All tests passed!"
```

## Pattern 6: State Management

**Directories:** `.state/`, `cache/`

### When to Use

**Use .state/ when:**
- ✅ Multi-session operations (resume capability)
- ✅ Progress tracking across invocations
- ✅ Session data persistence

**Use cache/ when:**
- ✅ API response caching
- ✅ Expensive computation results
- ✅ Temporary file storage

### Structure

```
skill-name/
├── .state/                   # GITIGNORE
│   ├── session.json         # Current session state
│   └── progress.json        # Progress tracking
├── cache/                    # GITIGNORE
│   ├── api-responses/
│   └── computed-results/
└── .gitignore               # Add: .state/, cache/
```

### State File Example

```json
{
  "session_id": "abc123",
  "current_phase": 2,
  "started_at": "2025-01-15T10:00:00Z",
  "completed_phases": [0, 1],
  "data": {
    "sources_found": 25,
    "validated_sources": 18
  }
}
```

### SKILL.md Integration

```markdown
## Session Persistence

State is saved in `.state/session.json`:
- Resume interrupted operations
- Track progress across invocations
- Maintain context between phases

To reset state: `rm -rf .state/`
```

## Pattern 7: Multi-Language Scripts

**Directory:** `scripts/<language>/`

### When to Use

**Use language subdirectories when:**
- ✅ Scripts in 3+ different languages
- ✅ Language-specific organization helps clarity
- ✅ Different runtime requirements per language

**Don't use when:**
- ❌ Only 1-2 languages (flat structure is fine)
- ❌ Scripts are simple wrappers

### Structure

```
skill-name/
└── scripts/
    ├── python/
    │   ├── requirements.txt
    │   ├── processor.py
    │   └── validator.py
    ├── javascript/
    │   ├── package.json
    │   └── transform.js
    ├── bash/
    │   ├── deploy.sh
    │   └── setup.sh
    └── README.md            # Which script to use when
```

### Alternative: Flat with Prefixes

```
skill-name/
└── scripts/
    ├── py-processor.py
    ├── py-validator.py
    ├── js-transform.js
    └── sh-deploy.sh
```

## Pattern 8: Archived Content

**Directory:** `archived/`

### When to Use

**Use archived/ when:**
- ✅ Deprecated features with historical value
- ✅ Old configs for reference
- ✅ Superseded approaches worth documenting
- ✅ Breaking changes replaced old implementations

### Structure

```
skill-name/
└── archived/
    ├── README.md            # Why archived, migration path
    ├── v1-deprecated/
    │   └── old-script.py
    └── deprecated-configs/
        └── old-config.json
```

### README.md Template

```markdown
# Archived Content

This directory contains deprecated features and configurations.

## Deprecated Items

- **v1-deprecated/** - Old script implementation (replaced 2025-01-15)
  - Reason: New API version released
  - Migration: See [Migration Guide](../references/v2-migration.md)

- **deprecated-configs/** - Old configuration format
  - Reason: JSON schema updated
  - Migration: Run `scripts/migrate-config.sh`
```

## Pattern 9: Dependency Files

**Files:** Root-level dependency manifests

### Common Dependency Files

```
skill-name/
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
├── Gemfile                 # Ruby dependencies
├── go.mod                  # Go dependencies
├── Dockerfile              # Container definition
├── docker-compose.yml      # Multi-container setup
└── .tool-versions          # asdf version manager
```

### requirements.txt Example

```
# requirements.txt
requests>=2.28.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### SKILL.md Integration

```markdown
## Prerequisites

Install dependencies:

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

See [Setup Guide](./references/setup.md) for detailed instructions.
```

### Docker Pattern

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /skill
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scripts/ ./scripts/
COPY config/ ./config/

ENTRYPOINT ["python", "scripts/main.py"]
```

## Pattern 10: Human Documentation

**File:** `README.md` (skill root level)

### Purpose

- `SKILL.md` - Instructions for Claude
- `README.md` - Documentation for humans
- Both can coexist with different audiences

### When to Use README.md

**Use README.md when:**
- ✅ Skill shared across team
- ✅ Manual script execution by humans
- ✅ Contributing guidelines needed
- ✅ Installation steps complex

### README.md Template

```markdown
# Skill Name

> For Claude instructions, see [SKILL.md](./SKILL.md)

## Overview
What this skill does and why it exists.

## Installation
How to set up dependencies and configuration.

## Usage
How humans can use scripts directly.

## Scripts
- `scripts/process.py` - Main processor
- `scripts/validate.sh` - Validation

## Contributing
Guidelines for team contributions.

## Troubleshooting
Common issues and solutions.
```

## Complete Advanced Structure

Combining all patterns:

```
.claude/skills/<skill-name>/
│
├── SKILL.md                    # Claude instructions
├── README.md                   # Human documentation
├── CHANGELOG.md                # Version history
├── LICENSE.txt
│
├── workflows/                  # Different operations
│   └── *.md
│
├── phases/                     # Sequential stages (NEW)
│   ├── 0-init/
│   └── 1-process/
│
├── scripts/                    # Executable code
│   ├── python/                # Multi-language (NEW)
│   ├── bash/
│   └── *.py, *.sh
│
├── references/                 # Loaded on-demand docs
│   └── *.md
│
├── assets/                     # Templates & boilerplate
│   └── templates/
│
├── config/                     # Configuration (NEW)
│   ├── default.json
│   ├── .env.template
│   └── schemas/
│
├── data/                       # Reference data (NEW)
│   ├── schemas/
│   ├── samples/
│   └── fixtures/
│
├── tests/                      # Testing infrastructure (NEW)
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── output/                     # Generated files - GITIGNORE (NEW)
│   ├── reports/
│   └── logs/
│
├── .state/                     # Session state - GITIGNORE (NEW)
│   └── session.json
│
├── cache/                      # Cached data - GITIGNORE (NEW)
│   └── api-responses/
│
├── archived/                   # Deprecated content (NEW)
│   └── v1-deprecated/
│
├── agents/                     # Custom specialized agents
│   └── *.md
│
├── commands/                   # Slash commands
│   └── *.md
│
├── requirements.txt            # Python deps (NEW)
├── package.json                # Node deps (NEW)
├── Dockerfile                  # Containerization (NEW)
└── .gitignore                  # CRITICAL for output/cache/.state
```

## .gitignore Requirements

**ALWAYS include in .gitignore:**

```
# Generated outputs
output/
*.log
logs/

# State and cache
.state/
cache/

# Secrets and local config
config/.env
config/local.*
*.key
*.pem
*secret*
*credentials*

# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# OS files
.DS_Store
Thumbs.db
```

## Decision Matrix: Which Pattern to Use?

| Need | Pattern | Directory |
|------|---------|-----------|
| Different operations | Basic | workflows/ |
| Sequential stages | Advanced | phases/ |
| Generated files | Advanced | output/ |
| Environment settings | Advanced | config/ |
| Reference data | Advanced | data/ |
| Script validation | Advanced | tests/ |
| Multi-session operations | Advanced | .state/ |
| API caching | Advanced | cache/ |
| Multiple languages | Advanced | scripts/<lang>/ |
| Deprecated features | Advanced | archived/ |
| External deps | Advanced | requirements.txt, etc. |
| Human users | Advanced | README.md |

## Real-World Examples

### Example 1: Research Skill (Multi-Phase)

```
research/
├── SKILL.md
├── phases/                   # Sequential research stages
│   ├── 0-initialization/
│   ├── 1-discovery/
│   ├── 2-validation/
│   ├── 3-analysis/
│   └── 4-synthesis/
├── agents/                   # Specialized research agents
├── assets/                   # Templates
├── scripts/                  # Automation
└── research-output/          # Generated reports
```

**Why these patterns:**
- `phases/` - Research has clear sequential stages
- `agents/` - Multiple specialist roles (validator, analyst, synthesizer)
- `research-output/` - Generates reports, analyses, source lists

### Example 2: MCP Manager Skill (Workflows + Config)

```
mcp-manager/
├── SKILL.md
├── workflows/                # Different MCP operations
│   ├── add-server.md
│   ├── remove-server.md
│   ├── sync-user.md
│   └── validate.md
├── scripts/                  # Automation scripts
├── archived/                 # Deprecated configs
└── README.md                 # Human docs
```

**Why these patterns:**
- `workflows/` - Distinct operations (add vs remove vs sync)
- `archived/` - Old MCP server configs for reference
- `README.md` - Team collaboration on config management

### Example 3: API Integration Skill (Config + Testing)

```
api-client/
├── SKILL.md
├── scripts/
│   └── python/
│       ├── client.py
│       └── validator.py
├── config/
│   ├── .env.template
│   └── api-endpoints.json
├── tests/
│   ├── unit/
│   └── integration/
├── cache/                    # GITIGNORE
│   └── api-responses/
└── requirements.txt
```

**Why these patterns:**
- `config/` - API keys and endpoint configuration
- `tests/` - Validate API integration reliability
- `cache/` - Cache API responses to reduce calls
- `requirements.txt` - Python dependencies

## Verification Checklist

When using advanced patterns:

**File references:**
- [ ] All directories referenced in SKILL.md
- [ ] .gitignore includes output/, .state/, cache/, config/.env
- [ ] README.md exists if skill shared with team
- [ ] Dependency files (requirements.txt, etc.) documented

**Organization:**
- [ ] phases/ used for sequential stages, workflows/ for different operations
- [ ] No duplication between SKILL.md and advanced directories
- [ ] Each pattern serves clear purpose
- [ ] Advanced patterns documented in SKILL.md

**Maintenance:**
- [ ] archived/ includes migration guides
- [ ] Tests exist for critical scripts
- [ ] Configuration templates provided
- [ ] Dependencies pinned to versions

## Summary

**Basic structure:** scripts, references, assets, workflows, agents, commands

**Advanced patterns add:**
- `phases/` - Multi-stage sequential execution
- `output/` - Generated file organization
- `config/` - Environment/settings management
- `data/` - Reference data and fixtures
- `tests/` - Validation infrastructure
- `.state/`, `cache/` - Stateful operations
- `archived/` - Deprecated content
- Multi-language scripts, dependency files, human docs

**Use advanced patterns when needed - don't over-engineer simple skills.**
