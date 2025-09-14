#!/usr/bin/env bash
set -euo pipefail

# Think Hard Hook
#
# This hook injects a simple "Think hard" instruction to encourage
# deeper analysis and critical thinking in Claude's responses.
# 
# Installation:
# - This script is executed as a UserPromptSubmit hook
# - Output is injected into Claude's context before processing user prompts

# Simple prompt enhancement - encourage critical thinking
echo -e "\nThink hard.\n"