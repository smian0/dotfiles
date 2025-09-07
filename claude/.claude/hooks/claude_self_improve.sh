#!/bin/bash
set -euo pipefail
trap 'echo "claude_self_improve.sh error at line $LINENO, exit code $? from $BASH_COMMAND" >&2; exit 1' ERR

# Claude Self-Improvement Hook
#
# This hook analyzes conversation patterns and suggests improvements to add
# to the user's CLAUDE.md file for better future interactions.
#
# Installation:
# 1. Save this script and chmod +x it to make it executable.
# 2. Within Claude Code, /hooks / UserPromptSubmit > Add a new hook (this file)
#
# How it works:
# Analyzes the last 15 exchanges for patterns like:
# - Repeated corrections (user fixes same issues 3+ times)
# - Workflow inefficiencies (always using same tool combinations)
# - Missing context (user explains same concepts repeatedly)
# - Style preferences (consistent formatting corrections)

stdin=$(cat)
transcript_path=$(echo "$stdin" | jq -r ".transcript_path")

# Configuration
ANALYSIS_DEPTH=15
PATTERN_THRESHOLD=3
CLAUDE_MD_PATH="$HOME/.claude/CLAUDE.md"

# Initialize pattern tracking (using simple counters for compatibility)
correction_naming=0
correction_formatting=0
correction_scope=0
correction_tools=0
workflow_read_edit=0
workflow_multi_edit=0
workflow_git=0
workflow_search_read=0
context_architecture=0
context_tech_stack=0
context_dev_workflow=0
context_standards=0

# Get the last N exchanges for analysis
get_recent_exchanges() {
    local depth="${1:-$ANALYSIS_DEPTH}"
    grep '"role"' "$transcript_path" | tail -n "$((depth * 2))"
}

# Extract text content from a JSON message
extract_message_text() {
    local json_line="$1"
    echo "$json_line" | jq -r '
        if .message.content then
            if (.message.content | type) == "array" then
                .message.content[] | select(.type == "text") | .text // empty
            else
                .message.content.text // .message.content // empty
            end
        else
            empty
        end
    ' 2>/dev/null || echo ""
}

# Detect repeated corrections pattern
detect_correction_patterns() {
    while IFS= read -r line; do
        local role=$(echo "$line" | jq -r '.role // empty' 2>/dev/null)
        local text=$(extract_message_text "$line")
        
        if [[ "$role" == "user" && -n "$text" ]]; then
            # Check for common correction phrases
            if [[ "$text" =~ (fix|change|correct|actually|instead|don\'t|should be|use.*not) ]]; then
                # Categorize the correction
                if [[ "$text" =~ (snake_case|camelCase|kebab-case) ]]; then
                    ((correction_naming++))
                elif [[ "$text" =~ (indent|format|style|spacing) ]]; then
                    ((correction_formatting++))
                elif [[ "$text" =~ (don\'t.*create|avoid.*file|just.*edit) ]]; then
                    ((correction_scope++))
                elif [[ "$text" =~ (use.*instead|prefer.*over|always.*use) ]]; then
                    ((correction_tools++))
                fi
            fi
        fi
    done < <(get_recent_exchanges)
}

# Detect workflow patterns
detect_workflow_patterns() {
    while IFS= read -r line; do
        local role=$(echo "$line" | jq -r '.role // empty' 2>/dev/null)
        local text=$(extract_message_text "$line")
        
        if [[ "$role" == "assistant" && -n "$text" ]]; then
            # Extract tool usage patterns
            if [[ "$text" =~ Read.*Edit ]]; then
                ((workflow_read_edit++))
            elif [[ "$text" =~ MultiEdit ]]; then
                ((workflow_multi_edit++))
            elif [[ "$text" =~ (Bash.*git|git.*commit) ]]; then
                ((workflow_git++))
            elif [[ "$text" =~ (Grep.*Read|search.*read) ]]; then
                ((workflow_search_read++))
            fi
        fi
    done < <(get_recent_exchanges)
}

# Detect missing context patterns  
detect_context_patterns() {
    while IFS= read -r line; do
        local role=$(echo "$line" | jq -r '.role // empty' 2>/dev/null)
        local text=$(extract_message_text "$line")
        
        if [[ "$role" == "user" && -n "$text" ]]; then
            # Look for explanatory patterns
            if [[ "$text" =~ (this.*project|our.*codebase|we.*use|this.*is.*about) ]]; then
                if [[ "$text" =~ (architecture|system|design) ]]; then
                    ((context_architecture++))
                elif [[ "$text" =~ (framework|library|tool) ]]; then
                    ((context_tech_stack++))
                elif [[ "$text" =~ (workflow|process|way.*work) ]]; then
                    ((context_dev_workflow++))
                elif [[ "$text" =~ (convention|standard|rule) ]]; then
                    ((context_standards++))
                fi
            fi
        fi
    done < <(get_recent_exchanges)
}

# Generate suggestions based on detected patterns
generate_suggestions() {
    # Check correction patterns and generate suggestions
    if [[ "$correction_naming" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Code Style|Always follow consistent naming conventions (detected $correction_naming corrections)||echo '- **Naming Consistency**: Use consistent naming conventions throughout the project' >> ~/.claude/CLAUDE.md"
    fi
    
    if [[ "$correction_formatting" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Code Style|Automatic code formatting preferences (detected $correction_formatting corrections)||echo '- **Auto-Format**: Apply consistent code formatting and indentation' >> ~/.claude/CLAUDE.md"
    fi
    
    if [[ "$correction_scope" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Scope Control|Enhanced scope discipline (detected $correction_scope scope corrections)||echo '- **Scope Discipline**: Build only what is explicitly requested, avoid scope creep' >> ~/.claude/CLAUDE.md"
    fi
    
    if [[ "$correction_tools" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Tool Preferences|Tool selection optimization (detected $correction_tools tool corrections)||echo '- **Tool Selection**: Use preferred tools based on established patterns' >> ~/.claude/CLAUDE.md"
    fi
    
    # Check workflow patterns
    if [[ "$workflow_read_edit" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Workflow Rules|Always read before editing (detected $workflow_read_edit instances)||echo '- **Read First**: Always read existing files before making edits to understand context' >> ~/.claude/CLAUDE.md"
    fi
    
    if [[ "$workflow_multi_edit" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Performance|Prefer batch operations (detected $workflow_multi_edit instances)||echo '- **Batch Operations**: Use MultiEdit for multiple file changes instead of individual edits' >> ~/.claude/CLAUDE.md"
    fi
    
    if [[ "$workflow_search_read" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Workflow Rules|Search-first approach (detected $workflow_search_read instances)||echo '- **Search Strategy**: Use search tools to locate relevant code before detailed reading' >> ~/.claude/CLAUDE.md"
    fi
    
    # Check context patterns
    if [[ "$context_architecture" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Project Context|Document architecture patterns (detected $context_architecture explanations)||echo '- **Architecture**: [Document your specific architecture patterns here]' >> ~/.claude/CLAUDE.md"
    fi
    
    if [[ "$context_tech_stack" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Project Context|Document technology stack (detected $context_tech_stack explanations)||echo '- **Tech Stack**: [Document your preferred technologies and frameworks]' >> ~/.claude/CLAUDE.md"
    fi
    
    if [[ "$context_dev_workflow" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Workflow Rules|Document development process (detected $context_dev_workflow explanations)||echo '- **Dev Workflow**: [Document your specific development workflow patterns]' >> ~/.claude/CLAUDE.md"
    fi
    
    if [[ "$context_standards" -ge "$PATTERN_THRESHOLD" ]]; then
        echo "## Project Context|Document coding standards (detected $context_standards explanations)||echo '- **Standards**: [Document your specific coding standards and conventions]' >> ~/.claude/CLAUDE.md"
    fi
}

# Main execution
main() {
    # Run pattern detection
    detect_correction_patterns
    detect_workflow_patterns  
    detect_context_patterns
    
    # Generate suggestions
    local suggestion_output
    suggestion_output=$(generate_suggestions)
    
    # Only output if we have suggestions
    if [[ -z "$suggestion_output" ]]; then
        exit 0
    fi
    
    # Store suggestions in array (compatible with older bash)
    local suggestions=()
    local count=0
    while IFS= read -r line && [[ "$count" -lt 3 ]]; do
        suggestions+=("$line")
        ((count++))
    done <<< "$suggestion_output"
    
    # Format output as system reminder
    cat <<'HEADER'
<system-reminder>
🔄 **Claude Self-Improvement Suggestions**

Based on recent conversation patterns, consider adding these to your CLAUDE.md:

HEADER

    for suggestion in "${suggestions[@]}"; do
        IFS='|' read -r category description details command <<< "$suggestion"
        cat <<EOF
**$category**: $description
$details
\`\`\`bash
$command
\`\`\`

EOF
    done
    
    echo "</system-reminder>"
}

# Execute main function
main

exit 0