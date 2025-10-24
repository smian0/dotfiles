"""
Workflow Generator

Helpers for creating new workflows in the correct project location.
Similar to Agno's workflow creation pattern.
"""

from pathlib import Path
import os


def get_project_root() -> Path:
    """
    Get the project root directory.

    Looks for common indicators like .git, pyproject.toml, etc.
    Falls back to current working directory.
    """
    cwd = Path.cwd()

    # Check current and parent directories
    check_dir = cwd
    for _ in range(5):  # Check up to 5 levels up
        indicators = [
            check_dir / '.git',
            check_dir / 'pyproject.toml',
            check_dir / 'package.json',
            check_dir / 'setup.py',
            check_dir / '.claude',
        ]

        if any(p.exists() for p in indicators):
            return check_dir

        check_dir = check_dir.parent

    # Fallback to current directory
    return cwd


def get_workflows_dir() -> Path:
    """
    Get the claude_workflows directory for the current project.

    Creates it if it doesn't exist.
    Similar to Agno's agno_workflows/ pattern.

    Returns:
        Path to claude_workflows/ directory
    """
    project_root = get_project_root()
    workflows_dir = project_root / "claude_workflows"

    # Create if doesn't exist
    workflows_dir.mkdir(exist_ok=True)

    return workflows_dir


def create_workflow_directory(workflow_name: str) -> Path:
    """
    Create a directory for a new workflow.

    Similar to Agno's pattern:
        <project_root>/agno_workflows/workflow_name/

    Claude SDK equivalent:
        <project_root>/claude_workflows/workflow_name/

    Args:
        workflow_name: Name of the workflow (e.g., "research_workflow")

    Returns:
        Path to the created workflow directory
    """
    workflows_dir = get_workflows_dir()
    workflow_dir = workflows_dir / workflow_name

    # Create workflow directory
    workflow_dir.mkdir(exist_ok=True)

    # Create docs subdirectory for outputs
    (workflow_dir / "docs").mkdir(exist_ok=True)

    return workflow_dir


def get_workflow_script_path(workflow_name: str) -> Path:
    """
    Get the path for a workflow script.

    Args:
        workflow_name: Name of the workflow

    Returns:
        Path to workflow.py file
    """
    workflow_dir = create_workflow_directory(workflow_name)
    return workflow_dir / "workflow.py"


def copy_template_to_project(template_name: str, workflow_name: str) -> Path:
    """
    Copy a template to the project's claude_workflows directory.

    Args:
        template_name: Name of template (simple, parallel, custom_tool, hybrid)
        workflow_name: Name for the new workflow

    Returns:
        Path to the created workflow file

    Example:
        # Copy simple_workflow template to project
        path = copy_template_to_project("simple", "my_research")
        # Creates: <project_root>/claude_workflows/my_research/workflow.py
    """
    # Get skill templates directory
    skill_dir = Path(__file__).parent.parent
    templates_dir = skill_dir / "templates"

    template_file = templates_dir / f"{template_name}_workflow.py"
    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_name}_workflow.py")

    # Create workflow directory
    workflow_path = get_workflow_script_path(workflow_name)

    # Copy template content
    template_content = template_file.read_text()

    # Update helper path in template (since it will be in a different location)
    # Change from: sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))
    # To: Absolute path to skill helpers
    helpers_dir = skill_dir / "helpers"
    template_content = template_content.replace(
        'sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))',
        f'sys.path.insert(0, "{helpers_dir}")'
    )

    # Write to project
    workflow_path.write_text(template_content)

    # Make executable
    workflow_path.chmod(0o755)

    return workflow_path


def create_workflow_from_template(template: str, workflow_name: str, description: str = "") -> dict:
    """
    Create a new workflow in the project from a template.

    Args:
        template: Template to use (simple, parallel, custom_tool, hybrid)
        workflow_name: Name for the workflow
        description: Optional description

    Returns:
        dict with paths and info

    Example:
        result = create_workflow_from_template(
            template="parallel",
            workflow_name="multi_angle_research",
            description="Research a topic from multiple angles"
        )
        print(f"Created: {result['workflow_path']}")
    """
    workflow_path = copy_template_to_project(template, workflow_name)
    workflow_dir = workflow_path.parent
    docs_dir = workflow_dir / "docs"

    # Create README in workflow directory
    readme_content = f"""# {workflow_name.replace('_', ' ').title()}

{description if description else 'Workflow created from ' + template + ' template'}

## Usage

```bash
# Run workflow
python {workflow_path.name}

# Or make executable and run
chmod +x {workflow_path.name}
./{workflow_path.name}
```

## Structure

- `workflow.py` - Main workflow script
- `docs/` - Output directory for reports

## Template

Based on: `{template}_workflow.py`
"""

    (workflow_dir / "README.md").write_text(readme_content)

    return {
        "workflow_path": workflow_path,
        "workflow_dir": workflow_dir,
        "docs_dir": docs_dir,
        "template": template,
        "name": workflow_name,
        "readme": workflow_dir / "README.md"
    }


def list_workflows() -> list[dict]:
    """
    List all workflows in the project's claude_workflows directory.

    Returns:
        List of workflow info dicts
    """
    workflows_dir = get_workflows_dir()

    workflows = []
    for workflow_dir in sorted(workflows_dir.iterdir()):
        if workflow_dir.is_dir():
            workflow_file = workflow_dir / "workflow.py"
            if workflow_file.exists():
                workflows.append({
                    "name": workflow_dir.name,
                    "path": workflow_file,
                    "dir": workflow_dir,
                    "has_docs": (workflow_dir / "docs").exists(),
                    "has_readme": (workflow_dir / "README.md").exists()
                })

    return workflows


# CLI-friendly function
def create_workflow_interactive():
    """Interactive workflow creation (for use from command line)."""
    print("Claude Agent Workflow Generator")
    print("=" * 50)

    # Choose template
    print("\nAvailable templates:")
    print("1. simple     - Sequential multi-step workflow")
    print("2. parallel   - Parallel subagent execution")
    print("3. custom_tool - Custom MCP tool integration")
    print("4. hybrid     - Sequential + parallel combination")

    template_choice = input("\nSelect template (1-4): ").strip()
    template_map = {"1": "simple", "2": "parallel", "3": "custom_tool", "4": "hybrid"}
    template = template_map.get(template_choice, "simple")

    # Get workflow name
    workflow_name = input("Workflow name (e.g., 'my_research'): ").strip()
    if not workflow_name:
        workflow_name = "new_workflow"

    # Get description
    description = input("Description (optional): ").strip()

    # Create workflow
    print(f"\nCreating workflow '{workflow_name}' from '{template}' template...")
    result = create_workflow_from_template(template, workflow_name, description)

    print(f"\n✓ Workflow created successfully!")
    print(f"\nWorkflow directory: {result['workflow_dir']}")
    print(f"Main script: {result['workflow_path']}")
    print(f"Output directory: {result['docs_dir']}")
    print(f"\nRun with: python {result['workflow_path']}")


if __name__ == "__main__":
    create_workflow_interactive()
