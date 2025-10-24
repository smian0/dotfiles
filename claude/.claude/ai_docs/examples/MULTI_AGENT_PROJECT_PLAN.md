# Claude + Agno Multi-Agent System - Project Plan

**Last Updated:** 2025-10-13

## Overview

A complete, production-ready multi-agent system demonstrating Claude Agent SDK orchestrating specialized Agno agents. Each agent is individually testable, composable, and follows best practices.

---

## Architecture Principles

### 1. Separation of Concerns
- **Agents**: Specialized workers (research, calculation, analysis)
- **Orchestrators**: Coordination logic (direct calls, MCP tools, hybrid)
- **Tools**: Bridge layer between Claude SDK and Agno agents
- **Examples**: Real-world use cases showing composition

### 2. Testability
- Each agent can be tested in isolation
- Orchestrators have unit tests
- Integration tests verify full workflows
- Mock capabilities for fast testing

### 3. Composability
- Agents are independent, reusable modules
- Orchestrators compose agents into workflows
- Easy to add new agents without breaking existing ones

### 4. Extensibility
- Plugin-based agent system
- Configuration-driven agent creation
- Multiple orchestration patterns supported

---

## Directory Structure

```
claude-agno-orchestration/
│
├── README.md                           # Quick start guide
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Project metadata
├── .env.example                        # Environment template
│
├── src/                                # Source code
│   └── orchestration/                  # Main package
│       ├── __init__.py
│       │
│       ├── agents/                     # Agent definitions
│       │   ├── __init__.py
│       │   ├── base.py                 # BaseAgent class & factory
│       │   ├── research.py             # ResearchAgent
│       │   ├── calculator.py           # CalculatorAgent
│       │   ├── code_analyzer.py        # CodeAnalyzerAgent
│       │   ├── documentation.py        # DocumentationAgent
│       │   └── sentiment.py            # SentimentAgent
│       │
│       ├── orchestrators/              # Orchestration patterns
│       │   ├── __init__.py
│       │   ├── base.py                 # BaseOrchestrator
│       │   ├── direct.py               # DirectOrchestrator (simplest)
│       │   ├── mcp.py                  # MCPOrchestrator (tool-based)
│       │   └── hybrid.py               # HybridOrchestrator (mixed)
│       │
│       ├── tools/                      # Claude SDK tools
│       │   ├── __init__.py
│       │   └── agno_bridges.py         # MCP tool wrappers
│       │
│       ├── workflows/                  # Pre-built workflows
│       │   ├── __init__.py
│       │   ├── code_review.py          # Code review workflow
│       │   ├── data_analysis.py        # Data analysis workflow
│       │   └── research_synthesis.py   # Research workflow
│       │
│       └── config/                     # Configuration management
│           ├── __init__.py
│           ├── agent_config.py         # Agent configurations
│           └── settings.py             # Global settings
│
├── examples/                           # Example scripts
│   ├── 01_simple_calculation.py        # Basic 2-agent example
│   ├── 02_code_review_system.py        # Code review use case
│   ├── 03_research_assistant.py        # Multi-step research
│   ├── 04_data_pipeline.py             # Data processing pipeline
│   └── 05_custom_workflow.py           # Building custom workflows
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures
│   ├── unit/                           # Unit tests
│   │   ├── test_agents.py              # Individual agent tests
│   │   ├── test_orchestrators.py       # Orchestrator tests
│   │   └── test_tools.py               # Tool tests
│   ├── integration/                    # Integration tests
│   │   ├── test_workflows.py           # Workflow tests
│   │   └── test_end_to_end.py          # Full system tests
│   └── fixtures/                       # Test data
│       ├── sample_code.py              # Sample code for testing
│       └── sample_data.json            # Sample data
│
├── config/                             # Configuration files
│   ├── agents.yaml                     # Agent definitions
│   ├── workflows.yaml                  # Workflow definitions
│   └── models.yaml                     # Model configurations
│
├── docs/                               # Documentation
│   ├── architecture.md                 # System architecture
│   ├── agents.md                       # Agent guide
│   ├── orchestration.md                # Orchestration patterns
│   ├── workflows.md                    # Workflow examples
│   ├── testing.md                      # Testing guide
│   └── api/                            # API documentation
│       ├── agents.md
│       ├── orchestrators.md
│       └── tools.md
│
└── scripts/                            # Utility scripts
    ├── setup.sh                        # Initial setup
    ├── test.sh                         # Run all tests
    └── demo.sh                         # Run all examples
```

---

## Component Design

### 1. Base Agent (`src/orchestration/agents/base.py`)

**Purpose**: Abstract base class for all agents

**Key Features**:
- Standard interface: `run(prompt) -> result`
- Configuration loading
- Error handling
- Logging
- Metrics collection

**Interface**:
```python
class BaseAgent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent = self._create_agent()

    @abstractmethod
    def _create_agent(self) -> Agent:
        """Create underlying Agno agent"""
        pass

    def run(self, prompt: str) -> AgentResult:
        """Execute agent with prompt"""
        pass

    def validate_input(self, prompt: str) -> bool:
        """Validate input before execution"""
        pass
```

### 2. Specialized Agents

Each agent is a standalone module with:
- Clear single responsibility
- Configurable model/parameters
- Input/output validation
- Unit tests

**Example: ResearchAgent** (`src/orchestration/agents/research.py`)
```python
class ResearchAgent(BaseAgent):
    """Specialized in finding factual information"""

    def _create_agent(self) -> Agent:
        return Agent(
            model=Claude(id=self.config.model_id),
            instructions="""You are a research specialist.
            Provide concise, factual information with sources."""
        )

    def validate_input(self, prompt: str) -> bool:
        # Research-specific validation
        return len(prompt) > 10
```

### 3. Orchestrators

Three orchestration patterns, each extending `BaseOrchestrator`:

#### A. DirectOrchestrator
- Simplest pattern
- Python functions call agents directly
- Good for: Simple workflows, scripting

```python
class DirectOrchestrator(BaseOrchestrator):
    def orchestrate(self, task: str) -> Result:
        # Step 1: Research
        research = self.agents['research'].run(task)

        # Step 2: Analysis
        analysis = self.agents['analyzer'].run(research.content)

        # Step 3: Synthesize
        return self.synthesize([research, analysis])
```

#### B. MCPOrchestrator
- Tool-based pattern
- Wraps agents as MCP tools
- Claude SDK discovers and calls tools
- Good for: Dynamic workflows, Claude Code integration

```python
class MCPOrchestrator(BaseOrchestrator):
    def create_mcp_server(self):
        tools = [self._wrap_agent(name, agent)
                 for name, agent in self.agents.items()]
        return create_sdk_mcp_server(name="agno_workers", tools=tools)
```

#### C. HybridOrchestrator
- Combines both patterns
- Some agents are direct, some are tools
- Good for: Complex workflows, optimization

### 4. Pre-built Workflows

Common multi-agent workflows packaged as reusable components:

**CodeReviewWorkflow**:
```python
class CodeReviewWorkflow:
    agents = ['code_analyzer', 'documentation', 'security']

    def run(self, code: str) -> ReviewReport:
        # Parallel execution
        results = self.orchestrator.run_parallel([
            ('analyze', code),
            ('check_docs', code),
            ('security_scan', code)
        ])

        return self.synthesize_review(results)
```

---

## Testing Strategy

### 1. Unit Tests (`tests/unit/`)

**Test individual agents in isolation**:
```python
def test_research_agent():
    agent = ResearchAgent(config)
    result = agent.run("What is Python?")

    assert result.success
    assert "programming language" in result.content.lower()
    assert result.duration < 30.0  # Performance check
```

**Test with mocks for speed**:
```python
@patch('orchestration.agents.research.Agent')
def test_research_agent_mock(mock_agent):
    mock_agent.return_value.run.return_value = MockResult("Python is...")

    agent = ResearchAgent(config)
    result = agent.run("What is Python?")

    mock_agent.assert_called_once()
```

### 2. Integration Tests (`tests/integration/`)

**Test agent composition**:
```python
def test_orchestrator_workflow():
    orchestrator = DirectOrchestrator()
    orchestrator.add_agent('research', ResearchAgent())
    orchestrator.add_agent('calculator', CalculatorAgent())

    result = orchestrator.run("California population density")

    assert result.steps == 2  # Research + Calculate
    assert "238" in result.final_answer
```

### 3. End-to-End Tests

**Test real workflows**:
```python
def test_code_review_e2e():
    workflow = CodeReviewWorkflow()

    sample_code = load_fixture('sample_code.py')
    review = workflow.run(sample_code)

    assert review.has_issues
    assert review.critical_count >= 0
    assert review.recommendation in ['approve', 'request_changes', 'reject']
```

---

## Example Use Cases

### Example 1: Simple Calculation (`examples/01_simple_calculation.py`)

**Goal**: Show basic orchestration with 2 agents

```python
from orchestration import DirectOrchestrator, ResearchAgent, CalculatorAgent

# Setup
orchestrator = DirectOrchestrator()
orchestrator.add_agent('research', ResearchAgent())
orchestrator.add_agent('calculator', CalculatorAgent())

# Execute
result = orchestrator.run("What's the population density of California?")
print(result.final_answer)
```

**Output**:
```
🔍 Research: California population = 39M, area = 163,696 sq mi
🧮 Calculate: 39,000,000 / 163,696 = 238.25
📊 Answer: California has 238 people per square mile
```

### Example 2: Code Review System (`examples/02_code_review_system.py`)

**Goal**: Show parallel agent execution

```python
from orchestration.workflows import CodeReviewWorkflow

# Setup workflow
workflow = CodeReviewWorkflow(
    agents=['code_analyzer', 'documentation', 'security']
)

# Review code
code = open('my_code.py').read()
review = workflow.run(code)

# Results
print(f"Quality Score: {review.quality_score}/10")
print(f"Issues Found: {review.issue_count}")
print(f"Recommendation: {review.recommendation}")
```

### Example 3: Research Assistant (`examples/03_research_assistant.py`)

**Goal**: Show multi-step reasoning with agent chaining

```python
from orchestration import HybridOrchestrator

# Create research pipeline
orchestrator = HybridOrchestrator()
orchestrator.add_agents([
    ('research', ResearchAgent()),
    ('analyzer', DataAnalyzerAgent()),
    ('summarizer', SummarizerAgent())
])

# Execute research workflow
query = "Compare GDP growth of US vs China 2020-2024"
report = orchestrator.run(query)

print(report.summary)
print(report.key_findings)
print(report.sources)
```

### Example 4: Custom Workflow (`examples/05_custom_workflow.py`)

**Goal**: Show how to build custom multi-agent systems

```python
from orchestration import BaseOrchestrator
from orchestration.agents import ResearchAgent, CalculatorAgent, SentimentAgent

class CustomWorkflow(BaseOrchestrator):
    def run(self, news_article: str):
        # Step 1: Extract facts
        facts = self.agents['research'].run(f"Extract key facts: {news_article}")

        # Step 2: Analyze sentiment
        sentiment = self.agents['sentiment'].run(news_article)

        # Step 3: Calculate impact score
        impact = self.agents['calculator'].run(
            f"Score impact 1-10 based on: {facts.content}"
        )

        # Synthesize
        return {
            'facts': facts.content,
            'sentiment': sentiment.content,
            'impact_score': impact.content
        }

# Use it
workflow = CustomWorkflow()
result = workflow.run(news_article)
```

---

## Configuration System

### Agent Configuration (`config/agents.yaml`)

```yaml
agents:
  research:
    model: claude-sonnet-4
    instructions: "You are a research specialist..."
    temperature: 0.3
    max_tokens: 2000

  calculator:
    model: claude-sonnet-4
    instructions: "You are a calculator..."
    temperature: 0.0
    max_tokens: 500

  code_analyzer:
    model: claude-sonnet-4
    instructions: "You are a senior code reviewer..."
    temperature: 0.5
    max_tokens: 4000
```

### Workflow Configuration (`config/workflows.yaml`)

```yaml
workflows:
  code_review:
    agents:
      - code_analyzer
      - documentation
      - security
    execution: parallel
    timeout: 120

  research_synthesis:
    agents:
      - research
      - analyzer
      - summarizer
    execution: sequential
    timeout: 180
```

---

## Implementation Plan

### Phase 1: Foundation (Day 1)
1. ✅ Create directory structure
2. ✅ Implement `BaseAgent` class
3. ✅ Implement `BaseOrchestrator` class
4. ✅ Set up testing infrastructure
5. ✅ Create configuration system

### Phase 2: Core Agents (Day 2)
1. ✅ Implement `ResearchAgent`
2. ✅ Implement `CalculatorAgent`
3. ✅ Implement `CodeAnalyzerAgent`
4. ✅ Write unit tests for each agent
5. ✅ Test agents individually

### Phase 3: Orchestration (Day 3)
1. ✅ Implement `DirectOrchestrator`
2. ✅ Implement `MCPOrchestrator`
3. ✅ Create bridge tools
4. ✅ Write integration tests
5. ✅ Test orchestration patterns

### Phase 4: Workflows (Day 4)
1. ✅ Implement `CodeReviewWorkflow`
2. ✅ Implement `ResearchWorkflow`
3. ✅ Create example scripts
4. ✅ End-to-end testing
5. ✅ Performance optimization

### Phase 5: Documentation (Day 5)
1. ✅ Write architecture docs
2. ✅ Create API documentation
3. ✅ Write usage examples
4. ✅ Create troubleshooting guide
5. ✅ Record demo videos

---

## Key Benefits of This Structure

### 1. **Testability**
- Each agent can be tested alone
- Mock capabilities for fast tests
- Integration tests verify composition
- E2E tests validate real workflows

### 2. **Modularity**
- Add new agents without touching existing code
- Swap agents easily (e.g., GPT-4 → Claude)
- Reuse agents across workflows
- Clear separation of concerns

### 3. **Discoverability**
- Clear directory structure
- Consistent naming conventions
- Well-documented interfaces
- Example-driven documentation

### 4. **Production-Ready**
- Error handling throughout
- Logging and metrics
- Configuration management
- Performance monitoring

### 5. **Extensibility**
- Plugin architecture for agents
- Multiple orchestration patterns
- Custom workflow support
- Configuration-driven behavior

---

## Quick Start for Developers

### 1. Using Existing Agents
```python
from orchestration import ResearchAgent, CalculatorAgent

research = ResearchAgent()
result = research.run("What is quantum computing?")
print(result.content)
```

### 2. Creating New Agents
```python
from orchestration.agents import BaseAgent

class CustomAgent(BaseAgent):
    def _create_agent(self):
        return Agent(
            model=Claude(id="claude-sonnet-4"),
            instructions="Your specialized instructions..."
        )

agent = CustomAgent()
result = agent.run("Your task")
```

### 3. Building Workflows
```python
from orchestration import DirectOrchestrator

orchestrator = DirectOrchestrator()
orchestrator.add_agent('agent1', Agent1())
orchestrator.add_agent('agent2', Agent2())

result = orchestrator.run("Complex task")
```

### 4. Testing Your Code
```bash
# Test single agent
pytest tests/unit/test_agents.py::test_research_agent

# Test workflow
pytest tests/integration/test_workflows.py

# Test everything
pytest tests/
```

---

## Next Steps

1. **Review this plan** - Does the structure make sense?
2. **Adjust if needed** - Any changes to directory structure or components?
3. **Implement** - Start with Phase 1 (foundation)
4. **Iterate** - Build incrementally, test frequently

---

## Questions to Consider

1. **Agent Scope**: Should we add more specialized agents (e.g., Translator, Classifier)?
2. **Orchestration**: Do we need additional patterns beyond Direct/MCP/Hybrid?
3. **Workflows**: What other pre-built workflows would be useful?
4. **Configuration**: Should we support environment-based configs (dev/staging/prod)?
5. **Deployment**: Should we include Docker/K8s deployment configs?

---

**Ready to implement?** Let me know if you'd like to adjust the plan or proceed with implementation!
