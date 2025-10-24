"""
Test workflow with sub-agent delegation to verify hierarchy visualization.
"""
import asyncio
from claude import Claude
from helpers.workflow_helpers import setup_workflow_hooks, log_hook_event


async def main():
    # Setup hooks
    log_file = setup_workflow_hooks("subagent_test")

    client = Claude()

    # Create a task that will spawn sub-agents
    messages = [{
        "role": "user",
        "content": "Please research two topics in parallel using sub-agents: 1) Latest Python 3.14 features, and 2) Latest JavaScript ES2024 features. Keep each research task brief (2-3 paragraphs)."
    }]

    print(f"Starting workflow with sub-agent delegation...")
    print(f"Log file: {log_file}")

    response = await client.messages.create_async(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=messages
    )

    print(f"\n✅ Workflow completed!")
    print(f"📄 Full logs in: {log_file}")
    print(f"📊 Transcript in: ~/.claude/projects/.../session-id.jsonl")


if __name__ == "__main__":
    asyncio.run(main())
