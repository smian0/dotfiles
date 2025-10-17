# MLflow Tracing for Claude Code

This document explains how to use MLflow tracing to capture and analyze your Claude Code interactions in the dotfiles project.

## Overview

MLflow tracing automatically captures:
- User prompts and assistant responses
- Tool usage (file operations, code execution, web searches, etc.)
- Conversation timing and duration
- Tool execution results
- Session metadata (working directory, user information)

## Setup

The dotfiles project is configured with MLflow tracing enabled:

### Installation

```bash
# Install MLflow (already done)
pip3 install mlflow
```

### Configuration

The tracing hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python -c \"from mlflow.claude_code.hooks import stop_hook_handler; stop_hook_handler()\""
          }
        ]
      }
    ]
  },
  "environment": {
    "MLFLOW_CLAUDE_TRACING_ENABLED": "true"
  }
}
```

## Usage

### Starting the MLflow UI

```bash
# Start the MLflow UI server (runs in background)
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000 &
```

The UI will be available at: http://127.0.0.1:5000

### Using Claude Code with Tracing

When you use Claude Code from the `/Users/smian/dotfiles` directory, all interactions are automatically traced:

```bash
# Your interactions are automatically logged
claude -p 'your prompt here'
```

### Viewing Traces

1. Open http://127.0.0.1:5000 in your browser
2. Navigate to the "Traces" tab
3. View detailed traces of all your Claude Code sessions

### Disabling Tracing

If you want to disable tracing temporarily:

```bash
# Disable tracing
mlflow autolog claude --disable

# Re-enable later
mlflow autolog claude
```

## Files and Database

### Database Location

The SQLite database is stored at:
```
/Users/smian/dotfiles/mlflow.db
```

### MLflow Artifacts

MLflow stores additional data in:
```
/Users/smian/dotfiles/mlruns/
```

## Important Notes

### Scope

- **Project-specific**: Tracing only applies to Claude Code sessions started in `/Users/smian/dotfiles`
- Other projects are not affected unless you configure them separately

### Privacy Considerations

MLflow captures:
- ✅ All prompts you send
- ✅ All responses from Claude
- ✅ All tool calls and file operations
- ✅ Code content from files accessed

**Be aware**: Sensitive data in your prompts and files will be logged to the MLflow database.

### Performance

- Minimal overhead for most operations
- Database grows with each session
- Consider periodic cleanup of old traces

## Maintenance

### Starting MLflow UI on System Startup

To automatically start MLflow UI when you work on dotfiles:

1. Add to your shell RC file (~/.zshrc):
```bash
# Auto-start MLflow UI for dotfiles if not running
if [[ "$PWD" == "$HOME/dotfiles" ]] && ! pgrep -f "mlflow ui.*port 5000" > /dev/null; then
    mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000 &>/dev/null &
fi
```

### Database Cleanup

To remove old traces and reduce database size:

```bash
# Delete experiments (careful!)
mlflow experiments delete --experiment-id 0

# Or manually remove old data
rm -rf mlruns/ mlflow.db
mlflow autolog claude  # Reconfigure
```

## Troubleshooting

### MLflow UI Not Starting

```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process
pkill -f "mlflow ui"

# Restart
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000 &
```

### Tracing Not Working

```bash
# Verify configuration
cat .claude/settings.json

# Check environment variable
echo $MLFLOW_CLAUDE_TRACING_ENABLED

# Reconfigure if needed
mlflow autolog claude
```

### Database Locked

```bash
# Stop all MLflow processes
pkill -f mlflow

# Restart UI
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000 &
```

## Advanced Usage

### Custom Experiments

```bash
# Create a new experiment
mlflow experiments create --experiment-name "feature-development"

# Set active experiment
export MLFLOW_EXPERIMENT_NAME="feature-development"
```

### Analyzing Traces Programmatically

```python
import mlflow

# Get all traces
client = mlflow.tracking.MlflowClient()
traces = client.search_traces()

# Analyze specific trace
trace = client.get_trace("trace_id_here")
print(trace.info)
```

## References

- [MLflow Tracing Documentation](https://mlflow.org/docs/latest/genai/tracing/)
- [Claude Code Tracing Integration](https://mlflow.org/docs/latest/genai/tracing/integrations/listing/claude_code/)

---
Last Updated: 2025-10-16
