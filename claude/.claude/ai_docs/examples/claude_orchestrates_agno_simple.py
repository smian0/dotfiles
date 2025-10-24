#!/usr/bin/env python3
"""
Simple Claude + Agno Orchestration Demo
========================================

Demonstrates Claude Agent SDK calling Agno agents as specialized workers.

This is a minimal, clear example showing:
  1. Claude Agent SDK creates custom tools that wrap Agno agents
  2. User asks a question requiring multiple steps
  3. Claude delegates subtasks to Agno agents
  4. Agno agents return results
  5. Claude synthesizes final answer

Usage:
  python3 claude_orchestrates_agno_simple.py

Real-world use case: News analysis requiring web research + sentiment analysis
"""

import asyncio
from claude_agent_sdk import tool, query, ClaudeAgentOptions, create_sdk_mcp_server, AssistantMessage, TextBlock

# Mock Agno for demo (replace with real Agno if installed)
try:
    from agno.agent import Agent
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False
    class Agent:
        def __init__(self, instructions="", **kwargs):
            self.instructions = instructions

        def run(self, prompt):
            class Result:
                def __init__(self, content):
                    self.content = content

            # Simulate specialized agent responses
            if "sentiment" in self.instructions.lower():
                return Result("SENTIMENT ANALYSIS: The text shows POSITIVE sentiment (confidence: 85%)")
            elif "summarize" in self.instructions.lower():
                return Result("SUMMARY: Key points extracted: Market growth, new partnerships, increased revenue.")
            else:
                return Result(f"Agno agent processed: {prompt[:50]}...")


# ============================================================================
# Agno Specialized Workers
# ============================================================================

def create_sentiment_analyzer():
    """Agno agent specialized in sentiment analysis"""
    return Agent(
        instructions="You analyze text sentiment. Return POSITIVE, NEGATIVE, or NEUTRAL with confidence score."
    )

def create_text_summarizer():
    """Agno agent specialized in summarization"""
    return Agent(
        instructions="You summarize text into key bullet points. Be concise."
    )


# ============================================================================
# Bridge Tools (Claude → Agno)
# ============================================================================

@tool(
    "agno_sentiment_analyzer",
    "Analyzes sentiment of provided text using specialized Agno agent",
    {"text": "string - Text to analyze"}
)
async def agno_sentiment_analyzer(args):
    """Bridge: Claude delegates sentiment analysis to Agno"""
    text = args["text"]
    print(f"\n  🎭 [AGNO SENTIMENT] Analyzing: '{text[:60]}...'")

    agent = create_sentiment_analyzer()
    result = agent.run(text)

    print(f"  ✅ [AGNO SENTIMENT] Result: {result.content}")
    return {"content": [{"type": "text", "text": result.content}]}


@tool(
    "agno_text_summarizer",
    "Summarizes long text into key points using specialized Agno agent",
    {"text": "string - Text to summarize"}
)
async def agno_text_summarizer(args):
    """Bridge: Claude delegates summarization to Agno"""
    text = args["text"]
    print(f"\n  📝 [AGNO SUMMARIZER] Processing: '{text[:60]}...'")

    agent = create_text_summarizer()
    result = agent.run(text)

    print(f"  ✅ [AGNO SUMMARIZER] Result: {result.content}")
    return {"content": [{"type": "text", "text": result.content}]}


# ============================================================================
# Claude Orchestrator
# ============================================================================

async def orchestrate_analysis(article_text: str):
    """Claude orchestrates: delegates to Agno workers, synthesizes results"""

    print("\n" + "="*80)
    print("📰 ARTICLE TO ANALYZE:")
    print("="*80)
    print(f"{article_text}\n")
    print("="*80)

    # Create MCP server with Agno worker tools
    agno_workers = create_sdk_mcp_server(
        name="agno_workers",
        version="1.0.0",
        tools=[agno_sentiment_analyzer, agno_text_summarizer]
    )

    options = ClaudeAgentOptions(
        system_prompt="""You are an orchestrator that delegates work to Agno agents.

Available Agno workers:
- agno_sentiment_analyzer: Analyzes text sentiment
- agno_text_summarizer: Summarizes text to key points

When given an article:
1. Use agno_text_summarizer to get key points
2. Use agno_sentiment_analyzer to determine sentiment
3. Combine both results into a comprehensive analysis

IMPORTANT: You MUST use both Agno tools before providing your final answer.""",
        mcp_servers={"agno_workers": agno_workers},
        permission_mode='acceptEdits'
    )

    print("\n🤖 [CLAUDE ORCHESTRATOR] Starting analysis...\n")

    task = f"""Analyze this article by:
1. Summarizing the key points (use agno_text_summarizer)
2. Determining the sentiment (use agno_sentiment_analyzer)
3. Provide a final comprehensive analysis

Article:
{article_text}"""

    response_text = ""
    async for message in query(prompt=task, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text += block.text

    print("\n" + "="*80)
    print("📊 [CLAUDE ORCHESTRATOR] Final Analysis:")
    print("="*80)
    print(response_text)
    print("="*80 + "\n")


# ============================================================================
# Demo
# ============================================================================

async def main():
    print("\n" + "="*80)
    print("Claude Agent SDK Orchestrating Agno Agents - Simple Demo")
    print("="*80)

    if not AGNO_AVAILABLE:
        print("ℹ️  Using mock Agno agents (install agno for real implementation)")

    # Sample article for analysis
    article = """
    TechCorp announces breakthrough in AI technology. The company reported a 40%
    increase in quarterly revenue and signed partnerships with three Fortune 500
    companies. CEO Jane Smith stated: "We're excited about the future and our
    innovative products are transforming the industry." Analysts predict continued
    growth with strong market demand for their AI solutions.
    """

    await orchestrate_analysis(article)

    print("\n" + "="*80)
    print("Architecture Summary:")
    print("="*80)
    print("1. ✅ Claude Agent SDK acts as master orchestrator")
    print("2. ✅ Agno agents are specialized workers (sentiment, summarization)")
    print("3. ✅ @tool functions bridge Claude → Agno")
    print("4. ✅ Claude delegates subtasks to Agno agents")
    print("5. ✅ Claude synthesizes Agno results into final answer")
    print("\n💡 To extend: Add more Agno workers (translator, classifier, etc.)")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
