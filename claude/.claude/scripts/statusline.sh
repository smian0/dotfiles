#!/bin/bash
# Claude Code Status Line Generator
# Displays: user@host:path (branch) [model] [claude version] [output style] [base_url]

# Read JSON input from stdin
input=$(cat)

# Detect current project for project-specific temp files
project_id=$(basename "$(pwd)" | tr '/' '-' | tr ' ' '_')

# Extract values from JSON
current_dir=$(echo "$input" | jq -r '.workspace.current_dir')
model_name=$(echo "$input" | jq -r '.model.display_name')
claude_version=$(claude --version 2>/dev/null | cut -d' ' -f1 || echo 'N/A')
output_style=$(echo "$input" | jq -r '.output_style.name // "default"' | sed 's/default/std/')
transcript_path=$(echo "$input" | jq -r '.transcript_path // ""')

# Format directory path (replace home with ~)
short_dir=$(echo "$current_dir" | sed "s|^$HOME|~|")

# Colors
DIM='\033[2m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'  
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
DARK_GRAY='\033[90m'
DARK_CYAN='\033[36m'
RESET='\033[0m'

# Build status components
user_host="${DIM}${GREEN}$(whoami)@$(hostname -s)${RESET}"
dir_part="${DIM}:${BLUE}${short_dir}${RESET}"

# Git status (if in git repo)
if git -C "$current_dir" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$current_dir" branch --show-current 2>/dev/null || git -C "$current_dir" rev-parse --short HEAD 2>/dev/null)
    
    if git -C "$current_dir" diff --quiet && git -C "$current_dir" diff --cached --quiet; then
        git_status="($branch)"
    else
        git_status="($branch ✗)"
    fi
    git_part=" ${YELLOW}${git_status}${RESET}"
else
    git_part=""
fi

# Model and version info
model_part=" ${DIM}[${model_name}]${RESET}"
claude_part=" ${DIM}[claude ${claude_version}]${RESET}"
style_part=" ${DIM}[${output_style}]${RESET}"

# Base URL (if set)
if [ -n "$ANTHROPIC_BASE_URL" ]; then
    url_part=" ${DIM}[${ANTHROPIC_BASE_URL}]${RESET}"
else
    url_part=""
fi

# Summary from PostToolUse hook (if available and recent)
summary_part=""
if [ -f "/tmp/claude-${project_id}-last-summary.txt" ]; then
    # Read timestamp and summary
    summary_content=$(cat "/tmp/claude-${project_id}-last-summary.txt" 2>/dev/null)
    if [ -n "$summary_content" ]; then
        summary_timestamp=$(echo "$summary_content" | cut -d: -f1)
        summary_text=$(echo "$summary_content" | cut -d: -f2-)
        
        # Check if summary is recent (within 5 minutes = 300 seconds)
        current_time=$(date +%s)
        age=$((current_time - summary_timestamp))
        
        if [ "$age" -le 300 ] && [ -n "$summary_text" ]; then
            # Truncate summary to 120 characters max (since it's on its own line)
            if [ ${#summary_text} -gt 120 ]; then
                summary_text=$(echo "$summary_text" | cut -c1-117)...
            fi
            summary_part="\n${DARK_CYAN}[📝 ${summary_text}]${RESET}"
        fi
    fi
fi

# Current prompt from UserPromptSubmit hook (real-time capture)
prompt_part=""
session_id=$(echo "$input" | jq -r '.session_id // ""')

# Try project-specific quick access file first (fastest)
if [ -f "/tmp/claude-${project_id}-current-prompt.txt" ]; then
    current_prompt=$(cat "/tmp/claude-${project_id}-current-prompt.txt" 2>/dev/null)
elif [ -n "$session_id" ]; then
    # Fallback to session data file
    session_file="$HOME/.claude/data/sessions/${session_id}.json"
    if [ -f "$session_file" ]; then
        current_prompt=$(jq -r '.prompts[-1].text // .prompts[-1] // ""' "$session_file" 2>/dev/null)
    fi
fi

if [ -n "$current_prompt" ] && [ "$current_prompt" != "null" ] && [ "$current_prompt" != "" ]; then
    # Clean up prompt - remove newlines and excessive whitespace
    clean_prompt=$(echo "$current_prompt" | tr '\n' ' ' | sed 's/  \+/ /g' | sed 's/^ *//' | sed 's/ *$//')
    
    # Truncate to 120 characters max
    if [ ${#clean_prompt} -gt 120 ]; then
        clean_prompt=$(echo "$clean_prompt" | cut -c1-117)...
    fi
    
    # Get icon based on prompt type (real-time detection)
    icon="💬"
    if echo "$clean_prompt" | grep -q "^/"; then
        icon="⚡"
    elif echo "$clean_prompt" | grep -q "?"; then
        icon="❓"
    elif echo "$clean_prompt" | grep -iq "create\|write\|add\|implement\|build"; then
        icon="💡"
    elif echo "$clean_prompt" | grep -iq "fix\|debug\|error\|issue"; then
        icon="🐛"
    elif echo "$clean_prompt" | grep -iq "refactor\|improve\|optimize"; then
        icon="♻️"
    fi
    
    prompt_part="\n${DARK_GRAY}${icon} ${clean_prompt}${RESET}"
fi

# Output complete status line (prompt on line 2, summary on line 3)
printf "${user_host}${dir_part}${git_part}${model_part}${claude_part}${style_part}${url_part}${prompt_part}${summary_part}"