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
            if [[ "$user_text" =~ (show[[:space:]]full[[:space:]]vtree|detailed[[:space:]]vtree|vtree.*full|vtree.*detailed|comprehensive[[:space:]]vtree|expand[[:space:]]vtree|vtree.*complete|vtree.*all[[:space:]]details) ]]; then
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

# Simplified vtree template generation - minimal emojis, clean structure
generate_simplified_template() {
    local content_type="$1"
    local template=""
    
    case "$content_type" in
        "workflow"|"process")
            template="[1]  Process_Flow [📥 request] → (2)
[2]  ├─ Validation → (3)
     ├─ Processing → (3)
     └─ Output_Generation → (3)
[3]  Final_Result [📤 response]"
            ;;
        "architecture"|"system")
            template="[1]  System_Architecture [📥 input] → (2.1,2.2,2.3)
[2]  ├─ Frontend_Layer → (3)
     ├─ API_Layer → (3)
     └─ Backend_Layer → (3)
[3]  Response_Handler [📤 output]"
            ;;
        "components"|"agents")
            template="[1]  Orchestrator [📥 request] → (2.1,2.2,2.3)
[2]  ├─ Agent_Research → (3)
     ├─ Agent_Analysis → (3)
     └─ Agent_Execution → (3)
[3]  Result_Combiner [📤 final]"
            ;;
        "files"|"directory")
            template="[1]  Project_Structure [📥 files] → (2.1,2.2)
[2]  ├─ Source_Code → (3)
     └─ Tests → (3)
[3]  Build_Output [📤 artifacts]"
            ;;
        "decision")
            template="[1]  Decision_Point [📥 criteria] → (2,3,4)
[2]  ├─ Option_A → (END)
[3]  ├─ Option_B → (END)
[4]  └─ Default → (END)"
            ;;
        *)
            template="[1]  Main_Component [📥 input] → (2.1,2.2)
[2]  ├─ Sub_Component_A → (3)
     └─ Sub_Component_B → (3)
[3]  Output_Handler [📤 result]"
            ;;
    esac
    
    echo "$template"
}

# Enhanced vtree template generation with emojis, node IDs, and intelligent styling
generate_enhanced_template() {
    local content_type="$1"
    local template=""
    
    # Analyze content for comprehensive patterns
    detect_advanced_patterns "$text_content"
    
    case "$content_type" in
        "workflow"|"process")
            if [[ "$HAS_CONDITIONAL" == "true" && "$HAS_ERROR_HANDLING" == "true" ]]; then
                template="# =========== PROCESSING LAYER ===========
[1]     🔴 **Workflow_Orchestrator** [📥 request] → [🚀 result ← (1.1)+(1.2)]
[1.1]   ├─ Validator [📥 data ← (1)] → [if(valid) → (1.2) else → (1.1.E)]
[1.1.1] │  ├─ Schema_Check [⚡ 2.1ms] → [✅ → (1.1)]
[1.1.2] │  └─ Rate_Limiter [@redis-cluster] → [✅ → (1.1)]
[1.1.E] │  └─ ❌ Error_Handler → [📤 error → (1)]
[1.2]   └─ Async_Processor [⏳ background] → [📤 → (1)]  # ML Pipeline"
            else
                template="[1]     **Process_Orchestrator** [📥 request] → [🚀 result → (END)]
[1.1]   ├─ Step_1 [📥 raw ← (1)] → [🔄 processed → (1.2)]
[1.2]   ├─ Step_2 [📊 data ← (1.1)] → [✅ validated → (1.3)]
[1.3]   └─ Step_3 [💾 validated ← (1.2)] → [📤 final → (1)]"
            fi
            ;;
        "architecture"|"system")
            if [[ "$HAS_INFRASTRUCTURE" == "true" && "$HAS_SECURITY" == "true" ]]; then
                template="# =========== FRONTEND LAYER ===========
[1]     🌐 **Load_Balancer** [@nginx-ingress] → [🎯 → (1.1,1.2,1.3)]
[1.1]   ├─ Web_Server_1 [⚡ 1.2ms, 99.9% uptime] → [📤 → (2)]
[1.2]   ├─ Web_Server_2 [⚡ 1.4ms, 99.8% uptime] → [📤 → (2)]
[1.3]   └─ Web_Server_3 [🐌 5.2ms, 95% uptime] → [📤 → (2)]

# =========== API LAYER ===========
[2]     🔒 **API_Gateway** [Auth: oauth2] → [if(authenticated) → (3) else → (2.E)]
[2.E]   └─ ❌ Auth_Failure → [📤 401_error]

# =========== DATA LAYER ===========
[3]     💾 Database_Cluster [@kubernetes-prod, CPU: 16 cores] → [📤 data]"
            else
                template="[1]     **System_Orchestrator** [📥 user_request] → [📤 response → (END)]
[1.1]   ├─ Frontend_Layer [📥 UI_events ← (1)] → [🎯 API_calls → (1.2)]
[1.2]   ├─ API_Layer [📥 requests ← (1.1)] → [🔄 data → (1.3)]
[1.3]   └─ Backend_Layer [📥 queries ← (1.2)] → [💾 results → (1.2)]"
            fi
            ;;
        "components"|"agents")
            if [[ "$HAS_PARALLEL" == "true" ]]; then
                template="# =========== ORCHESTRATION LAYER ===========
[1]     🔴 **Master_Controller** [📥 request] → [🎯 → (2.1||2.2||2.3)]
[2.1]   ├─ ⚡ Research_Agent [@aws-lambda, 4GB] → [📊 analysis → (3)]
[2.2]   ├─ ⚡ Code_Agent [🔒 Auth: service] → [💻 code → (3)]
[2.3]   └─ ⚡ QA_Agent [⏸️ Rate: 100/min] → [✅ validated → (3)]

# =========== AGGREGATION LAYER ===========
[3]     🟡 **Result_Combiner** [📥 ← (2.1)+(2.2)+(2.3)] → [🚀 final]
[3.E]   Emergency_Fallback ← (2.1,2.2,2.3) → [🔧 recovery]  # Auto-retry logic"
            else
                template="[1]     **Agent_Orchestrator** [📥 request] → [🎯 distribute → (2.1,2.2,2.3)]
[2.1]   ├─ Agent_A [📥 task ← (1)] → [⚡ result_a → (3)]
[2.2]   ├─ Agent_B [📥 data ← (1)] → [🔄 result_b → (3)]
[2.3]   └─ Agent_C [⏳ task ← (1)] → [📤 result_c → (3)]
[3]     **Result_Coordinator** [📥 results ← (2.1)+(2.2)+(2.3)] → [📤 final]"
            fi
            ;;
        "files"|"directory")
            template="# =========== PROJECT STRUCTURE ===========
[1]     **Project_Organizer** [📥 files] → [📤 organized → (END)]
[1.1]   ├─ src/ [📥 source ← (1)] → [💻 compiled → (1.3)]
[1.1.1] │  ├─ components/ [📥 ← (1.1)] → [🔄 → (1.1)]  # React Components
[1.1.2] │  └─ utils/ [📥 ← (1.1)] → [🔄 → (1.1)]  # Helper Functions
[1.2]   └─ tests/ [📥 specs ← (1)] → [✅ validated → (1.3)]
[1.3]   Build_Output [📥 ← (1.1)+(1.2)] → [📤 ← (1)]"
            ;;
        "decision")
            template="[1]     **Decision_Controller** [📥 criteria] → [🎯 choice → (2,3,4)]
[2]     Condition_A [📥 check ← (1)] → [if(passes) → (END) else → (3)]
[3]     Condition_B [📥 check ← (1)] → [if(passes) → (END) else → (4)]
[4]     🟡 Default_Handler [📥 fallback ← (1)] → [📤 default_action → (END)]
[4.E]   ❌ Error_State ← (2,3,4) → [🔧 emergency_stop]  # Circuit breaker"
            ;;
        *)
            template="[1]     🟢 **System_Orchestrator** [📥 params] → [📤 results → (END)]
[1.1]   ├─ Component_1 [📥 data ← (1)] → [🔄 processed → (1.2)]
[1.2]   ├─ Component_2 [📥 processed ← (1.1)] → [⚡ enhanced → (1.3)]
[1.3]   └─ Component_3 [📥 enhanced ← (1.2)] → [📤 final → (1)]"
            ;;
    esac
    
    echo "$template"
}

# Generate the appropriate template based on request type
if [[ "$FULL_VTREE_REQUESTED" == "true" ]]; then
    vtree_template=$(generate_enhanced_template "$content_type")
    VTREE_MODE="full"
else
    vtree_template=$(generate_simplified_template "$content_type")
    VTREE_MODE="simplified"
fi

# Generate system reminder based on mode
if [[ "$VTREE_MODE" == "simplified" ]]; then
    cat <<EOF
<system-reminder>
The response you just provided describes a hierarchical structure, workflow, or system that would benefit from ASCII tree visualization.

Please append a vtree diagram at the end of your response using this format:

\`\`\`
$vtree_template
\`\`\`

Use these formatting rules:

**Core Structure:**
- Node IDs: [1], [2], [2.1] for reference tracking
- Connections: Use ├─ └─ for tree structure  
- Data Flow: → (node_id) for outputs, ← (node_id) for inputs
- Multiple outputs: → (A,B,C) for distribution to multiple nodes

**Visual Indicators:**
- Minimal emojis: 📥 input, 📤 output only
- Clear component names describing function
- Simple connections showing data flow

**Spacing:**
- 3-5 spaces per indentation level
- Keep lines concise and readable

For detailed vtree with performance metrics, security annotations, error handlers, and infrastructure details, say "show full vtree" in your next message.

Add a brief note: "Simplified vtree for quick understanding" after the diagram.
</system-reminder>
EOF
else
    cat <<EOF
<system-reminder>
The response you just provided describes a hierarchical structure, workflow, or system that would benefit from comprehensive ASCII tree visualization.

Please append a comprehensive vtree diagram at the end of your response using this exact format:

\`\`\`
$vtree_template
\`\`\`

Use these comprehensive formatting rules:

**Core Structure:**
- Node IDs: [1], [1.1], [1.2.1] for explicit reference tracking
- Connections: Use ├─ │ └─ for tree structure
- Data Flow: → (node_id) for outputs, ← (node_id) for inputs
- Multiple I/O: ← (A)+(B) for combined inputs, → (A,B) for split outputs

**Advanced Notation:**
- Conditional Logic: if(condition) → (success) else → (error)
- Parallel Processing: → (1.1||1.2||1.3) for concurrent execution
- Error Handlers: [1.1.E] suffix for error handling nodes

**Visual Indicators:**
- Priority: 🔴 Critical/P0, 🟡 Important/P1, 🟢 Normal/P2
- Status: ⚡ Active/Fast, ⏸️ Paused/Waiting, 🐌 Slow/Bottleneck
- Operations: 📥 input, 📤 output, 🔄 process, 📊 analyze, 💾 store, 🌐 external
- Security: 🔒 Secure, 🛡️ Protected, [Auth: level]

**Organization:**
- System Grouping: # =========== LAYER NAME ===========
- Infrastructure: [@deployment-target, resources]
- Comments: # Inline explanatory comments
- Performance: [2.3ms, 99.9% uptime] metrics

**Text Styling:**
- *italics* for optional/async/external elements
- **bold** for critical paths and main processes
- Normal text for standard required operations

**Spacing:**
- 3-7 spaces per indentation level for readability
- Keep under 120 characters per line when possible

Add a brief note: "Comprehensive vtree optimized for terminal display with advanced semantic indicators" after the diagram.
</system-reminder>
EOF
fi

exit 0