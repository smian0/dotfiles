# Getting Started with Claude + Agno Orchestration

**Complete guide to using the multi-agent orchestration system**

---

## 📖 Table of Contents

1. [What You've Built](#what-youve-built)
2. [Quick Start](#quick-start)
3. [Understanding the Architecture](#understanding-the-architecture)
4. [Using Individual Agents](#using-individual-agents)
5. [Building Orchestrations](#building-orchestrations)
6. [Running Examples](#running-examples)
7. [Testing](#testing)
8. [Extending the System](#extending-the-system)
9. [Next Steps](#next-steps)

---

## 🎯 What You've Built

A **production-ready multi-agent orchestration framework** where:

- **Claude Agent SDK** acts as the master orchestrator
- **Agno agents** are specialized workers (research, calculation, analysis, etc.)
- **Orchestrators** coordinate multiple agents into powerful workflows
- **Everything is testable, modular, and extensible**

**Key Achievement**: Demonstrated that Claude Agent SDK can orchestrate Agno agents through simple Python function calls!

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd claude-agno-orchestration
pip install -r requirements.txt
```

### 2. Run Your First Example

```bash
python examples/01_simple_calculation.py
```

**Output**:
```
✅ Success! Completed in 4.25s

🎯 Final Answer:
────────────────────────────────────────────────────────────────────────────────
Answer: 238.25 people per square mile

Details:
- Research: California population: 39,236,000; Area: 163,696 sq mi
- Calculation: 238.25

This answers: "What's California's population density?"
────────────────────────────────────────────────────────────────────────────────
```

### 3. Explore More Examples

```bash
python examples/02_deep_web_research.py
```

---

## 🏗️ Understanding the Architecture

### Component Hierarchy

```
User Query
    ↓
DirectOrchestrator
    ├─→ ResearchAgent (Agno)
    │     ↓
    │   Claude Model
    │     ↓
    │   Result
    │
    ├─→ CalculatorAgent (Agno)
    │     ↓
    │   Claude Model
    │     ↓
    │   Result
    │
    ↓
Synthesis
    ↓
Final Answer
```

### File Organization

```
src/orchestration/
├── agents/               # Individual AI workers
│   ├── base.py           # Base class with error handling, metrics
│   ├── research.py       # Finds facts and data
│   ├── calculator.py     # Performs calculations
│   ├── code_analyzer.py  # Analyzes code quality
│   └── deep_web_researcher.py  # Comprehensive research
│
└── orchestrators/        # Agent coordination
    ├── base.py           # Base orchestrator class
    └── direct.py         # Direct function call pattern
```

### Key Classes

#### BaseAgent
**Purpose**: Standard interface for all agents

**Provides**:
- Input validation
- Error handling
- Execution metrics
- Logging

**Usage**:
```python
class MyAgent(BaseAgent):
    def _default_config(self) -> AgentConfig:
        return AgentConfig(name="MyAgent", ...)

    def _create_agent(self) -> Agent:
        return Agent(model=Claude(...), instructions="...")
```

#### BaseOrchestrator
**Purpose**: Coordinate multiple agents

**Provides**:
- Agent management (add, remove, get)
- Execution coordination
- Result synthesis
- Statistics tracking

**Usage**:
```python
orch = DirectOrchestrator()
orch.add_agent('agent1', Agent1())
orch.add_agent('agent2', Agent2())
result = orch.run("task")
```

---

## 🤖 Using Individual Agents

### ResearchAgent

**When to use**: Finding facts, statistics, or general information

```python
from orchestration import ResearchAgent

agent = ResearchAgent()
result = agent.run("What is the capital of France?")

print(result.content)    # "Paris"
print(result.duration)   # 1.85 (seconds)
print(result.success)    # True
```

### CalculatorAgent

**When to use**: Mathematical calculations

```python
from orchestration import CalculatorAgent

agent = CalculatorAgent()
result = agent.run("Calculate 39000000 / 163696")

print(result.content)  # "238.25"
```

### CodeAnalyzerAgent

**When to use**: Code reviews, bug finding, quality analysis

```python
from orchestration import CodeAnalyzerAgent

agent = CodeAnalyzerAgent()
code = '''
def divide(a, b):
    return a / b
'''

result = agent.run(f"Analyze this code:\n{code}")
print(result.content)  # Detailed analysis with issues and ratings
```

### DeepWebResearcherAgent

**When to use**: Comprehensive research requiring multiple sources

```python
from orchestration import DeepWebResearcherAgent

agent = DeepWebResearcherAgent()
result = agent.run("Research quantum computing breakthroughs in 2024")

print(result.content)  # Structured research report
```

---

## 🎭 Building Orchestrations

### Pattern 1: Simple Sequential

```python
from orchestration import DirectOrchestrator, ResearchAgent, CalculatorAgent

# Setup
orch = DirectOrchestrator()
orch.add_agent('research', ResearchAgent())
orch.add_agent('calculator', CalculatorAgent())

# Execute - orchestrator handles the flow automatically
result = orch.run("What's the population density of California?")

print(result.final_answer)
print(f"Steps: {len(result.steps)}")
print(f"Duration: {result.duration:.2f}s")
```

### Pattern 2: Custom Workflow

```python
def my_workflow(orch, task, **kwargs):
    """Custom orchestration logic"""

    # Step 1: Research
    research_result = orch.get_agent('research').run(task)

    # Step 2: Analyze
    analysis_prompt = f"Analyze this data: {research_result.content}"
    analysis_result = orch.get_agent('analyzer').run(analysis_prompt)

    # Synthesize
    final = f"Research: {research_result.content}\n\nAnalysis: {analysis_result.content}"

    return [research_result, analysis_result], final

# Setup
orch = DirectOrchestrator()
orch.add_agent('research', ResearchAgent())
orch.add_agent('analyzer', CodeAnalyzerAgent())
orch.set_workflow(my_workflow)

# Execute custom workflow
result = orch.run("Research Python and analyze its design")
```

### Pattern 3: Conditional Logic

```python
def conditional_workflow(orch, task, **kwargs):
    """Workflow with conditional agent selection"""

    # Always start with research
    research = orch.get_agent('research').run(task)

    # Conditionally use calculator based on content
    if any(word in research.content.lower() for word in ['number', 'calculate', 'divide']):
        calc = orch.get_agent('calculator').run(f"Calculate from: {research.content}")
        return [research, calc], f"Research: {research.content}\nCalculation: {calc.content}"

    return [research], research.content

# Setup and execute
orch = DirectOrchestrator()
orch.add_agent('research', ResearchAgent())
orch.add_agent('calculator', CalculatorAgent())
orch.set_workflow(conditional_workflow)

result = orch.run("What's 50% of California's population?")
```

---

## 🎬 Running Examples

### Example 1: Simple Calculation

```bash
python examples/01_simple_calculation.py
```

**What it demonstrates**:
- Basic orchestration
- Research → Calculate pattern
- Result synthesis
- Statistics tracking

### Example 2: Deep Web Research

```bash
python examples/02_deep_web_research.py
```

**What it demonstrates**:
- Advanced single-agent use
- Structured research reports
- Extended methods (`research_with_sources()`)
- Extensibility points for real web search

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/unit/test_agents.py
```

### Run with Coverage

```bash
pytest --cov=src tests/
```

### Test Examples

**Test individual agent**:
```python
# In tests/unit/test_agents.py
def test_research_agent():
    agent = ResearchAgent()
    result = agent.run("What is Python?")

    assert result.success
    assert "programming" in result.content.lower()
```

**Test orchestration**:
```python
# In tests/integration/test_workflows.py
def test_simple_orchestration():
    orch = DirectOrchestrator()
    orch.add_agent('research', ResearchAgent())

    result = orch.run("What is AI?")

    assert result.success
    assert len(result.steps) > 0
```

---

## 🔧 Extending the System

### Adding a New Agent

**Step 1: Create agent file**

```python
# src/orchestration/agents/translator.py
from agno.agent import Agent
from agno.models.anthropic import Claude
from .base import BaseAgent, AgentConfig

class TranslatorAgent(BaseAgent):
    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="TranslatorAgent",
            model_id="claude-sonnet-4",
            instructions="You are a translator. Translate text accurately.",
            temperature=0.3,
            max_tokens=2000
        )

    def _create_agent(self) -> Agent:
        return Agent(
            model=Claude(id=self.config.model_id),
            instructions=self.config.instructions
        )

    def validate_input(self, prompt: str) -> tuple[bool, str | None]:
        is_valid, error = super().validate_input(prompt)
        if not is_valid:
            return is_valid, error

        # Custom validation
        if len(prompt.split()) < 3:
            return False, "Translation input too short"

        return True, None
```

**Step 2: Export from `__init__.py`**

```python
# src/orchestration/agents/__init__.py
from .translator import TranslatorAgent

__all__ = [
    # ... existing exports
    'TranslatorAgent',
]
```

**Step 3: Use it**

```python
from orchestration import TranslatorAgent

agent = TranslatorAgent()
result = agent.run("Translate 'Hello world' to Spanish")
print(result.content)  # "Hola mundo"
```

### Adding a New Orchestration Pattern

**Step 1: Create orchestrator file**

```python
# src/orchestration/orchestrators/parallel.py
from concurrent.futures import ThreadPoolExecutor
from .base import BaseOrchestrator, OrchestrationResult

class ParallelOrchestrator(BaseOrchestrator):
    """Execute agents in parallel"""

    def orchestrate(self, task: str, **kwargs) -> OrchestrationResult:
        # Execute all agents in parallel
        with ThreadPoolExecutor() as executor:
            futures = {
                key: executor.submit(agent.run, task)
                for key, agent in self._agents.items()
            }

            results = {key: future.result() for key, future in futures.items()}

        # Synthesize
        final_answer = self.synthesize_results(list(results.values()))

        return OrchestrationResult(
            success=True,
            final_answer=final_answer,
            steps=[...],
            duration=...
        )
```

**Step 2: Use it**

```python
from orchestration import ParallelOrchestrator, Agent1, Agent2

orch = ParallelOrchestrator()
orch.add_agent('agent1', Agent1())
orch.add_agent('agent2', Agent2())

result = orch.run("task")  # Agents run in parallel!
```

---

## 🎯 Next Steps

### Immediate Actions

1. **Run the examples**
   ```bash
   python examples/01_simple_calculation.py
   python examples/02_deep_web_research.py
   ```

2. **Try your own query**
   ```python
   from orchestration import DirectOrchestrator, ResearchAgent
   orch = DirectOrchestrator()
   orch.add_agent('research', ResearchAgent())
   result = orch.run("Your question here")
   print(result.final_answer)
   ```

3. **Create a custom agent** for your use case

4. **Build a custom workflow** combining multiple agents

### Advanced Enhancements

1. **Add Real Web Search**
   - Integrate web-search-prime MCP
   - Add Claude Agent SDK WebSearch tool
   - Connect to custom search APIs

2. **Add More Orchestration Patterns**
   - ParallelOrchestrator (execute agents in parallel)
   - MCPOrchestrator (tool-based discovery)
   - HybridOrchestrator (mixed approach)

3. **Add More Agents**
   - SentimentAgent (sentiment analysis)
   - TranslatorAgent (language translation)
   - SummarizerAgent (text summarization)
   - ClassifierAgent (text classification)

4. **Build Pre-configured Workflows**
   - CodeReviewWorkflow (analyzer + docs + security)
   - DataAnalysisWorkflow (research + calculate + visualize)
   - ContentCreationWorkflow (research + write + review)

5. **Add Persistence**
   - Save orchestration history
   - Cache agent results
   - Store configurations in database

6. **Add Monitoring**
   - Performance metrics dashboard
   - Error tracking
   - Usage analytics

---

## 💡 Tips & Best Practices

### Agent Design

✅ **DO**:
- Keep agents focused on single responsibility
- Add thorough input validation
- Provide clear instructions in config
- Log important events
- Collect execution metrics

❌ **DON'T**:
- Make agents too generic
- Skip error handling
- Ignore performance metrics
- Hard-code configuration values

### Orchestrator Design

✅ **DO**:
- Design clear, logical workflows
- Handle errors gracefully
- Provide informative synthesis
- Track execution statistics
- Make workflows testable

❌ **DON'T**:
- Create overly complex workflows
- Ignore agent failures
- Skip result validation
- Hard-code agent keys

### Testing

✅ **DO**:
- Test agents in isolation
- Mock external dependencies
- Test orchestration logic
- Write integration tests
- Measure test coverage

❌ **DON'T**:
- Only test happy paths
- Skip error cases
- Ignore edge cases
- Forget performance tests

---

## 📚 Additional Resources

- **README.md**: Complete project documentation
- **MULTI_AGENT_PROJECT_PLAN.md**: Detailed architecture plan
- **examples/**: Working code examples
- **tests/**: Test examples and patterns
- **[Agno Documentation](https://github.com/agno-agi/agno)**: Agno framework docs
- **[Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk)**: Claude SDK docs

---

## 🙋 FAQ

**Q: Can I use OpenAI models instead of Claude?**
A: Yes! Change the model in AgentConfig:
```python
from agno.models.openai import OpenAIChat
config = AgentConfig(model_id="gpt-4")
```

**Q: How do I add real web search?**
A: Integrate MCP tools or web search APIs into your agents. See DeepWebResearcherAgent for extension points.

**Q: Can agents run in parallel?**
A: Yes! Implement a ParallelOrchestrator or use ThreadPoolExecutor in your custom workflow.

**Q: How do I persist results?**
A: Add database or file storage in your orchestrator's `run()` method after successful execution.

**Q: Can I use this with Claude Code?**
A: Yes! The system works great with Claude Code's authentication. No separate API keys needed.

---

**You now have a complete, production-ready multi-agent orchestration system!** 🎉

Start by running the examples, then build your own agents and workflows for your specific use cases.

---

**Last Updated**: 2025-10-13
