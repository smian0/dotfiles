# RSS Intelligence Workflow Audit System

Agno-native audit system for traceable, auditable workflow execution using built-in event storage with minimal custom code (~200 lines).

## Quick Start - Debug Workflow Steps

```bash
# 1. List recent runs to get session_id
python .audit/inspector.py list --limit 5

# 2. View all steps in a run
python .audit/inspector.py steps <session_id>

# 3. Debug a specific step (shows output, errors, artifacts)
python .audit/inspector.py step <session_id> fetch_feeds
python .audit/inspector.py step <session_id> log_rss_articles
python .audit/inspector.py step <session_id> generate_newsletter

# 4. View full run details
python .audit/inspector.py inspect <session_id>
```

## Architecture

```
Agno Native (0 lines)          Custom Layer (~200 lines)
├─ store_events=True           ├─ audit_helpers.py (~60 lines)
├─ session_state               ├─ inspector.py (~120 lines)
├─ SQLite persistence          └─ __init__.py (~20 lines)
└─ add_workflow_history
```

## Features

✅ **Agno-Native Event Storage** - Captures all workflow execution events automatically
✅ **Session State Tracking** - Auto-initialized audit metadata in session_state
✅ **SQLite Query Tools** - CLI for inspecting runs, sessions, and events
✅ **Optional Artifact Saving** - File-based artifacts for easy inspection
✅ **Zero Workflow Impact** - Audit failures don't break workflow execution

## Directory Structure

```
.audit/
├── README.md                # This file
├── __init__.py              # Package init
├── audit_helpers.py         # AuditArtifacts class
├── inspector.py             # CLI tool
└── runs/                    # Generated at runtime
    └── 20251115_073000/
        ├── log_rss_articles/
        │   ├── articles.json
        │   └── articles.json.meta.json
        └── generate_newsletter/
            ├── technical_newsletter.md
            └── technical_newsletter.md.meta.json

../rss_intelligence.db       # Agno's SQLite database
```

## Usage

### 1. Inspect Recent Workflow Runs

```bash
python -m .audit.inspector list --limit 5
```

**Output:**
```json
[
  {
    "session_id": "6216035e-fbe6-47ed-82cd-352ca93f7d39",
    "workflow_id": "rss-intelligence",
    "created_at": "2025-11-15T07:20:52",
    "audit_run_id": "20251115_072052",
    "audit_version": "1.0.0",
    "run_count": 1
  }
]
```

### 2. Inspect Specific Run Details

```bash
python -m .audit.inspector inspect <session_id>
```

Shows:
- Session metadata
- Audit run ID and version
- Session state (including `_audit_run_id`, `_audit_start_time`)
- Workflow data
- Run events (if `store_events=True`)

### 3. View Session State Changes

```bash
python -m .audit.inspector diff <session_id>
```

Shows state modifications during workflow execution.

### 4. View Step Execution History

```bash
python .audit/inspector.py steps <session_id>
```

Shows step-by-step execution timeline with detailed results:

**Output:**
```json
[
  {
    "step_name": "fetch_feeds",
    "executor_name": "fetch_rss_feeds",
    "content": "Fetched 0 new articles from 4 feeds",
    "success": true,
    "error": null,
    "metrics": null,
    "step_id": "11702d48-db39-4bd7-a2a4-8ad861ceee89"
  },
  {
    "step_name": "log_rss_articles",
    "executor_name": "log_rss_articles",
    "content": "No new articles to log",
    "success": true,
    "error": null
  }
]
```

### 4a. Inspect Individual Step (Debug Single Step)

```bash
python .audit/inspector.py step <session_id> <step_name>
```

Shows detailed information about a specific step including:
- Step output/content
- Success/failure status
- Error details (if failed)
- Performance metrics
- Saved artifacts (if any)

**Examples:**
```bash
# Debug the fetch_feeds step
python .audit/inspector.py step cd8e7052-fb28-481b-9757-d48b67319b11 fetch_feeds

# Debug the newsletter generation step
python .audit/inspector.py step cd8e7052-fb28-481b-9757-d48b67319b11 generate_newsletter
```

**Output:**
```json
{
  "step_name": "fetch_feeds",
  "executor_name": "fetch_rss_feeds",
  "content": "Fetched 0 new articles from 4 feeds",
  "success": true,
  "error": null,
  "metrics": null,
  "artifacts": []
}
```

### 5. View Session State Changes

```bash
python .audit/inspector.py diff <session_id>
```

Shows state modifications during workflow execution.

### 6. Inspect Artifact Files

Navigate to `.audit/runs/<run_id>/` to view saved artifacts:

```bash
# View articles ingested
cat .audit/runs/20251115_073000/log_rss_articles/articles.json

# View generated newsletter
cat .audit/runs/20251115_073000/generate_newsletter/technical_newsletter.md

# View metadata
cat .audit/runs/20251115_073000/generate_newsletter/technical_newsletter.md.meta.json
```

## Agno Configuration

The workflow is configured with:

```python
workflow = Workflow(
    name="RSS Intelligence",

    # ✅ Agno Native Event Storage
    store_events=True,  # Capture all workflow execution events
    add_workflow_history_to_steps=True,  # Provide step-level history

    # Session state with audit metadata (auto-initialized)
    session_state={
        "_audit_run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "_audit_start_time": time.time(),
        "_audit_workflow_version": "1.0.0",
        "processed_urls": [],
    },

    db=SqliteDb(
        session_table="rss_intelligence_sessions",
        db_file="rss_intelligence.db",
    ),
)
```

## Adding Audit Saving to Steps

To save artifacts from any step:

```python
from .audit import AuditArtifacts

def my_step(step_input: StepInput, session_state: dict) -> StepOutput:
    # ... normal logic
    result = process_data(step_input.input)

    # Optional: save artifact for inspection
    if session_state.get("_audit_run_id"):
        try:
            audit = AuditArtifacts(session_state)
            audit.save(
                step_name="my_step",
                filename="output.json",
                content=result,
                metadata={"custom_field": "value"}
            )
        except Exception as e:
            # Don't fail workflow if audit save fails
            print(f"⚠️ Warning: Failed to save audit artifact: {e}")

    return StepOutput(content=result)
```

## Database Schema

**Table:** `rss_intelligence_sessions`

| Column | Type | Description |
|--------|------|-------------|
| `session_id` | VARCHAR | Unique session identifier |
| `workflow_id` | VARCHAR | "rss-intelligence" |
| `session_data` | JSON | **Double-encoded JSON** containing nested `session_state` with audit metadata |
| `workflow_data` | JSON | Workflow configuration |
| `runs` | JSON | Run history and events (populated by `store_events=True`) |
| `created_at` | BIGINT | Unix timestamp |
| `updated_at` | BIGINT | Unix timestamp |

**Important:** Agno double-encodes `session_data` as a JSON string of a JSON string. The inspector handles this by:
1. First `json.loads()` returns a string
2. Second `json.loads()` returns the actual dict with `session_state` nested inside

Example structure after double-parse:
```json
{
  "session_state": {
    "_audit_run_id": "20251115_082631",
    "_audit_start_time": 1763213191.990866,
    "_audit_workflow_version": "1.0.0-test",
    "processed_urls": [],
    "new_articles": []
  },
  "session_metrics": {}
}
```

## Benefits

- **90% less code** - Leverage Agno's built-in features
- **Agno-idiomatic** - Uses native framework capabilities
- **No decorators** - Simple, optional helper calls
- **Traceable** - File artifacts + SQLite events
- **Auditable** - Query database for any run details
- **Maintainable** - Minimal custom logic

## Troubleshooting

### No audit_run_id in old sessions

Sessions created before the audit system was enabled won't have `_audit_run_id` metadata. Only new runs will show audit data.

### Artifact saving fails

Check:
1. `.audit/runs/` directory permissions
2. Disk space
3. `session_state` contains `_audit_run_id`

Audit failures are non-blocking - the workflow continues normally.

### Inspector shows "N/A" for audit fields

This means the session was created before audit metadata was added to `session_state`. Run a new workflow execution to see audit data.

## Last Updated

2025-11-15
