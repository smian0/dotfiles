# RSS Intelligence - Quick Start Guide

## Clean Directory (2025-11-15)

The workspace has been cleaned and organized for production use.

### 🎯 Run the Workflow

**Full workflow (continuous loop):**
```bash
python rss_intelligence_workflow.py
```

**Single run (test):**
```bash
python test_audit_system.py
```

### 🔍 Debug with Audit System

```bash
# 1. List recent runs
python .audit/inspector.py list --limit 5

# 2. View all steps in a run
python .audit/inspector.py steps <session_id>

# 3. Debug a specific step
python .audit/inspector.py step <session_id> fetch_feeds
python .audit/inspector.py step <session_id> log_rss_articles
python .audit/inspector.py step <session_id> generate_newsletter
```

### 📂 Directory Structure

```
rss-intelligence/
├── rss_intelligence_workflow.py   # Main workflow
├── test_audit_system.py            # Test script
├── processed_urls.json             # Tracked URLs
├── rss_intelligence.db             # SQLite database
│
├── .audit/                         # Audit system
│   ├── inspector.py                # CLI tool
│   ├── audit_helpers.py            # Artifact saver
│   └── runs/                       # Audit artifacts
│
├── .archive/                       # Archived files (71 files)
│   ├── design-docs/
│   ├── test-scripts/
│   ├── logs/
│   ├── old-data/
│   └── backups/
│
├── agents/                         # Agent configs
├── newsletters/                    # Generated outputs
└── rss_logs/                       # Active logs
```

### 🗄️ Archived Files

71 files moved to `.archive/` on 2025-11-15:
- **6** design docs (old planning)
- **16** test scripts (obsolete)
- **43** log files (historical)
- **5** old data files
- **1** backup file

See `.archive/README.md` for restoration instructions.

### ✨ Fresh Start

The directory is now clean and ready for:
- Running fresh workflows
- Testing audit system
- Generating new newsletters
- Creating new experiments

All archived files are preserved in `.archive/` and can be restored if needed.

---
**Last Updated**: 2025-11-15
