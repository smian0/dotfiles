#!/bin/bash
set -euo pipefail
trap 'echo "at line $LINENO, exit code $? from $BASH_COMMAND" >&2; exit 1' ERR

# This is a Claude Code hook to automatically suggest vtree visualization when appropriate.
#
# Installation:
# 1. Save this script and chmod +x it to make it executable.
# 2. Within Claude Code, /hooks / UserPromptSubmit > Add a new hook (this file)
#
# How it works:
# This script analyzes the assistant's recent responses to detect hierarchical structures,
# workflows, system architectures, and other content that would benefit from tree visualization.
# When detected, it appends a system reminder with appropriate vtree format templates.

stdin=$(cat)
transcript_path=$(echo "$stdin" | jq -r ".transcript_path")

# Get the last assistant response (excluding thinking blocks)
last_response=$(grep '"role":"assistant"' "$transcript_path" | tail -n 1)
[[ -z "$last_response" ]] && exit 0

# Extract text content
text_content=""
if [[ "$(jq -r '.message.content[0].type // empty' <<< "$last_response")" == "text" ]]; then
    text_content=$(jq -r '.message.content[0].text' <<< "$last_response")
fi

[[ -z "$text_content" ]] && exit 0

# Initialize full vtree flag
FULL_VTREE_REQUESTED=false

# Check for full vtree keywords in user messages (last few messages to catch requests)
last_user_messages=$(grep '"role":"user"' "$transcript_path" | tail -n 2)
if [[ -n "$last_user_messages" ]]; then
    while IFS= read -r user_msg; do
        if [[ "$(jq -r '.message.content[0].type // empty' <<< "$user_msg")" == "text" ]]; then
            user_text=$(jq -r '.message.content[0].text' <<< "$user_msg")
            if [[ "$user_text" =~ (\*vtree|show[[:space:]]full[[:space:]]vtree|detailed[[:space:]]vtree|vtree.*full|vtree.*detailed|comprehensive[[:space:]]vtree|expand[[:space:]]vtree|vtree.*complete|vtree.*all[[:space:]]details) ]]; then
                FULL_VTREE_REQUESTED=true
                break
            fi
        fi
    done <<< "$last_user_messages"
fi

# Comprehensive pattern detection for advanced vtree features
detect_advanced_patterns() {
    local text="$1"
    
    # Styling patterns
    local has_async=false
    local has_external=false
    local has_critical=false
    local has_optional=false
    
    # Advanced patterns
    local has_conditional=false
    local has_parallel=false
    local has_error_handling=false
    local has_performance=false
    local has_infrastructure=false
    local has_security=false
    
    # Detect async patterns
    if [[ "$text" =~ (async|await|promise|callback|defer|queue|background) ]]; then
        has_async=true
    fi
    
    # Detect external/third-party patterns
    if [[ "$text" =~ (api|external|third.party|service|client|remote|network|http) ]]; then
        has_external=true
    fi
    
    # Detect critical/main path patterns
    if [[ "$text" =~ (main|primary|critical|core|essential|key|important|required) ]]; then
        has_critical=true
    fi
    
    # Detect optional patterns
    if [[ "$text" =~ (optional|maybe|fallback|backup|alternative|cache) ]]; then
        has_optional=true
    fi
    
    # Detect conditional logic patterns
    if [[ "$text" =~ (if|condition|branch|decision|validate|check|success|fail) ]]; then
        has_conditional=true
    fi
    
    # Detect parallel processing patterns
    if [[ "$text" =~ (parallel|concurrent|simultaneous|fork|spawn|worker|thread) ]]; then
        has_parallel=true
    fi
    
    # Detect error handling patterns
    if [[ "$text" =~ (error|exception|fail|retry|fallback|handler|catch) ]]; then
        has_error_handling=true
    fi
    
    # Detect performance-related content
    if [[ "$text" =~ (performance|speed|latency|throughput|optimization|bottleneck) ]]; then
        has_performance=true
    fi
    
    # Detect infrastructure patterns
    if [[ "$text" =~ (deploy|kubernetes|docker|server|cluster|infrastructure) ]]; then
        has_infrastructure=true
    fi
    
    # Detect security patterns
    if [[ "$text" =~ (auth|security|permission|access|secure|encrypt|private) ]]; then
        has_security=true
    fi
    
    # Export all patterns for template generation
    export STYLE_ASYNC="$has_async"
    export STYLE_EXTERNAL="$has_external" 
    export STYLE_CRITICAL="$has_critical"
    export STYLE_OPTIONAL="$has_optional"
    export HAS_CONDITIONAL="$has_conditional"
    export HAS_PARALLEL="$has_parallel"
    export HAS_ERROR_HANDLING="$has_error_handling"
    export HAS_PERFORMANCE="$has_performance"
    export HAS_INFRASTRUCTURE="$has_infrastructure"
    export HAS_SECURITY="$has_security"
}

# Initialize scoring for vtree worthiness
score=0
content_type=""

# Check if vtree was already mentioned or provided
if [[ "$text_content" =~ [Vv]tree|tree.diagram|ASCII.tree ]]; then
    exit 0
fi


# Run comprehensive pattern detection early to influence scoring
detect_advanced_patterns "$text_content"

# Positive indicators scoring
# Workflow/process keywords (+2)
if [[ "$text_content" =~ (workflow|process|pipeline|procedure|sequence|steps|phases|stages) ]]; then
    score=$((score + 2))
    content_type="workflow"
fi

# Architecture/system keywords (+2)
if [[ "$text_content" =~ (architecture|system|framework|component|module|structure|hierarchy) ]]; then
    score=$((score + 2))
    content_type="architecture"
fi

# Multi-agent/component systems (+2)
if [[ "$text_content" =~ (agent|component|service|microservice|pipeline|network|chain) ]]; then
    score=$((score + 2))
    content_type="components"
fi

# Data flow indicators (+2)
if [[ "$text_content" =~ (→|->|input|output|transform|flow|data.flow|pipeline) ]]; then
    score=$((score + 2))
fi

# Numbered lists detection (+2)
numbered_lists=$(echo "$text_content" | grep -c '^[[:space:]]*[0-9]\+\.' || true)
if [[ $numbered_lists -ge 3 ]]; then
    score=$((score + 2))
fi

# Multi-level structure detection (+3)
# Look for nested patterns, indentation, or bullet points
if [[ "$text_content" =~ \-[[:space:]]*.*\n[[:space:]]*\-|[[:space:]]{4,}|├─|└─|│ ]]; then
    score=$((score + 3))
fi

# File operation detection (+3)
# Multiple file creates/edits suggest directory structure
file_ops=$(echo "$text_content" | grep -c -i 'create\|edit\|file\|directory\|folder' || true)
if [[ $file_ops -ge 3 ]]; then
    score=$((score + 3))
    content_type="files"
fi

# Decision trees (+2)
if [[ "$text_content" =~ (decision|choice|branch|condition|if.*then|case) ]]; then
    score=$((score + 2))
    content_type="decision"
fi

# Additional scoring based on comprehensive patterns
if [[ "$HAS_INFRASTRUCTURE" == "true" ]]; then
    score=$((score + 2))
fi

if [[ "$HAS_SECURITY" == "true" ]]; then
    score=$((score + 2))
fi

if [[ "$HAS_PERFORMANCE" == "true" ]]; then
    score=$((score + 1))
fi

if [[ "$HAS_PARALLEL" == "true" ]]; then
    score=$((score + 2))
fi

if [[ "$HAS_CONDITIONAL" == "true" ]]; then
    score=$((score + 1))
fi

if [[ "$HAS_ERROR_HANDLING" == "true" ]]; then
    score=$((score + 1))
fi

# Negative indicators
# Brief responses (-5)
char_count=${#text_content}
if [[ $char_count -lt 100 ]]; then
    score=$((score - 5))
fi

# Simple factual content (-3)
if [[ "$text_content" =~ ^(The|A|An)[[:space:]].*\.$|^[0-9]+$|^(Yes|No)\.?$|weather|temperature ]]; then
    score=$((score - 3))
fi

# Exit if score doesn't meet threshold
[[ $score -lt 5 ]] && exit 0

# Generate conditional logic notation
generate_conditional_notation() {
    local condition="$1"
    local success_node="$2"
    local failure_node="$3"
    echo "if($condition) → ($success_node) else → ($failure_node)"
}

# Generate parallel processing notation
generate_parallel_notation() {
    local nodes="$1"
    echo "→ ($nodes)"
}

# Generate error handler node ID with .E suffix
generate_error_node_id() {
    local base_id="$1"
    echo "[$base_id.E]"
}

# Generate system grouping header
generate_system_header() {
    local section_name="$1"
    echo "# =========== ${section_name^^} ==========="
}

# Add inline comment
add_inline_comment() {
    local base_line="$1"
    local comment="$2"
    echo "$base_line  # $comment"
}

# Add performance metrics
add_performance_metrics() {
    local node_name="$1"
    local metrics="$2"
    echo "$node_name [$metrics]"
}

# Add infrastructure info
add_infrastructure_info() {
    local node_name="$1"
    local deployment="$2"
    echo "$node_name [@$deployment]"
}

# Add security markers
add_security_markers() {
    local node_name="$1"
    local auth_level="$2"
    echo "$node_name [Auth: $auth_level]"
}

# Get priority emoji based on content
get_priority_emoji() {
    local text="$1"
    if [[ "$text" =~ (critical|urgent|p0|high.priority) ]]; then
        echo "🔴"
    elif [[ "$text" =~ (important|p1|medium.priority) ]]; then
        echo "🟡"
    else
        echo "🟢"
    fi
}

# Get status emoji based on content
get_status_emoji() {
    local text="$1"
    if [[ "$text" =~ (running|active|executing) ]]; then
        echo "⚡"
    elif [[ "$text" =~ (waiting|pending|queued) ]]; then
        echo "⏸️"
    elif [[ "$text" =~ (slow|bottleneck|performance) ]]; then
        echo "🐌"
    else
        echo "🔄"
    fi
}

# Apply selective styling to node names - no asterisks, meaningful hierarchy
apply_comprehensive_styling() {
    local node_name="$1"
    local styled_name="$node_name"
    
    # Apply priority indicators (keep these)
    if [[ "$node_name" =~ (critical|urgent) ]] || [[ "$STYLE_CRITICAL" == "true" ]]; then
        styled_name="🔴 $styled_name"
    elif [[ "$node_name" =~ (important|key) ]]; then
        styled_name="🟡 $styled_name"
    fi
    
    # Note: Text styling (bold/italic) will be applied directly in templates
    # without asterisks to avoid visual clutter and maintain semantic meaning
    
    echo "$styled_name"
}


# Generate minimal hint based on content type
case "$content_type" in
    "workflow"|"process")
        hint="📊 Workflow detected. Type '*vtree' for process visualization."
        ;;
    "architecture"|"system")
        hint="🏗️ Architecture described. Use '*vtree' for system diagram."
        ;;
    "components"|"agents")
        hint="🔧 Multi-component system. Consider '*vtree' visualization."
        ;;
    "files"|"directory")
        hint="📁 File structure detected. Type '*vtree' for directory tree."
        ;;
    "decision")
        hint="🎯 Decision tree identified. Use '*vtree' for visualization."
        ;;
    *)
        hint="💡 Type '*vtree' to visualize this hierarchical structure."
        ;;
esac

echo "<system-reminder>$hint</system-reminder>"

exit 0