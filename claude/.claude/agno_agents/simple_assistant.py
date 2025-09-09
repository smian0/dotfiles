#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["agno>=1.7.0", "ollama>=0.5.3", "click>=8.1.0"]
# ///

import click
from agno.agent import Agent
from agno.models.ollama import Ollama

agent = Agent(
    model=Ollama(id="llama3.1:8b"),
    instructions="""You are a helpful assistant that can answer questions and help with various tasks. 
    You can provide information, explain concepts, help with problem-solving, and assist with 
    general knowledge questions. Be friendly, concise, and practical in your responses."""
)

@click.command()
@click.option('-p', '--prompt', help='Single prompt for non-interactive mode')
def main(prompt):
    if prompt:
        print(agent.run(prompt).content)
    else:
        print("💬 Interactive mode - type 'exit' to quit")
        while True:
            try:
                user_input = input("You: ").strip().strip('\'"')
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    break
                if user_input:
                    print(f"🤖 {agent.run(user_input).content}")
            except (KeyboardInterrupt, EOFError):
                break

if __name__ == "__main__":
    main()