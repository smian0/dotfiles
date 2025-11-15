# RSS Intelligence - Archive

This directory contains archived files from the RSS Intelligence project cleanup on 2025-11-15.

## Archive Structure

```
.archive/
├── design-docs/       # Old planning and analysis documents
├── test-scripts/      # Obsolete test and utility scripts
├── logs/              # Historical execution logs
├── old-data/          # Deprecated data files and outputs
└── backups/           # Old backup files
```

## What's Archived

### Design Docs (6 files)
- CONSUMER_NEWSLETTER_DESIGN.md
- CONSUMER_VS_TECHNICAL_COMPARISON.md
- ENHANCEMENT_PLAN.md
- INTELLIGENCE_ENHANCEMENTS_CONSENSUS.md
- PHASE1_INTEGRATION_COMPLETE.md
- phase1_analysis/ (directory)

### Test Scripts (16 files)
- generate_consumer_newsletter.py
- generate_newsletter_only.py
- generate_phase1_newsletter.py
- graphiti_ingest_async.py
- graphiti_ingestion.py
- ingest_episodes_to_graphiti.py
- ingest_pending_episodes.py
- newsletter_from_test.py
- run_intelligence_analysis.py
- test_intelligence_analysis.py
- test_intelligence_minimal.py
- test_intelligence_step.py
- test_phase1_raw.py
- test_phase1_workflow_integration.py
- test_single_run.py
- test_compound_scoring.py

### Logs (43 files)
All `.log` files from development and testing.

### Old Data (5 files)
- graphiti_episodes_pending.json
- graphiti_episodes_pending.json.completed
- test_episode.json
- intelligence_brief_*.md
- intelligence_output_debug.txt

### Backups (1 file)
- rss_intelligence_workflow.py.backup-20251114_113029

## Retention Policy

**Keep for**: 30-60 days for reference

**Delete after**: Once confirmed that no archived files are needed

## Restoration

To restore a file:
```bash
cp .archive/<category>/<filename> .
```

To restore all files from a category:
```bash
cp .archive/<category>/* .
```

---
**Last Updated**: 2025-11-15
