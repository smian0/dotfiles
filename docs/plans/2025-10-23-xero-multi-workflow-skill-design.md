# Xero Multi-Workflow Skill Design

**Date**: 2025-10-23
**Purpose**: Merge xero-invoice-copy into xero skill using directory-based workflow composition pattern
**Status**: Design Complete - Ready for Implementation

## Overview

Transform the Xero skill from single-purpose to multi-workflow architecture by merging the specialized invoice-copy workflow while building infrastructure for future workflows (contact-merge, payment-batch, etc.).

## Architecture

### Directory Structure

```
.claude/skills/xero/
├── SKILL.md                              # Main routing + shared protocols (150 lines)
├── workflows/                            # Specialized workflows
│   ├── invoice-copy.md                   # Month increment workflow (100 lines)
│   ├── contact-merge.md                  # Future: merge duplicates
│   └── payment-batch.md                  # Future: batch payments
├── scripts/                              # Shared infrastructure
│   ├── xero-oauth-flow.js               # Token acquisition
│   └── xero-mcp-wrapper.sh              # MCP server wrapper
└── references/
    └── xero-scopes.md                   # OAuth scope documentation
```

### Key Architectural Decisions

**1. Main SKILL.md Responsibilities** (150 lines):
- Workflow detection & routing table
- Shared approval protocol (3-phase gates)
- OAuth token management
- Common troubleshooting
- Standard CRUD operations

**2. Workflow Files** (~100 lines each):
- Pattern-specific validation and parsing
- Specialized execution steps
- Custom approval preview formats
- Workflow-specific error handling

**3. Extensibility**:
- Future workflows: Create new .md file in workflows/
- Same routing mechanism applies
- Reuse shared approval protocol

## Routing Mechanism

### Pattern Matching Table

Located at top of main SKILL.md, immediately after "When to Use":

```markdown
## Workflow Detection & Routing

| User Request Pattern | Workflow File | Trigger Conditions |
|---------------------|---------------|-------------------|
| "copy invoice INV-*-YYYY-MMM-*" | `workflows/invoice-copy.md` | Invoice number matches monthly pattern |
| "merge contacts [names]" | `workflows/contact-merge.md` | Multiple contact names (future) |
| "batch payments [file]" | `workflows/payment-batch.md` | Keyword "batch" + payment type (future) |
| Other write operations | Standard approval protocol below | No workflow match |
| Read operations | Direct execution | No approval needed |

**Routing Instructions:**

1. Parse user request - Extract operation type and invoice number/parameters
2. Check workflow patterns - Match against table (top to bottom priority)
3. If workflow matches:
   - Announce: "I'm using the [workflow name] workflow"
   - Read: `workflows/[filename].md`
   - Follow those specific instructions
   - Return to main skill for shared approval protocol
4. If no workflow matches - Use standard operation flow below
```

### Routing Behavior

**Example: Copy Invoice Request**

1. User: "copy invoice INV-XOLV-2025-AUG-PEETA"
2. Claude parses: operation=copy, invoice=INV-XOLV-2025-AUG-PEETA
3. Pattern matches row 1: `INV-*-YYYY-MMM-*` format detected
4. Claude announces: "I'm using the Invoice Copy with Month Increment workflow"
5. Claude reads `workflows/invoice-copy.md`
6. Executes workflow-specific steps
7. Uses shared approval protocol for validation

## Shared Approval Protocol

### Location
Defined once in main SKILL.md, referenced by all workflows.

### Structure

```markdown
## 🚨 MANDATORY APPROVAL PROTOCOL (Shared by All Workflows)

**CRITICAL: Before ANY write operation to Xero, you MUST obtain explicit human approval.**

### Three-Phase Process

**Phase 1: Analysis & Preview (MANDATORY)**

All workflows must show:
1. Current state (for updates/deletes)
2. Proposed changes
3. Impact explanation
4. Approval question

**Phase 2: Wait for Approval**

STOP and wait for user response.

✅ Approval words: "yes", "proceed", "approve", "confirmed", "ok", "go ahead"
❌ Cancel words: "no", "stop", "cancel", "abort", "wait", "don't"

**Phase 3: Execution (Only if approved)**

Execute MCP tool call and confirm success.

### Custom Preview Formats

Each workflow may customize the preview format while maintaining:
- ✅ All three phases (mandatory)
- ✅ Clear current state → proposed changes
- ✅ Impact explanation
- ✅ Explicit approval question
```

### Workflow Integration

Workflows reference the shared protocol while providing custom preview formats:

**In workflows/invoice-copy.md:**

```markdown
**Step 5: Build Approval Preview**

Use the shared approval protocol with this custom format:

📝 PROPOSED XERO OPERATION: Copy Invoice with Month Increment

**Source Invoice:**
- Number: [source]
- Contact: [name]
- Total: $[amount]

**New Invoice:**
- Number: [incremented] ← AUTO-INCREMENTED MONTH
- Contact: [same]
- Total: $[amount]
- Date: [today]

⚠️ IMPACT:
- Creates new sales invoice
- Month auto-incremented from [OLD] → [NEW]
- All line items copied exactly
- Status: DRAFT (editable)

✅ Proceed with copying this invoice?
```

## Workflow File Structure

### Template for workflows/invoice-copy.md

```markdown
# Workflow: Invoice Copy with Month Increment

**Purpose**: Copy sales invoices with automatic month incrementing

**Pattern**: `INV-CODE-YYYY-MMM-SUFFIX`

## Trigger Conditions

✅ This workflow activates when:
- User says "copy invoice [number]"
- Invoice number matches: `INV-{CODE}-{YYYY}-{MMM}-{SUFFIX}`
- Pattern example: `INV-XOLV-2025-AUG-PEETA`

❌ Does NOT activate when:
- Invoice number missing or doesn't match pattern
- User says "create invoice" instead of "copy"

## Execution Steps

**Step 1: Validate Pattern**
Extract and validate invoice number components

**Step 2: Parse Components**
```
INV-XOLV-2025-AUG-PEETA
→ CODE: XOLV
→ YEAR: 2025
→ MONTH: AUG
→ SUFFIX: PEETA
```

**Step 3: Increment Month**
Use month mapping table:
- JAN → FEB, FEB → MAR, ..., NOV → DEC (same year)
- DEC → JAN (year + 1)

**Step 4: Fetch Source Invoice**
Use `list-invoices` to get complete details

**Step 5: Build Approval Preview**
Follow shared approval protocol with custom format

**Step 6: Wait for Approval**
Reference main skill approval gates

**Step 7: Create Invoice** (only if approved)
Call `create-invoice` with all copied details + new invoice number

**Step 8: Confirm Success**
Show new invoice number and Xero deep link

## Month Increment Logic

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

## Error Handling

**Source invoice not found:**
- Inform user
- Ask to verify invoice number

**Invalid pattern:**
- Show detected pattern
- Ask for confirmation or correction

**Duplicate invoice number:**
- If new number already exists in Xero
- Inform user
- Suggest manual override or skip month
```

### Key Design Principles

1. **Clear trigger conditions** - Explicit activation rules with examples
2. **Step-by-step execution** - Numbered, imperative instructions
3. **Reference shared protocols** - No duplication of approval/auth logic
4. **Workflow-specific validation** - Pattern parsing and error handling
5. **Custom preview formats** - Optimized for operation type

## Migration Process

### Step 1: Create workflows/ directory

```bash
cd /Users/smian/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero
mkdir -p workflows
```

### Step 2: Extract invoice-copy content

**Source**: `xero-invoice-copy/SKILL.md`

**Extract to** `workflows/invoice-copy.md`:
- Invoice number pattern rules (lines 10-22)
- Month increment logic (lines 130-147)
- Execution steps (lines 24-127)
- Custom approval format (lines 72-105)
- Error handling (lines 169-182)

### Step 3: Add routing table to main xero/SKILL.md

**Location**: After "When to Use" section (after line 25)

**Insert**:
- Workflow detection & routing section
- Pattern matching table
- Routing instructions (4-step process)

### Step 4: Keep shared protocols in main SKILL.md

**What stays in main skill** (not duplicated in workflows):
- OAuth token management (lines 152-189)
- Mandatory approval protocol (lines 29-150)
- Xero MCP configuration (lines 207-230)
- Troubleshooting (lines 245-275)
- Available operations overview (lines 232-243)

### Step 5: Update skill description

**Change frontmatter** in `xero/SKILL.md`:

```yaml
# Before
---
name: xero
description: Xero integration with OAuth2 token management and mandatory approval protocol - obtain tokens, manage access, and enforce human approval before any CREATE/UPDATE/DELETE operations
---

# After
---
name: xero
description: Xero integration with smart workflow routing, OAuth2 token management, and mandatory approval protocol
---
```

### Step 6: Delete xero-invoice-copy skill

After migration is complete and tested:

```bash
rm -rf /Users/smian/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero-invoice-copy
```

## Results

### Before Migration

**xero skill:**
- Single SKILL.md: 283 lines
- No workflow routing
- General purpose only

**xero-invoice-copy skill:**
- Separate skill: 237 lines
- Standalone operation
- Total: 520 lines (2 skills)

### After Migration

**xero skill:**
- Main SKILL.md: ~150 lines (routing + shared protocols)
- workflows/invoice-copy.md: ~100 lines (specialized logic)
- Total: 250 lines (1 skill)

**Improvements:**
- 47% reduction in main skill file size
- 52% reduction in total lines
- More modular and maintainable
- Easy to add future workflows
- Single source of truth for OAuth/approval

## Future Workflow Examples

### Contact Merge Workflow

```markdown
# Workflow: Contact Merge

**Pattern**: Multiple contact names or IDs

**Trigger**: "merge contacts [name1] [name2]"

**Steps**:
1. Find both contacts
2. Show details side-by-side
3. Ask which to keep (primary)
4. Preview merge (which fields transfer)
5. Get approval
6. Execute merge
7. Archive duplicate
```

### Payment Batch Workflow

```markdown
# Workflow: Payment Batch

**Pattern**: "batch" + payment file/list

**Trigger**: "create payment batch from [file]"

**Steps**:
1. Parse payment file (CSV/JSON)
2. Validate all invoices exist
3. Calculate total amount
4. Show batch preview
5. Get approval (single approval for entire batch)
6. Execute all payments
7. Report results (success/failures)
```

## Benefits of This Design

### Organization
- Clear separation: Routing logic vs workflow logic
- Easy to add: New workflow = new .md file
- Discoverable: `ls workflows/` shows all operations

### Maintainability
- Independent: Change one workflow without touching others
- Testable: Each workflow validated separately
- Reusable: Shared protocols defined once, used by all

### Claude-Friendly
- Explicit routing: "Read workflows/X.md" is clear
- Context-efficient: Load only relevant workflow file
- Progressive disclosure: Main skill → workflow → protocols

### User Experience
- Automatic pattern detection (no special commands)
- Consistent approval flow across all operations
- Clear workflow announcements ("I'm using X workflow")
- Specialized previews optimized for operation type

## Implementation Checklist

Migration tasks:
- [ ] Create workflows/ directory
- [ ] Extract invoice-copy content to workflows/invoice-copy.md
- [ ] Add routing table to main SKILL.md
- [ ] Verify shared protocols not duplicated
- [ ] Update skill description frontmatter
- [ ] Test invoice-copy workflow activation
- [ ] Test fallback to standard operations
- [ ] Delete xero-invoice-copy skill directory

Validation:
- [ ] Pattern matching works (INV-XOLV-2025-AUG-PEETA triggers workflow)
- [ ] Month increment logic preserved
- [ ] Approval protocol correctly referenced
- [ ] Standard operations still work
- [ ] Non-matching patterns use standard flow

## Related Documentation

- Multi-Workflow Composition Guide: `/Users/smian/dotfiles/claude/.claude/skills/skill-creator/references/multi-workflow-composition.md`
- Original xero skill: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero/SKILL.md`
- Original invoice-copy skill: `/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.claude/skills/xero-invoice-copy/SKILL.md`

---

**Design Status**: ✅ Complete and validated
**Next Step**: Implementation via worktree setup and planning handoff
