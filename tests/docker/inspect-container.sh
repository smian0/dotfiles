#!/usr/bin/env bash
# Docker Test Container Inspector
# Allows inspection of test containers and their filesystems

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

# Logging functions
log() { echo -e "${GREEN}[INFO]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Show help
show_help() {
    cat << EOF
${BOLD}Docker Test Container Inspector${NC}

This tool helps you inspect and debug Docker test containers.

Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    list                List all test containers and volumes
    shell [LEVEL]       Start interactive shell in test container
    inspect [LEVEL]     Inspect filesystem of test container
    export [LEVEL]      Export container filesystem to local directory
    logs [LEVEL]        Show logs from test container
    diff [LEVEL]        Show filesystem changes in container
    keep [LEVEL]        Run test and keep container running
    clean               Clean up all test containers and volumes
    help                Show this help

LEVELS:
    quick               Quick validation test container
    unit                Unit test container
    integration         Integration test container
    e2e                 End-to-end test container
    stress              Stress test container

EXAMPLES:
    $0 list                     # List all containers
    $0 shell quick              # Open shell in quick test container
    $0 inspect unit             # Browse unit test container filesystem
    $0 export integration       # Export integration test results
    $0 diff quick              # Show what changed in quick test
    $0 keep unit               # Run unit test and keep container
    $0 logs e2e                # View e2e test logs

EOF
}

# List all test containers and volumes
list_containers() {
    log "Docker Test Containers:"
    echo "======================="
    
    # List containers
    echo -e "\n${BOLD}Containers:${NC}"
    docker ps -a --filter "name=dotfiles-" --format "table {{.Names}}\t{{.Status}}\t{{.CreatedAt}}"
    
    # List volumes
    echo -e "\n${BOLD}Volumes:${NC}"
    docker volume ls --filter "name=test-home" --format "table {{.Name}}\t{{.Driver}}\t{{.CreatedAt}}"
    
    # Show disk usage
    echo -e "\n${BOLD}Disk Usage:${NC}"
    docker system df 2>/dev/null | grep -E "TYPE|Containers|Volumes|Local" || echo "No containers or volumes found"
}

# Start interactive shell in container
start_shell() {
    local level="${1:-quick}"
    local service="dotfiles-$level"
    
    log "Starting interactive shell in $service container..."
    
    # Check if container exists
    if ! docker ps -a | grep -q "$service"; then
        warn "Container $service doesn't exist. Creating it..."
        
        # Build and create container
        docker-compose -f "$COMPOSE_FILE" build "$service"
        docker-compose -f "$COMPOSE_FILE" run --rm --entrypoint /bin/bash "$service"
    else
        # Container exists, check if running
        if docker ps | grep -q "$service"; then
            log "Connecting to running container..."
            docker exec -it "$service" /bin/bash
        else
            log "Starting stopped container..."
            docker start -i "$service"
        fi
    fi
}

# Inspect container filesystem
inspect_filesystem() {
    local level="${1:-quick}"
    local service="dotfiles-$level"
    
    log "Inspecting filesystem of $service container..."
    
    # Create temporary inspection container
    docker-compose -f "$COMPOSE_FILE" run --rm --entrypoint /bin/bash "$service" -c "
        echo '${BOLD}=== Home Directory Structure ===${NC}'
        ls -la ~
        echo
        
        echo '${BOLD}=== Dotfiles Source ===${NC}'
        ls -la ~/dotfiles-source
        echo
        
        echo '${BOLD}=== Installed Symlinks ===${NC}'
        find ~ -maxdepth 2 -type l -ls 2>/dev/null | head -20
        echo
        
        echo '${BOLD}=== Git Configuration ===${NC}'
        if [[ -f ~/.gitconfig ]]; then
            echo 'Git config exists:'
            ls -la ~/.gitconfig
            head -10 ~/.gitconfig
        else
            echo 'No git configuration found'
        fi
        echo
        
        echo '${BOLD}=== Test Results ===${NC}'
        if [[ -d ~/dotfiles-source/tests/logs ]]; then
            ls -la ~/dotfiles-source/tests/logs 2>/dev/null | tail -5
        fi
        
        echo '${BOLD}=== Disk Usage ===${NC}'
        du -sh ~ 2>/dev/null
        df -h ~ 2>/dev/null | tail -1
    "
}

# Export container filesystem
export_filesystem() {
    local level="${1:-quick}"
    local service="dotfiles-$level"
    local export_dir="$PROJECT_ROOT/tests/exports/${level}-$(date +%Y%m%d_%H%M%S)"
    
    log "Exporting $service container filesystem to $export_dir..."
    
    # Create export directory
    mkdir -p "$export_dir"
    
    # Create container if needed
    docker-compose -f "$COMPOSE_FILE" create "$service" 2>/dev/null || true
    
    # Get container ID
    container_id=$(docker ps -aq -f "name=$service" | head -1)
    
    if [[ -z "$container_id" ]]; then
        error "Container $service not found"
        return 1
    fi
    
    # Export home directory
    log "Exporting home directory..."
    docker cp "$container_id:/home/testuser" "$export_dir/home" 2>/dev/null || warn "Could not export home directory"
    
    # Export specific directories of interest
    log "Exporting test results..."
    docker cp "$container_id:/home/testuser/dotfiles-source/tests/logs" "$export_dir/test-logs" 2>/dev/null || true
    
    # Create summary
    cat > "$export_dir/summary.txt" << EOF
Docker Test Export Summary
==========================
Container: $service
Export Date: $(date)
Container ID: $container_id

Directory Structure:
$(ls -la "$export_dir")

Test Container Status:
$(docker ps -a --filter "id=$container_id" --format "Status: {{.Status}}")
EOF
    
    success "Exported to: $export_dir"
    echo "You can browse the exported filesystem at: $export_dir"
}

# Show container logs
show_logs() {
    local level="${1:-quick}"
    local service="dotfiles-$level"
    
    log "Showing logs for $service container..."
    
    if docker ps -a | grep -q "$service"; then
        docker-compose -f "$COMPOSE_FILE" logs --tail=100 "$service"
    else
        warn "Container $service not found. Running test first..."
        docker-compose -f "$COMPOSE_FILE" run --rm "$service"
    fi
}

# Show filesystem differences
show_diff() {
    local level="${1:-quick}"
    local service="dotfiles-$level"
    
    log "Showing filesystem changes in $service container..."
    
    # Get container ID
    container_id=$(docker ps -aq -f "name=$service" | head -1)
    
    if [[ -z "$container_id" ]]; then
        error "Container $service not found. Run test first."
        return 1
    fi
    
    # Show Docker diff
    echo -e "${BOLD}Filesystem changes:${NC}"
    docker diff "$container_id" | head -50
    
    echo -e "\n${BOLD}Legend:${NC}"
    echo "  A = Added"
    echo "  C = Changed"
    echo "  D = Deleted"
}

# Run test and keep container
keep_container() {
    local level="${1:-quick}"
    local service="dotfiles-$level"
    
    log "Running $level test and keeping container for inspection..."
    
    # Override entrypoint to keep container running
    docker-compose -f "$COMPOSE_FILE" run -d --name "${service}-inspect" --entrypoint "tail -f /dev/null" "$service"
    
    # Run the actual test commands
    log "Running test commands..."
    case "$level" in
        quick)
            docker exec "${service}-inspect" bash -c "cd /home/testuser/dotfiles-source && ./tests/docker/test-cases/makefile-validation.sh"
            ;;
        unit)
            docker exec "${service}-inspect" bash -c "cd /home/testuser/dotfiles-source && ./tests/docker/test-cases/installation-validation.sh && ./tests/docker/test-cases/security-validation.sh"
            ;;
        integration)
            docker exec "${service}-inspect" bash -c "cd /home/testuser/dotfiles-source && ./tests/docker/test-cases/backup-restore-test.sh && ./tests/docker/test-cases/profile-switching.sh"
            ;;
        *)
            warn "No specific test commands for level: $level"
            ;;
    esac
    
    success "Container ${service}-inspect is running"
    echo
    echo "You can now inspect it with:"
    echo "  docker exec -it ${service}-inspect /bin/bash"
    echo "  $0 inspect $level"
    echo "  $0 export $level"
    echo
    echo "When done, remove with:"
    echo "  docker rm -f ${service}-inspect"
}

# Clean up all test containers
clean_all() {
    log "Cleaning up all test containers and volumes..."
    
    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans
    
    # Remove any inspection containers
    docker ps -a --filter "name=dotfiles-" --format "{{.Names}}" | xargs -r docker rm -f
    
    # Clean volumes
    docker volume ls --filter "name=test-home" --format "{{.Name}}" | xargs -r docker volume rm
    
    # Prune system
    docker system prune -f
    
    success "Cleanup completed"
}

# Main execution
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        list)
            list_containers
            ;;
        shell)
            start_shell "$@"
            ;;
        inspect)
            inspect_filesystem "$@"
            ;;
        export)
            export_filesystem "$@"
            ;;
        logs)
            show_logs "$@"
            ;;
        diff)
            show_diff "$@"
            ;;
        keep)
            keep_container "$@"
            ;;
        clean)
            clean_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Success message helper
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Run main
main "$@"