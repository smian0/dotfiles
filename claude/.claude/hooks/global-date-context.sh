#!/usr/bin/env bash
set -euo pipefail

# Configuration
TZ=${CLAUDE_TIMEZONE:-$(date +%Z)}
export TZ

# Generate comprehensive temporal context
CURRENT_DATE=$(date +'%Y-%m-%d')
CURRENT_TIME=$(date +'%H:%M:%S %Z')
CURRENT_YEAR=$(date +%Y)
ISO_TIMESTAMP=$(date -Iseconds)

# Inject context that Claude will always see
printf "[TEMPORAL CONTEXT]\n"
printf "Current Date: %s\n" "$CURRENT_DATE"
printf "Current Time: %s\n" "$CURRENT_TIME" 
printf "Current Year: %s\n" "$CURRENT_YEAR"
printf "ISO Timestamp: %s\n" "$ISO_TIMESTAMP"
printf "Timezone: %s\n" "$TZ"
printf "\n[INSTRUCTION] Always use %s as the current year for searches, recommendations, and time-sensitive operations.\n\n" "$CURRENT_YEAR"