# Xero Multi-Workflow Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Merge xero-invoice-copy into xero skill using directory-based multi-workflow pattern

**Architecture:** Extract invoice-copy workflow into workflows/ subdirectory, add routing table to main SKILL.md, consolidate shared protocols (OAuth, approval) in main skill file

**Tech Stack:** Markdown skill files, Claude Code workflow routing, Xero MCP server integration

**Design Reference:** `docs/plans/2025-10-23-xero-multi-workflow-skill-design.md`

---

## Pre-Implementation Checklist

- [ ] Design document reviewed: `docs/plans/2025-10-23-xero-multi-workflow-skill-design.md`
- [ ] Working directory: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero`
- [ ] Backup created of existing xero and xero-invoice-copy skills

---

## Task 1: Create Workflows Directory

**Files:**
- Create: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero/workflows/` (directory)

**Step 1: Create workflows directory**

```bash
cd "/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero"
mkdir -p workflows
```

**Step 2: Verify directory created**

Run: `ls -la workflows`
Expected: Empty directory exists

**Step 3: Commit**

```bash
git add workflows/.gitkeep
git commit -m "feat(xero): create workflows directory for multi-workflow pattern"
```

Note: Create empty `.gitkeep` file if needed to track empty directory

---

## Task 2: Extract Invoice Copy Workflow

**Files:**
- Read: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero-invoice-copy/SKILL.md`
- Create: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero/workflows/invoice-copy.md`

**Step 1: Read source skill**

Read the entire xero-invoice-copy/SKILL.md to extract content.

**Step 2: Create workflow file with header**

Create `workflows/invoice-copy.md` with:

```markdown
# Workflow: Invoice Copy with Month Increment

**Purpose**: Copy sales invoices with automatic month incrementing in invoice numbers

**Pattern**: `INV-CODE-YYYY-MMM-SUFFIX`

## Trigger Conditions

✅ This workflow activates when:
- User says "copy invoice [number]"
- Invoice number matches: `INV-{CODE}-{YYYY}-{MMM}-{SUFFIX}`
- Pattern example: `INV-XOLV-2025-AUG-PEETA`

❌ Does NOT activate when:
- Invoice number missing or doesn't match pattern
- User says "create invoice" instead of "copy"
- Pattern doesn't include month component
```

**Step 3: Add invoice number pattern section**

Extract from xero-invoice-copy/SKILL.md lines 10-22 and add:

```markdown
## Invoice Number Pattern

**Format**: `INV-CODE-YYYY-MMM-SUFFIX`

**Example**: `INV-XOLV-2025-AUG-PEETA`

**Components**:
- `INV` - Fixed prefix
- `CODE` - Preserved from original (e.g., XOLV)
- `YYYY` - Year, auto-increments on year rollover
- `MMM` - 3-letter month (JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC)
- `SUFFIX` - Preserved from original (e.g., PEETA)
```

**Step 4: Add execution steps**

Extract from xero-invoice-copy/SKILL.md lines 24-127 and adapt:

```markdown
## Execution Steps

**Step 1: Parse Source Invoice Number**

Extract components from pattern:
```
INV-XOLV-2025-AUG-PEETA
→ CODE: XOLV
→ YEAR: 2025
→ MONTH: AUG
→ SUFFIX: PEETA
```

**Step 2: Increment Month**

Auto-increment to next month with year rollover:

```
JAN → FEB (same year)
FEB → MAR (same year)
...
NOV → DEC (same year)
DEC → JAN (year + 1)
```

**Example**:
- `INV-XOLV-2025-AUG-PEETA` → `INV-XOLV-2025-SEP-PEETA`
- `INV-XOLV-2025-DEC-PEETA` → `INV-XOLV-2026-JAN-PEETA`

**Step 3: Fetch Source Invoice**

Use `list-invoices` with invoice number to get complete details:
- All line items (description, quantity, unit amount, account code, tax type)
- Contact ID
- Line amount types
- Currency
- All other settings

**Step 4: Build Approval Preview**

Follow the shared approval protocol from main xero skill with this custom format:

📝 PROPOSED XERO OPERATION: Copy Invoice with Month Increment

**Source Invoice:**
- Number: [source invoice number]
- Contact: [contact name]
- Total: $[amount]
- Date: [original date]
- Line Items: [N items]

**New Invoice:**
- Number: [incremented invoice number] ← AUTO-INCREMENTED MONTH
- Contact: [same as source]
- Total: $[same as source]
- Date: [today's date]
- Status: DRAFT
- Line Items:
  • [Item 1 description] - $[amount]
  • [Item 2 description] - $[amount]
  • [All items copied exactly]

⚠️ IMPACT:
- Creates new sales invoice in Xero
- Invoice number auto-incremented from [OLD MONTH] → [NEW MONTH]
- All line items preserved exactly
- Invoice date set to today
- Status: DRAFT (can be edited/deleted)

✅ Proceed with copying this invoice?
Type "yes", "proceed", or "approve" to continue
Type "no", "cancel", or "stop" to abort

**Step 5: Wait for Approval**

STOP and wait for user response.

✅ **Approval words**: "yes", "proceed", "approve", "confirmed", "ok", "go ahead"
❌ **Cancel words**: "no", "stop", "cancel", "abort", "wait", "don't"

**Step 6: Create Invoice** (Only if Approved)

Call `create-invoice` with:
- Type: ACCREC (sales invoice)
- Invoice number: Incremented pattern
- Contact ID: From source
- Line items: Exact copy from source
- Date: Today's date
- Status: DRAFT
- All other settings: Preserved from source

**Step 7: Confirm Success**

Show confirmation with deep link to new invoice in Xero.

✅ Invoice copied successfully!
- New invoice: [new invoice number]
- Total: $[amount]
- Status: DRAFT
- [Deep link to Xero]
```

**Step 5: Add month increment logic**

Extract from xero-invoice-copy/SKILL.md lines 130-147:

```markdown
## Month Increment Logic

Use this mapping for month increment:

```javascript
const monthIncrement = {
  'JAN': { next: 'FEB', yearInc: 0 },
  'FEB': { next: 'MAR', yearInc: 0 },
  'MAR': { next: 'APR', yearInc: 0 },
  'APR': { next: 'MAY', yearInc: 0 },
  'MAY': { next: 'JUN', yearInc: 0 },
  'JUN': { next: 'JUL', yearInc: 0 },
  'JUL': { next: 'AUG', yearInc: 0 },
  'AUG': { next: 'SEP', yearInc: 0 },
  'SEP': { next: 'OCT', yearInc: 0 },
  'OCT': { next: 'NOV', yearInc: 0 },
  'NOV': { next: 'DEC', yearInc: 0 },
  'DEC': { next: 'JAN', yearInc: 1 }
};
```
```

**Step 6: Add pattern validation**

Extract from xero-invoice-copy/SKILL.md lines 150-166:

```markdown
## Pattern Validation

Before processing, validate invoice number matches expected pattern:

**Valid patterns**:
- `INV-XXXX-YYYY-MMM-XXXXX` (standard)
- Components separated by hyphens
- Month must be valid 3-letter code (JAN-DEC)
- Year must be 4 digits

**Invalid patterns**:
- Missing components
- Wrong separator
- Invalid month code
- Non-numeric year

If pattern doesn't match, inform user and ask for clarification.
```

**Step 7: Add error handling**

Extract from xero-invoice-copy/SKILL.md lines 169-182:

```markdown
## Error Handling

**Source invoice not found**:
- Inform user
- Ask them to verify invoice number

**Invalid month in pattern**:
- Show detected month
- Ask user to check if pattern is correct

**Duplicate invoice number**:
- If new invoice number already exists in Xero
- Inform user
- Suggest manual override or skip month
```

**Step 8: Add integration notes**

```markdown
## Integration with Main Xero Skill

This workflow extends the main `xero` skill and follows its approval protocol.

**Prerequisites**:
- Xero MCP server configured
- OAuth tokens in `.env`
- User has read access to source invoice
- User has permission to create sales invoices

**Shared Protocols**:
- OAuth token management (see main skill)
- Mandatory approval protocol (see main skill)
- Error handling (see main skill troubleshooting)
```

**Step 9: Verify workflow file completeness**

Check that workflows/invoice-copy.md contains:
- ✅ Trigger conditions
- ✅ Invoice number pattern
- ✅ Execution steps (7 steps)
- ✅ Month increment logic
- ✅ Pattern validation
- ✅ Error handling
- ✅ Integration notes

**Step 10: Commit**

```bash
git add workflows/invoice-copy.md
git commit -m "feat(xero): extract invoice-copy workflow to workflows/ directory"
```

---

## Task 3: Add Routing Table to Main SKILL.md

**Files:**
- Modify: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero/SKILL.md:25` (insert after "When to Use")

**Step 1: Read main SKILL.md**

Read the current xero/SKILL.md to find insertion point after "When to Use" section.

**Step 2: Insert routing section**

After the "When to Use" section (around line 25), add:

```markdown
## Workflow Detection & Routing

Claude automatically detects specialized workflows based on user request patterns.

**Pattern Matching Table:**

| User Request Pattern | Workflow File | Trigger Conditions |
|---------------------|---------------|-------------------|
| "copy invoice INV-*-YYYY-MMM-*" | `workflows/invoice-copy.md` | Invoice number matches monthly pattern |
| "merge contacts [names]" | `workflows/contact-merge.md` | Multiple contact names (future) |
| "batch payments [file]" | `workflows/payment-batch.md` | Keyword "batch" + payment type (future) |
| Other write operations | Standard approval protocol below | No workflow match |
| Read operations | Direct execution | No approval needed |

**Routing Instructions for Claude:**

1. **Parse user request** - Extract operation type and invoice number/parameters
2. **Check workflow patterns** - Match against table above (top to bottom priority)
3. **If workflow matches**:
   - Announce: "I'm using the [workflow name] workflow"
   - Read the workflow file: `Read workflows/[filename].md`
   - Follow those specific instructions
   - Return to main skill for shared approval protocol
4. **If no workflow matches** - Use standard operation flow below
```

**Step 3: Verify routing section placement**

Check that routing section appears:
- ✅ After "When to Use" section
- ✅ Before "Mandatory Approval Protocol" section
- ✅ Properly formatted table
- ✅ Clear routing instructions

**Step 4: Commit**

```bash
git add SKILL.md
git commit -m "feat(xero): add workflow routing table to main skill"
```

---

## Task 4: Update Skill Description

**Files:**
- Modify: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero/SKILL.md:3` (frontmatter)

**Step 1: Read current frontmatter**

Current:
```yaml
---
name: xero
description: Xero integration with OAuth2 token management and mandatory approval protocol - obtain tokens, manage access, and enforce human approval before any CREATE/UPDATE/DELETE operations
---
```

**Step 2: Update description**

Change to:
```yaml
---
name: xero
description: Xero integration with smart workflow routing, OAuth2 token management, and mandatory approval protocol
---
```

**Step 3: Verify change**

Check that description:
- ✅ Mentions "smart workflow routing"
- ✅ Keeps OAuth2 and approval protocol
- ✅ More concise (under 120 characters)

**Step 4: Commit**

```bash
git add SKILL.md
git commit -m "feat(xero): update description to mention workflow routing"
```

---

## Task 5: Verify Shared Protocols Not Duplicated

**Files:**
- Read: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero/SKILL.md`
- Read: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero/workflows/invoice-copy.md`

**Step 1: Check OAuth section exists only in main SKILL.md**

Verify main SKILL.md contains:
- ✅ OAuth Token Management section
- ✅ Prerequisites (Xero Developer Portal setup)
- ✅ Get Initial Tokens instructions
- ✅ OAuth Scopes section
- ✅ Integration with MCP Server

Verify workflows/invoice-copy.md:
- ✅ References OAuth (does not duplicate)
- ✅ Says "see main skill" for token management

**Step 2: Check approval protocol exists only in main SKILL.md**

Verify main SKILL.md contains:
- ✅ Mandatory Approval Protocol section
- ✅ Three-phase process (Analysis, Wait, Execution)
- ✅ Approval/cancel word lists
- ✅ Operations requiring approval
- ✅ Read-only operations (no approval)

Verify workflows/invoice-copy.md:
- ✅ References approval protocol (does not duplicate)
- ✅ Shows custom preview format only
- ✅ Says "follow shared approval protocol"

**Step 3: Check troubleshooting exists only in main SKILL.md**

Verify main SKILL.md contains:
- ✅ Troubleshooting section
- ✅ Common errors (port 8080, browser, redirect URI, tokens)

Verify workflows/invoice-copy.md:
- ✅ Workflow-specific errors only
- ✅ References main skill troubleshooting

**Step 4: Document findings**

Create checklist of shared vs workflow-specific content:

**Shared (Main SKILL.md only)**:
- OAuth token management
- Mandatory approval protocol
- Xero MCP configuration
- General troubleshooting
- Security notes

**Workflow-specific (workflows/invoice-copy.md)**:
- Pattern parsing
- Month increment logic
- Custom approval preview format
- Workflow-specific validation
- Workflow-specific errors

No commit needed (verification only).

---

## Task 6: Test Workflow Pattern Detection

**Files:**
- Test: Workflow routing logic

**Step 1: Test invoice-copy pattern match**

Simulate user request: "copy invoice INV-XOLV-2025-AUG-PEETA"

Expected Claude behavior:
1. ✅ Parses request: operation=copy, invoice=INV-XOLV-2025-AUG-PEETA
2. ✅ Checks routing table
3. ✅ Matches row 1: INV-*-YYYY-MMM-* pattern
4. ✅ Announces: "I'm using the Invoice Copy with Month Increment workflow"
5. ✅ Reads workflows/invoice-copy.md
6. ✅ Follows workflow-specific steps

**Step 2: Test non-matching pattern fallback**

Simulate user request: "create invoice for John Doe $500"

Expected Claude behavior:
1. ✅ Parses request: operation=create
2. ✅ Checks routing table
3. ✅ No workflow match
4. ✅ Uses standard approval protocol
5. ✅ Follows standard operation flow

**Step 3: Test read operation (no approval)**

Simulate user request: "list all invoices"

Expected Claude behavior:
1. ✅ Parses request: operation=list
2. ✅ Checks routing table
3. ✅ Matches read operation row
4. ✅ Executes directly (no approval needed)

**Step 4: Document test results**

Create test log in commit message showing:
- Pattern matched correctly
- Workflow file loaded
- Fallback to standard flow worked
- Read operations skip approval

No files modified (testing only).

---

## Task 7: Delete xero-invoice-copy Skill

**Files:**
- Delete: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero-invoice-copy/` (entire directory)

**Step 1: Verify migration complete**

Check that:
- ✅ workflows/invoice-copy.md exists and is complete
- ✅ Routing table includes invoice-copy pattern
- ✅ All invoice-copy content migrated
- ✅ No references to old skill remain

**Step 2: Create backup before deletion**

```bash
cd "/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills"
cp -r xero-invoice-copy xero-invoice-copy.backup-$(date +%Y%m%d_%H%M%S)
```

**Step 3: Delete old skill directory**

```bash
rm -rf xero-invoice-copy
```

**Step 4: Verify deletion**

Run: `ls -la | grep xero`
Expected: Only `xero/` directory exists (no `xero-invoice-copy/`)

**Step 5: Commit**

```bash
git add -A
git commit -m "feat(xero): remove xero-invoice-copy skill (merged into xero workflows)"
```

---

## Task 8: Final Verification

**Files:**
- Read: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero/SKILL.md`
- Read: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero/workflows/invoice-copy.md`

**Step 1: Verify directory structure**

Check that xero/ skill has:
```
xero/
├── SKILL.md (updated with routing)
├── workflows/
│   └── invoice-copy.md
├── scripts/
│   ├── xero-oauth-flow.js
│   └── xero-mcp-wrapper.sh
└── references/
    └── xero-scopes.md
```

**Step 2: Verify main SKILL.md structure**

Check sections in order:
1. ✅ Frontmatter (updated description)
2. ✅ Xero Integration Manager header
3. ✅ When to Use
4. ✅ Workflow Detection & Routing (NEW)
5. ✅ Mandatory Approval Protocol
6. ✅ OAuth Token Management
7. ✅ OAuth Scopes
8. ✅ Integration with MCP Server
9. ✅ Available Xero Operations
10. ✅ Troubleshooting
11. ✅ Security Notes
12. ✅ References

**Step 3: Verify workflows/invoice-copy.md structure**

Check sections:
1. ✅ Workflow header
2. ✅ Trigger Conditions
3. ✅ Invoice Number Pattern
4. ✅ Execution Steps (7 steps)
5. ✅ Month Increment Logic
6. ✅ Pattern Validation
7. ✅ Error Handling
8. ✅ Integration with Main Xero Skill

**Step 4: Count lines**

Run:
```bash
wc -l SKILL.md workflows/invoice-copy.md
```

Expected approximately:
- SKILL.md: ~150 lines (was 283, reduced 47%)
- workflows/invoice-copy.md: ~100 lines
- Total: ~250 lines (was 520 across 2 skills, reduced 52%)

**Step 5: Verify no duplication**

Check that these sections appear ONLY in main SKILL.md:
- ✅ OAuth Token Management
- ✅ Mandatory Approval Protocol (phases)
- ✅ MCP Server Configuration
- ✅ General Troubleshooting

Check that these sections appear ONLY in workflows/invoice-copy.md:
- ✅ Invoice Number Pattern
- ✅ Month Increment Logic
- ✅ Pattern Validation
- ✅ Workflow-specific error handling

**Step 6: Document verification**

No commit needed (final verification only).

---

## Post-Implementation Checklist

After all tasks complete:

**Functionality:**
- [ ] Invoice-copy pattern detected automatically
- [ ] Workflow file loads correctly
- [ ] Month increment logic preserved
- [ ] Approval protocol works
- [ ] Standard operations still function
- [ ] Non-matching patterns use standard flow

**Code Quality:**
- [ ] No duplicated content (OAuth, approval, troubleshooting)
- [ ] Main skill ~150 lines
- [ ] Workflow file ~100 lines
- [ ] Total reduction ~52%
- [ ] Directory structure matches design

**Documentation:**
- [ ] Routing table clear and complete
- [ ] Trigger conditions explicit
- [ ] Custom approval format documented
- [ ] Integration notes present
- [ ] References to shared protocols correct

**Git:**
- [ ] All changes committed with clear messages
- [ ] Old skill directory deleted
- [ ] Backup created before deletion
- [ ] Git history clean

---

## Rollback Plan

If issues arise:

**Step 1: Restore from backup**
```bash
cd "/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills"
cp -r xero-invoice-copy.backup-* xero-invoice-copy
```

**Step 2: Revert commits**
```bash
git log --oneline | head -10  # Find commits to revert
git revert <commit-hash>..HEAD
```

**Step 3: Test original skills**
Verify both xero and xero-invoice-copy work independently.

---

## Success Criteria

Implementation complete when:

1. ✅ **Pattern Detection Works**
   - "copy invoice INV-XOLV-2025-AUG-PEETA" triggers invoice-copy workflow
   - Workflow announcement appears
   - Correct workflow file loads

2. ✅ **Workflow Execution Works**
   - Month increment logic functions
   - Approval preview shows correctly
   - Invoice creation succeeds

3. ✅ **Fallback Works**
   - Non-matching patterns use standard flow
   - Read operations skip approval
   - Standard CRUD operations function

4. ✅ **No Duplication**
   - Shared protocols in main skill only
   - Workflow-specific logic in workflow file only
   - No redundant content

5. ✅ **Code Quality**
   - 52% total line reduction achieved
   - Clear separation of concerns
   - Easy to add future workflows

6. ✅ **Documentation Complete**
   - Routing table accurate
   - Trigger conditions clear
   - Integration notes present
