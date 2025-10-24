#!/usr/bin/env python3
"""
Example 1: Simple Calculation
==============================

Demonstrates the simplest multi-agent orchestration pattern.

Scenario:
  User asks: "What's California's population density?"

  Orchestration flow:
    1. ResearchAgent finds California's population and area
    2. CalculatorAgent computes density (population / area)
    3. Orchestrator synthesizes final answer

This shows:
  ✓ Basic agent composition
  ✓ Sequential execution
  ✓ Result synthesis
  ✓ Real Agno agents (no mocks!)

Usage:
  python examples/01_simple_calculation.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestration import DirectOrchestrator, ResearchAgent, CalculatorAgent


def main():
    print("\n" + "="*80)
    print("Example 1: Simple Multi-Agent Calculation")
    print("="*80)

    print("\n📦 Setup: Creating agents and orchestrator...\n")

    # Create orchestrator
    orchestrator = DirectOrchestrator(name="SimpleCalculation")

    # Create and add specialized agents
    orchestrator.add_agent('research', ResearchAgent())
    orchestrator.add_agent('calculator', CalculatorAgent())

    print(f"✅ Orchestrator created with {len(orchestrator.agent_names)} agents:")
    for name in orchestrator.agent_names:
        agent = orchestrator.get_agent(name)
        print(f"   • {name}: {agent.__class__.__name__}")

    # Test questions
    questions = [
        "What's the population density of California?",
        "What's the population density of Tokyo?",
    ]

    for i, question in enumerate(questions, 1):
        print("\n" + "="*80)
        print(f"Question {i}: {question}")
        print("="*80)

        # Execute orchestration
        result = orchestrator.run(question)

        if result.success:
            print(f"\n✅ Success! Completed in {result.duration:.2f}s")
            print(f"\n📊 Execution Steps ({len(result.steps)}):")
            for j, step in enumerate(result.steps, 1):
                print(f"   {j}. {step['agent']}: {step['duration']:.2f}s")
                if step['content_preview']:
                    print(f"      Preview: {step['content_preview']}")

            print(f"\n🎯 Final Answer:")
            print("─" * 80)
            print(result.final_answer)
            print("─" * 80)
        else:
            print(f"\n❌ Failed: {result.error}")

    # Show orchestrator statistics
    print("\n" + "="*80)
    print("📊 Orchestrator Statistics")
    print("="*80)

    stats = orchestrator.stats
    print(f"Total executions: {stats['total_executions']}")
    print(f"Successful: {stats['successful_executions']}")
    print(f"Success rate: {stats['success_rate']:.1%}")

    # Show agent statistics
    print("\n📈 Agent Statistics:")
    for name in orchestrator.agent_names:
        agent = orchestrator.get_agent(name)
        agent_stats = agent.stats
        print(f"\n  {name}:")
        print(f"    Executions: {agent_stats['execution_count']}")
        print(f"    Avg duration: {agent_stats['average_duration']:.2f}s")

    print("\n" + "="*80)
    print("✅ Example Complete!")
    print("="*80)
    print("""
What happened:
  1. Created DirectOrchestrator with 2 specialized agents
  2. ResearchAgent found population and area data
  3. CalculatorAgent computed density
  4. Orchestrator synthesized coherent final answer
  5. All using real Agno agents with Claude models!

Key Takeaways:
  • Agents are independent, reusable modules
  • Orchestrator handles coordination and synthesis
  • Sequential execution with automatic flow
  • Production-ready error handling and metrics

Next: Try examples/02_code_review_system.py for parallel execution!
    """)


if __name__ == "__main__":
    main()
