#!/usr/bin/env python3
"""
Initialize research workspace and coordinator status file.
"""

import sys
from datetime import datetime
from pathlib import Path

def init_research(research_question: str, streams: int = 4, depth: str = "deep"):
    """Initialize research workspace."""

    # Get current timestamp
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    date_short = now.strftime("%Y-%m-%d")

    # Create workspace directories
    workspace = Path("./research-output")
    (workspace / "progress").mkdir(parents=True, exist_ok=True)
    (workspace / "sources").mkdir(parents=True, exist_ok=True)
    (workspace / "analysis").mkdir(parents=True, exist_ok=True)
    (workspace / "report").mkdir(parents=True, exist_ok=True)

    # Create coordinator status file
    coordinator_file = workspace / "progress" / "coordinator-status.md"

    coordinator_content = f"""---
research_question: "{research_question}"
streams: {streams}
depth: {depth}
started: {timestamp}
status: discovery_phase
---

## Research Angles (Parallel Streams)

### Stream 1: [Define angle 1]
- Focus: [specific focus]
- Status: Initializing
- Output: sources/stream-1-sources-{date_short}.md

### Stream 2: [Define angle 2]
- Focus: [specific focus]
- Status: Initializing
- Output: sources/stream-2-sources-{date_short}.md

### Stream 3: [Define angle 3]
- Focus: [specific focus]
- Status: Initializing
- Output: sources/stream-3-sources-{date_short}.md

### Stream 4: [Define angle 4]
- Focus: [specific focus]
- Status: Initializing
- Output: sources/stream-4-sources-{date_short}.md

## Phase Status
- [x] Phase 0: Initialization
- [ ] Phase 1: Discovery (parallel)
- [ ] Phase 2: Validation
- [ ] Phase 3: Analysis
- [ ] Phase 4: Synthesis
"""

    coordinator_file.write_text(coordinator_content)

    print(f"✅ Research workspace initialized: {workspace}")
    print(f"   - Timestamp: {timestamp}")
    print(f"   - Date: {date_short}")
    print(f"   - Streams: {streams}")
    print(f"   - Depth: {depth}")
    print(f"   - Coordinator: {coordinator_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python init-research.py <research_question> [streams] [depth]")
        print('Example: python init-research.py "Why is crypto suffering?" 4 deep')
        sys.exit(1)

    question = sys.argv[1]
    streams = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    depth = sys.argv[3] if len(sys.argv) > 3 else "deep"

    init_research(question, streams, depth)
