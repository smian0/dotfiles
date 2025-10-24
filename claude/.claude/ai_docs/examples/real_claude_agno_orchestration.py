#!/usr/bin/env python3
"""
Real Claude Agent SDK + Agno Orchestration
===========================================

REAL working example with actual agents (no mocks!).

Architecture:
  Claude Agent SDK (Master Orchestrator)
      ↓
  Custom MCP Tools
      ↓
  Real Agno Agents with Ollama Models

Use Case: Code Review System
  - User submits code for review
  - Claude orchestrates two Agno specialists:
    1. Code Analyzer (checks quality, bugs, improvements)
    2. Documentation Checker (validates docs, comments)
  - Claude synthesizes comprehensive review

Usage:
  python3 real_claude_agno_orchestration.py
"""

import asyncio
from claude_agent_sdk import tool, query, ClaudeAgentOptions, create_sdk_mcp_server, AssistantMessage, TextBlock
from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================================
# Real Agno Worker Agents (Specialized)
# ============================================================================

def create_code_analyzer_agent():
    """
    Real Agno agent: Specialized in code quality analysis
    Uses Ollama llama3.1:8b for analysis
    """
    return Agent(
        model=Ollama(id="llama3.1:8b"),
        instructions="""You are a senior code reviewer specialized in finding bugs, security issues, and suggesting improvements.

When analyzing code:
1. Look for potential bugs or errors
2. Check for security vulnerabilities
3. Suggest performance improvements
4. Identify code smells or anti-patterns
5. Rate the overall code quality (1-10)

Be concise but thorough. Focus on actionable feedback.""",
        markdown=True,
        show_tool_calls=False
    )


def create_documentation_checker_agent():
    """
    Real Agno agent: Specialized in documentation quality
    Uses Ollama llama3.1:8b for documentation review
    """
    return Agent(
        model=Ollama(id="llama3.1:8b"),
        instructions="""You are a documentation specialist who reviews code documentation quality.

When checking documentation:
1. Verify function/class docstrings exist and are clear
2. Check if comments explain WHY, not just WHAT
3. Look for missing or outdated documentation
4. Assess if code is self-documenting
5. Rate documentation quality (1-10)

Be specific about what's missing or needs improvement.""",
        markdown=True,
        show_tool_calls=False
    )


# ============================================================================
# Bridge Tools: Claude SDK → Agno Agents
# ============================================================================

@tool(
    "analyze_code_quality",
    "Delegates code quality analysis to specialized Agno agent. Returns bugs, improvements, and quality rating.",
    {"code": "string - The code to analyze"}
)
async def analyze_code_quality(args):
    """Bridge tool: Claude delegates code analysis to Agno specialist"""
    code = args["code"]

    print(f"\n{'='*80}")
    print("🔍 [AGNO CODE ANALYZER] Starting analysis...")
    print(f"{'='*80}")

    # Create and run real Agno agent
    analyzer = create_code_analyzer_agent()
    result = analyzer.run(f"Analyze this code:\n\n```python\n{code}\n```")

    analysis = result.content

    print(f"\n✅ [AGNO CODE ANALYZER] Analysis complete")
    print(f"{'='*80}\n")

    return {
        "content": [{
            "type": "text",
            "text": analysis
        }]
    }


@tool(
    "check_documentation_quality",
    "Delegates documentation review to specialized Agno agent. Returns documentation assessment and suggestions.",
    {"code": "string - The code to check documentation for"}
)
async def check_documentation_quality(args):
    """Bridge tool: Claude delegates documentation checking to Agno specialist"""
    code = args["code"]

    print(f"\n{'='*80}")
    print("📚 [AGNO DOC CHECKER] Starting documentation review...")
    print(f"{'='*80}")

    # Create and run real Agno agent
    doc_checker = create_documentation_checker_agent()
    result = doc_checker.run(f"Review documentation quality:\n\n```python\n{code}\n```")

    doc_review = result.content

    print(f"\n✅ [AGNO DOC CHECKER] Review complete")
    print(f"{'='*80}\n")

    return {
        "content": [{
            "type": "text",
            "text": doc_review
        }]
    }


# ============================================================================
# Claude Orchestrator Setup
# ============================================================================

def create_code_review_orchestrator():
    """
    Creates Claude Agent SDK orchestrator with Agno worker tools
    """

    # Wrap Agno bridge tools in MCP server
    agno_workers = create_sdk_mcp_server(
        name="agno_code_reviewers",
        version="1.0.0",
        tools=[analyze_code_quality, check_documentation_quality]
    )

    options = ClaudeAgentOptions(
        system_prompt="""You are a master code review orchestrator that delegates specialized reviews to Agno agents.

You have two expert Agno agents available:
1. analyze_code_quality - Expert in finding bugs, security issues, and improvements
2. check_documentation_quality - Expert in assessing documentation quality

When conducting a code review:
1. First, delegate code quality analysis to analyze_code_quality
2. Then, delegate documentation review to check_documentation_quality
3. Synthesize both reviews into a comprehensive final assessment

Your synthesis should:
- Summarize key findings from both Agno agents
- Prioritize critical issues
- Provide an overall recommendation (Approve/Request Changes/Reject)
- Be concise but actionable

IMPORTANT: You MUST use BOTH Agno agents before providing your final review.""",
        mcp_servers={"agno_workers": agno_workers},
        permission_mode='acceptEdits'
    )

    return options


# ============================================================================
# Demo: Real Code Review Orchestration
# ============================================================================

async def conduct_code_review(code: str, description: str = ""):
    """
    Conduct a real code review using Claude orchestrating Agno agents
    """

    print("\n" + "="*80)
    print("🚀 REAL CODE REVIEW: Claude Orchestrating Agno Agents")
    print("="*80)

    if description:
        print(f"\n📋 Code Description: {description}")

    print(f"\n📝 Code to Review:")
    print("="*80)
    print(code)
    print("="*80)

    options = create_code_review_orchestrator()

    print("\n🤖 [CLAUDE ORCHESTRATOR] Starting code review workflow...")
    print("   Claude will delegate to Agno specialists and synthesize results\n")

    # Claude orchestrates the review
    review_request = f"""Please conduct a comprehensive code review of this code:

```python
{code}
```

Follow the workflow:
1. Use analyze_code_quality to get quality assessment
2. Use check_documentation_quality to get documentation review
3. Synthesize both into final recommendation"""

    final_review = ""
    async for message in query(prompt=review_request, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    final_review += block.text

    print("\n" + "="*80)
    print("📊 [CLAUDE ORCHESTRATOR] FINAL CODE REVIEW")
    print("="*80)
    print(final_review)
    print("="*80 + "\n")


# ============================================================================
# Test Cases
# ============================================================================

async def demo_simple_function():
    """Demo 1: Review a simple function with issues"""

    code = '''
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)
'''

    await conduct_code_review(code, "Simple average calculator")


async def demo_complex_class():
    """Demo 2: Review a more complex class"""

    code = '''
class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, username, password):
        """Add a new user"""
        self.users[username] = password
        return True

    def authenticate(self, username, password):
        if username in self.users:
            if self.users[username] == password:
                return True
        return False

    def get_all_users(self):
        return list(self.users.keys())
'''

    await conduct_code_review(code, "User management system")


# ============================================================================
# Main
# ============================================================================

async def main():
    print("\n" + "="*80)
    print("REAL Claude Agent SDK + Agno Orchestration Demo")
    print("="*80)
    print("\nArchitecture:")
    print("  Claude Agent SDK (Master) → MCP Tools → Real Agno Agents (Ollama)")
    print("\nUse Case:")
    print("  Comprehensive code review with specialized Agno workers")
    print("="*80)

    # Run demo 1
    print("\n\n" + "="*80)
    print("DEMO 1: Simple Function Review")
    print("="*80)
    await demo_simple_function()

    # Run demo 2
    print("\n\n" + "="*80)
    print("DEMO 2: Complex Class Review")
    print("="*80)
    await demo_complex_class()

    # Summary
    print("\n" + "="*80)
    print("✅ REAL ORCHESTRATION COMPLETE!")
    print("="*80)
    print("\nWhat Happened:")
    print("  1. ✅ Claude Agent SDK acted as master orchestrator")
    print("  2. ✅ Two real Agno agents (Ollama llama3.1:8b) did specialized work:")
    print("      • Code Analyzer: Found bugs and improvements")
    print("      • Doc Checker: Assessed documentation quality")
    print("  3. ✅ Claude synthesized both Agno results into final review")
    print("\nNo Mocks!")
    print("  • Real Agno agents with real Ollama models")
    print("  • Real Claude Agent SDK orchestration")
    print("  • Real code analysis and review")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
