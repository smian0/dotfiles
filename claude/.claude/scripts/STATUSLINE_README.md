# Claude Code Statusline Configuration

## Current Setup

**Active Statusline:** claudia-statusline + current prompt (2-line display)
- Line 1: claudia-statusline (high-performance Rust-based with SQLite persistence)
- Line 2: Current prompt preview (captured via UserPromptSubmit hook)

## Backups

- Original custom script: `~/.claude/scripts/statusline.sh.backup`
- Original settings: `~/.claude/settings.json.backup`

**Note:** `~/.claude/settings.json` is symlinked to `~/dotfiles/claude/.claude/settings.json`

## claudia-statusline (Recommended)

**Location:** Uses `settings.local.json` (automatically configured during installation)

**Features:**
- ⚡ **High-performance Rust binary** with ~30% faster reads
- 🗄️ **SQLite persistence** for cross-session statistics
- 🔄 **Real-time compaction detection** via Claude Code hooks
- 📊 **Context tracking** with visual progress bar
- 💰 **Cost monitoring**: Session costs + hourly burn rate
- 🎨 **11 built-in themes**: dark, light, monokai, solarized, high-contrast, gruvbox, nord, dracula, one-dark, tokyo-night, catppuccin
- 🔐 **Multi-instance safe**: Handles multiple Claude instances
- 📁 **Git integration**: Branch + file changes (+added, ~modified, ?untracked)

**Current Configuration:**
```json
{
  "statusLine": {
    "type": "command",
    "command": "$HOME/.claude/scripts/statusline-with-prompt.sh",
    "padding": 0
  }
}
```

**Output format:**
```
Line 1: ~/dotfiles • main ~13 ?25 • day: $131.55
Line 2: 💬 Can we add this capture-prompt to 2nd line...
```

**Customization:**
Edit `~/.config/claudia-statusline/config.toml` to customize theme and settings.

**Theme Options:**
- dark (default), light, monokai, solarized-dark, solarized-light
- high-contrast-dark, high-contrast-light
- gruvbox, nord, dracula, one-dark, tokyo-night, catppuccin

**Install/Update:**
```bash
curl -fsSL https://raw.githubusercontent.com/hagan/claudia-statusline/main/scripts/quick-install.sh | bash
```

**Documentation:** https://github.com/hagan/claudia-statusline

## Switch Between Configurations

### Use claudia-statusline only (single line):
```bash
jq '.statusLine.command = "/Users/smian/.local/bin/statusline"' ~/.claude/settings.json > /tmp/settings.json && mv /tmp/settings.json ~/.claude/settings.json
```

### Use claudia-statusline + prompt preview (2 lines, current):
```bash
jq '.statusLine.command = "$HOME/.claude/scripts/statusline-with-prompt.sh"' ~/.claude/settings.json > /tmp/settings.json && mv /tmp/settings.json ~/.claude/settings.json
```

### Restore original custom statusline:
```bash
# Edit settings.json
jq '.statusLine.command = "$HOME/.claude/scripts/statusline.sh"' ~/.claude/settings.json > /tmp/settings.json && mv /tmp/settings.json ~/.claude/settings.json
```

---

## Alternatives Archive

<details>
<summary>Alternative statusline options (archived for reference)</summary>

### claude-powerline (Node-based)

Edit `~/.claude/settings.json`:
```json
"statusLine": {
  "type": "command",
  "command": "npx -y @owloops/claude-powerline@latest --style=powerline"
}
```

**Features:**
- 🧠 **Context window usage** with accurate percentage (e.g., `◔ 136,368 (9%)`)
- 📁 Directory name and git integration (`⎇ main ↑27 ●`)
- ✱ Model name display (`Sonnet`)
- § Session token tracking
- ☉ Daily cost with budget tracking (e.g., `$67.93 !100%`)
- 🎨 Multiple themes available (powerline, minimal, colorful)

**Example output:**
```
dotfiles ⎇ main ↑27 ● ✱ Sonnet § 0 tokens ☉ $67.93 !100% ◔ 136,368 (9%)
```

**Why claude-powerline?**
- Native context percentage calculation matches Claude Code's internal view
- No custom parsing logic needed - works out of the box
- Vim-style aesthetics with rich information density
- Active maintenance and regular updates

**Configuration Options:**
```bash
# Different styles
npx -y @owloops/claude-powerline@latest --style=minimal
npx -y @owloops/claude-powerline@latest --style=colorful

# Disable specific features
npx -y @owloops/claude-powerline@latest --no-git
npx -y @owloops/claude-powerline@latest --no-cost
```

**Documentation:**
- GitHub: https://github.com/Owloops/claude-powerline
- Run: `npx @owloops/claude-powerline --help`

### Dual-Context Display (Custom Script)

Edit `~/.claude/settings.json`:
```json
"statusLine": {
  "type": "command",
  "command": "$HOME/.claude/scripts/statusline-with-both-context.sh"
}
```

**Features:**
- 🧠 **API tokens**: What you're billed for (59%)
- 🧠 **CC (Claude Code) context**: What `/context` shows (106%)
- 💰 Session/daily/block costs
- 🔥 Burn rate
- Color-coded thresholds for both metrics

**Example output:**
```
🧠 API: 59% (117.8k) | CC: 106% (213k) | 💰 $0.23 session / $61.27 today | 🔥 $11.95/hr
```

**Why two numbers?**
- **API (59%)**: Actual tokens sent to Anthropic API (billable)
- **CC (106%)**: Includes system overhead, MCP tools, buffers (internal context management)

**Note:** Custom scripts removed in cleanup. Original backup available at `statusline.sh.backup`.

### ccusage statusline (NPM package)

Edit `~/.claude/settings.json`:
```json
"statusLine": {
  "type": "command",
  "command": "npx --yes ccusage statusline --context-low-threshold 50 --context-medium-threshold 80"
}
```

**Features:**
- 🧠 **Context percentage** (color-coded: green <50%, yellow 50-80%, red >80%)
- 💰 **Session/daily/block costs** with real-time tracking
- 🔥 **Burn rate** showing cost per hour
- 🤖 Model name display
- Automatic caching for performance
- Supports all Claude models with correct context limits

**Thresholds:**
- `--context-low-threshold 50`: Green if usage <50%
- `--context-medium-threshold 80`: Yellow if usage 50-80%, Red if >80%

### ccstatusline (NPM package)

Edit `~/.claude/settings.json`:
```json
"statusLine": {
  "type": "command",
  "command": "npx --yes ccstatusline"
}
```

**Features:**
- Context percentage (out of 200k)
- Usable context (accounts for 80% auto-compact = 160k)
- Color-coded progress bars
- Token usage tracking
- Real-time updates

**Documentation:**
- GitHub: https://github.com/sirmalloc/ccstatusline
- Run: `npx ccstatusline --help`

### Original Custom Statusline

Edit `~/.claude/settings.json`:
```json
"statusLine": {
  "type": "command",
  "command": "$HOME/.claude/scripts/statusline.sh"
}
```

**Features:**
- User@host:path display
- Git branch and status
- Model and version info
- Current prompt preview with icons
- Custom styling

**Note:** Backup available at `~/.claude/scripts/statusline.sh.backup`

</details>

## Requirements

**For prompt preview on line 2:**
- `capture-prompt.py` hook must be enabled in UserPromptSubmit hooks
- Hook writes current prompt to `/tmp/claude-{project}-current-prompt.txt`

**Last Updated:** 2025-11-12 (Added 2-line statusline: claudia-statusline + prompt preview)
