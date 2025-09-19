#!/usr/bin/env bash
# Dotfiles Validation Script
# Provides comprehensive validation for GNU Stow based dotfiles setup.
# Supports symlink integrity, profile/package validation, security checks,
# functional smoke tests, and idempotency verification.
# Can be used locally or in CI pipelines.

set -euo pipefail

# ---------- Argument Parsing ----------
DRY_RUN=0
while (("$#")); do
  case "$1" in
    --dry-run) DRY_RUN=1 ; shift ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# ---------- Helper Functions ----------
log()    { echo -e "[INFO] $*"; }
info()   { echo -e "[INFO] $*"; }
warn()   { echo -e "\033[1;33m[WARN]\033[0m $*"; }
error()  { echo -e "\033[1;31m[ERROR]\033[0m $*"; }
success(){ echo -e "\033[1;32m[PASS]\033[0m $*"; }

command_exists() { command -v "$1" >/dev/null 2>&1; }

# Determine OS for permission checks
if [[ "$OSTYPE" == "darwin"* ]]; then
  OS_TYPE="macos"
else
  OS_TYPE="linux"
fi

# Resolve repository root and home directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOME_DIR="${HOME:-/home/$(whoami)}"

# Result tracking
declare -A validation_results
ERRORS_FOUND=0
WARNINGS_FOUND=0

record_result() {
  local component="$1"
  local status="$2"
  local message="$3"
  validation_results["$component"]="$status:$message"
  case "$status" in
    PASS) success "$component: $message" ;;
    WARN) warn "$component: $message" ; ((WARNINGS_FOUND++)) ;;
    FAIL) error "$component: $message" ; ((ERRORS_FOUND++)) ;;
  esac
}

# ---------- Validation Functions ----------

validate_symlink_integrity() {
  log "Validating symlink integrity..."
  local total=0 broken=0
  while IFS= read -r -d '' link; do
    ((total++))
    local target
    target=$(readlink "$link")
    if [[ -e "$target" ]]; then
      record_result "Symlink: $(basename "$link")" PASS "points to existing target"
    else
      ((broken++))
      record_result "Symlink: $(basename "$link")" FAIL "broken (target $target missing)"
    fi
  done < <(find "$HOME_DIR" -type l -lname "$DOTFILES_ROOT/*" -print0 2>/dev/null)

  if (( total == 0 )); then
    record_result "Symlink Check" WARN "No stowed symlinks found"
  elif (( broken == 0 )); then
    record_result "Symlink Check" PASS "All $total symlinks valid"
  else
    record_result "Symlink Check" FAIL "$broken out of $total symlinks broken"
  fi
}

validate_profile_packages() {
  log "Validating profile package declarations..."
  local profile_dir="$DOTFILES_ROOT/profiles"
  if [[ ! -d "$profile_dir" ]]; then
    record_result "Profiles" WARN "profiles directory missing"
    return
  fi
  for profile_file in "$profile_dir"/*.txt; do
    local profile_name=$(basename "$profile_file" .txt)
    while IFS= read -r line || [[ -n $line ]]; do
      line=$(echo "$line" | tr -d '\r')
      [[ -z "$line" || "$line" == "#"* ]] && continue
      if [[ -d "$DOTFILES_ROOT/$line" ]]; then
        record_result "Profile $profile_name: $line" PASS "package exists"
      else
        record_result "Profile $profile_name: $line" FAIL "package missing in repository"
      fi
    done < "$profile_file"
  done
}

security_checks() {
  log "Performing security checks..."
  local ssh_dir="$HOME_DIR/.ssh"
  if [[ ! -d "$ssh_dir" ]]; then
    record_result "SSH Directory" WARN "$ssh_dir not found"
    return
  fi
  # Private key patterns
  shopt -s nullglob
  local key_files=($ssh_dir/id_* )
  shopt -u nullglob
  if (( ${#key_files[@]} == 0 )); then
    record_result "SSH Keys" WARN "No private SSH keys found"
    return
  fi
  for key in "${key_files[@]}"; do
    if [[ -f "$key" && ! -L "$key" ]]; then
      # Determine permission bits
      local perm
      if [[ "$OS_TYPE" == "macos" ]]; then
        perm=$(stat -f "%A" "$key")
      else
        perm=$(stat -c "%a" "$key")
      fi
      if [[ "$perm" == "600" || "$perm" == "400" ]]; then
        record_result "SSH Key $(basename "$key")" PASS "permissions $perm"
      else
        record_result "SSH Key $(basename "$key")" FAIL "insecure permissions $perm (should be 600 or 400)"
      fi
    fi
  done
}

functional_smoke_tests() {
  log "Running functional smoke tests (stow dry-run)..."
  if ! command_exists stow; then
    record_result "Stow" FAIL "stow command not found"
    return
  fi
  local pkg
  for pkg in $(ls -d "$DOTFILES_ROOT"/*/ | while read -r d; do basename "$d"; done); do
    # Skip non-package dirs (scripts, docs, .git, etc.)
    case "$pkg" in
      scripts|docs|.git|.github|.stow-global-ignore|.gitignore|README.md|Makefile) continue ;; esac
    # Run stow dry-run for this package
    if stow -n -t "$HOME_DIR" "$pkg" >/dev/null 2>&1; then
      record_result "Stow Smoke $pkg" PASS "dry-run successful"
    else
      record_result "Stow Smoke $pkg" FAIL "dry-run reported issues"
    fi
  done
}

idempotency_check() {
  log "Checking idempotency via stow dry-run on all packages..."
  # Reuse functional smoke logic but aggregate result
  local failures=0
  for pkg in $(ls -d "$DOTFILES_ROOT"/*/ | while read -r d; do basename "$d"; done); do
    case "$pkg" in
      scripts|docs|.git|.github|.stow-global-ignore|.gitignore|README.md|Makefile) continue ;; esac
    if ! stow -n -t "$HOME_DIR" "$pkg" >/dev/null 2>&1; then
      ((failures++))
    fi
  done
  if (( failures == 0 )); then
    record_result "Idempotency" PASS "Running install multiple times is safe"
  else
    record_result "Idempotency" FAIL "$failures package(s) reported changes on dry-run"
  fi
}

generate_report() {
  echo "\n==================================="
  echo "       Dotfiles Validation Report"
  echo "===================================\n"
  local pass=0 warn=0 fail=0
  for comp in "${!validation_results[@]}"; do
    IFS=':' read -r status msg <<< "${validation_results[$comp]}"
    case "$status" in
      PASS) ((pass++)) ;;
      WARN) ((warn++)) ;;
      FAIL) ((fail++)) ;;
    esac
  done
  echo "Results:"
  echo "  ✓ Passed : $pass"
  echo "  ⚠ Warn  : $warn"
  echo "  ✗ Failed: $fail\n"
  if (( ERRORS_FOUND > 0 )); then
    error "Validation completed with $ERRORS_FOUND error(s)."
    exit 1
  else
    success "All critical checks passed."
    exit 0
  fi
}

# ---------- Main Execution ----------
log "Starting dotfiles validation$( [[ $DRY_RUN -eq 1 ]] && echo " (dry-run mode)" )"

validate_symlink_integrity
validate_profile_packages
security_checks
functional_smoke_tests
idempotency_check

generate_report
