"""
Command-line interface for markdown query operations.

Provides simple function wrappers for direct invocation without MCP overhead.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union, Any

try:
    # Try relative imports first (when used as package)
    from .mq_engine import MQEngine
    from .obsidian_engine import ObsidianEngine
    from .lint_engine import LintEngine
    from .spec_engine import SpecEngine
    from .performance_engine import PerformanceEngine
    from .core import MarkdownParser, PATTERNS
except ImportError:
    # Fall back to direct imports (when used standalone)
    from mq_engine import MQEngine
    from obsidian_engine import ObsidianEngine
    from lint_engine import LintEngine
    from spec_engine import SpecEngine
    from performance_engine import PerformanceEngine
    from core import MarkdownParser, PATTERNS

_mq = MQEngine()
_obsidian = ObsidianEngine()
_lint = LintEngine()
_spec = SpecEngine()
_perf = PerformanceEngine()


def query(file_path: str, selector: str, output_format: str = 'json') -> Dict[str, Any]:
    """Execute MQ-style query on single file."""
    path = Path(file_path)
    if path.is_dir():
        return {"error": f"Path is a directory. Use 'bulk_query' for '{file_path}'"}
    return _mq.query(file_path, selector, output_format)


def bulk_query(path: Union[str, List[str]], selector: str) -> Dict[str, Any]:
    """Execute MQ-style query across multiple files or directory."""
    if isinstance(path, str):
        p = Path(path)
        if p.is_dir():
            file_paths = [str(f) for f in p.rglob("*.md")]
        elif p.is_file():
            file_paths = [str(p)]
        else:
            return {"error": f"Path not found: {path}"}
    else:
        file_paths = path
    
    if not file_paths:
        return {"error": f"No markdown files found"}
    
    return _mq.bulk_query(file_paths, selector, compact=True)


def analyze_docs(search_path: str) -> Dict[str, Any]:
    """Analyze documentation structure across markdown files."""
    return _mq.analyze_docs(search_path)


def generate_toc(file_path: str, max_depth: int = 3) -> Dict[str, Any]:
    """Generate table of contents from headers."""
    return _mq.generate_toc(file_path, max_depth)


def task_stats(search_path: str) -> Dict[str, Any]:
    """Generate task completion statistics across files."""
    return _mq.task_stats(search_path)


def find_wiki_links(file_path: str, target_link: Optional[str] = None) -> Dict[str, Any]:
    """Find wiki-style [[internal links]] with Obsidian alias support."""
    return _obsidian.find_wiki_links(file_path, target_link)


def find_embedded_content(file_path: str, content_type: Optional[str] = None) -> Dict[str, Any]:
    """Find embedded content using ![[]] syntax (Obsidian transclusion)."""
    return _obsidian.find_embedded_content(file_path, content_type)


def find_block_references(file_path: str) -> Dict[str, Any]:
    """Find block IDs (^block-id) and block links ([[note#^block]])."""
    return _obsidian.find_block_references(file_path)


def find_callouts(file_path: str, callout_type: Optional[str] = None) -> Dict[str, Any]:
    """Find callout/admonition blocks using > [!type] syntax."""
    return _obsidian.find_callouts(file_path, callout_type)


def parse_obsidian_links(file_path: str) -> Dict[str, Any]:
    """Comprehensive Obsidian link parser for all link types."""
    return _obsidian.parse_obsidian_links(file_path)


def extract_dataview_fields(file_path: str, field_name: Optional[str] = None) -> Dict[str, Any]:
    """Extract Dataview inline fields (field:: value)."""
    return _obsidian.extract_dataview_fields(file_path, field_name)


def build_vault_graph(search_path: str) -> Dict[str, Any]:
    """Build a graph structure of vault connections with nodes and edges."""
    return _obsidian.build_vault_graph(search_path)


def find_cross_references(search_path: str, term: str) -> Dict[str, Any]:
    """Find cross-references to a term across markdown files."""
    return _obsidian.find_cross_references(search_path, term)


def lint_document(file_path: str) -> Dict[str, Any]:
    """Analyze document for common markdown issues."""
    return _lint.lint_document(file_path)


def auto_fix(file_path: str, fix_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """Apply deterministic fixes to markdown document.
    
    Fix types: ["headers", "whitespace", "tasks"]
    """
    return _lint.auto_fix_document(file_path, fix_types)


def validate_spec(file_path: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """Validate markdown specification completeness with scoring.
    
    Analysis types: "semantics", "requirements", "constraints", 
                   "dependencies", "completeness", "comprehensive"
    """
    if analysis_type == "semantics":
        return _spec.analyze_spec_semantics(file_path)
    elif analysis_type == "requirements":
        return _spec.extract_spec_requirements(file_path)
    elif analysis_type == "constraints":
        return _spec.extract_spec_constraints(file_path)
    elif analysis_type == "dependencies":
        return _spec.extract_spec_dependencies(file_path)
    elif analysis_type == "completeness":
        return _spec.validate_spec_completeness(file_path)
    else:
        return _spec.validate_spec_document(file_path)


def get_performance_stats() -> Dict[str, Any]:
    """Get comprehensive performance statistics including cache hit ratios."""
    return _perf.get_performance_stats()


def clear_cache(cache_type: str = "all") -> Dict[str, Any]:
    """Clear server caches. Types: "all", "content", "results", "bulk"."""
    _perf.clear_cache(cache_type)
    return {"status": "ok", "message": f"Cleared {cache_type} cache"}


def bulk_analyze(search_path: str, max_files: int = 100) -> Dict[str, Any]:
    """Perform bulk analysis with performance optimization."""
    files = _perf.intelligent_file_discovery(search_path, "*.md", max_size_mb=50)
    if len(files) > max_files:
        files = files[:max_files]
    
    _perf.optimize_for_dataset(len(files), 10)
    
    def analyze_structure(file_path):
        """Helper to analyze single file structure."""
        content = MarkdownParser.read_file(file_path)
        try:
            from .core import safe_findall, safe_finditer
            from .performance_engine import Config
        except ImportError:
            from core import safe_findall, safe_finditer
            from performance_engine import Config
        
        u = Config.REGEX_TIMEOUT_SECONDS
        structure = {
            "headers": len(safe_findall(PATTERNS.HEADERS, content, u)),
            "wiki_links": len(safe_findall(PATTERNS.WIKI_LINKS, content, u)),
            "code_blocks": len(safe_findall(PATTERNS.CODE_BLOCKS, content, u)),
            "tasks": len(safe_findall(PATTERNS.TASKS, content, u)),
        }
        
        return {
            "file": file_path,
            "structure": structure,
            "content": {
                "lines": content.count('\n') + 1,
                "words": len(content.split()),
            }
        }
    
    return _perf.bulk_operation_optimized(
        files, 
        analyze_structure, 
        "bulk_analyze",
        batch_size=Config.MAX_BATCH_SIZE
    )


def get_document_outline(file_path: str) -> Dict[str, Any]:
    """Extract document outline with headers as navigable symbols."""
    content = MarkdownParser.read_file(file_path)
    try:
        from .core import safe_finditer
        from .performance_engine import Config
    except ImportError:
        from core import safe_finditer
        from performance_engine import Config
    
    headers = [
        {
            "level": len(match.group(1)),
            "title": match.group(2).strip(),
            "line": MarkdownParser.get_line_number(content, match.start()),
            "anchor": MarkdownParser.normalize_anchor(match.group(2).strip())
        }
        for match in safe_finditer(PATTERNS.HEADERS, content, Config.REGEX_TIMEOUT_SECONDS)
    ]
    
    return {
        "file": file_path,
        "outline": headers,
        "count": len(headers)
    }

