#!/usr/bin/env python3
"""
Generate Consumer-Friendly Intelligence Digest

Translates Phase 1 technical intelligence into accessible plain-language insights
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama


async def generate_consumer_newsletter():
    """Generate consumer-friendly newsletter from Phase 1 intelligence"""

    print("=" * 80)
    print("Consumer-Friendly Intelligence Digest Generation")
    print("=" * 80)
    print()

    # Initialize Graphiti MCP tools
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=60,
    )

    async with graphiti_mcp:
        await graphiti_mcp.initialize()

        # Step 1: Get Phase 1 technical intelligence
        print("🧠 Step 1: Running Phase 1 technical intelligence analysis...\n")

        technical_agent = Agent(
            name="Phase 1 Technical Analyst",
            model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
            tools=[graphiti_mcp],
            add_datetime_to_context=True,  # Inject today's date
            instructions="""
            Provide Phase 1 intelligence analysis with technical metrics.

            Output structured summary:
            - TOP 10 ENTITIES with mentions, z-scores, velocity, centrality
            - ANOMALIES with z-scores and severity
            - VELOCITY LEADERS with classifications
            - KEY NETWORKS with connections and types
            - CENTRALITY JUMPS
            - EMERGING/RECURRING topics
            """,
            markdown=False,
        )

        result = await technical_agent.arun(
            "Analyze rss-intelligence knowledge graph with Phase 1 metrics"
        )

        technical_analysis = result.content

        print("✅ Technical analysis complete\n")

        # Step 2: Translate to consumer-friendly format
        print("=" * 80)
        print("📝 Step 2: Translating to consumer-friendly format...")
        print("=" * 80)
        print()

        consumer_agent = Agent(
            name="Consumer Intelligence Digest Generator",
            model=Ollama(id="deepseek-v3.1:671b-cloud"),
            add_datetime_to_context=True,  # Inject today's date
            instructions="""
            You are a journalist translating intelligence analysis into consumer-friendly news.

            INPUT: Phase 1 technical intelligence (z-scores, velocity, centrality)
            OUTPUT: Accessible intelligence digest using plain language

            === CRITICAL TRANSLATION RULES ===

            ❌ NEVER USE THESE TECHNICAL TERMS:
            - Z-score, standard deviation, statistical significance
            - Centrality score, betweenness, PageRank
            - Velocity, acceleration, temporal dynamics
            - Kleinberg burst, anomaly threshold
            - Network topology, graph metrics

            ✅ ALWAYS USE PLAIN LANGUAGE INSTEAD:
            - "Getting 2-3x more attention than normal"
            - "Connected to X other stories"
            - "Mentions doubled in 24 hours"
            - "Heating up fast"
            - "Web of connections"

            === STRUCTURE ===

            # Your Intelligence Digest - [TODAY'S DATE]

            ## Today's Big Picture
            [2-3 sentence narrative about what's happening and why it matters.
            Connect the dots between top stories. Make it human and relatable.]

            ## 🔥 Getting Unusually High Attention

            For each anomaly (z-score > 2.0):
            **[Entity/Topic]**
            - Normal level: [baseline] stories per day
            - Today: [current] stories (2-3x normal)
            - Why it's surging: [Plain language reason]
            - Why you should care: [Practical impact for readers]

            ## 📈 Rising Fast (Mentions Doubled in 24 Hours)

            For each high-velocity entity:
            **[Entity/Topic]**
            - What's happening: [Describe the acceleration in everyday terms]
            - Speed: From [X] to [Y] mentions today
            - What this means: [Why the momentum matters]

            ## 🌐 Most Connected Stories (Touching Everything)

            For high-centrality entities:
            **[Entity/Topic]**
            - Connected to: [N] different stories today
            - Touches: [List domains/topics in plain language]
            - Why this matters: [Ripple effects, not isolated]
            - What's unusual: [Why this interconnectedness is notable]

            ## ⚠️ Needs Your Attention

            For entities with anomaly + velocity + centrality:
            **[Entity/Topic]**

            This story hits all three warning signs:
            ✓ Getting 2-3x more attention than normal
            ✓ Mentions doubled in the last 24 hours
            ✓ Connected to [N]+ other major stories

            **What this means**: [Explain in one sentence why this combination matters]

            **What to watch**: [Specific next developments to follow]

            ## What to Watch Tomorrow

            Based on today's patterns, here are stories likely to grow:

            **[Entity/Topic]** - [Why it's likely to expand, in plain language]

            === TONE & STYLE ===

            - Informative but accessible (8th grade reading level)
            - Professional but conversational
            - Data-driven but human
            - No fear-mongering, honest about significance
            - Use "you" to engage readers
            - Short paragraphs (2-3 sentences max)
            - Active voice
            - Concrete examples over abstract concepts

            === QUALITY CHECKS ===

            Before finishing, verify:
            1. ✓ Zero technical jargon (no z-scores, centrality, etc.)
            2. ✓ Every insight answers "So what?"
            3. ✓ Clear visual hierarchy (icons, short sections)
            4. ✓ Narrative flow (tells a story)
            5. ✓ Actionable (what to watch tomorrow)

            CRITICAL: Your grandmother should understand this newsletter without
            needing a statistics degree. Translate the intelligence, don't just
            simplify it.
            """,
            markdown=True,
        )

        consumer_context = f"""Technical Intelligence Analysis for {datetime.now().strftime('%Y-%m-%d')}

{technical_analysis}

Translate this technical analysis into a consumer-friendly intelligence digest.

REMEMBER:
- No technical jargon (z-scores, centrality, velocity)
- Plain language ("2x normal attention" not "z-score 2.0")
- Answer "So what?" for every insight
- Make it scannable and engaging
"""

        result = consumer_agent.run(consumer_context)
        consumer_newsletter = result.content

        # Step 3: Save both versions
        newsletters_dir = Path("newsletters")
        newsletters_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save consumer version
        consumer_file = newsletters_dir / f"newsletter_consumer_{timestamp}.md"
        with open(consumer_file, "w") as f:
            f.write(consumer_newsletter)

        # Save technical version for comparison
        technical_file = newsletters_dir / f"newsletter_technical_{timestamp}.md"
        with open(technical_file, "w") as f:
            f.write(f"""# Phase 1 Technical Intelligence Analysis - {datetime.now().strftime('%Y-%m-%d')}

{technical_analysis}
""")

        print(f"\n✅ Consumer newsletter saved: {consumer_file}")
        print(f"✅ Technical analysis saved: {technical_file}\n")

        print("=" * 80)
        print("Consumer-Friendly Newsletter:")
        print("=" * 80)
        print(consumer_newsletter)
        print("=" * 80)

        return 0


def main():
    try:
        return asyncio.run(generate_consumer_newsletter())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
