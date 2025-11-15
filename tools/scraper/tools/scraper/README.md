# Web Scraping Agent with Chrome DevTools MCP

AI-powered web scraping agent with interactive automation, data extraction, and monitoring capabilities. Uses Chrome DevTools MCP to control Chrome browser with your existing profile (preserves cookies, sessions, and authentication).

## Features

- 🤖 **Interactive Automation** - Click, fill forms, navigate multi-step processes
- 📊 **Data Extraction** - Extract structured data (JSON, CSV, Markdown)
- 👀 **Monitoring** - Track changes over time with alerts
- 🧠 **LLM Analysis** - Summarize and analyze scraped data
- 🔐 **Profile Persistence** - Use your Chrome profile (stay logged in)
- 26 **Chrome DevTools MCP Tools** - Full browser automation

## Quick Start

### 1. Start Chrome with Remote Debugging

```bash
# macOS (uses your actual Chrome profile with cookies/logins)
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome" \
  --profile-directory="Default"

# Linux
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.config/google-chrome" \
  --profile-directory="Default"
```

### 2. Verify Chrome is Running

Open http://127.0.0.1:9222/json in another browser. You should see JSON listing open tabs.

### 3. Make Agent Executable

```bash
chmod +x scraper_agent.py
```

### 4. Run the Agent

```bash
# See all commands
./scraper_agent.py --help

# Show setup instructions
./scraper_agent.py setup

# Test scraping
./scraper_agent.py scrape https://example.com
```

## Commands

### `scrape` - Extract Data from URL

Scrape data from a website and save to files.

**Basic usage:**
```bash
# Scrape and display
./scraper_agent.py scrape https://example.com

# Save to JSON
./scraper_agent.py scrape https://example.com -o data.json

# Save as Markdown report
./scraper_agent.py scrape https://portfolio123.com/app/taxonomy \
  -o taxonomy.md --format markdown

# Custom extraction prompt
./scraper_agent.py scrape https://example.com \
  --prompt "Extract all product names, prices, and availability status"
```

**Options:**
- `--output, -o` - Output file path (JSON, CSV, or Markdown)
- `--format` - Output format: `json` (default), `csv`, or `markdown`
- `--prompt, -p` - Custom extraction instructions

### `monitor` - Track Changes Over Time

Periodically scrape a URL and alert on changes.

**Basic usage:**
```bash
# Check every 60 seconds (default)
./scraper_agent.py monitor https://example.com

# Check every 5 minutes
./scraper_agent.py monitor https://example.com -i 300

# Alert on specific conditions
./scraper_agent.py monitor https://example.com/product \
  --condition "price < 50" \
  --alert-file price_alerts.txt

# Run 10 times then exit
./scraper_agent.py monitor https://example.com --max-runs 10
```

**Options:**
- `--interval, -i` - Check interval in seconds (default: 60)
- `--condition, -c` - Alert condition (e.g., "price < 100")
- `--alert-file, -a` - File to append alerts
- `--max-runs` - Maximum number of checks (0 = infinite)

**Use cases:**
- Price monitoring
- Inventory tracking
- News/content updates
- Application status checks

### `analyze` - Analyze Scraped Data

Use LLM to analyze and summarize scraped data.

**Basic usage:**
```bash
# Analyze and display summary
./scraper_agent.py analyze data.json

# Save analysis to file
./scraper_agent.py analyze data.json -o analysis.md

# Just display data without summarizing
./scraper_agent.py analyze data.json --no-summarize
```

**Options:**
- `--summarize/--no-summarize` - Generate LLM summary (default: yes)
- `--output, -o` - Output file for analysis

### `chat` - Interactive Mode

Conversational interface for ad-hoc scraping tasks.

**Usage:**
```bash
./scraper_agent.py chat
```

**Example session:**
```
🕷️  Web Scraping Agent - Interactive Mode
==================================================

Tell me what to scrape, and I'll handle it!
Type 'exit' or 'quit' to stop.

> Go to portfolio123.com/app/taxonomy and extract all category names

[Agent navigates and extracts data]

> Now get the description for each category

[Agent extracts descriptions]

> exit

👋 Goodbye!
```

### `setup` - Show Setup Instructions

Display detailed setup instructions for Chrome and MCP.

```bash
./scraper_agent.py setup
```

## Global Options

Available for all commands:

```bash
--chrome-url URL      # Chrome remote debugging URL (default: http://127.0.0.1:9222)
--model MODEL         # Ollama model to use (default: glm-4.6:cloud)
--debug/--no-debug    # Enable debug output (default: no)
```

**Example:**
```bash
./scraper_agent.py --debug --model gpt-oss:120b-cloud scrape https://example.com
```

## Real-World Examples

### Extract Taxonomy Categories

**Target:** https://www.portfolio123.com/app/taxonomy

```bash
# Scrape and save as JSON
./scraper_agent.py scrape https://portfolio123.com/app/taxonomy \
  -o taxonomy_data.json \
  --prompt "Extract all taxonomy categories with their names, codes, and descriptions as structured JSON"

# Analyze the data
./scraper_agent.py analyze taxonomy_data.json -o taxonomy_analysis.md
```

### Monitor Stock Prices

```bash
./scraper_agent.py monitor https://finance.yahoo.com/quote/AAPL \
  --condition "price < 150" \
  --alert-file apple_alerts.txt \
  --interval 300
```

### Extract Product Catalog

```bash
./scraper_agent.py scrape https://example.com/products \
  --prompt "Extract all products with: name, price, SKU, availability, image URL" \
  -o products.json
```

### Multi-Page Scraping (Interactive)

```bash
./scraper_agent.py chat

> Go to example.com/products page 1
> Extract all product names and URLs
> Click the "Next Page" button
> Extract products from page 2
> Continue until no more pages
```

## How It Works

### Architecture

```
CLI (Click)
  ↓
Agno Agent
  ↓
Chrome DevTools MCP (26 tools)
  ↓
Chrome Browser (your profile)
```

### Agent Workflow

1. **Navigate** - Use `navigate_page` to go to URL
2. **Inspect** - Use `take_snapshot` to understand page structure
3. **Interact** - Use `click`, `fill`, `fill_form` for automation
4. **Extract** - Use `evaluate_script` with JavaScript to get data
5. **Return** - Agent returns structured JSON data

### Available Chrome DevTools MCP Tools

**Navigation (6 tools):**
- `navigate_page`, `new_page`, `close_page`, `select_page`, `list_pages`, `wait_for`

**Interaction (8 tools):**
- `click`, `fill`, `fill_form`, `drag`, `hover`, `press_key`, `handle_dialog`, `upload_file`

**Extraction (3 tools):**
- `take_snapshot`, `evaluate_script`, `take_screenshot`

**Network (2 tools):**
- `list_network_requests`, `get_network_request`

**Console (2 tools):**
- `list_console_messages`, `get_console_message`

**Emulation (2 tools):**
- `emulate`, `resize_page`

**Performance (3 tools):**
- `performance_start_trace`, `performance_stop_trace`, `performance_analyze_insight`

## Advanced Usage

### Custom JavaScript Extraction

The agent can execute JavaScript to extract complex data:

```javascript
// Example: Extract table data
() => {
  const rows = Array.from(document.querySelectorAll('table tr'));
  return rows.map(row => {
    const cells = Array.from(row.querySelectorAll('td'));
    return cells.map(cell => cell.innerText);
  });
}
```

The agent automatically uses patterns like this when you ask for specific extractions.

### Authentication & Sessions

Since the agent uses your Chrome profile, you can:
- Stay logged into websites (cookies preserved)
- Access authenticated pages
- Bypass login forms (already authenticated)

### Error Handling

The agent includes automatic retry with exponential backoff:
- 3 retries on failures
- Delays: 15s, 30s, 60s
- Handles transient network/browser errors

### Large Pages

Configured with 198K context window to handle:
- Complex single-page applications
- Large data tables
- Multi-page content

## Configuration

### MCP Server (Optional)

If you want to configure the MCP server in `.mcp.json`:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--browser-url=http://127.0.0.1:9222"
      ],
      "description": "Chrome DevTools for web scraping"
    }
  }
}
```

### Custom Chrome Profile

To use a different Chrome profile:

```bash
# Use a different profile (e.g., "Profile 1", "Work", etc.)
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome" \
  --profile-directory="Profile 1"

# Or use a completely separate user data directory
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/path/to/custom/profile"

# Run agent (connects to port 9222 by default)
./scraper_agent.py scrape https://example.com
```

## Troubleshooting

### Chrome Not Responding

**Problem:** `Connection refused` or timeout errors

**Solution:**
1. Verify Chrome is running with remote debugging
2. Check http://127.0.0.1:9222/json shows tabs
3. Ensure port 9222 is not blocked by firewall

### Profile Lock Error

**Problem:** Chrome says profile is in use

**Solution:** Close all other Chrome instances or use a different user-data-dir

### Permission Denied

**Problem:** Can't access Chrome profile directory

**Solution:**
```bash
chmod +x scraper_agent.py
# Or run with: uv run scraper_agent.py
```

### Network Errors

**Problem:** Intermittent failures during scraping

**Solution:** Agent automatically retries with exponential backoff (3 attempts). Increase retries if needed by editing the agent code.

### Large Pages Timeout

**Problem:** Pages with lots of JavaScript take too long

**Solution:** Use `wait_for` to wait for specific elements instead of full page load

## Development

### Technologies

- **Agno** - Agent framework with MCP integration
- **Chrome DevTools MCP** - Browser automation protocol
- **Click** - CLI interface framework
- **Ollama** - LLM backend (glm-4.6:cloud with 198K context)
- **uv** - Fast Python package management

### Dependencies

Automatically managed by `uv` via inline script metadata:
- `agno` (editable local install)
- `ollama`
- `click`

### Project Structure

```
tools/scraper/
├── scraper_agent.py    # Main agent (single-file with uv)
└── README.md           # This file
```

## License

MIT

## Resources

- **Chrome DevTools MCP:** https://github.com/modelcontextprotocol/servers
- **Agno Documentation:** https://docs.agno.com
- **Model Context Protocol:** https://modelcontextprotocol.io

---

**Last Updated:** 2025-11-11
