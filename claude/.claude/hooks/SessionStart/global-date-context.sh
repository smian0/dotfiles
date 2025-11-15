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

# Inject context that Claude will always see (session start only)
printf "[TEMPORAL CONTEXT] Current Date: %s | Current Time: %s | Current Year: %s | ISO Timestamp: %s | Timezone: %s\n\n[INSTRUCTION] Always use %s as the current year or full date+time(if applicable) for searches, recommendations, and time-sensitive operations.\n\n" "$CURRENT_DATE" "$CURRENT_TIME" "$CURRENT_YEAR" "$ISO_TIMESTAMP" "$TZ" "$CURRENT_YEAR"