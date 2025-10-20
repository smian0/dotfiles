# Archived Scripts

This directory contains deprecated scripts that have been replaced by better implementations.

## morning-watch-list.sh.deprecated

**Status:** DEPRECATED as of October 6, 2025

**Reason:** Replaced by pure Claude command `/morning-watch-list`

**Old approach:** 350+ line bash script that parsed CSV files and daily updates
**New approach:** Claude command that reads files directly and provides richer analysis

**Why the change:**
- ✅ Claude can add market context from portfolio summaries
- ✅ Better error handling and user feedback
- ✅ Can highlight CSV warnings (legal issues, liquidity)
- ✅ Adapts output based on market conditions
- ✅ Easier to maintain (single markdown file vs complex bash)
- ✅ Can cross-reference with upcoming catalysts

**Migration:**
- Old: `bash ~/dotfiles/scripts/morning-watch-list.sh --portfolio=quantum-computing`
- New: `/morning-watch-list --portfolio=quantum-computing`

The bash script is kept here for reference but should not be used.
