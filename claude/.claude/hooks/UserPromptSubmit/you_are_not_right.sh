#!/bin/bash
set -euo pipefail
trap 'echo "at line $LINENO, exit code $? from $BASH_COMMAND" >&2; exit 1' ERR

# This is a Claude Code hook to: 
# 1) discourage reflexive agreement ("you are right"), and 
# 2) discourage overconfident claims (e.g. "production-ready") without validation.
#
# Installation:
# 1. Save this script and chmod +x it to make it executable.
# 2. Within Claude Code, /hooks / UserPromptSubmit > Add a new hook (this file)
#
# How it works:
# This script checks whether the assistant has recently told the user they are right.
# If so, it appends a system-reminder to the following user prompt,
# reminding the assistant not to do that, and giving it constructive
# examples of how it should respond to the user instead.

stdin=$(cat)
transcript_path=$(echo "$stdin" | jq -r ".transcript_path")

# We'll look through the last 8 items in the transcript.
# Sometimes the final item will be assistant thinking,
# and the previous one will be "you're right".
# We'll look for any triggering phrase like "You're right"
# or "you are absolutely correct".
items=$(grep '"role":"assistant"' "$transcript_path" | tail -n 8)
needs_agreement_reminder=false
needs_confidence_reminder=false
# Track if any overconfident phrase was detected in recent assistant text
overconfident_detected=false
# Regex of overconfident phrases we want to discourage unless validated
overconfident_regex='(production[- ]ready|ready for production|battle[- ]tested|bug[- ]free|100% (test(ed)?|coverage)|fully (tested|covered)|zero bugs|works (perfectly|flawlessly)|guaranteed|safe to deploy|drop[- ]in replacement|rock[- ]solid|mission[- ]critical)'
while IFS= read -r item; do
[[ "$(jq -r '.type // empty' <<< "$item")" == "assistant" ]] || continue
[[ "$(jq -r '.message.content[0].type // empty' <<< "$item")" == "text" ]] || continue
text=$(jq -r '.message.content[0].text' <<< "$item")
[[ "${text:0:80}" =~ .*[Yy]ou.*(right|correct) ]] && needs_agreement_reminder=true
[[ "${text:0:80}" =~ .*[Aa]bsolutely ]] && needs_agreement_reminder=true
# Check for overconfident language in the full message text (case-insensitive)
if grep -E -iq "$overconfident_regex" <<< "$text"; then
overconfident_detected=true
fi
done <<< "$items"

# If we saw overconfident language, look for recent evidence of testing/builds/lints
if [[ "$overconfident_detected" == "true" ]]; then
  # Scan a larger recent window of the transcript for evidence commands
recent=$(tail -n 300 "$transcript_path" || true)
evidence_regex='(pytest|uv run pytest|tox|jest|vitest|nose2|pytest -|npm test|pnpm test|yarn test|go test|cargo test|mvn (test|package)|gradle (test|build)|dotnet (test|build)|tsc|mypy|flake8|pylint|ruff|go vet|staticcheck|npm run build|pnpm build|yarn build|make (test|build))'
if ! grep -E -iq "$evidence_regex" <<< "$recent"; then
needs_confidence_reminder=true
fi
fi

# Exit if no reminders are needed
if [[ "$needs_agreement_reminder" != "true" && "$needs_confidence_reminder" != "true" ]]; then
exit 0
fi

# Log when hook triggers (minimal logging approach)
agreement_json=$( [[ "$needs_agreement_reminder" == "true" ]] && echo true || echo false )
overconfidence_json=$( [[ "$needs_confidence_reminder" == "true" ]] && echo true || echo false )
printf '{"timestamp":"%s","triggered":true,"session_id":"%s","agreement":%s,"overconfidence":%s}\n' \
"$(date -Iseconds)" "$(basename "$transcript_path" .jsonl)" "$agreement_json" "$overconfidence_json" \
>> "$(dirname "$0")/../logs/you_are_not_right.jsonl"

# upon exit code 0, Claude Code will append stdout to the context and proceed.
# Emit only the relevant reminders based on what was detected.
echo "<system-reminder>"
if [[ "$needs_agreement_reminder" == "true" ]]; then
echo "You MUST NOT use reflexive agreement like 'you are right'. Provide substantive technical analysis."
echo "If the user is correct, state why concretely and then proceed with the work."
echo "<example>"
echo "user: It's failing on empty inputs, so we should add a null-check."
echo "assistant: That avoids the immediate issue but misses the empty-string case."
echo "A more general fix is to check for falsy values to cover both."
echo "</example>"
fi
if [[ "$needs_confidence_reminder" == "true" ]]; then
echo "Avoid overconfident claims like 'production-ready', 'battle-tested', or 'bug-free' without validation."
echo "Before such claims, identify and run appropriate tests/builds/lints for this project and summarize results."
echo "- If tests exist: run them (e.g., pytest/jest/go test) and report pass/fail."
echo "- If no tests: perform a smoke build/lint and clearly state limitations."
echo "Until validated, use cautious language (e.g., 'appears correct locally; not yet production-validated')."
fi
echo "</system-reminder>"

exit 0
