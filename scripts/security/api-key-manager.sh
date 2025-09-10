#!/usr/bin/env bash
# API Key Management Script
# Handles secure storage, retrieval, and management of API keys using pass

set -euo pipefail

# Source OS detection for environment setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/os-detect.sh" ]]; then
    source "$SCRIPT_DIR/os-detect.sh"
else
    # Fallback logging functions
    log() { echo "[INFO] $1"; }
    info() { echo "[INFO] $1"; }
    warn() { echo "[WARN] $1"; }
    error() { echo "[ERROR] $1"; return 1; }
    success() { echo "✓ $1"; }
    command_exists() { command -v "$1" >/dev/null 2>&1; }
fi

# Configuration
PASS_STORE_DIR="${PASSWORD_STORE_DIR:-$HOME/.password-store}"
API_KEY_BASE_PATH="api"

# Parse command line arguments
ACTION=""
SERVICE=""
KEY_VALUE=""
KEY_PATH=""
FORCE=false
DRY_RUN=false
VERBOSE=false

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            store|add)
                ACTION="store"
                shift
                ;;
            get|show)
                ACTION="get"
                shift
                ;;
            list|ls)
                ACTION="list"
                shift
                ;;
            rotate)
                ACTION="rotate"
                shift
                ;;
            delete|remove|rm)
                ACTION="delete"
                shift
                ;;
            validate)
                ACTION="validate"
                shift
                ;;
            --service)
                SERVICE="$2"
                shift 2
                ;;
            --key)
                KEY_VALUE="$2"
                shift 2
                ;;
            --path)
                KEY_PATH="$2"
                shift 2
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                # If no action specified yet, treat as service name
                if [[ -z "$ACTION" ]]; then
                    SERVICE="$1"
                    shift
                else
                    error "Unknown option: $1"
                    show_help
                    exit 1
                fi
                ;;
        esac
    done
}

show_help() {
    cat << EOF
API Key Management Script

Usage: $(basename "$0") ACTION [SERVICE] [OPTIONS]

ACTIONS:
    store/add           Store a new API key for a service
    get/show           Retrieve an API key for a service
    list/ls            List all stored API keys
    rotate             Rotate an existing API key
    delete/remove/rm   Remove an API key
    validate           Validate API key format and accessibility

SERVICE EXAMPLES:
    github             GitHub personal access token
    openai             OpenAI API key
    anthropic          Anthropic API key
    google             Google API key
    perplexity         Perplexity API key
    custom/service     Custom service under api/custom/service

OPTIONS:
    --service SERVICE   Service name (alternative to positional)
    --key KEY          API key value (will prompt if not provided)
    --path PATH        Custom path under api/ directory
    --force            Overwrite existing key without confirmation
    --dry-run          Show what would be done
    --verbose          Show detailed output
    --help             Show this help

EXAMPLES:
    $(basename "$0") store github                    # Store GitHub token (will prompt for key)
    $(basename "$0") store --service openai --key sk-... # Store OpenAI key directly
    $(basename "$0") get github                      # Retrieve GitHub token
    $(basename "$0") list                           # List all API keys
    $(basename "$0") rotate openai                   # Rotate OpenAI key
    $(basename "$0") validate github                 # Validate GitHub token format

DIRECTORY STRUCTURE:
    ~/.password-store/api/
    ├── github                 # GitHub tokens
    ├── openai                 # OpenAI API keys
    ├── anthropic              # Anthropic API keys
    ├── google/                # Google services
    │   ├── api-key           # Google API key
    │   └── oauth-client      # OAuth client secrets
    └── custom/               # Custom services
        └── service-name       # Custom service keys

EOF
}

# Check dependencies
check_dependencies() {
    local missing=()
    
    if ! command_exists pass; then
        missing+=("pass")
    fi
    
    if ! command_exists gpg; then
        missing+=("gpg")
    fi
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing[*]}"
        info "Install with: brew install ${missing[*]}"
        return 1
    fi
    
    # Check if pass is initialized
    if [[ ! -f "$PASS_STORE_DIR/.gpg-id" ]]; then
        error "Pass store not initialized. Run: pass init <gpg-key-id>"
        return 1
    fi
    
    [[ "$VERBOSE" == true ]] && info "All dependencies available"
}

# Validate service name
validate_service_name() {
    local service="$1"
    
    if [[ -z "$service" ]]; then
        error "Service name is required"
        return 1
    fi
    
    # Check for valid characters (alphanumeric, hyphen, underscore, slash)
    if [[ ! "$service" =~ ^[a-zA-Z0-9/_-]+$ ]]; then
        error "Invalid service name: $service"
        info "Service names can only contain letters, numbers, hyphens, underscores, and slashes"
        return 1
    fi
    
    return 0
}

# Validate API key format for known services
validate_api_key_format() {
    local service="$1"
    local key="$2"
    
    case "$service" in
        github)
            # GitHub personal access tokens: ghp_, gho_, ghu_, ghs_, ghr_
            if [[ ! "$key" =~ ^gh[pours]_[A-Za-z0-9]{36}$ ]]; then
                warn "GitHub token format appears incorrect (expected: gh[pours]_36chars)"
                return 1
            fi
            ;;
        openai)
            # OpenAI API keys: sk-...
            if [[ ! "$key" =~ ^sk-[A-Za-z0-9]{48}$ ]]; then
                warn "OpenAI API key format appears incorrect (expected: sk-48chars)"
                return 1
            fi
            ;;
        anthropic)
            # Anthropic API keys: sk-ant-...
            if [[ ! "$key" =~ ^sk-ant-[A-Za-z0-9_-]+$ ]]; then
                warn "Anthropic API key format appears incorrect (expected: sk-ant-...)"
                return 1
            fi
            ;;
        google)
            # Google API keys are variable length, just check it's not empty
            if [[ ${#key} -lt 10 ]]; then
                warn "Google API key appears too short"
                return 1
            fi
            ;;
        *)
            # For unknown services, just check it's not obviously wrong
            if [[ ${#key} -lt 8 ]]; then
                warn "API key appears too short for service: $service"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Get full path for API key
get_api_key_path() {
    local service="$1"
    local custom_path="$2"
    
    if [[ -n "$custom_path" ]]; then
        echo "$API_KEY_BASE_PATH/$custom_path"
    else
        echo "$API_KEY_BASE_PATH/$service"
    fi
}

# Store API key
store_api_key() {
    local service="$1"
    local key="$2"
    local path
    
    validate_service_name "$service" || return 1
    path=$(get_api_key_path "$service" "$KEY_PATH")
    
    # Prompt for key if not provided
    if [[ -z "$key" ]]; then
        echo -n "Enter API key for $service: "
        read -rs key
        echo
        
        if [[ -z "$key" ]]; then
            error "API key cannot be empty"
            return 1
        fi
    fi
    
    # Validate key format
    if ! validate_api_key_format "$service" "$key"; then
        if [[ "$FORCE" != true ]]; then
            echo -n "Continue anyway? (y/n): "
            read -r response
            [[ "$response" != "y" ]] && return 1
        fi
    fi
    
    # Check if key already exists
    if pass show "$path" >/dev/null 2>&1 && [[ "$FORCE" != true ]]; then
        warn "API key for $service already exists at $path"
        echo -n "Overwrite? (y/n): "
        read -r response
        [[ "$response" != "y" ]] && return 1
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would store API key for $service at $path"
        return 0
    fi
    
    # Store the key with metadata
    local metadata="Service: $service\nCreated: $(date -Iseconds)\nCreated-By: $(whoami)@$(hostname)"
    
    {
        echo "$key"
        echo "---"
        echo -e "$metadata"
    } | pass insert -m "$path"
    
    success "API key stored for $service at $path"
    
    # Add to git if pass store is a git repository
    if [[ -d "$PASS_STORE_DIR/.git" ]]; then
        cd "$PASS_STORE_DIR"
        git add "$path.gpg" 2>/dev/null || true
        git commit -m "Add API key for $service" 2>/dev/null || true
        cd - >/dev/null
    fi
}

# Get API key
get_api_key() {
    local service="$1"
    local path
    
    validate_service_name "$service" || return 1
    path=$(get_api_key_path "$service" "$KEY_PATH")
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would retrieve API key for $service from $path"
        return 0
    fi
    
    if ! pass show "$path" >/dev/null 2>&1; then
        error "No API key found for service: $service"
        info "Available services: $(list_api_keys_brief)"
        return 1
    fi
    
    # Extract just the key (first line before ---)
    local key_data
    key_data=$(pass show "$path")
    
    if [[ "$VERBOSE" == true ]]; then
        echo "$key_data"
    else
        echo "$key_data" | head -1
    fi
}

# List API keys
list_api_keys() {
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would list API keys"
        return 0
    fi
    
    if [[ ! -d "$PASS_STORE_DIR/$API_KEY_BASE_PATH" ]]; then
        warn "No API keys directory found"
        return 0
    fi
    
    log "Stored API keys:"
    echo ""
    
    # Use pass to list keys in api/ directory
    pass ls "$API_KEY_BASE_PATH" 2>/dev/null | grep -v "^$API_KEY_BASE_PATH" | while read -r line; do
        # Clean up the output format
        local clean_line
        clean_line=$(echo "$line" | sed 's/^[├└│─ ]*//' | sed 's/\.gpg$//')
        
        if [[ -n "$clean_line" && "$clean_line" != "$API_KEY_BASE_PATH" ]]; then
            echo "  • $clean_line"
        fi
    done
}

# Brief list for error messages
list_api_keys_brief() {
    if [[ ! -d "$PASS_STORE_DIR/$API_KEY_BASE_PATH" ]]; then
        echo "none"
        return 0
    fi
    
    pass ls "$API_KEY_BASE_PATH" 2>/dev/null | grep -v "^$API_KEY_BASE_PATH" | \
        sed 's/^[├└│─ ]*//' | sed 's/\.gpg$//' | grep -v "^$" | \
        grep -v "^$API_KEY_BASE_PATH$" | tr '\n' ', ' | sed 's/, $//'
}

# Rotate API key
rotate_api_key() {
    local service="$1"
    local path
    
    validate_service_name "$service" || return 1
    path=$(get_api_key_path "$service" "$KEY_PATH")
    
    if ! pass show "$path" >/dev/null 2>&1; then
        error "No existing API key found for service: $service"
        return 1
    fi
    
    warn "Key rotation for $service"
    info "This will:"
    echo "  1. Show the current key"
    echo "  2. Prompt for a new key"
    echo "  3. Store the new key with rotation metadata"
    echo ""
    
    if [[ "$FORCE" != true ]]; then
        echo -n "Continue? (y/n): "
        read -r response
        [[ "$response" != "y" ]] && return 1
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would rotate API key for $service"
        return 0
    fi
    
    # Show current key
    log "Current key for $service:"
    get_api_key "$service"
    echo ""
    
    # Get new key
    echo -n "Enter new API key for $service: "
    read -rs new_key
    echo
    
    if [[ -z "$new_key" ]]; then
        error "New API key cannot be empty"
        return 1
    fi
    
    # Validate new key format
    validate_api_key_format "$service" "$new_key" || true
    
    # Store with rotation metadata
    local metadata="Service: $service\nRotated: $(date -Iseconds)\nRotated-By: $(whoami)@$(hostname)\nPrevious-Key-Hash: $(get_api_key "$service" | sha256sum | cut -d' ' -f1)"
    
    {
        echo "$new_key"
        echo "---"
        echo -e "$metadata"
    } | pass insert -m "$path"
    
    success "API key rotated for $service"
}

# Delete API key
delete_api_key() {
    local service="$1"
    local path
    
    validate_service_name "$service" || return 1
    path=$(get_api_key_path "$service" "$KEY_PATH")
    
    if ! pass show "$path" >/dev/null 2>&1; then
        error "No API key found for service: $service"
        return 1
    fi
    
    warn "This will permanently delete the API key for $service"
    
    if [[ "$FORCE" != true ]]; then
        echo -n "Continue? (y/n): "
        read -r response
        [[ "$response" != "y" ]] && return 1
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would delete API key for $service"
        return 0
    fi
    
    pass rm "$path"
    success "API key deleted for $service"
}

# Validate API key
validate_api_key() {
    local service="$1"
    local path
    
    validate_service_name "$service" || return 1
    path=$(get_api_key_path "$service" "$KEY_PATH")
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would validate API key for $service"
        return 0
    fi
    
    if ! pass show "$path" >/dev/null 2>&1; then
        error "No API key found for service: $service"
        return 1
    fi
    
    local key
    key=$(get_api_key "$service")
    
    log "Validating API key for $service..."
    
    # Format validation
    if validate_api_key_format "$service" "$key"; then
        success "API key format is valid for $service"
    else
        warn "API key format validation failed for $service"
    fi
    
    # Accessibility test
    if [[ -n "$key" && ${#key} -gt 0 ]]; then
        success "API key is accessible and non-empty"
    else
        error "API key is empty or inaccessible"
        return 1
    fi
    
    # Show metadata if verbose
    if [[ "$VERBOSE" == true ]]; then
        echo ""
        info "Full key data:"
        get_api_key "$service" --verbose
    fi
}

# Main function
main() {
    parse_args "$@"
    
    if [[ -z "$ACTION" ]]; then
        error "No action specified"
        show_help
        exit 1
    fi
    
    check_dependencies
    
    case "$ACTION" in
        store)
            if [[ -z "$SERVICE" ]]; then
                error "Service name required for store action"
                exit 1
            fi
            store_api_key "$SERVICE" "$KEY_VALUE"
            ;;
        get)
            if [[ -z "$SERVICE" ]]; then
                error "Service name required for get action"
                exit 1
            fi
            get_api_key "$SERVICE"
            ;;
        list)
            list_api_keys
            ;;
        rotate)
            if [[ -z "$SERVICE" ]]; then
                error "Service name required for rotate action"
                exit 1
            fi
            rotate_api_key "$SERVICE"
            ;;
        delete)
            if [[ -z "$SERVICE" ]]; then
                error "Service name required for delete action"
                exit 1
            fi
            delete_api_key "$SERVICE"
            ;;
        validate)
            if [[ -z "$SERVICE" ]]; then
                error "Service name required for validate action"
                exit 1
            fi
            validate_api_key "$SERVICE"
            ;;
        *)
            error "Unknown action: $ACTION"
            show_help
            exit 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi