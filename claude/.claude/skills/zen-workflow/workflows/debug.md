# Debug Workflow

**Purpose**: Systematic code investigation for complex bugs

## Workflow Steps

### Step 1: Initial Investigation

**Tool**: `mcp__zen__thinkdeep`

**Model selection**: `qwen3-coder:480b-cloud` (best for code analysis)

**Parameters**:
```json
{
  "prompt": "Investigate bug: [description]\n\nSymptoms:\n- [symptom 1]\n- [symptom 2]\n\nRelevant files:\n- [file paths]",
  "model": "qwen3-coder:480b-cloud",
  "step": "[Investigation approach]",
  "step_number": 1,
  "total_steps": 4,
  "next_step_required": true,
  "findings": "[Initial observations]",
  "hypothesis": "[Theory about root cause]",
  "confidence": "low",
  "relevant_files": ["[absolute paths]"],
  "files_checked": ["[files examined]"]
}
```

**Output**: Hypothesis about root cause with evidence

### Step 2: Deep Debugging

**Tool**: `mcp__zen__debug`

**Model selection**:
- Default: `qwen3-coder:480b-cloud`
- If multi-language codebase: `deepseek-v3.1:671b-cloud`

**Parameters**:
```json
{
  "prompt": "Debug investigation continued",
  "model": "qwen3-coder:480b-cloud",
  "step": "[Current debugging step]",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "[Evidence gathered]",
  "hypothesis": "[Updated theory]",
  "confidence": "medium",
  "relevant_files": ["[files containing bug]"],
  "files_checked": ["[all files examined]"],
  "continuation_id": "[from previous step if continuing]"
}
```

**Output**: Root cause identification with fix approach

### Step 3: Validation

**Tool**: `mcp__zen__codereview`

**Model selection**:
- Default: `deepseek-v3.1:671b-cloud` (strong code review)
- If large codebase (>100K LOC): Escalate to `gpt-5`

**Parameters**:
```json
{
  "prompt": "Review proposed fix",
  "model": "deepseek-v3.1:671b-cloud",
  "step": "Validate fix for: [bug description]",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": false,
  "findings": "Proposed fix:\n[code changes]\n\nVerify:\n- Fixes root cause\n- No regressions\n- Follows patterns",
  "relevant_files": ["[files being changed]"],
  "files_checked": ["[all reviewed files]"],
  "review_type": "full",
  "confidence": "high"
}
```

**Output**: Validation report with potential issues

## Example Execution

```
User: "zen debug: authentication flow broken, users logged out after 5 minutes"

Claude: I'm using the zen-workflow skill for systematic debugging.

Step 1: Initial investigation with qwen3-coder
Analyzing authentication flow across codebase

[Execute thinkdeep with qwen3-coder]

Investigation findings:
Files examined: auth.py, session.py, middleware.py, config.py
Hypothesis: Session timeout misconfigured
Evidence:
- config.py sets SESSION_TIMEOUT=300 (5 minutes)
- auth.py expects timeout in seconds
- middleware.py logs session expiry every 5 minutes
Confidence: Medium

Step 2: Deep debugging with qwen3-coder
Tracing session lifecycle

[Execute debug tool]

Root cause identified:
- config.py: SESSION_TIMEOUT=300 (intended as minutes)
- auth.py interprets as seconds (300s = 5 minutes)
- Mismatch between config intent vs code interpretation

Fix approach:
- Change config.py: SESSION_TIMEOUT=300 to SESSION_TIMEOUT_MINUTES=300
- Update auth.py: timeout = config.SESSION_TIMEOUT_MINUTES * 60
- Or change config value to 18000 (5 hours in seconds)

Confidence: High
Files affected: 2 (config.py, auth.py)

Step 3: Validation with deepseek-v3.1
Reviewing proposed fix for issues

[Execute codereview]

Validation results:
✅ Fix addresses root cause
✅ No regressions in session handling
✅ Follows existing config patterns (other timeouts use _MINUTES suffix)
⚠️  Need to update tests (mock SESSION_TIMEOUT_MINUTES)
⚠️  Document breaking config change in migration guide

Recommendation: Proceed with fix + test updates

Cost: $0 (all Ollama Cloud models)
Time: ~4-6 minutes
Confidence: Very High
```

## Quality Checks

**After initial investigation**:
- Is hypothesis specific and testable?
- Are relevant files identified?
- If too vague → Continue investigation or use deepseek for broader analysis

**After debugging**:
- Is root cause clearly identified?
- Is fix approach practical?
- If uncertainty remains → Escalate to gpt-5 or o3

**After validation**:
- Are potential regressions identified?
- Is fix complete (tests, docs, migration)?
- If complex codebase → Use gpt-5 for thorough review

## Escalation Strategy

**Use paid models if**:
- Bug in unfamiliar codebase (use gpt-5 for learning curve)
- Security vulnerability (use o3 or gemini-2.5-pro for depth)
- Performance issue requiring profiling (use gpt-5)
- Race condition or concurrency bug (use o3 for extended thinking)

**Recommended paid alternatives**:
- Investigation: gpt-5 (better at unfamiliar code)
- Debugging: gpt-5 or o3 (extended thinking for complex bugs)
- Validation: gpt-5 (thorough review), gemini-2.5-pro (large codebase)

## Debug Patterns

### Simple Bugs (Single file, obvious cause)
**Don't use workflow** - Use native Claude with Read tool

### Medium Bugs (2-3 files, clear symptoms)
**Abbreviated workflow**:
1. Skip thinkdeep → Go directly to debug with qwen3-coder
2. Use codereview for validation

### Complex Bugs (5+ files, unclear cause)
**Full workflow** as described above

### Heisenbug (Intermittent, hard to reproduce)
**Extended workflow**:
1. Thinkdeep with deepseek-v3.1 (better reasoning for patterns)
2. Debug with continuation for multiple investigation rounds
3. Consider escalating to o3 if race conditions involved

## Bug Type to Model Mapping

**Syntax errors**: Don't use workflow (native Claude sufficient)

**Logic errors**:
- Investigation: qwen3-coder
- Debugging: qwen3-coder
- Validation: deepseek-v3.1

**Integration bugs**:
- Investigation: deepseek-v3.1 (better at system thinking)
- Debugging: deepseek-v3.1
- Validation: deepseek-v3.1 or gpt-5

**Performance issues**:
- Investigation: qwen3-coder → gpt-5 if profiling needed
- Debugging: gpt-5 (better at optimization)
- Validation: gpt-5

**Security vulnerabilities**:
- Investigation: deepseek-v3.1 → o3 if critical
- Debugging: o3 (extended thinking for security implications)
- Validation: o3 or gemini-2.5-pro

**Concurrency bugs**:
- Investigation: deepseek-v3.1
- Debugging: o3 (extended thinking essential)
- Validation: o3 or gpt-5
