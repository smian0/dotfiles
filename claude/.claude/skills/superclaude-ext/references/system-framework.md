# System Framework Domain Guide

## Overview

The System Framework domain specializes in designing, generating, and validating multi-agent systems with intelligent orchestration and comprehensive documentation.

## Available Agents

### meta-builder
Multi-agent system architect and generator:
- Complete agent ecosystem design
- Orchestration pattern implementation
- Communication protocol definition
- Validation framework creation
- System documentation generation

**Best for**: Creating new multi-agent systems, workflow automation, complex orchestrations

### framework-validator
Framework validation and compliance specialist:
- Code quality validation
- Architecture compliance checking
- Security assessment
- Performance validation
- Best practices enforcement

**Best for**: System audits, quality assurance, compliance checking, pre-deployment validation

## Orchestration Patterns

### Sequential Pipeline
```
Agent1 → Agent2 → Agent3 → Result
```
**Use when**: Tasks have strict dependencies
**Example**: Data processing pipeline

### Parallel Processing
```
       ┌→ Agent1 →┐
Input →├→ Agent2 →├→ Merge → Result
       └→ Agent3 →┘
```
**Use when**: Tasks are independent
**Example**: Multi-perspective analysis

### Hierarchical Delegation
```
    Supervisor
    /    |    \
Agent1 Agent2 Agent3
```
**Use when**: Complex task decomposition needed
**Example**: Customer support system

### Mesh Collaboration
```
Agent1 ↔ Bus ↔ Agent2
   ↑       ↓      ↑
   └──Agent3──────┘
```
**Use when**: Dynamic collaboration required
**Example**: Real-time trading system

### MapReduce Pattern
```
        ┌→ Worker1 →┐
        ├→ Worker2 →├→ Reducer → Result
Mapper →├→ Worker3 →┘
        └→ WorkerN →┘
```
**Use when**: Large-scale parallel processing
**Example**: Data analysis system

## Common Use Cases

### Generate Multi-Agent System
```
@superclaude-ext/meta-builder create customer support multi-agent system
```

### Validate Existing System
```
@superclaude-ext/framework-validator validate architecture in ./src
```

### Design Workflow
```
@superclaude-ext/meta-builder design data processing pipeline with validation
```

## System Components

### Agent Definition
Each agent requires:
- **Name**: Unique identifier
- **Purpose**: Clear responsibility
- **Tools**: Required capabilities
- **Model**: Appropriate AI model
- **Interface**: Input/output schema

### Communication Protocols
- **Direct Message**: Agent-to-agent
- **Broadcast**: One-to-many
- **Pub/Sub**: Event-driven
- **Request/Response**: Synchronous
- **Stream**: Continuous data flow

### Context Management
- **Shared State**: Global context store
- **Message Passing**: Include in messages
- **File-Based**: Persistent storage
- **Database**: Structured storage
- **Cache**: Fast access layer

### Error Handling
- **Retry Logic**: Exponential backoff
- **Circuit Breaker**: Failure protection
- **Fallback**: Alternative paths
- **Compensation**: Rollback actions
- **Dead Letter**: Failed message queue

## Implementation Patterns

### Agent Template
```yaml
name: agent-name
description: Clear purpose and triggers
tools: Tool1, Tool2, Tool3
model: sonnet
---
# Agent implementation
```

### Orchestrator Template
```python
class Orchestrator:
    def __init__(self):
        self.agents = {}
        self.context = {}

    def execute_workflow(self, input_data):
        # Workflow logic
        pass
```

### Validation Framework
```python
def validate_system():
    # Check agent definitions
    # Verify communication paths
    # Test error handling
    # Measure performance
    return validation_report
```

## Best Practices

### System Design
1. **Single Responsibility**: Each agent one purpose
2. **Loose Coupling**: Minimal dependencies
3. **High Cohesion**: Related logic together
4. **Clear Interfaces**: Explicit contracts
5. **Fault Tolerance**: Graceful degradation

### Implementation
1. **Incremental Development**: Build iteratively
2. **Test Early**: Validate each component
3. **Document Thoroughly**: Clear documentation
4. **Monitor Everything**: Comprehensive logging
5. **Version Control**: Track all changes

### Deployment
1. **Environment Parity**: Dev/staging/prod similar
2. **Configuration Management**: External config
3. **Secret Management**: Secure credentials
4. **Health Checks**: Liveness/readiness
5. **Rollback Plan**: Quick recovery

## Validation Checklist

### Architecture
- [ ] Clear agent responsibilities
- [ ] Defined communication patterns
- [ ] Error handling implemented
- [ ] Performance requirements met
- [ ] Scalability considered

### Code Quality
- [ ] Consistent style
- [ ] No code duplication
- [ ] Appropriate complexity
- [ ] Security best practices
- [ ] Comprehensive tests

### Documentation
- [ ] System overview
- [ ] Agent specifications
- [ ] API documentation
- [ ] Deployment guide
- [ ] Troubleshooting guide

## Example Systems

### Customer Support System
```
Components:
- Classifier: Route inquiries
- Specialists: Handle specific issues
- Escalator: Complex cases
- Responder: Generate responses
- QA: Validate quality

Pattern: Hierarchical with specialization
```

### Trading System
```
Components:
- Scanner: Identify opportunities
- Analyzer: Technical/fundamental
- Risk: Position sizing
- Executor: Order management
- Monitor: Track performance

Pattern: Pipeline with feedback
```

### Content Generation System
```
Components:
- Researcher: Gather information
- Writer: Create content
- Editor: Refine quality
- SEO: Optimize for search
- Publisher: Deploy content

Pattern: Sequential with iteration
```

## Advanced Techniques

### Dynamic Scaling
```python
def scale_agents(load):
    if load > threshold:
        spawn_workers(count)
    elif load < minimum:
        terminate_workers(count)
```

### A/B Testing
```python
def route_request(request):
    if random() < 0.1:  # 10% to variant
        return variant_workflow(request)
    return standard_workflow(request)
```

### Canary Deployment
```python
def canary_rollout(new_version):
    route_percentage(5)  # Start with 5%
    monitor_metrics()
    if healthy():
        increase_gradually()
    else:
        rollback()
```

## Performance Optimization

### Token Efficiency
- Use appropriate models
- Compress context
- Cache results
- Batch operations

### Latency Reduction
- Parallel execution
- Async operations
- Connection pooling
- Result caching

### Resource Management
- Memory limits
- CPU allocation
- Network optimization
- Storage efficiency

## Monitoring and Observability

### Key Metrics
- **Throughput**: Requests/second
- **Latency**: Response times
- **Error Rate**: Failure percentage
- **Availability**: Uptime percentage
- **Cost**: Token usage, compute

### Logging Strategy
```python
logger.info(f"Workflow started: {workflow_id}")
logger.debug(f"Agent {agent_id} processing")
logger.error(f"Agent {agent_id} failed: {error}")
logger.info(f"Workflow completed: {duration}ms")
```

### Alerting Rules
- Error rate > 1%
- Latency p95 > 1000ms
- Agent failure > 3 consecutive
- Memory usage > 80%
- Token usage > budget

## Integration Examples

### With Business Domain
```
1. @superclaude-ext/meta-builder design sales system
2. @superclaude-ext/business-panel validate business logic
3. @superclaude-ext/framework-validator verify implementation
```

### With Macro Domain
```
1. @superclaude-ext/meta-builder create trading bot architecture
2. @superclaude-ext/macro-analyst define trading strategies
3. @superclaude-ext/framework-validator validate risk management
```