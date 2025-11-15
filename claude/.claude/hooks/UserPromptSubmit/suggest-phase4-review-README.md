# Phase 4 Review Suggestion Hook (Complexity-Aware)

## Purpose

Intelligently suggests running Phase 4 post-implementation review based on change complexity. Avoids noise for trivial changes while strongly recommending review for large or security-sensitive modifications.

## How It Works

**Trigger:** On every user prompt submit (UserPromptSubmit hook)

**Detection logic:**
1. Checks if `.serena/memories/` directory exists
2. Counts saved `zen_plan_*.md` files
3. Checks git status for uncommitted changes
4. **Analyzes complexity metrics:**
   - File count (changed files)
   - Lines changed (insertions + deletions)
   - File types (code vs config vs docs)
   - Critical file patterns (auth, security, database)
5. Classifies complexity level
6. Generates context-aware suggestion (or skips if too trivial)

## Complexity Levels

| Level | Criteria | Suggestion Type | Example Output |
|-------|----------|-----------------|----------------|
| **SKIP** | 1-2 files, <20 lines | None (silent) | _(no output)_ |
| **LOW** | 3-5 files OR 20-100 lines | Soft suggestion | "💡 Phase 4 Review Available" |
| **MEDIUM** | 6-15 files OR 100-500 lines | Recommend | "💡 Phase 4 Review Recommended" |
| **HIGH** | 16+ files OR 500+ lines | Strong recommendation | "⚠️ Large Changes - Review Strongly Recommended" |
| **CRITICAL** | Security/auth/database files | Strong recommendation | "🚨 Critical Files Changed - Review Strongly Recommended" |

**Critical file patterns:**
- auth*, security*, database*, migration*
- *secret*, *credential*, *password*, *token*
- crypto*, jwt*, oauth*

**Example output (MEDIUM complexity):**
```
💡 **Phase 4 Review Recommended**

Moderate changes detected:
- 8 file(s) changed (6 code, 1 config, 1 docs)
- 245 line(s) modified
- 2 saved plan(s) available
- Most recent plan: zen_plan_2025-11-14_authentication-system.md

**Consider:** Phase 4 post-implementation review:
- Say: "review implementation" or "verify changes against plan"
- Checks: plan alignment, scope creep, deferred features
- Output: Structured report with actionable recommendations
```

**Example output (CRITICAL complexity):**
```
🚨 **Critical Files Changed - Review Strongly Recommended**

Security-sensitive files detected:
- 4 file(s) changed (3 code, 1 config, 0 docs)
- 87 line(s) modified
- 2 saved plan(s) available

**Critical files:**
auth/oauth2.py
auth/jwt_handler.py
security/csrf.py

**Recommended:** Run Phase 4 review before merging:
- Say: "review implementation" or "verify changes against plan"
- Validates: plan alignment, scope creep, security gaps
- Uses: Codex CLI with git/linter execution
- Output: Structured report + merge recommendation
```

## Configuration

**File:** `~/.claude/settings.json`

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/UserPromptSubmit/suggest-phase4-review.sh",
            "timeout": 3
          }
        ]
      }
    ]
  }
}
```

## When It Suggests

✅ **Will suggest when:**
- Plans exist in `.serena/memories/zen_plan_*.md`
- Git repository has uncommitted changes
- **Complexity threshold met:**
  - 3+ files changed, OR
  - 20+ lines modified, OR
  - Security/auth/database files changed (any amount)

❌ **Will NOT suggest when:**
- No plans exist
- No git changes detected
- Not in a git repository
- `.serena/memories/` doesn't exist
- **Changes too trivial:** 1-2 files with <20 lines (unless critical files)

## Complexity Metrics Breakdown

**File count threshold:**
- SKIP: 1-2 files
- LOW: 3-5 files
- MEDIUM: 6-15 files
- HIGH: 16+ files

**Lines changed threshold:**
- SKIP: <20 lines
- LOW: 20-100 lines
- MEDIUM: 100-500 lines
- HIGH: 500+ lines

**File type classification:**
- **Code:** .py, .js, .ts, .tsx, .jsx, .go, .rs, .java, .cpp, .c, .h
- **Config:** .json, .yaml, .yml, .toml, .ini, .env, .conf
- **Docs:** .md, .txt, .rst

**Critical patterns override:** Any changes to files matching critical patterns immediately trigger "CRITICAL" level, regardless of file count or lines changed

## Customization Options

### Option 1: Adjust Complexity Thresholds

Modify thresholds to match your team's needs:

```bash
# In the hook script, change lines 76-91:

# More strict (fewer suggestions):
elif [[ "$FILE_COUNT" -ge 20 ]] || [[ "$LINES_CHANGED" -ge 1000 ]]; then
  COMPLEXITY="HIGH"
  SUGGESTION_TYPE="strongly_recommend"
elif [[ "$FILE_COUNT" -ge 10 ]] || [[ "$LINES_CHANGED" -ge 200 ]]; then
  COMPLEXITY="MEDIUM"
  SUGGESTION_TYPE="recommend"
elif [[ "$FILE_COUNT" -ge 5 ]] || [[ "$LINES_CHANGED" -ge 50 ]]; then
  COMPLEXITY="LOW"
  SUGGESTION_TYPE="consider"

# More lenient (more suggestions):
elif [[ "$FILE_COUNT" -ge 10 ]] || [[ "$LINES_CHANGED" -ge 200 ]]; then
  COMPLEXITY="HIGH"
  SUGGESTION_TYPE="strongly_recommend"
elif [[ "$FILE_COUNT" -ge 4 ]] || [[ "$LINES_CHANGED" -ge 50 ]]; then
  COMPLEXITY="MEDIUM"
  SUGGESTION_TYPE="recommend"
elif [[ "$FILE_COUNT" -ge 2 ]] || [[ "$LINES_CHANGED" -ge 10 ]]; then
  COMPLEXITY="LOW"
  SUGGESTION_TYPE="consider"
```

### Option 2: Add Custom Critical Patterns

Add project-specific critical files:

```bash
# In the hook script, modify line 62:

# Add your patterns:
CRITICAL_PATTERNS="(auth|security|database|migration|secret|credential|password|token|crypto|jwt|oauth|payment|billing|admin)"

# Or make it project-specific:
# E-commerce: payment, checkout, cart
# Healthcare: patient, medical, hipaa
# Financial: transaction, ledger, account
```

### Option 3: Add Cooldown (Don't Suggest Too Frequently)

Add state tracking to avoid repeated suggestions:

```bash
# Create state file
STATE_FILE="${HOME}/.claude/hooks/.phase4-last-suggested"

# Check if suggested recently (within last 30 minutes)
if [[ -f "$STATE_FILE" ]]; then
  LAST_SUGGESTED=$(cat "$STATE_FILE")
  CURRENT_TIME=$(date +%s)
  TIME_DIFF=$((CURRENT_TIME - LAST_SUGGESTED))

  if [[ $TIME_DIFF -lt 1800 ]]; then
    # Suggested less than 30 minutes ago, skip
    exit 0
  fi
fi

# Suggest and update state
echo "$(date +%s)" > "$STATE_FILE"
```

### Option 4: Only Suggest for Code Files

Ignore changes to docs/config, only suggest when code files changed:

```bash
# In the hook script, after line 69, add:

# Skip if no code files changed
if [[ "$CODE_FILES" -eq 0 ]]; then
  exit 0
fi
```

## Testing

**Manual test:**
```bash
CLAUDE_CWD=/path/to/project bash ~/.claude/hooks/UserPromptSubmit/suggest-phase4-review.sh
```

**Expected output:**
- If conditions met: Phase 4 review suggestion
- If conditions not met: No output (silent)

## Troubleshooting

### Hook doesn't trigger

1. Check hook is registered in `~/.claude/settings.json`
2. Verify script is executable: `chmod +x ~/.claude/hooks/UserPromptSubmit/suggest-phase4-review.sh`
3. Check Claude Code restarted after config change
4. Test manually with command above

### Too many suggestions

**Solutions:**
- Add cooldown mechanism (Option 2)
- Filter to code files only (Option 1)
- Use phrase-based triggering (Option 3)
- Increase timeout to limit execution frequency

### Suggestions not helpful

**Disable the hook:**
Remove from `settings.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          // Remove the suggest-phase4-review.sh entry
        ]
      }
    ]
  }
}
```

## Integration with zen-plan Skill

This hook complements the zen-plan skill's Phase 4 workflow:

**Complete workflow:**
1. User creates plan with `zen plan`
2. Plan saved to `.serena/memories/zen_plan_*.md`
3. User implements features (Write/Edit tools)
4. Git changes accumulate
5. **Hook suggests Phase 4 review** ← This hook
6. User says "review implementation"
7. zen-plan Phase 4 validates code against plan
8. Report generated with alignment matrix
9. User fixes issues or merges

## Alternative Approaches

### PostToolUse Hook (After Write/Edit)

More granular but potentially noisier:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/PostToolUse/suggest-phase4-after-edit.sh",
            "timeout": 3
          }
        ]
      }
    ]
  }
}
```

Pros: Immediate suggestion after code changes
Cons: Triggers frequently, may interrupt flow

### Manual Invocation (No Hook)

Users simply remember to run Phase 4 review:
- Say "review implementation" when done
- No automatic suggestion needed

Pros: Full user control, no noise
Cons: Easy to forget, less consistent

## Recommended Setup

**For most users:** Current UserPromptSubmit hook with cooldown

**For minimal noise:** Phrase-based triggering (Option 3)

**For no automation:** Disable hook, manual invocation only

## Related Files

- Hook script: `~/.claude/hooks/UserPromptSubmit/suggest-phase4-review.sh`
- Config: `~/.claude/settings.json`
- zen-plan skill: `.claude/skills/zen-plan/SKILL.md`
- Saved plans: `.serena/memories/zen_plan_*.md`
