# Changelog - agno-workflow-builder Skill

## 2025-01-14 - Major Update: Production Patterns

### New Reference Guides

#### 1. Structured Outputs Guide (`references/structured_outputs_guide.md`)
**What:** Complete guide to using Pydantic models for type-safe agent communication

**Key Learnings:**
- Use `output_schema` parameter with Pydantic models for robust workflows
- **Critical:** Agent instructions MUST explicitly list ALL required Pydantic fields
- Prevents manual text parsing errors
- Enables IDE autocomplete and type checking
- Real-world example from production Xero workflow

**Example:**
```python
class ParsedQuery(BaseModel):
    action: Literal["create", "update", "delete"]
    entity: str
    parameters: Dict[str, Any]

parser = Agent(
    output_schema=ParsedQuery,
    instructions=(
        "Parse query and return ParsedQuery with:\n"
        "1. action: create/update/delete\n"
        "2. entity: target object type\n"
        "3. parameters: extracted values"
    )
)
```

**Why Important:**
- Eliminates fragile text-based communication
- Catches errors at validation time, not execution time
- Makes workflows production-ready

#### 2. Output Control Patterns Guide (`references/output_control_patterns.md`)
**What:** Production vs development output modes for workflows

**Key Learnings:**
- **Critical:** Use `aprint_response()` (not `print_response()`) with async tools like MCPTools
- Implement CLI flags for output control (`--show-steps`, `--show-time`, `--stream`)
- Production mode: Clean output via `workflow.arun()`
- Development mode: Rich formatted output via `workflow.aprint_response()`
- Shows structured Pydantic outputs in beautiful formatted boxes

**Example:**
```python
if show_details:
    await workflow.aprint_response(
        input=query,
        show_step_details=True,  # Shows structured outputs
        show_time=True,          # Shows execution time
    )
else:
    result = await workflow.arun(query)  # Clean output
```

**Why Important:**
- Makes workflows usable in production AND debuggable in development
- Same codebase serves both use cases
- Excellent developer experience

#### 3. Model Selection Patterns Guide (`references/model_selection_patterns.md`)
**What:** Data-driven model selection for optimal workflow performance

**Key Learnings:**
- **Always consult `@ollama-model-selector` skill** before hardcoding models
- Different agents in same workflow should use different models based on task type
- Parsing → fast models (glm-4.6:cloud, 192 tok/s)
- Reasoning → powerful models (deepseek-v3.1:671b-cloud, 76 tok/s)
- Tool calling → models with good tool support (glm-4.6:cloud)
- Document model choices with rationale and performance metrics

**Example:**
```python
# 3-step workflow with optimized models
parser = Agent(model=Ollama(id="glm-4.6:cloud"))               # Fast parsing
validator = Agent(model=Ollama(id="deepseek-v3.1:671b-cloud")) # Deep reasoning
executor = Agent(model=Ollama(id="glm-4.6:cloud"))             # Fast tools
```

**Why Important:**
- Prevents suboptimal one-size-fits-all approach
- Balances speed and accuracy based on task requirements
- Measurable performance improvements (2-3x faster for simple tasks, better accuracy for complex)

### Updated SKILL.md

**Added Sections:**
- Structured outputs configuration example
- Output control configuration example
- Updated model selection recommendations to reference ollama-model-selector
- Added new reference guides to documentation table
- Updated workflow creation steps to include structured outputs, model selection, and output control

### Real-World Validation

All patterns validated in production Xero workflow (`xero_workflow_cli.py`):
- ✅ 3-step workflow with structured outputs (ParsedOperation → ValidationResult → Final Result)
- ✅ Data-driven model selection (glm-4.6 for parsing/execution, deepseek-v3.1 for validation)
- ✅ CLI flags for output control (default clean, `--show-steps --show-time` for detailed)
- ✅ Robust rate limit handling with retry logic
- ✅ Type-safe communication between all workflow steps

**Performance:**
- Parser: ~2s (192 tok/s)
- Validator: ~6s (76 tok/s) - acceptable for accuracy
- Executor: ~4s (192 tok/s + API latency)
- Total: ~12s average (balanced speed + accuracy)

### Benefits

1. **Robustness:** Structured outputs eliminate text parsing errors
2. **Performance:** Data-driven model selection optimizes speed vs accuracy tradeoff
3. **Developer Experience:** Output control provides great debugging without cluttering production output
4. **Production-Ready:** All patterns tested in real-world workflow

### Migration Path

**For existing workflows:**
1. Add Pydantic models with `output_schema` parameter
2. Update agent instructions to explicitly list all required fields
3. Consult `@ollama-model-selector` for optimal model choices
4. Add CLI flags for output control (`--show-steps`, `--show-time`)
5. Change `print_response()` to `aprint_response()` if using async tools

**Backward Compatible:** All changes are additive, existing workflows continue to work.

---

## Previous Versions

### Initial Release
- Basic workflow templates
- Simple agent CLI examples
- MCP integration patterns
- Team workflow examples
- Debug guide
- Workflow patterns reference

