# Perplexity Search

Search Perplexity AI for the query using Chrome automation.

Usage: `/perplexity <query>`

## Task

Automate a Perplexity AI search using the chrome-devtools MCP server to control Chrome Profile 7.

**Query:** {all_text_after_command}

## Steps

### 1. Prerequisites Check

Verify Chrome is running with debugging enabled:
```javascript
try {
  const pages = await mcp__chrome-devtools__list_pages();
  // Chrome is running with debug mode
} catch (error) {
  // Ask user to launch Chrome with debugging
  return "❌ Chrome not running with debugging. Please run: ./scripts/launch-chrome.sh 'Profile 7' enable-debug";
}
```

### 2. Navigate to Perplexity

```javascript
await mcp__chrome-devtools__navigate_page({ url: "https://www.perplexity.ai" });
```

### 3. Wait for Page Load

```javascript
await mcp__chrome-devtools__wait_for({ text: "Ask anything", timeout: 10000 });
```

### 4. Find Search Box

Take a snapshot to locate the search textarea:
```javascript
const snapshot = await mcp__chrome-devtools__take_snapshot();
```

Look for: `textbox "Ask anything or @mention a Space"` and note its UID.

### 5. Fill Search Query

```javascript
await mcp__chrome-devtools__fill({
  uid: "[TEXTAREA_UID_FROM_SNAPSHOT]",
  value: "{all_text_after_command}"
});
```

### 6. Submit Search

After filling, the Submit button becomes enabled. Find it in the snapshot (usually nearby the textarea) and click it:
```javascript
await mcp__chrome-devtools__click({ uid: "[SUBMIT_BUTTON_UID]" });
```

### 7. Wait for Results

```javascript
await mcp__chrome-devtools__wait_for({ text: "Answer", timeout: 15000 });
```

Wait a few more seconds for the AI to generate the response:
```javascript
// Use JavaScript to wait
await mcp__chrome-devtools__evaluate_script({
  function: "() => new Promise(resolve => setTimeout(resolve, 8000))"
});
```

### 8. Extract Results

```javascript
const result = await mcp__chrome-devtools__evaluate_script({
  function: `() => {
    // Find the main answer content
    const mainContent = document.querySelector('main');
    if (mainContent) {
      return mainContent.innerText.substring(0, 3000);
    }
    return document.body.innerText.substring(0, 2000);
  }`
});
```

### 9. Present Results

Format and display to user:

```markdown
🔍 **Perplexity Search:** {all_text_after_command}

================================================================================

[EXTRACTED_CONTENT]

================================================================================

📍 Full results visible in Chrome Profile 7
🔗 Page: https://www.perplexity.ai
```

## Error Handling

- If Chrome not running → Ask user to launch it
- If Cloudflare challenge → Wait 10 seconds and retry
- If textarea not found → Take screenshot for debugging
- If timeout → Increase wait time and retry once

## Important Notes

- Element UIDs change each time - always use fresh snapshot
- Submit button only enabled after filling textarea
- AI response takes 5-15 seconds to generate
- Don't present results until AI finishes generating
