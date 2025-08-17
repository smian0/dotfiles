#!/usr/bin/env bash
# Incremental Docker Test Runner
# Runs tests in order of speed and criticality

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.incremental.yml"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="$PROJECT_ROOT/tests/logs"

# Test levels in order of execution
QUICK_TESTS=("dotfiles-quick")
UNIT_TESTS=("dotfiles-unit" "dotfiles-security")
INTEGRATION_TESTS=("dotfiles-integration")
E2E_TESTS=("dotfiles-e2e")
STRESS_TESTS=("dotfiles-stress")

# Logging functions
log() { echo -e "${GREEN}[INFO]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }

# Setup logging
setup_logging() {
    mkdir -p "$LOG_DIR"
    exec 1> >(tee "$LOG_DIR/test-run-${TIMESTAMP}.log")
    exec 2> >(tee "$LOG_DIR/test-errors-${TIMESTAMP}.log" >&2)
}

# Show help
show_help() {
    cat << EOF
${BOLD}Incremental Docker Test Runner${NC}

Usage: $0 [OPTIONS] [TEST_LEVEL]

TEST LEVELS:
    quick       Quick validation tests (30s)
    unit        Unit and security tests (2-3min)
    integration Package installation tests (5-10min)
    e2e         End-to-end full tests (10-15min)
    stress      All profiles stress tests (20+min)
    all         Run all tests in sequence

OPTIONS:
    -h, --help     Show this help
    -v, --verbose  Verbose output
    -c, --clean    Clean containers before running
    -k, --keep     Keep containers after tests
    -f, --fail-fast Stop on first failure
    --logs         Show logs directory

EXAMPLES:
    $0 quick                    # Run quick tests only
    $0 unit                     # Run unit tests
    $0 integration --clean      # Clean and run integration tests
    $0 all --fail-fast         # Run all tests, stop on failure

EOF
}

# Run specific test level
run_test_level() {
    local level="$1"
    local services=()
    
    case "$level" in
        quick)
            services=("${QUICK_TESTS[@]}")
            ;;
        unit)
            services=("${UNIT_TESTS[@]}")
            ;;
        integration)
            services=("${INTEGRATION_TESTS[@]}")
            ;;
        e2e)
            services=("${E2E_TESTS[@]}")
            ;;
        stress)
            services=("${STRESS_TESTS[@]}")
            ;;
        *)
            error "Unknown test level: $level"
            return 1
            ;;
    esac
    
    log "Running $level tests..."
    
    for service in "${services[@]}"; do
        info "Starting $service..."
        
        # Run the service
        docker-compose -f "$COMPOSE_FILE" run --rm "$service"
        local exit_code=$?
        
        if [[ $exit_code -eq 0 ]]; then
            success "$service completed successfully"
        else
            error "$service failed with exit code $exit_code"
            
            if [[ "${FAIL_FAST:-false}" == "true" ]]; then
                error "Failing fast due to --fail-fast option"
                return $exit_code
            fi
        fi
    done
    
    success "$level tests completed!"
}

# Clean containers and volumes
clean_containers() {
    log "Cleaning Docker containers and volumes..."
    
    docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans 2>/dev/null || true
    
    # Remove any dangling containers
    docker container prune -f 2>/dev/null || true
    docker volume prune -f 2>/dev/null || true
    
    success "Cleanup completed"
}

# Show test results
show_results() {
    echo
    info "Test Results Summary:"
    echo "  Log files: $LOG_DIR/test-*-${TIMESTAMP}.log"
    echo "  Containers: docker ps -a | grep dotfiles"
    echo "  Volumes: docker volume ls | grep test"
    echo
    
    if [[ "${KEEP_CONTAINERS:-false}" == "false" ]]; then
        log "Cleaning up containers..."
        clean_containers
    else
        info "Keeping containers for inspection (use --clean to remove)"
        echo "  Inspect: docker-compose -f $COMPOSE_FILE logs [service]"
        echo "  Connect: docker-compose -f $COMPOSE_FILE exec [service] bash"
    fi
}

# Parse arguments
VERBOSE=false
CLEAN=false
KEEP_CONTAINERS=false
FAIL_FAST=false
TEST_LEVEL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -k|--keep)
            KEEP_CONTAINERS=true
            shift
            ;;
        -f|--fail-fast)
            FAIL_FAST=true
            shift
            ;;
        --logs)
            echo "Logs directory: $LOG_DIR"
            ls -la "$LOG_DIR" 2>/dev/null || echo "No logs found"
            exit 0
            ;;
        quick|unit|integration|e2e|stress|all)
            TEST_LEVEL="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    setup_logging
    
    log "Starting incremental Docker tests..."
    info "Test level: ${TEST_LEVEL:-all}"
    info "Timestamp: $TIMESTAMP"
    info "Project root: $PROJECT_ROOT"
    
    # Clean if requested
    if [[ "$CLEAN" == "true" ]]; then
        clean_containers
    fi
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Export environment variables for docker-compose
    export FAIL_FAST
    export VERBOSE
    export KEEP_CONTAINERS
    
    # Run tests based on level
    case "${TEST_LEVEL:-all}" in
        all)
            log "Running all test levels in sequence..."
            for level in quick unit integration e2e stress; do
                run_test_level "$level"
            done
            ;;
        quick|unit|integration|e2e|stress)
            run_test_level "$TEST_LEVEL"
            ;;
        "")
            error "No test level specified"
            show_help
            exit 1
            ;;
    esac
    
    show_results
    success "All tests completed successfully! 🎉"
}

# Trap for cleanup on exit
trap 'show_results' EXIT

main "$@"