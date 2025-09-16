# OpenCode Plugin Tests

## Test Scripts

### Comprehensive Agent Transformer Test (`test-agent-transformer.js`)

The `test-agent-transformer.js` script provides comprehensive testing with three phases:
1. **Detailed Audit Analysis** - Shows step-by-step transformation process
2. **Unit Test Validation** - Verifies output against expected results  
3. **File Output & Summary** - Saves converted files and provides overall assessment

### Usage

**Comprehensive Test:**
```bash
# Test default fixture with full audit + unit test validation
node test-agent-transformer.js

# Test specific agent file (audit only, no unit test comparison)
node test-agent-transformer.js /path/to/agent.md

# Returns exit code 0 (pass) or 1 (fail) for CI/automation
node test-agent-transformer.js; echo "Exit code: $?"

# Test from any directory
node /Users/smian/dotfiles/opencode/.config/opencode/tests/test-agent-transformer.js
```

### What It Tests

1. **YAML Parsing** - Verifies frontmatter is correctly parsed
2. **Field Transformation** - Shows which fields are added/removed
3. **Description Processing** - Tests sentence formatting
4. **Body Content** - Validates Claude→OpenCode reference updates
5. **OpenCode Compatibility** - Checks if result meets OpenCode requirements
6. **File Output** - Saves converted agent to `test-output/converted/` directory

### Output Sections

- **Original Format** - Shows Claude agent frontmatter
- **Transformation Steps** - Field-by-field changes
- **Transformed Format** - Final OpenCode-compatible result
- **Output Saved** - File path and size of converted agent
- **Validation Checks** - Compatibility verification
- **Summary** - Size changes and modifications

### Example Output

```
🔍 TRANSFORMATION AUDIT: news.md
==================================================

📄 ORIGINAL CLAUDE FORMAT:
---------------------------
 1: ---
 2: name: news
 3: description: Advanced news aggregation...
 4: tools: Read, Write, Grep...

🔧 TRANSFORMATION STEPS:
-------------------------
   name: "news" → REMOVED
   tools: "Read, Write..." → REMOVED
   mode: NEW → "all"
   model: NEW → "zhipuai/glm-4.5"

💾 OUTPUT SAVED:
-----------------
✅ Converted file: /path/to/tests/test-output/converted/news-converted.md
📏 File size: 5717 bytes

✅ PASS - Agent should work in OpenCode
```

### Troubleshooting

If the script fails:
1. Check that the target agent file exists
2. Verify the file has valid YAML frontmatter (wrapped in `---`)
3. Ensure Node.js supports ES modules

### Output Files

Converted agents are saved with `-converted.md` suffix:
- Input: `news.md` → Output: `news-converted.md`
- Location: `tests/test-output/converted/`
- Format: Ready-to-use OpenCode agent files

### Files Tested

This script uses the exact same transformation logic as the live plugin at:
`/Users/smian/dotfiles/opencode/.config/opencode/plugin/agent-transformer.js`