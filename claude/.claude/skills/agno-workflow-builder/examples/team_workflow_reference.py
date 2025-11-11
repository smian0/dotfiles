#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "agno",
# ]
# ///
"""
Reference Example: Team in Workflow (Verified Working)

Simplest possible demonstration of using a Team within a Workflow.
This example has been tested end-to-end and verified to work.

Pattern: Workflow with Team step for collaborative research.
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

from agno.agent import Agent
from agno.team import Team
from agno.workflow import Workflow, Step
from agno.models.ollama import Ollama


# Step 1: Create two specialist agents
researcher_a = Agent(
    name="Researcher A",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Research technical aspects of the topic",
    instructions=[
        "Focus on technical details and implementation.",
        "Provide 2-3 key technical points.",
        "Keep response concise (3-4 sentences).",
    ],
)

researcher_b = Agent(
    name="Researcher B",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Research business and market aspects",
    instructions=[
        "Focus on business value and market trends.",
        "Provide 2-3 key business points.",
        "Keep response concise (3-4 sentences).",
    ],
)


# Step 2: Create collaborative research team
research_team = Team(
    name="Research Team",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    members=[researcher_a, researcher_b],
    instructions=[
        "You coordinate research on the given topic.",
        "First, ask Researcher A for technical insights.",
        "Then, ask Researcher B for business insights.",
        "Finally, provide a brief 2-3 sentence synthesis.",
    ],
    show_members_responses=True,
)


# Step 3: Create summarizer agent
summarizer = Agent(
    name="Summarizer",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Create executive summary from research",
    instructions=[
        "Read the research team's findings.",
        "Create a clear 3-4 sentence executive summary.",
        "Start with '## Executive Summary'",
    ],
)


# Step 4: Create workflow
simple_workflow = Workflow(
    name="Team Research Workflow",
    description="Collaborative research followed by summarization",
    steps=[
        Step(
            name="Research Phase",
            team=research_team,
            description="Team collaborates on research",
        ),
        Step(
            name="Summarize",
            agent=summarizer,
            description="Create executive summary",
        ),
    ],
)


# Step 5: Test execution
if __name__ == "__main__":
    print("="*80)
    print("Testing Team in Workflow Pattern")
    print("="*80 + "\n")

    topic = "AI agent frameworks"
    print(f"Topic: {topic}\n")

    try:
        result = simple_workflow.run(
            input=topic,
            stream=False,  # stream=True returns generator, False returns result object
        )

        if result and result.content:
            print("\n" + "="*80)
            print("✅ Workflow completed successfully")
            print("="*80 + "\n")
            print(result.content)
        else:
            print("❌ Workflow returned no content")

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
