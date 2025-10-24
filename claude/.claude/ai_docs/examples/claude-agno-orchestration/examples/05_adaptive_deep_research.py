#!/usr/bin/env python3
"""
Example 5: Adaptive Deep Research Agent
========================================

Demonstrates the advanced AdaptiveDeepResearchAgent with:
- Adaptive planning strategies (simple/ambiguous/complex)
- Multi-hop reasoning patterns
- Self-reflective mechanisms
- Evidence management
- 4-phase workflow (Discovery → Investigation → Synthesis → Reporting)

This agent is more sophisticated than DeepWebResearcherAgent.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestration import (
    AdaptiveDeepResearchAgent,
    create_adaptive_researcher,
    DirectOrchestrator,
    ResearchOutputManager,
    generate_summary
)


def example_simple_query():
    """Example 1: Simple query with Planning-Only strategy."""
    print("\n" + "="*80)
    print("Example 1: Simple Query (Planning-Only Strategy)")
    print("="*80)
    print()

    agent = AdaptiveDeepResearchAgent()

    query = "What is quantum computing?"

    print(f"Query: {query}")
    print(f"Expected Strategy: PLANNING-ONLY (direct execution)")
    print()

    result = agent.run(query)

    if result.success:
        print(f"✅ Research completed in {result.duration:.2f}s")
        print(f"Output length: {len(result.content):,} chars")
        print(f"\nDetected complexity: {result.metadata.get('complexity', 'unknown')}")
        print(f"\nFirst 500 chars:\n{result.content[:500]}...")
    else:
        print(f"❌ Failed: {result.error}")


def example_ambiguous_query():
    """Example 2: Ambiguous query with Intent-Planning strategy."""
    print("\n" + "="*80)
    print("Example 2: Ambiguous Query (Intent-Planning Strategy)")
    print("="*80)
    print()

    agent = AdaptiveDeepResearchAgent()

    query = "Research AI developments"

    print(f"Query: {query}")
    print(f"Expected Strategy: INTENT-PLANNING (clarification or best interpretation)")
    print()

    result = agent.run(query, complexity="ambiguous")

    if result.success:
        print(f"✅ Research completed in {result.duration:.2f}s")
        print(f"Output length: {len(result.content):,} chars")
        print(f"\nDetected complexity: {result.metadata.get('complexity', 'unknown')}")
        print(f"\nFirst 500 chars:\n{result.content[:500]}...")
    else:
        print(f"❌ Failed: {result.error}")


def example_complex_query():
    """Example 3: Complex query with Unified Planning strategy."""
    print("\n" + "="*80)
    print("Example 3: Complex Query (Unified Planning Strategy)")
    print("="*80)
    print()

    agent = AdaptiveDeepResearchAgent()

    query = """Research the intersection of quantum computing and drug discovery.

Focus on:
1. Current state of quantum computing applications in pharmaceutical research
2. Key breakthroughs and success stories
3. Technical challenges and limitations
4. Timeline for practical deployment
5. Major players and investments

Provide comprehensive analysis with recent data and expert perspectives."""

    print(f"Query: {query[:100]}...")
    print(f"Expected Strategy: UNIFIED PLANNING (present plan, then execute)")
    print()

    result = agent.run(query, complexity="complex", max_hops=3)

    if result.success:
        print(f"✅ Research completed in {result.duration:.2f}s")
        print(f"Output length: {len(result.content):,} chars")
        print(f"\nDetected complexity: {result.metadata.get('complexity', 'unknown')}")
        print(f"Max hops: {result.metadata.get('max_hops', 'unknown')}")
        print(f"\nFirst 800 chars:\n{result.content[:800]}...")
    else:
        print(f"❌ Failed: {result.error}")


def example_self_reflection():
    """Example 4: Research with self-reflection and iteration."""
    print("\n" + "="*80)
    print("Example 4: Self-Reflective Research")
    print("="*80)
    print()

    agent = AdaptiveDeepResearchAgent()

    query = "Analyze the impact of large language models on software development"

    print(f"Query: {query}")
    print(f"Strategy: Self-reflection with min confidence 0.7")
    print(f"Will iterate up to 3 times if confidence is low")
    print()

    result = agent.run_with_reflection(
        query,
        min_confidence=0.7,
        max_iterations=3
    )

    if result.success:
        print(f"✅ Research completed in {result.duration:.2f}s")
        print(f"Output length: {len(result.content):,} chars")
        print(f"\nFinal confidence: {result.metadata.get('final_confidence', 0):.2f}")
        print(f"Iterations: {result.metadata.get('iterations', 0)}")
        print(f"\nFirst 500 chars:\n{result.content[:500]}...")
    else:
        print(f"❌ Failed: {result.error}")


def example_orchestration():
    """Example 5: Using adaptive agent with orchestrator."""
    print("\n" + "="*80)
    print("Example 5: Orchestrated Adaptive Research")
    print("="*80)
    print()

    # Create orchestrator with adaptive agent
    orchestrator = DirectOrchestrator(name="AdaptiveResearchOrch")
    agent = create_adaptive_researcher(
        temperature=0.2,  # Lower for consistency
        max_tokens=15000  # Extended for comprehensive output
    )
    orchestrator.add_agent('adaptive_researcher', agent)

    query = """Research emerging trends in renewable energy storage technologies for 2025.

Include:
- Battery technology advances
- Alternative storage methods (hydrogen, thermal, etc.)
- Cost trends and economics
- Environmental impact
- Market leaders and innovations"""

    print(f"Query: {query[:100]}...")
    print(f"Using DirectOrchestrator with AdaptiveDeepResearchAgent")
    print()

    result = orchestrator.run(query)

    if result.success:
        print(f"✅ Orchestration completed in {result.duration:.2f}s")

        # Show artifacts
        if result.artifacts:
            print(f"\n📊 Execution Artifacts:")
            print(f"   Workflow: {result.artifacts.workflow_type}")
            print(f"   Agents: {result.artifacts.total_agents_used}")
            print(f"   Duration: {result.artifacts.total_duration:.2f}s")

            for agent_artifact in result.artifacts.agent_artifacts:
                print(f"\n   Agent: {agent_artifact.agent_name}")
                print(f"   ├─ Model: {agent_artifact.model_id}")
                print(f"   ├─ Input: {agent_artifact.input_prompt[:100]}...")
                print(f"   ├─ Output: {len(agent_artifact.output_content):,} chars")
                print(f"   └─ Duration: {agent_artifact.execution_time:.2f}s")

        print(f"\nFirst 500 chars of report:\n{result.final_answer[:500]}...")
    else:
        print(f"❌ Failed: {result.error}")


def example_save_with_output_manager():
    """Example 6: Full research workflow with output management."""
    print("\n" + "="*80)
    print("Example 6: Complete Research Workflow")
    print("="*80)
    print()

    current_date = datetime.now().strftime("%B %d, %Y")
    run_start = datetime.now()

    # Initialize components
    output_manager = ResearchOutputManager(base_dir="outputs")
    orchestrator = DirectOrchestrator(name="RenewableEnergyResearch")
    agent = AdaptiveDeepResearchAgent()
    orchestrator.add_agent('adaptive_researcher', agent)

    query = f"""As of {current_date}, research the state of fusion energy development.

Provide institutional-grade analysis covering:
1. Recent breakthrough announcements
2. Major projects and timelines (ITER, NIF, private ventures)
3. Technical challenges remaining
4. Investment landscape
5. Commercial viability timeline
6. Competitive landscape
7. Geopolitical implications"""

    print(f"Date: {current_date}")
    print(f"Query: {query[:150]}...")
    print()
    print("🔍 Executing adaptive deep research with full output management...")
    print()

    result = orchestrator.run(query)

    if result.success:
        print(f"✅ Research completed in {result.duration:.2f}s")

        # Prepare metadata
        run_duration = (datetime.now() - run_start).total_seconds()
        metadata = {
            'research_date': current_date,
            'run_timestamp': run_start.isoformat(),
            'duration': result.duration,
            'total_run_duration': run_duration,
            'success': result.success,
            'agent_type': 'AdaptiveDeepResearchAgent',
            'agents_used': result.metadata.get('agent_count', 0),
            'workflow_type': result.metadata.get('workflow_type', 'unknown'),
        }

        # Convert artifacts
        artifacts_dict = result.artifacts.to_dict() if result.artifacts else None

        # Generate summary
        summary = generate_summary(result, run_duration)

        # Save outputs
        run_dir = output_manager.save_full_run(
            run_name="fusion_energy_research",
            query=query,
            report_content=result.final_answer,
            artifacts_data=artifacts_dict,
            metadata=metadata,
            summary=summary
        )

        print(f"\n💾 Research outputs saved to:")
        print(f"   {run_dir.absolute()}")
        print(f"\n📁 Files created:")
        print(f"   - README.md")
        print(f"   - report.md ({len(result.final_answer):,} chars)")
        print(f"   - artifacts.json")
        print(f"   - metadata.json")
        print(f"   - query.txt")
        print(f"   - summary.txt")

    else:
        print(f"❌ Failed: {result.error}")


def compare_agents():
    """Example 7: Compare standard vs adaptive agent."""
    print("\n" + "="*80)
    print("Example 7: Comparing Standard vs Adaptive Agent")
    print("="*80)
    print()

    from orchestration import DeepWebResearcherAgent

    query = "Research the impact of climate change on Arctic ecosystems"

    print(f"Query: {query}")
    print()

    # Standard agent
    print("Running DeepWebResearcherAgent (standard)...")
    standard_agent = DeepWebResearcherAgent()
    standard_result = standard_agent.run(query)

    # Adaptive agent
    print("Running AdaptiveDeepResearchAgent (adaptive)...")
    adaptive_agent = AdaptiveDeepResearchAgent()
    adaptive_result = adaptive_agent.run(query)

    # Compare results
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)
    print()

    comparison = [
        ("Agent Type", "DeepWebResearcherAgent", "AdaptiveDeepResearchAgent"),
        ("Success",
         "✅" if standard_result.success else "❌",
         "✅" if adaptive_result.success else "❌"),
        ("Duration",
         f"{standard_result.duration:.2f}s",
         f"{adaptive_result.duration:.2f}s"),
        ("Output Length",
         f"{len(standard_result.content):,} chars",
         f"{len(adaptive_result.content):,} chars"),
        ("Complexity Detection",
         "N/A",
         adaptive_result.metadata.get('complexity', 'N/A')),
        ("Max Hops",
         "N/A",
         str(adaptive_result.metadata.get('max_hops', 'N/A'))),
        ("Strategy Used",
         "Fixed institutional format",
         f"{adaptive_result.metadata.get('complexity', 'N/A')} strategy"),
    ]

    # Print comparison table
    print(f"{'Metric':<25} | {'Standard':<30} | {'Adaptive':<30}")
    print("-" * 90)
    for metric, standard, adaptive in comparison:
        print(f"{metric:<25} | {standard:<30} | {adaptive:<30}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("ADAPTIVE DEEP RESEARCH AGENT - COMPREHENSIVE EXAMPLES")
    print("="*80)

    # Run examples
    example_simple_query()
    example_ambiguous_query()
    example_complex_query()
    example_self_reflection()
    example_orchestration()
    example_save_with_output_manager()
    compare_agents()

    print("\n" + "="*80)
    print("✅ All Examples Complete!")
    print("="*80)
    print()
    print("Key Differences:")
    print("- AdaptiveDeepResearchAgent detects query complexity")
    print("- Uses appropriate strategy (Planning-Only/Intent/Unified)")
    print("- Implements multi-hop reasoning (up to 5 levels)")
    print("- Self-reflection and iteration capabilities")
    print("- More structured 4-phase workflow")
    print("- Enhanced evidence management")
    print()


if __name__ == "__main__":
    main()
