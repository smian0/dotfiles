#!/usr/bin/env python3
"""
Custom Research: Polymarket Ecosystem Development
==================================================

Research query on Polymarket with current date context.
Date: October 13, 2025
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestration import DeepWebResearcherAgent, DirectOrchestrator, ResearchOutputManager, generate_summary


def main():
    # Get current date
    current_date = datetime.now().strftime("%B %d, %Y")
    run_start = datetime.now()

    print("\n" + "="*80)
    print("Polymarket Ecosystem Development Research")
    print("="*80)
    print(f"Research Date: {current_date}")
    print("="*80)

    # Initialize output manager
    output_manager = ResearchOutputManager(base_dir="outputs")

    # Create orchestrator with deep researcher
    print("\n📦 Setup: Creating Orchestration System...\n")
    orchestrator = DirectOrchestrator(name="PolymarketResearch")
    researcher = DeepWebResearcherAgent()
    orchestrator.add_agent('deep_web_researcher', researcher)

    print(f"✅ Orchestrator created: {orchestrator.name}")
    print(f"✅ Agent registered: {researcher.config.name}")
    print(f"   Model: {researcher.config.model_id}")
    print(f"   Max tokens: {researcher.config.max_tokens}")

    # Research query with date context
    query = f"""Research the Polymarket ecosystem development as of {current_date}.

Focus on:
1. Recent platform developments and new features
2. Trading volume and user growth trends
3. Regulatory developments affecting prediction markets
4. Competitive landscape (other prediction market platforms)
5. Technical infrastructure and blockchain integration
6. Notable markets and trading activity
7. Future roadmap and planned features

Provide a comprehensive institutional-grade investment research report with quantitative data, risk assessment, and strategic recommendations."""

    print(f"\n📋 Query:\n{query}\n")
    print("="*80)
    print("\n🔍 Researching Polymarket ecosystem... (this may take 15-30 seconds)\n")

    # Execute research via orchestrator for full artifact tracking
    result = orchestrator.run(query)

    if result.success:
        print(f"✅ Research completed in {result.duration:.2f}s\n")
        print("=" * 80)
        print("📊 INSTITUTIONAL-GRADE RESEARCH REPORT")
        print("=" * 80)
        print(result.final_answer)
        print("\n" + "=" * 80)

        # Show detailed artifacts
        if result.artifacts:
            print("\n" + "="*80)
            print("🔍 DETAILED EXECUTION ARTIFACTS")
            print("="*80)

            artifacts = result.artifacts

            print(f"\n📋 Orchestration Summary:")
            print(f"   Orchestrator: {artifacts.orchestrator_name}")
            print(f"   Workflow Type: {artifacts.workflow_type}")
            print(f"   Total Duration: {artifacts.total_duration:.2f}s")
            print(f"   Agents Used: {artifacts.total_agents_used}")

            print(f"\n🤖 Agent Execution Details:")
            for i, agent_artifact in enumerate(artifacts.agent_artifacts, 1):
                print(f"\n   Agent {i}: {agent_artifact.agent_name}")
                print(f"   ├─ Type: {agent_artifact.agent_type}")
                print(f"   ├─ Model: {agent_artifact.model_id}")
                print(f"   ├─ Temperature: {agent_artifact.temperature}")
                print(f"   ├─ Max Tokens: {agent_artifact.max_tokens}")
                print(f"   ├─ Input Length: {len(agent_artifact.input_prompt)} chars")
                print(f"   ├─ Output Length: {len(agent_artifact.output_content)} chars")
                print(f"   ├─ Execution Time: {agent_artifact.execution_time:.2f}s")
                print(f"   ├─ Success: {'✅' if agent_artifact.success else '❌'}")
                print(f"   └─ Timestamp: {agent_artifact.timestamp}")

            print(f"\n📊 Orchestration Metadata:")
            meta = artifacts.orchestration_metadata
            print(f"   Task (preview): {meta.get('task', '')[:100]}...")
            print(f"   Start Time: {meta.get('start_time')}")
            print(f"   End Time: {meta.get('end_time')}")
            print(f"   Agent Sequence: {' → '.join(meta.get('agent_sequence', []))}")

            print("\n" + "="*80)

        # Show agent stats
        stats = researcher.stats
        print(f"\n📈 Agent Statistics:")
        print(f"   Total queries: {stats['execution_count']}")
        print(f"   Total time: {stats['total_duration']:.2f}s")
        print(f"   Average time: {stats['average_duration']:.2f}s")

    else:
        print(f"❌ Research failed: {result.error}")

    # Save outputs to timestamped directory
    print("\n" + "="*80)
    print("💾 SAVING RESEARCH OUTPUTS")
    print("="*80)

    if result.success:
        # Prepare metadata
        run_duration = (datetime.now() - run_start).total_seconds()
        metadata = {
            'research_date': current_date,
            'run_timestamp': run_start.isoformat(),
            'duration': result.duration,
            'total_run_duration': run_duration,
            'success': result.success,
            'agents_used': result.metadata.get('agent_count', 0),
            'workflow_type': result.metadata.get('workflow_type', 'unknown'),
            'orchestrator': result.metadata.get('orchestrator', 'unknown')
        }

        # Convert artifacts to dict for JSON serialization
        artifacts_dict = None
        if result.artifacts:
            artifacts_dict = result.artifacts.to_dict()

        # Generate summary
        summary = generate_summary(result, run_duration)

        # Save all outputs
        run_dir = output_manager.save_full_run(
            run_name="polymarket_research",
            query=query,
            report_content=result.final_answer,
            artifacts_data=artifacts_dict,
            metadata=metadata,
            summary=summary
        )

        print(f"\n✅ Research outputs saved to:")
        print(f"   {run_dir.absolute()}")
        print(f"\n📁 Files created:")
        print(f"   - README.md          (Index and overview)")
        print(f"   - report.md          (Full research report)")
        print(f"   - artifacts.json     (Execution details)")
        print(f"   - metadata.json      (Run metadata)")
        print(f"   - query.txt          (Original query)")
        print(f"   - summary.txt        (Quick summary)")

    print("\n" + "="*80)
    print("✅ Research Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
