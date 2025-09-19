# Multi‑Agent Coordination Demo (`coord-demo.sh`)

This demo showcases the **coordinator → researcher → coder → summary** pattern described in the recent research on multi‑agent coordination.

## Features

- **Explicit CLI flags** (`--task`, `--workdir`).
- **JSON context files** containing the payload filename and a SHA‑256 checksum.
- **Validation** of checksums before each stage to ensure integrity.
- **Modular stages** (coordinator, researcher, coder, summary) all implemented in a single script for simplicity.
- **Basic error handling** with clear messages and exit codes.
- **Self‑contained** – no external dependencies besides `jq` (common on macOS/Linux) and `sha256sum`.

## Directory layout (generated in `--workdir`)
```
workdir/
├─ task.txt                 # original task description
├─ coordinator.json         # context for coordinator stage
├─ research.txt             # simulated research output
├─ researcher.json          # context for researcher stage
├─ generated_code.sh        # dummy code produced by the coder stage
├─ coder.json               # context for coder stage
├─ summary.txt              # human‑readable summary of the whole workflow
└─ summary.json             # context for summary stage
```

## Example usage
```bash
# Make the script executable (once)
chmod +x ./coord-demo.sh

# Run the demo with a simple task description
./coord-demo.sh --task "Create a hello‑world script in Python"
```

The script prints the final summary to STDOUT and leaves all intermediate files in the working directory for inspection.

## How it works
1. **Coordinator** writes the task description and creates `coordinator.json` with a checksum.
2. **Researcher** reads the task, generates `research.txt`, and writes `researcher.json`.
3. **Coder** validates the researcher context, generates `generated_code.sh`, and writes `coder.json`.
4. **Summary** validates the coder context, assembles `summary.txt`, and writes `summary.json`.

Each stage calls `validate_context` to verify that the previous payload has not been tampered with.

## Extending the demo
- Replace the placeholder researcher/coder logic with calls to real agents (e.g., via the Claude API).
- Add more stages or richer JSON schemas.
- Plug this script into your automation pipeline.
