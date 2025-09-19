#!/usr/bin/env bash

# coord-demo.sh – Demonstration of multi‑agent coordination pattern
#
# Workflow:
#   coordinator → researcher → coder → summary
#
# The script simulates four agents using separate stages.  Context is
# exchanged via JSON files that include a SHA‑256 checksum of the payload.
# Each stage validates the checksum before proceeding.
#
# Flags (recommended CLI structure):
#   --task "<description>"   Description of the problem to solve (required)
#   --workdir <dir>          Working directory for intermediate files (default: ./agent_demo)
#   --help                    Show this help message
#
# Example usage:
#   ./coord-demo.sh --task "Create a hello‑world script in Python" 
#
# The script will create a directory, run the researcher, coder and finally
# output a summary to STDOUT.

set -euo pipefail

# ---------- utility functions ----------

usage() {
  grep '^#' "$0" | cut -c4-
  exit 1
}

error() {
  echo "Error: $*" >&2
  exit 1
}

# Compute SHA‑256 checksum of a file (hex string without trailing spaces)
checksum() {
  sha256sum "$1" | awk '{print $1}'
}

# Write a JSON context file with a checksum and payload path
write_context() {
  local payload_file=$1
  local ctx_file=$2
  local sum=$(checksum "$payload_file")
  cat > "$ctx_file" <<EOF
{
  "payload": "$(basename "$payload_file")",
  "checksum": "$sum"
}
EOF
}

# Validate a JSON context file against its payload
validate_context() {
  local ctx_file=$1
  local dir=$(dirname "$ctx_file")
  local payload=$(jq -r .payload "$ctx_file")
  local expected=$(jq -r .checksum "$ctx_file")
  local actual=$(checksum "$dir/$payload")
  if [[ "$expected" != "$actual" ]]; then
    error "Checksum mismatch for $payload"
  fi
}

# ---------- argument parsing ----------

TASK=""
WORKDIR="./agent_demo"

while (( "$#" )); do
  case $1 in
    --task)
      TASK=$2; shift 2;;
    --workdir)
      WORKDIR=$2; shift 2;;
    --help)
      usage;;
    *)
      error "Unknown argument: $1";;
  esac
done

if [[ -z "$TASK" ]]; then
  error "--task is required"
fi

# Ensure working directory exists
mkdir -p "$WORKDIR"

# ---------- coordinator stage ----------
# Write the initial task description
TASK_FILE="$WORKDIR/task.txt"
echo "$TASK" > "$TASK_FILE"
write_context "$TASK_FILE" "$WORKDIR/coordinator.json"

echo "[coordinator] task written and context generated"

# ---------- researcher stage ----------
# Simulate a researcher generating findings based on the task
RESEARCH_FILE="$WORKDIR/research.txt"
cat <<EOF > "$RESEARCH_FILE"
Research Findings for task: $(cat "$TASK_FILE")
- Relevant concepts identified
- Potential approaches outlined
EOF
write_context "$RESEARCH_FILE" "$WORKDIR/researcher.json"

echo "[researcher] research completed and context generated"

# Validate coordinator context before proceeding (example of cross‑check)
validate_context "$WORKDIR/coordinator.json"

# ---------- coder stage ----------
# Simulate a coder generating code based on research
CODE_FILE="$WORKDIR/generated_code.sh"
cat <<'EOS' > "$CODE_FILE"
#!/usr/bin/env bash
# Generated hello‑world script
echo "Hello, World!"
EOS
chmod +x "$CODE_FILE"
write_context "$CODE_FILE" "$WORKDIR/coder.json"

echo "[coder] code generated and context created"

validate_context "$WORKDIR/researcher.json"

# ---------- summary stage ----------
# Assemble a human‑readable summary
SUMMARY_FILE="$WORKDIR/summary.txt"
cat <<EOF > "$SUMMARY_FILE"
Summary of Coordination Demo
============================
Task: $(cat "$TASK_FILE")

Research Findings:
$(cat "$RESEARCH_FILE")

Generated Code (excerpt):
$(head -n 5 "$CODE_FILE")
EOF
write_context "$SUMMARY_FILE" "$WORKDIR/summary.json"

echo "[summary] summary assembled"

# Final output to STDOUT
cat "$SUMMARY_FILE"

echo "
Demo completed successfully. Context files are located in $WORKDIR"
