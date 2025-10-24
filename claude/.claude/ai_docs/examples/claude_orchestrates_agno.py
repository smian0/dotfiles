#!/usr/bin/env python3
"""
Claude Agent SDK Orchestrating Agno Agents
===========================================

Demonstrates Claude Agent SDK as the master orchestrator with Agno agents as specialized workers.

Architecture:
  Claude Agent SDK (Master)
      ↓
  Custom Tools (Bridge)
      ↓
  Agno Agents (Workers)

Example: User asks about California's population density
  1. Claude decides to research California stats
  2. Calls research_agno_agent tool → Agno research agent returns data
  3. Claude decides to calculate density
  4. Calls calculator_agno_agent tool → Agno calculator returns result
  5. Claude synthesizes final answer

Usage:
  python3 claude_orchestrates_agno.py
"""

import asyncio
from claude_agent_sdk import tool, query, ClaudeAgentOptions, create_sdk_mcp_server, AssistantMessage, TextBlock

# Import Agno (will use mock if not installed)
try:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    AGNO_AVAILABLE = True
except ImportError:
    print("⚠️  Agno not installed - using mock agents for demonstration")
    AGNO_AVAILABLE = False

    # Mock Agno Agent for demonstration
    class Agent:
        def __init__(self, instructions=None, **kwargs):
            self.instructions = instructions

        def run(self, prompt):
            class MockResult:
                def __init__(self, content):
                    self.content = content

            # Simple mock responses based on agent type
            if "research" in self.instructions.lower():
                if "california" in prompt.lower():
                    return MockResult("California has a population of approximately 39 million people and covers an area of 163,696 square miles.")
                elif "tokyo" in prompt.lower():
                    return MockResult("Tokyo has a population of approximately 14 million people and covers an area of 2,194 square kilometers.")
                else:
                    return MockResult(f"Research result for: {prompt}")
            elif "calculate" in self.instructions.lower():
                # Try to do actual calculation
                try:
                    if "/" in prompt:
                        parts = prompt.split("/")
                        num1 = float(parts[0].strip())
                        num2 = float(parts[1].strip())
                        result = num1 / num2
                        return MockResult(f"{result:.2f}")
                    elif "*" in prompt:
                        parts = prompt.split("*")
                        num1 = float(parts[0].strip())
                        num2 = float(parts[1].strip())
                        result = num1 * num2
                        return MockResult(f"{result:.2f}")
                except:
                    return MockResult(f"Calculation result for: {prompt}")
            return MockResult(f"Result for: {prompt}")


# =============================================================================
# Agno Worker Agents (Specialized)
# =============================================================================

def create_research_agent():
    """Create an Agno agent specialized in research"""
    return Agent(
        instructions="""You are a research assistant specialized in finding factual information.
        When asked about places, provide population, area, and other key statistics.
        Be concise and focus on facts and numbers."""
    )


def create_calculator_agent():
    """Create an Agno agent specialized in calculations"""
    return Agent(
        instructions="""You are a calculator assistant specialized in mathematical computations.
        When given numbers and operations, perform the calculation and return just the numerical result.
        Be precise and concise - return only the computed value."""
    )


# =============================================================================
# Bridge Tools (Claude → Agno)
# =============================================================================

@tool(
    "research_agno_agent",
    "Delegates research tasks to specialized Agno research agent. Use this when you need factual information, statistics, or data about places, people, or topics.",
    {
        "query": "string - The research query or question to ask the Agno research agent"
    }
)
async def research_agno_agent(args):
    """Bridge tool: Claude calls this to delegate to Agno research agent"""
    query_text = args["query"]

    print(f"\n🔍 [AGNO RESEARCH AGENT] Processing: {query_text}")

    # Create and run Agno research agent
    agent = create_research_agent()
    result = agent.run(query_text)

    response = result.content
    print(f"✅ [AGNO RESEARCH AGENT] Result: {response}")

    return {
        "content": [{
            "type": "text",
            "text": response
        }]
    }


@tool(
    "calculator_agno_agent",
    "Delegates mathematical calculations to specialized Agno calculator agent. Use this when you need to perform arithmetic operations, compute formulas, or process numerical data.",
    {
        "expression": "string - The mathematical expression or calculation to perform (e.g., '39000000 / 163696')"
    }
)
async def calculator_agno_agent(args):
    """Bridge tool: Claude calls this to delegate to Agno calculator agent"""
    expression = args["expression"]

    print(f"\n🧮 [AGNO CALCULATOR AGENT] Processing: {expression}")

    # Create and run Agno calculator agent
    agent = create_calculator_agent()
    result = agent.run(expression)

    response = result.content
    print(f"✅ [AGNO CALCULATOR AGENT] Result: {response}")

    return {
        "content": [{
            "type": "text",
            "text": response
        }]
    }


# =============================================================================
# Claude Orchestrator Setup
# =============================================================================

def create_orchestrator_options():
    """Create Claude Agent SDK options with Agno worker tools"""

    # Wrap Agno bridge tools in MCP server
    agno_server = create_sdk_mcp_server(
        name="agno_workers",
        version="1.0.0",
        tools=[research_agno_agent, calculator_agno_agent]
    )

    options = ClaudeAgentOptions(
        system_prompt="""You are an intelligent orchestrator that delegates work to specialized Agno agents.

You have two specialized Agno worker agents available:
1. research_agno_agent - For finding factual information and statistics
2. calculator_agno_agent - For mathematical calculations

When a user asks a question:
- Analyze what information is needed
- Delegate to the appropriate Agno agent(s)
- Synthesize their responses into a coherent answer

Example workflow for "What's the population density of California?":
1. Call research_agno_agent to get California's population and area
2. Call calculator_agno_agent to compute density (population / area)
3. Provide final answer with proper units

Be efficient - only call the agents you need.""",
        mcp_servers={"agno_workers": agno_server},
        permission_mode='acceptEdits'
    )

    return options


# =============================================================================
# Demo Scenarios
# =============================================================================

async def run_orchestration_demo(user_query: str):
    """Run a demo showing Claude orchestrating Agno agents"""

    print(f"\n{'='*70}")
    print(f"👤 USER QUERY: {user_query}")
    print(f"{'='*70}")

    options = create_orchestrator_options()

    print("\n🤖 [CLAUDE ORCHESTRATOR] Analyzing query and delegating to Agno workers...\n")

    response_text = ""
    async for message in query(prompt=user_query, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text += block.text

    print(f"\n{'='*70}")
    print(f"📊 [CLAUDE ORCHESTRATOR] Final Answer:")
    print(f"{'='*70}")
    print(response_text)
    print(f"{'='*70}\n")

    return response_text


# =============================================================================
# Main Demo
# =============================================================================

async def main():
    """Run orchestration demos"""

    print("\n" + "="*70)
    print("Claude Agent SDK Orchestrating Agno Agents")
    print("="*70)

    if not AGNO_AVAILABLE:
        print("\n⚠️  Running with mock Agno agents (install agno for real demo)")

    # Demo 1: Population density question
    print("\n\n📋 DEMO 1: Research + Calculation")
    print("-" * 70)
    await run_orchestration_demo(
        "What is the population density of California? Give me the answer in people per square mile."
    )

    # Demo 2: Comparison requiring multiple research calls
    print("\n\n📋 DEMO 2: Multi-Research Comparison")
    print("-" * 70)
    await run_orchestration_demo(
        "Which city is more densely populated: Tokyo or New York City? Calculate the density for both."
    )

    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70)
    print("\nKey Architecture Points:")
    print("  • Claude Agent SDK acts as master orchestrator")
    print("  • Agno agents are specialized workers (research, calculator)")
    print("  • @tool decorated functions bridge Claude → Agno")
    print("  • Claude decides which agents to use and synthesizes results")
    print("  • Single file, easy to extend with more Agno workers")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
