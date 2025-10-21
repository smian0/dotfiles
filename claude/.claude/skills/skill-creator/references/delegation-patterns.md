# Delegation Patterns for Level 2 Skills

This reference provides templates and patterns for skills that need to delegate specific tasks to specialized subagents.

## When to Use Delegation

Delegation is appropriate when a skill needs occasional specialized help that:
- Requires deep, multi-source research
- Needs domain expertise outside the skill's focus
- Benefits from specialized analysis or validation
- Is separable from the main workflow
- Can complete asynchronously

## Core Delegation Pattern

### Basic Syntax

```python
from Task import Task

Task(
    subagent_type="<agent-name>",
    description="<short-description>",
    prompt="""<detailed-prompt>"""
)
```

### Key Components

1. **subagent_type:** Name of the specialized agent (see Available Agents below)
2. **description:** Short summary for logging/tracking (3-5 words)
3. **prompt:** Detailed instructions for the subagent

---

## Available Subagents

### Research Agents

#### web-researcher
**Use for:** Comprehensive multi-source research, documentation lookup, comparative analysis

```python
Task(
    subagent_type="web-researcher",
    description="Research {topic} documentation",
    prompt="""
Research {specific_topic} comprehensively:

1. Find official documentation and authoritative sources
2. Identify key concepts, patterns, and best practices
3. Note any security considerations or limitations
4. Compare approaches if multiple exist
5. Extract specific information about: {specific_requirements}

Provide a structured summary with:
- Primary sources (URLs)
- Key findings
- Best practices
- Important warnings/limitations
- Recommended approach
"""
)
```

#### deep-research-agent
**Use for:** Deep analysis with adaptive strategies, investigative research

```python
Task(
    subagent_type="deep-research-agent",
    description="Deep analysis of {topic}",
    prompt="""
Conduct deep analysis of {topic}:

Research Questions:
1. {question_1}
2. {question_2}
3. {question_3}

Required Depth:
- Primary sources only
- Cross-reference findings
- Identify contradictions
- Assess credibility

Deliverable: Comprehensive report with evidence, sources, and confidence levels
"""
)
```

### Code Analysis Agents

#### code-reviewer
**Use for:** Code quality review, best practices validation

```python
Task(
    subagent_type="code-reviewer",
    description="Review {component} code",
    prompt="""
Review the following code for quality and best practices:

Focus Areas:
- Code structure and organization
- Error handling
- Performance considerations
- Maintainability
- Documentation quality

Code to review: {code_or_file_path}

Provide:
- Issues found (categorized by severity)
- Specific recommendations
- Example fixes for critical issues
"""
)
```

#### security-engineer
**Use for:** Security vulnerability analysis, threat modeling

```python
Task(
    subagent_type="security-engineer",
    description="Security audit of {component}",
    prompt="""
Perform security analysis of {component}:

Analysis Scope:
- Input validation
- Authentication/authorization
- Data sanitization
- Injection vulnerabilities
- Secrets management
- {domain_specific_concerns}

Code/Design: {code_or_design_doc}

Provide:
- Vulnerabilities found (with severity: critical/high/medium/low)
- Exploitation scenarios
- Remediation steps
- Prevention best practices
"""
)
```

#### performance-engineer
**Use for:** Performance analysis, bottleneck identification

```python
Task(
    subagent_type="performance-engineer",
    description="Analyze {component} performance",
    prompt="""
Analyze performance characteristics of {component}:

Focus Areas:
- Time complexity
- Space complexity
- I/O patterns
- Caching opportunities
- Bottlenecks

Code: {code_or_file_path}

Provide:
- Performance profile
- Bottlenecks identified
- Optimization recommendations
- Expected impact of each optimization
"""
)
```

### Problem-Solving Agents

#### root-cause-analyst
**Use for:** Systematic problem investigation, debugging complex issues

```python
Task(
    subagent_type="root-cause-analyst",
    description="Investigate {issue}",
    prompt="""
Investigate the root cause of: {issue_description}

Symptoms:
- {symptom_1}
- {symptom_2}
- {symptom_3}

Context:
{relevant_context}

Required Analysis:
1. Hypothesis generation
2. Evidence gathering
3. Hypothesis testing
4. Root cause identification
5. Solution recommendations

Provide systematic analysis with confidence levels for findings.
"""
)
```

---

## Delegation Patterns by Use Case

### Pattern 1: API Documentation Research

**Scenario:** Building an MCP server or API integration skill

```python
# In SKILL.md, add this section:

## Phase 1: API Research

Before implementing tools, comprehensively research the API:

from Task import Task

Task(
    subagent_type="web-researcher",
    description="Research {service_name} API",
    prompt="""
Research the {service_name} API comprehensively:

Required Information:
1. Official API documentation URL
2. Authentication methods (API key, OAuth, etc.)
3. Base URL and endpoint structure
4. Rate limits and pagination
5. Top 10 most useful endpoints for {use_case}
6. Request/response formats
7. Error handling patterns
8. Common gotchas or limitations

Deliverable: Structured summary with URLs, endpoint details, and implementation guidance
"""
)

# Use the research results to inform tool implementation
```

### Pattern 2: Security Validation

**Scenario:** Code generation skill that needs security validation

```python
# After generating code, validate security

## Security Validation

After generating code, validate security:

from Task import Task

Task(
    subagent_type="security-engineer",
    description="Validate {component} security",
    prompt="""
Review the generated code for security issues:

Code: {file_path_or_code}

Security Checklist:
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Authentication checks
- [ ] Authorization enforcement
- [ ] Secrets management
- [ ] Error message sanitization

Provide:
- Security issues found
- Risk level for each
- Specific fixes required
"""
)

# Apply security fixes before finalizing
```

### Pattern 3: Best Practices Validation

**Scenario:** Code generation that needs framework-specific validation

```python
# Validate against framework best practices

## Best Practices Validation

Validate generated code against {framework} best practices:

from Task import Task

Task(
    subagent_type="web-researcher",
    description="Research {framework} best practices",
    prompt="""
Research current best practices for {framework}:

Focus Areas:
1. Project structure conventions
2. Configuration patterns
3. Error handling approaches
4. Testing strategies
5. Performance optimization
6. Common anti-patterns to avoid

Compare generated code against these best practices and identify any deviations.
"""
)

# Refactor code to align with best practices
```

### Pattern 4: Comparative Analysis

**Scenario:** Architecture decision requiring comparison of approaches

```python
# Compare multiple approaches before recommending one

## Architecture Decision: {decision_point}

Compare approaches for {decision_point}:

from Task import Task

Task(
    subagent_type="deep-research-agent",
    description="Compare {approach_A} vs {approach_B}",
    prompt="""
Compare these approaches for {use_case}:

Approach A: {approach_A_description}
Approach B: {approach_B_description}

Comparison Criteria:
- Performance characteristics
- Scalability
- Maintainability
- Community support
- Learning curve
- Use case fit

Provide:
- Side-by-side comparison
- Pros/cons for each
- Recommendation with rationale
- Migration path considerations
"""
)

# Use analysis to make informed architecture decision
```

---

## Integration Patterns

### Pattern A: Sequential Integration

Delegation happens at a specific point in the workflow:

```markdown
## Workflow

1. Gather user requirements
2. **Delegate:** Research best practices
3. Generate implementation based on research
4. **Delegate:** Validate security
5. Apply fixes from validation
6. Finalize and document
```

### Pattern B: Conditional Integration

Delegation happens only when certain conditions are met:

```markdown
## Workflow

1. Analyze requirements
2. If complexity > threshold:
   - **Delegate:** Deep analysis
   - Use analysis to inform approach
3. Implement solution
4. If security-sensitive:
   - **Delegate:** Security audit
   - Apply fixes
5. Finalize
```

### Pattern C: Iterative Integration

Delegation happens in refinement iterations:

```markdown
## Workflow

1. Generate initial implementation
2. **Iterate:**
   - **Delegate:** Code review
   - Apply recommendations
   - If issues remain, repeat
3. **Delegate:** Final validation
4. Finalize
```

---

## Decision Criteria: Delegate vs. Handle Directly

### Delegate When:
- ✅ Research requires 3+ sources
- ✅ Analysis needs domain expertise outside skill's focus
- ✅ Validation requires specialized knowledge
- ✅ Task benefits from systematic investigation
- ✅ Results are used to inform subsequent steps

### Handle Directly When:
- ❌ Simple, well-known information
- ❌ Single-source lookup
- ❌ Within skill's domain expertise
- ❌ Deterministic operation
- ❌ Already have necessary context

---

## Best Practices for Delegation

### 1. Clear Prompts
```python
# ❌ Vague
Task(
    subagent_type="web-researcher",
    prompt="Research the API"
)

# ✅ Specific
Task(
    subagent_type="web-researcher",
    prompt="""
Research the Stripe Payment API:
1. Authentication methods
2. Top 5 payment endpoints
3. Webhook handling patterns
4. Rate limits
5. Test mode vs live mode

Focus on payment processing workflows.
"""
)
```

### 2. Structured Prompts

Use numbered lists, sections, and clear deliverables:

```python
Task(
    subagent_type="deep-research-agent",
    prompt="""
## Research Question
{specific_question}

## Required Depth
- Primary sources only
- Cross-reference 3+ sources
- Identify consensus vs. debate

## Deliverable Format
- Summary (2-3 paragraphs)
- Key findings (bullet points)
- Sources (URLs with descriptions)
- Confidence level (high/medium/low)
"""
)
```

### 3. Context Provision

Provide relevant context to the subagent:

```python
Task(
    subagent_type="security-engineer",
    prompt="""
## Context
Application: {app_description}
User roles: {roles}
Data sensitivity: {sensitivity_level}

## Code to Audit
{code}

## Threat Model
Primary concerns: {concerns}

## Analysis Required
{specific_security_analysis}
"""
)
```

### 4. Result Utilization

Document how to use delegation results:

```markdown
## After Delegation

The subagent will return: {expected_format}

Use the results to:
1. {specific_action_1}
2. {specific_action_2}
3. {specific_action_3}

If findings indicate {condition}, then {alternative_action}.
```

---

## Common Anti-Patterns

### ❌ Over-Delegation
**Problem:** Delegating trivial tasks that the skill can handle

```python
# ❌ Bad: Delegating simple lookup
Task(
    subagent_type="web-researcher",
    prompt="What is the Python requests library?"
)

# ✅ Good: Handle simple lookups directly
# Just use WebFetch for official docs
```

### ❌ Under-Specification
**Problem:** Vague prompts that produce unfocused results

```python
# ❌ Bad: Vague delegation
Task(
    subagent_type="web-researcher",
    prompt="Research best practices"
)

# ✅ Good: Specific delegation
Task(
    subagent_type="web-researcher",
    prompt="""
Research React hooks best practices specifically for:
1. useEffect dependency arrays
2. Custom hooks patterns
3. Performance optimization

Focus on official React docs and Kent C. Dodds recommendations.
"""
)
```

### ❌ Ignoring Results
**Problem:** Delegating but not using the results

```python
# ❌ Bad: Delegate then ignore
Task(subagent_type="security-engineer", prompt="Audit code")
# ... continue without checking results

# ✅ Good: Delegate and integrate
Task(subagent_type="security-engineer", prompt="Audit code")
# Wait for results
# Apply security fixes based on findings
# Validate fixes were applied
```

---

## Template Library

### Template: API Research
```python
Task(
    subagent_type="web-researcher",
    description="Research {api_name} API",
    prompt="""
Research {api_name} API:

Required Information:
1. Official documentation URL
2. Authentication method
3. Base URL
4. Rate limits
5. Top 10 endpoints for {use_case}
6. Response formats
7. Error handling
8. Code examples

Deliverable: Structured summary with implementation guidance
"""
)
```

### Template: Security Audit
```python
Task(
    subagent_type="security-engineer",
    description="Security audit of {component}",
    prompt="""
Security audit of {component}:

Code: {file_or_code}

Checklist:
- [ ] Input validation
- [ ] Authentication/authorization
- [ ] Injection vulnerabilities
- [ ] Secrets management
- [ ] Error handling
- [ ] {domain_specific_checks}

Provide: Issues, severity, fixes
"""
)
```

### Template: Performance Analysis
```python
Task(
    subagent_type="performance-engineer",
    description="Analyze {component} performance",
    prompt="""
Performance analysis of {component}:

Code: {file_or_code}

Focus:
- Algorithm complexity
- Memory usage
- I/O patterns
- Caching opportunities

Provide: Profile, bottlenecks, optimizations
"""
)
```

### Template: Best Practices Validation
```python
Task(
    subagent_type="web-researcher",
    description="Research {framework} best practices",
    prompt="""
Research {framework} best practices:

Topics:
1. {topic_1}
2. {topic_2}
3. {topic_3}

Sources: Official docs, authoritative blogs

Provide: Best practices, anti-patterns, recommendations
"""
)
```

---

## Verification Checklist

Before finalizing delegation in a skill:

- [ ] Delegation point is clearly needed (not trivial)
- [ ] Correct subagent type selected
- [ ] Prompt is specific and structured
- [ ] Expected results are documented
- [ ] Integration of results is explained
- [ ] Alternative paths considered (if delegation fails)
- [ ] User can understand when delegation happens
- [ ] Delegation adds value (not just overhead)

---

## Examples from Real Skills

### Example 1: fastmcp-builder

```python
# Phase 1.3: Study FastMCP Documentation
Task(
    subagent_type="web-researcher",  # Uses Context7 internally
    description="Research FastMCP v2 documentation",
    prompt="""
Research FastMCP v2 patterns:

Topics:
- Tool decoration patterns
- Context usage
- Pydantic validation
- Sampling for LLM completions
- Resource access

Sources: /jlowin/fastmcp on GitHub

Provide: Implementation patterns, code examples, best practices
"""
)
```

### Example 2: mcp-builder (hypothetical Level 2 enhancement)

```python
# Phase 1.5: Exhaustive API Study
Task(
    subagent_type="web-researcher",
    description="Research {service_name} API comprehensively",
    prompt="""
Research {service_name} API:

1. Official API documentation
2. Authentication requirements
3. Rate limiting
4. Top 20 endpoints by usefulness
5. Pagination patterns
6. Error responses
7. Data models
8. SDKs and code examples

Deliverable: Comprehensive API reference summary for MCP server implementation
"""
)
```

---

Remember: Delegation is a tool, not a requirement. Use it when it genuinely adds value to the skill's capabilities.
