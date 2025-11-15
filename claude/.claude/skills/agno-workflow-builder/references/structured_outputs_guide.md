# Structured Outputs with Pydantic - Best Practices

## Overview

Structured outputs using Pydantic models are **essential** for robust workflows. They provide:
- ✅ Type-safe agent communication
- ✅ Automatic validation of agent outputs
- ✅ IDE autocomplete and type checking
- ✅ Clear contracts between workflow steps
- ✅ Prevention of manual text parsing errors

**When to use:** Multi-step workflows where agents pass data to each other.

---

## Basic Pattern

```python
from pydantic import BaseModel, Field
from agno.agent import Agent

class ParsedQuery(BaseModel):
    """Structured output from parser agent."""
    action: Literal["create", "update", "delete", "list"]
    entity: str = Field(..., description="Target entity type")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    intent: str = Field(..., description="User's intent in one sentence")

# Agent with structured output
parser = Agent(
    name="Query Parser",
    model=Ollama(id="glm-4.6:cloud"),
    output_schema=ParsedQuery,  # Enforces Pydantic model
    instructions="Parse user queries into structured operations..."
)

# Usage
result = await parser.arun("create contact ABC Corp")
# result is guaranteed to be ParsedQuery with all fields
print(result.action)  # "create"
print(result.entity)  # "contact"
```

---

## CRITICAL: Agent Instructions Must List All Required Fields

**Problem:** If agent instructions don't explicitly tell the agent to populate ALL Pydantic fields, you'll get validation errors.

**❌ Bad (Incomplete Instructions):**
```python
class ValidationResult(BaseModel):
    is_valid: bool
    operation: ParsedQuery  # Required field!
    validated_params: Dict[str, Any]

validator = Agent(
    output_schema=ValidationResult,
    instructions=(
        "Validate the operation.\n"
        "Set is_valid=True if valid.\n"
        "Include validated_params."
        # ❌ MISSING: No mention of 'operation' field!
    )
)

# Result: Validation error "Field required: operation"
```

**✅ Good (Complete Instructions):**
```python
validator = Agent(
    output_schema=ValidationResult,
    instructions=(
        "Validate the operation and return a ValidationResult.\n\n"
        "**Required Output Fields:**\n"
        "1. **operation**: Include the complete ParsedQuery you received\n"
        "2. **is_valid**: Set to True if validation passes, False otherwise\n"
        "3. **validated_params**: Dictionary with API-ready parameters\n\n"
        "All fields are required - do not omit any."
    )
)

# Result: Clean validation, all fields populated ✅
```

---

## Multi-Step Workflow Pattern

```python
from agno.workflow import Workflow, Step

class ParsedQuery(BaseModel):
    action: str
    entity: str
    parameters: Dict[str, Any]

class ValidationResult(BaseModel):
    is_valid: bool
    operation: ParsedQuery  # Nested Pydantic model
    validated_params: Dict[str, Any]
    errors: list[str] = Field(default_factory=list)

# Step 1: Parse
parser = Agent(
    output_schema=ParsedQuery,
    instructions="Parse query into structured operation with action, entity, parameters"
)

# Step 2: Validate (receives ParsedQuery)
validator = Agent(
    output_schema=ValidationResult,
    instructions=(
        "Validate the parsed operation.\n\n"
        "**CRITICAL: Include ALL fields in output:**\n"
        "1. operation: The ParsedQuery you received\n"
        "2. is_valid: True/False\n"
        "3. validated_params: API-ready parameters\n"
        "4. errors: List of validation error messages (empty if valid)"
    )
)

# Step 3: Execute (receives ValidationResult)
executor = Agent(
    tools=[api_tools],
    instructions=(
        "Execute the validated operation.\n"
        "Input: You'll receive a ValidationResult with validated_params.\n"
        "Use validated_params exactly as provided to call the API."
    )
)

workflow = Workflow(
    steps=[
        Step(name="parse", agent=parser),
        Step(name="validate", agent=validator),
        Step(name="execute", agent=executor),
    ]
)

result = await workflow.arun("create contact ABC Corp")
```

---

## Field Types & Validation

### Basic Types
```python
class MySchema(BaseModel):
    # Simple types
    name: str
    count: int
    price: float
    active: bool
    
    # Optional fields
    description: Optional[str] = None
    
    # Default values
    status: str = "pending"
    
    # Lists
    tags: list[str] = Field(default_factory=list)
```

### Advanced Types
```python
from typing import Literal

class AdvancedSchema(BaseModel):
    # Enums (better than plain strings)
    action: Literal["create", "update", "delete"]
    
    # Nested models
    metadata: Optional[Dict[str, Any]] = None
    
    # Validated fields
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    
    # Min/max constraints
    priority: int = Field(..., ge=1, le=5)
    
    # Description for agent clarity
    intent: str = Field(..., description="User's intent in one sentence")
```

### Complex Nested Models
```python
class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float

class Invoice(BaseModel):
    contact_name: str
    line_items: list[LineItem]  # List of nested models
    total: float
    status: Literal["draft", "submitted", "paid"]
```

---

## Debugging Structured Outputs

### Enable Workflow Debugging

```python
workflow = Workflow(
    steps=[...],
    debug_mode=False  # Clean output
)

# To see structured outputs at each step:
await workflow.aprint_response(
    input=user_query,
    show_step_details=True,  # Shows structured JSON per step
    show_time=True,
    markdown=True
)
```

**Output:**
```
┏━ Step 1: parse (Completed) ━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Structured Output:                                   ┃
┃ {                                                    ┃
┃   "action": "create",                                ┃
┃   "entity": "contact",                               ┃
┃   "parameters": {"name": "ABC Corp"}                 ┃
┃ }                                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Common Validation Errors

**Error:** `Field required: field_name`
- **Cause:** Agent instructions don't mention the field
- **Fix:** Add explicit instruction to populate that field

**Error:** `Input should be a valid string/int/etc`
- **Cause:** Agent returned wrong type
- **Fix:** Add type clarification to instructions

**Error:** `Value error, expected Literal['a', 'b']`
- **Cause:** Agent returned invalid enum value
- **Fix:** List valid values in instructions

---

## Best Practices

### 1. Keep Schemas Flat
```python
# ✅ Good: Flat structure
class Result(BaseModel):
    items: list[str]  # Simple list

# ⚠️ Acceptable: Shallow nesting
class Result(BaseModel):
    items: list[Dict[str, str]]

# ❌ Avoid: Deep nesting (harder for agents)
class Result(BaseModel):
    items: list[ComplexModel[NestedModel[DeepModel]]]
```

### 2. Provide Clear Field Descriptions
```python
class Query(BaseModel):
    action: Literal["create", "update", "delete"] = Field(
        ..., 
        description="Operation type: create (new), update (existing), delete (remove)"
    )
    entity: str = Field(
        ...,
        description="Target entity: contact, invoice, payment, etc."
    )
```

### 3. Use Defaults for Optional Fields
```python
class Result(BaseModel):
    # Required
    status: str
    
    # Optional with None default
    error_message: Optional[str] = None
    
    # Optional with factory default (for mutable types)
    tags: list[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### 4. Validate Early in Workflow
```python
# ✅ Good: Validate structure early
workflow = Workflow(steps=[
    Step("parse", parser_agent),        # Output: ParsedQuery
    Step("validate", validator_agent),  # Output: ValidationResult
    Step("execute", executor_agent),    # Uses validated data
])

# ❌ Bad: No validation, executor gets unpredictable data
workflow = Workflow(steps=[
    Step("execute", executor_agent),  # Receives raw text, hopes for best
])
```

### 5. Document Expected Inputs in Instructions
```python
validator = Agent(
    output_schema=ValidationResult,
    instructions=(
        "You will receive a ParsedQuery with these fields:\n"
        "- action: str (create/update/delete)\n"
        "- entity: str (contact/invoice/etc)\n"
        "- parameters: dict\n\n"
        "Your job: Validate and return ValidationResult with:\n"
        "- operation: The ParsedQuery you received (pass it through)\n"
        "- is_valid: True if all checks pass\n"
        "- validated_params: Clean, API-ready parameters\n"
        "- errors: List of error messages (empty if valid)"
    )
)
```

---

## Comparison: Structured vs Text-Based

### ❌ Text-Based (Fragile)
```python
parser = Agent(instructions="Parse query and return action, entity, params")
result = await parser.arun("create contact ABC")

# Result: "Action: create\nEntity: contact\nParams: name=ABC"
# Now you have to manually parse this string... error-prone!
```

### ✅ Structured (Robust)
```python
parser = Agent(
    output_schema=ParsedQuery,
    instructions="Parse query into structured ParsedQuery"
)
result = await parser.arun("create contact ABC")

# Result: ParsedQuery(action="create", entity="contact", parameters={"name": "ABC"})
# Type-safe, validated, ready to use!
print(result.action)  # IDE autocomplete works!
```

---

## Real-World Example: Xero Workflow

From `xero_workflow_cli.py` - Production pattern with 3-step workflow:

```python
class ParsedOperation(BaseModel):
    action: Literal["list", "create", "update", "delete", "count", "get"]
    entity: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    filters: Optional[Dict[str, Any]] = None
    intent: str

class ValidationResult(BaseModel):
    is_valid: bool
    operation: ParsedOperation  # Nested model
    mcp_tool_name: str
    validated_params: Dict[str, Any]
    pagination_needed: bool = False
    validation_errors: list[str] = Field(default_factory=list)

# Parser Agent
parser = Agent(
    model=Ollama(id="glm-4.6:cloud"),
    output_schema=ParsedOperation,
    instructions=(
        "Extract structured information:\n"
        "1. **Action**: list/create/update/delete/count/get\n"
        "2. **Entity**: invoice/contact/payment/etc\n"
        "3. **Parameters**: Specific values (amounts, names, IDs)\n"
        "4. **Filters**: Conditions (status, dates)\n"
        "5. **Intent**: One-sentence summary"
    )
)

# Validator Agent
validator = Agent(
    model=Ollama(id="deepseek-v3.1:671b-cloud"),
    output_schema=ValidationResult,
    instructions=(
        "Validate and return ValidationResult.\n\n"
        "**CRITICAL: Output must include ALL fields:**\n"
        "1. **operation**: The complete ParsedOperation you received\n"
        "2. **is_valid**: True if passes validation\n"
        "3. **mcp_tool_name**: Exact MCP tool to call\n"
        "4. **validated_params**: API-ready parameters\n"
        "5. **pagination_needed**: True for list operations\n"
        "6. **validation_errors**: List of errors (empty if valid)"
    )
)

# Executor Agent
executor = Agent(
    model=Ollama(id="glm-4.6:cloud"),
    tools=[xero_mcp_tools],
    instructions=(
        "Execute operation using validated parameters.\n"
        "Input: ValidationResult with validated_params.\n"
        "Use validated_params exactly as provided."
    )
)

workflow = Workflow(steps=[
    Step("parse_query", parser),
    Step("validate_operation", validator),
    Step("execute_operation", executor),
])
```

**Benefits in production:**
- ✅ 100% type-safe data flow
- ✅ Automatic validation at each step
- ✅ Clear error messages when validation fails
- ✅ No manual text parsing
- ✅ IDE support for debugging

---

## Key Takeaways

1. **Always use `output_schema`** for multi-step workflows
2. **Explicitly list ALL required fields** in agent instructions
3. **Validate early** - don't let bad data reach execution
4. **Keep schemas flat** - simpler for agents to generate
5. **Debug with `show_step_details=True`** to see structured outputs
6. **Use `Literal` for enums** instead of plain strings
7. **Provide descriptions** for complex fields

Structured outputs transform fragile text-based workflows into robust, type-safe systems. Always prefer structured over text-based communication between agents.

