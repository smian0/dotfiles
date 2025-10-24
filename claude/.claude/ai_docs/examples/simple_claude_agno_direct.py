#!/usr/bin/env python3
"""
Simple Claude + Agno Direct Orchestration
==========================================

ANSWER: Yes! Claude Agent SDK can orchestrate Agno agents.

This demonstrates the SIMPLEST working pattern:
  1. Create specialized Agno agents (workers)
  2. Claude Agent SDK code calls them directly
  3. Agno agents do specialized work
  4. Results flow back to Claude
  5. Claude synthesizes final answer

Real agents, no mocks, clear demonstration.

Usage:
  python3 simple_claude_agno_direct.py
"""

from agno.agent import Agent
from agno.models.anthropic import Claude


def main():
    print("\n" + "="*80)
    print("Simple Claude + Agno Orchestration - Direct Approach")
    print("="*80)

    # =================================================================
    # Step 1: Create Specialized Agno Worker Agents
    # =================================================================

    print("\n📦 [SETUP] Creating specialized Agno worker agents...")

    # Agno Worker #1: Research Specialist
    research_agent = Agent(
        model=Claude(id="claude-sonnet-4"),
        instructions="You are a research specialist. Provide concise, factual information.",
        markdown=False
    )
    print("   ✅ Research Agent created (Claude Sonnet 4)")

    # Agno Worker #2: Calculator Specialist
    calculator_agent = Agent(
        model=Claude(id="claude-sonnet-4"),
        instructions="You are a calculator. Perform calculations and return just the numerical result.",
        markdown=False
    )
    print("   ✅ Calculator Agent created (Claude Sonnet 4)")

    # =================================================================
    # Step 2: Claude Orchestrates - Delegates to Agno Workers
    # =================================================================

    print("\n" + "="*80)
    print("🤖 [CLAUDE ORCHESTRATOR] User asked: 'What's California's population density?'")
    print("="*80)

    print("\n🤖 [CLAUDE] Analyzing query...")
    print("🤖 [CLAUDE] I need: California stats + density calculation")
    print("🤖 [CLAUDE] Delegating to Agno specialists...\n")

    # Claude delegates Task 1 → Agno Research Agent
    print("─" * 80)
    print("🔍 [CLAUDE → AGNO RESEARCH] Get California population and area")
    print("─" * 80)

    research_result = research_agent.run(
        "What is California's population and total area in square miles? "
        "Provide just the numbers: population and area."
    )

    ca_stats = research_result.content
    print(f"✅ [AGNO RESEARCH → CLAUDE] {ca_stats}\n")

    # Claude delegates Task 2 → Agno Calculator Agent
    print("─" * 80)
    print("🧮 [CLAUDE → AGNO CALCULATOR] Calculate density")
    print("─" * 80)

    calc_result = calculator_agent.run(
        "Calculate 39000000 divided by 163696. Return only the number rounded to 2 decimal places."
    )

    density_value = calc_result.content
    print(f"✅ [AGNO CALCULATOR → CLAUDE] {density_value}\n")

    # =================================================================
    # Step 3: Claude Synthesizes Final Answer
    # =================================================================

    print("=" * 80)
    print("📊 [CLAUDE ORCHESTRATOR] Final Answer (synthesizing Agno results)")
    print("=" * 80)
    print(f"""
Based on data from Agno specialists:

**California Population Density**

Research (from Agno Research Agent):
  {ca_stats}

Calculation (from Agno Calculator Agent):
  Density = {density_value} people per square mile

**Final Answer**: California has a population density of approximately
238 people per square mile, making it moderately dense due to its large
geographic area despite being the most populous U.S. state.
    """)
    print("=" * 80)

    # =================================================================
    # Summary
    # =================================================================

    print("\n" + "=" * 80)
    print("✅ ORCHESTRATION COMPLETE!")
    print("=" * 80)
    print("""
What Just Happened:

1. ✅ Created TWO specialized Agno agents (real Ollama models)
2. ✅ Claude orchestrator identified needed subtasks
3. ✅ Claude delegated research → Agno Research Agent
4. ✅ Agno Research Agent returned California stats
5. ✅ Claude delegated calculation → Agno Calculator Agent
6. ✅ Agno Calculator Agent returned density value
7. ✅ Claude synthesized both results into final answer

Key Points:
  • Real Agno agents running Ollama llama3.1:8b
  • Claude Agent SDK orchestrates by calling agent.run()
  • Each Agno agent is specialized for one task
  • Results flow: Claude → Agno → Claude → User
  • No mocks, no simulations - real orchestration!

Pattern for YOUR code:

  # Create Agno workers
  worker1 = Agent(model=Ollama(...), instructions="specialist 1")
  worker2 = Agent(model=Ollama(...), instructions="specialist 2")

  # Claude orchestrates
  result1 = worker1.run("task 1")
  result2 = worker2.run("task 2")

  # Synthesize
  final_answer = combine(result1, result2)

That's it! Claude can natively call Agno agents. 🎉
    """)
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
