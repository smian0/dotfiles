#!/usr/bin/env bash
# UserPromptSubmit hook for Phase 4 review suggestions with complexity detection
#
# Detects when changes exist and intelligently suggests Phase 4 review
# based on change complexity (file count, lines changed, file types).
#
# Complexity levels:
# - SKIP: 1-2 trivial files, <20 lines
# - LOW: 3-5 files or 20-100 lines
# - MEDIUM: 6-15 files or 100-500 lines
# - HIGH: 16+ files or 500+ lines
# - CRITICAL: Security/auth/database files changed
#
# Output: Context-aware suggestion based on complexity

set -euo pipefail

# Get current working directory
CWD="${CLAUDE_CWD:-$(pwd)}"

# Check if .serena/memories exists and has plans
MEMORY_DIR="${CWD}/.serena/memories"
if [[ ! -d "$MEMORY_DIR" ]]; then
  exit 0
fi

# Count zen_plan files
PLAN_COUNT=$(find "$MEMORY_DIR" -name "zen_plan_*.md" -type f 2>/dev/null | wc -l | tr -d ' ')

if [[ "$PLAN_COUNT" -eq 0 ]]; then
  exit 0
fi

# Check if in git repo
if ! git -C "$CWD" rev-parse --is-inside-work-tree &>/dev/null; then
  exit 0
fi

# Get git status
GIT_STATUS=$(git -C "$CWD" status --porcelain 2>/dev/null || echo "")

if [[ -z "$GIT_STATUS" ]]; then
  exit 0
fi

# === COMPLEXITY ANALYSIS ===

# Count changed files
FILE_COUNT=$(echo "$GIT_STATUS" | wc -l | tr -d ' ')

# Get line changes (insertions + deletions)
GIT_DIFFSTAT=$(git -C "$CWD" diff HEAD --shortstat 2>/dev/null || echo "")
LINES_CHANGED=0
if [[ -n "$GIT_DIFFSTAT" ]]; then
  # Extract numbers from "X files changed, Y insertions(+), Z deletions(-)"
  INSERTIONS=$(echo "$GIT_DIFFSTAT" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo "0")
  DELETIONS=$(echo "$GIT_DIFFSTAT" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo "0")
  LINES_CHANGED=$((INSERTIONS + DELETIONS))
fi

# Detect critical file patterns (security, auth, database, migrations)
CRITICAL_PATTERNS="(auth|security|database|migration|secret|credential|password|token|crypto|jwt|oauth)"
CRITICAL_FILES=$(echo "$GIT_STATUS" | awk '{print $2}' | grep -iE "$CRITICAL_PATTERNS" || echo "")
HAS_CRITICAL=$([[ -n "$CRITICAL_FILES" ]] && echo "true" || echo "false")

# Detect code vs config vs docs
CODE_FILES=$(echo "$GIT_STATUS" | awk '{print $2}' | grep -E '\.(py|js|ts|tsx|jsx|go|rs|java|cpp|c|h)$' | wc -l | tr -d ' ')
CONFIG_FILES=$(echo "$GIT_STATUS" | awk '{print $2}' | grep -E '\.(json|yaml|yml|toml|ini|env|conf)$' | wc -l | tr -d ' ')
DOC_FILES=$(echo "$GIT_STATUS" | awk '{print $2}' | grep -E '\.(md|txt|rst)$' | wc -l | tr -d ' ')

# === COMPLEXITY CLASSIFICATION ===

COMPLEXITY="SKIP"
SUGGESTION_TYPE="none"

if [[ "$HAS_CRITICAL" == "true" ]]; then
  COMPLEXITY="CRITICAL"
  SUGGESTION_TYPE="strongly_recommend"
elif [[ "$FILE_COUNT" -ge 16 ]] || [[ "$LINES_CHANGED" -ge 500 ]]; then
  COMPLEXITY="HIGH"
  SUGGESTION_TYPE="strongly_recommend"
elif [[ "$FILE_COUNT" -ge 6 ]] || [[ "$LINES_CHANGED" -ge 100 ]]; then
  COMPLEXITY="MEDIUM"
  SUGGESTION_TYPE="recommend"
elif [[ "$FILE_COUNT" -ge 3 ]] || [[ "$LINES_CHANGED" -ge 20 ]]; then
  COMPLEXITY="LOW"
  SUGGESTION_TYPE="consider"
else
  # 1-2 files with <20 lines - skip suggestion unless critical
  COMPLEXITY="SKIP"
  SUGGESTION_TYPE="none"
fi

# Skip if complexity too low
if [[ "$SUGGESTION_TYPE" == "none" ]]; then
  exit 0
fi

# === GENERATE CONTEXT-AWARE SUGGESTION ===

# Get most recent plan
RECENT_PLAN=$(find "$MEMORY_DIR" -name "zen_plan_*.md" -type f -print0 2>/dev/null | \
              xargs -0 ls -t 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo "")

# Build suggestion based on complexity
case "$SUGGESTION_TYPE" in
  strongly_recommend)
    if [[ "$HAS_CRITICAL" == "true" ]]; then
      URGENCY="🚨 **Critical Files Changed - Review Strongly Recommended**"
      REASONING="Security-sensitive files detected:"
      CRITICAL_LIST=$(echo "$CRITICAL_FILES" | head -5)
    else
      URGENCY="⚠️ **Large Changes - Phase 4 Review Strongly Recommended**"
      REASONING="Significant changes detected:"
    fi
    ;;
  recommend)
    URGENCY="💡 **Phase 4 Review Recommended**"
    REASONING="Moderate changes detected:"
    ;;
  consider)
    URGENCY="💡 **Phase 4 Review Available**"
    REASONING="I notice you have:"
    ;;
esac

cat <<EOF

$URGENCY

$REASONING
- $FILE_COUNT file(s) changed ($CODE_FILES code, $CONFIG_FILES config, $DOC_FILES docs)
- $LINES_CHANGED line(s) modified
- $PLAN_COUNT saved plan(s) available
${RECENT_PLAN:+- Most recent plan: $RECENT_PLAN}

EOF

if [[ "$HAS_CRITICAL" == "true" ]]; then
  cat <<EOF
**Critical files:**
$CRITICAL_LIST

EOF
fi

case "$SUGGESTION_TYPE" in
  strongly_recommend)
    cat <<EOF
**Recommended:** Run Phase 4 review before merging:
- Say: "review implementation" or "verify changes against plan"
- Validates: plan alignment, scope creep, security gaps
- Uses: Codex CLI with git/linter execution
- Output: Structured report + merge recommendation

EOF
    ;;
  recommend)
    cat <<EOF
**Consider:** Phase 4 post-implementation review:
- Say: "review implementation" or "verify changes against plan"
- Checks: plan alignment, scope creep, deferred features
- Output: Structured report with actionable recommendations

EOF
    ;;
  consider)
    cat <<EOF
Consider running Phase 4 review if implementation complete:
- Say: "review implementation" or "verify changes against plan"
- Checks: plan alignment, scope creep, critical gaps

EOF
    ;;
esac

exit 0
