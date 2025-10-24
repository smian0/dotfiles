# Multi-Workflow Skill Composition

When a skill needs to handle **2+ specialized workflows** (different operation types with distinct procedures), use the **directory-based workflows pattern**.

## When to Use Multi-Workflow Pattern

**Triggers:**
- Skill handles 2+ distinct operation types (e.g., invoice copy, contact merge, payment batch)
- Each operation has unique validation/approval/execution logic
- Operations share common infrastructure (auth, API client, approval protocol)
- Future workflows likely to be added

**Examples:**
- **Xero skill**: Standard CRUD + specialized workflows (invoice-copy, contact-merge, payment-batch)
- **Git skill**: Standard commands + specialized workflows (release-flow, hotfix-flow, feature-flow)
- **Database skill**: Standard queries + specialized workflows (migration, backup-restore, schema-sync)

## Directory Structure

```
.claude/skills/<skill-name>/
├── SKILL.md                    # Main routing + shared protocols
├── workflows/                  # Specialized workflows
│   ├── workflow-one.md
│   ├── workflow-two.md
│   └── workflow-three.md
├── scripts/                    # Shared scripts
├── references/                 # Shared documentation
└── assets/                     # Shared templates
```

## Main SKILL.md Structure

```markdown
---
name: skill-name
description: [Include "with smart workflow routing" if multi-workflow]
---

# Skill Name

## When to Use
[Triggers for main skill and all workflows]

## Workflow Detection & Routing

**Pattern Matching Table:**

| User Request Pattern | Workflow File | Trigger Conditions |
|---------------------|---------------|-------------------|
| "operation-A [params]" | `workflows/operation-a.md` | Keyword + pattern match |
| "operation-B [params]" | `workflows/operation-b.md` | Keyword + pattern match |
| Other operations | Standard flow below | No workflow match |

**Routing Instructions:**

1. **Parse user request** - Extract operation type and parameters
2. **Check workflow patterns** - Match against table (top to bottom)
3. **If workflow matches**:
   - Announce: "I'm using the [workflow name] workflow"
   - Read the workflow file: `Read workflows/[filename].md`
   - Follow those specific instructions
   - Return to main skill for shared protocols
4. **If no workflow matches** - Use standard operation flow below

## Shared Protocols

[Shared logic used by ALL workflows - approval, auth, error handling, etc.]

## Standard Operations

[Default behavior when no specialized workflow matches]
```

## Workflow File Structure

**Template for workflows/[name].md:**

```markdown
# Workflow: [Descriptive Name]

**Purpose**: [One-line description]

**Pattern**: [Specific pattern this workflow handles]

## Trigger Conditions

✅ This workflow activates when:
- [Condition 1 - keywords]
- [Condition 2 - pattern match]
- [Condition 3 - parameters]

## Execution Steps

**Step 1: [Action Name]**
[Detailed instructions]

**Step 2: [Action Name]**
[Detailed instructions]

**Step N: [Action Name]**
[Detailed instructions]

## Custom Approval/Validation (if needed)

[Workflow-specific approval format or validation logic]

## Error Handling

[Workflow-specific error cases and recovery]

## Examples

[Typical usage examples for this workflow]
```

## Shared vs Workflow-Specific Logic

**Main SKILL.md (Shared):**
- Authentication and token management
- Common approval protocol (gates, required/optional)
- API client initialization
- Error codes and troubleshooting
- Prerequisite setup instructions

**Workflow Files (Specific):**
- Pattern detection and parsing
- Workflow-specific validation
- Custom approval preview format
- Operation-specific parameters
- Specialized error handling

## Routing Mechanism Best Practices

### 1. Pattern Matching Order

Match patterns **top to bottom** - most specific first:

```markdown
| "copy invoice INV-*-YYYY-MMM-*" | workflows/invoice-copy.md | MOST SPECIFIC |
| "copy invoice *" | workflows/invoice-simple-copy.md | LESS SPECIFIC |
| "create invoice" | Standard flow | GENERIC |
```

### 2. Clear Trigger Conditions

Each workflow file should explicitly state activation conditions:

```markdown
## Trigger Conditions

✅ Activates when:
- User says "copy invoice [number]"
- Invoice number matches: `INV-{CODE}-{YYYY}-{MMM}-{SUFFIX}`
- Pattern example: `INV-XOLV-2025-AUG-PEETA`

❌ Does NOT activate when:
- Invoice number is missing
- Pattern doesn't match (e.g., `INV-123-2025`)
- User says "create invoice" instead of "copy"
```

### 3. Workflow Announcement

Claude should announce which workflow is being used:

```
User: "copy invoice INV-XOLV-2025-AUG-PEETA"

Claude: "I'm using the Invoice Copy with Month Increment workflow."
[Proceeds with workflow-specific steps]
```

### 4. Shared Protocol References

Workflows should reference (not duplicate) shared protocols:

```markdown
**Step 5: Get Approval**

Follow the shared approval protocol from main skill with this custom preview:

[Custom approval format for this workflow]
```

## Benefits of This Pattern

### Organization
- **Clear separation**: Routing logic vs workflow logic
- **Easy to add**: New workflow = new .md file
- **Discoverable**: `ls workflows/` shows all specialized operations

### Maintainability
- **Independent**: Change one workflow without touching others
- **Testable**: Each workflow can be validated separately
- **Reusable**: Shared protocols defined once, used by all

### Claude-Friendly
- **Explicit routing**: "Read workflows/X.md" is clear instruction
- **Context-efficient**: Load only relevant workflow file
- **Progressive disclosure**: Main SKILL.md → workflow file → shared protocols

## When NOT to Use This Pattern

**Don't use multi-workflow pattern if:**
- ❌ Only 1 specialized operation (just include in main SKILL.md)
- ❌ Operations are trivially similar (use parameters instead)
- ❌ Each "workflow" is just 2-3 lines (too granular)

**Use simpler patterns:**
- **Parameters**: If logic is same, just different values
- **Conditional sections**: If small variations in main workflow
- **Delegation**: If operation needs different specialist (use Task tool)

## Migration Path

### Converting Single-Workflow to Multi-Workflow

If a skill grows from 1 → 2+ specialized workflows:

1. **Create workflows/ directory**
2. **Move specialized logic** to workflows/[name].md
3. **Add routing table** to main SKILL.md
4. **Keep shared protocols** in main SKILL.md
5. **Update description** to mention "smart workflow routing"

### Example: Xero Skill Evolution

**Before (single-workflow):**
```
.claude/skills/xero/SKILL.md (400 lines - everything)
```

**After (multi-workflow):**
```
.claude/skills/xero/
├── SKILL.md (150 lines - routing + shared)
└── workflows/
    ├── invoice-copy.md (100 lines)
    ├── contact-merge.md (80 lines)
    └── payment-batch.md (90 lines)
```

**Benefits:**
- Main skill is 62% shorter and clearer
- Each workflow is focused and testable
- Adding new workflow doesn't touch existing code

## Redundancy Analysis After Refactoring

After splitting a skill into multi-workflow pattern, **check for redundant content** that now lives in both the main skill and workflow files.

### Common Redundancy Patterns

**1. Duplicated Examples**

❌ **Problem:**
```markdown
# Main SKILL.md
## Workflow Examples
- Example: Sync user-level MCP servers
  - Run: ~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh
  - Expected: Servers appear in claude mcp list
...

# workflows/sync-user.md
## Example
Run: ~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh
Expected: Servers appear in claude mcp list
```

✅ **Solution:**
```markdown
# Main SKILL.md
## Examples & Checklists

**For workflow-specific examples and checklists, see individual workflow files:**

**Quick links:**
- [Sync User: Example](./workflows/sync-user.md#example)
- [Add Server: Example & Checklist](./workflows/add-server.md#example)
```

**2. Duplicated Checklists**

❌ **Problem:**
```markdown
# Main SKILL.md
## Checklist
**Add Server:**
- [ ] Configuration validated
- [ ] Server shows as connected
...

# workflows/add-server.md
## Checklist
- [ ] Configuration validated
- [ ] Server shows as connected
```

✅ **Solution:**
Keep checklists ONLY in workflow files. Main skill references them:
```markdown
# Main SKILL.md
See individual workflow files for complete checklists:
- [Add Server Checklist](./workflows/add-server.md#checklist)
```

**3. Duplicated Error Handling**

❌ **Problem:**
Same troubleshooting steps in both main skill and workflow file.

✅ **Solution:**
- **Workflow-specific errors** → workflow file only
- **Common errors across workflows** → main skill only
- Reference shared errors from workflows: "See main skill troubleshooting"

### Redundancy Detection Process

**Step 1: Identify duplicate sections**

Compare main SKILL.md against workflow files for:
- Examples sections
- Checklists sections
- Troubleshooting steps
- Best practices

**Step 2: Determine ownership**

Ask: "Is this specific to one workflow or shared across all?"
- **Workflow-specific** → Keep in workflow file ONLY
- **Shared across all** → Keep in main skill ONLY

**Step 3: Replace with references**

In main SKILL.md:
```markdown
## Examples & Checklists

**For workflow-specific examples and checklists, see individual workflow files:**

Each workflow file contains:
- ✅ Complete step-by-step examples for that workflow
- ✅ Workflow-specific checklists
- ✅ Error handling examples
- ✅ Common patterns and use cases

**Quick links:**
- [Workflow A: Example](./workflows/workflow-a.md#example)
- [Workflow B: Checklist](./workflows/workflow-b.md#checklist)
```

**Step 4: Verify DRY compliance**

Check that each piece of content exists in exactly ONE place:
- [ ] No duplicated examples (reference instead)
- [ ] No duplicated checklists (reference instead)
- [ ] No duplicated error handling (reference instead)
- [ ] Shared content in main skill ONLY
- [ ] Workflow-specific content in workflow files ONLY

### Benefits of Removing Redundancy

**Single Source of Truth:**
- Update example once, not in multiple places
- Easier to keep content consistent
- Reduces file size and cognitive load

**Context Efficiency:**
- Main skill stays focused on routing and shared logic
- Workflow files contain complete, self-contained procedures
- No confusion about which version is "correct"

**File Length Management:**
- Removing redundancy can reduce main skill by 5-15%
- Makes skills easier to scan and understand
- Improves load time and clarity

### Example: mcp-manager Cleanup

**Before redundancy removal:**
```
Main SKILL.md: 887 lines
- Routing table
- Shared protocols
- Workflow Examples section (duplicates from workflow files)
- Checklist section (duplicates from workflow files)
```

**After redundancy removal:**
```
Main SKILL.md: 814 lines (8% reduction)
- Routing table
- Shared protocols
- Examples & Checklists reference section (22 lines with links)
```

**Impact:**
- Removed 73 lines of duplicated content
- Single source of truth maintained
- Easier to update and maintain

## Checklist for Multi-Workflow Skills

Creating a new multi-workflow skill:
- [ ] Created workflows/ subdirectory
- [ ] Main SKILL.md has routing table
- [ ] Each workflow file has clear trigger conditions
- [ ] Shared protocols in main SKILL.md (not duplicated)
- [ ] Routing instructions reference workflow files explicitly
- [ ] Description mentions "smart workflow routing"
- [ ] Tested pattern matching order (most specific first)

Converting existing skill to multi-workflow:
- [ ] Identified 2+ specialized workflows
- [ ] Extracted workflows to separate files
- [ ] Added routing table to main SKILL.md
- [ ] Verified shared protocols not duplicated
- [ ] **Performed redundancy analysis** (check for duplicate examples/checklists)
- [ ] **Replaced duplicates with references** to workflow files
- [ ] **Verified DRY compliance** (single source of truth)
- [ ] Updated skill description
- [ ] Tested workflow activation conditions

## Real-World Examples

### Example 1: Xero Integration

**Workflows:**
- `invoice-copy.md` - Copy invoices with month increment
- `contact-merge.md` - Merge duplicate contacts
- `payment-batch.md` - Process batch payments

**Shared in main:**
- OAuth token management
- Mandatory approval protocol
- API error handling

### Example 2: Git Flow

**Workflows:**
- `feature-flow.md` - Feature branch workflow
- `release-flow.md` - Release branch workflow
- `hotfix-flow.md` - Hotfix workflow

**Shared in main:**
- Branch naming conventions
- Commit message format
- PR creation

### Example 3: Database Operations

**Workflows:**
- `migration-flow.md` - Schema migration workflow
- `backup-restore.md` - Backup and restore
- `data-sync.md` - Cross-environment sync

**Shared in main:**
- Connection pooling
- Transaction handling
- Rollback procedures

## Summary

**Use multi-workflow pattern when:**
- 2+ specialized operation types
- Each has distinct procedures
- Shared infrastructure exists
- Future growth likely

**Structure:**
- Main SKILL.md: Routing + shared protocols
- workflows/: One file per specialized workflow
- Clear pattern matching and activation conditions
- Explicit workflow announcements

**Result:**
- Better organization and maintainability
- Easy to add new workflows
- Clear separation of concerns
- Claude-friendly routing logic
