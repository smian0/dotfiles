#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "fastmcp",
# ]
# ///
"""
Unified Markdown MCP Server

Combines MQ-style selectors with advanced Obsidian features and document linting
in a high-performance, cached architecture. Maintains full backward compatibility
with existing MCP clients while providing enhanced functionality.
"""

import subprocess
import sys
from pathlib import Path
from fastmcp import FastMCP

# Handle both package and script execution
try:
    from .core import PATTERNS, MarkdownParser
    from .obsidian_engine import ObsidianEngine
    from .lint_engine import LintEngine
    from .mq_engine import MQEngine
    from .performance_engine import PerformanceEngine
except ImportError:
    # Add current directory to path for direct script execution
    sys.path.insert(0, str(Path(__file__).parent))
    from core import PATTERNS, MarkdownParser
    from obsidian_engine import ObsidianEngine
    from lint_engine import LintEngine
    from mq_engine import MQEngine
    from performance_engine import PerformanceEngine

# Initialize MCP server
mcp = FastMCP()

# Initialize engines
obsidian = ObsidianEngine()
linter = LintEngine()
mq = MQEngine()
performance = PerformanceEngine()

# Standard markdown tools (using core utilities)
@mcp.tool
def get_document_outline(file_path: str):
    """Extract document outline with headers as navigable symbols."""
    # Check cache first
    cached_result = performance.get_cached_result(file_path, "document_outline")
    if cached_result is not None:
        return cached_result
    
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    try:
        content = MarkdownParser.read_file(file_path)
        headers = [
            {
                "level": len(m.group(1)),
                "title": m.group(2).strip(),
                "line": MarkdownParser.get_line_number(content, m.start()),
                "anchor": MarkdownParser.normalize_anchor(m.group(2).strip())
            }
            for m in PATTERNS.HEADERS.finditer(content)
        ]
        
        result = {
            "file": file_path,
            "outline": headers,
            "count": len(headers)
        }
        
        # Cache result
        performance.cache_result(file_path, "document_outline", result)
        return result
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def extract_frontmatter(file_path: str):
    """Extract YAML frontmatter metadata."""
    # Check cache first
    cached_result = performance.get_cached_result(file_path, "frontmatter")
    if cached_result is not None:
        return cached_result
    
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    try:
        content = MarkdownParser.read_file(file_path)
        match = PATTERNS.FRONTMATTER.search(content)
        
        if not match:
            result = {"file": file_path, "has_frontmatter": False, "frontmatter": {}}
        else:
            # Simple key:value parsing
            metadata = {}
            for line in match.group(1).split('\n'):
                if ':' in line and not line.strip().startswith('#'):
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"\'[]')
            
            result = {"file": file_path, "has_frontmatter": True, "frontmatter": metadata}
        
        # Cache result
        performance.cache_result(file_path, "frontmatter", result)
        return result
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def find_code_blocks(file_path: str, language: str = None):
    """Find code blocks, optionally filtered by language."""
    cache_params = {"language": language} if language else None
    cached_result = performance.get_cached_result(file_path, "code_blocks", cache_params)
    if cached_result is not None:
        return cached_result
    
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    try:
        content = MarkdownParser.read_file(file_path)
        blocks = [
            {
                "language": m.group(1) or "text",
                "code": m.group(2),
                "line": MarkdownParser.get_line_number(content, m.start()),
                "length": len(m.group(2).split('\n'))
            }
            for m in PATTERNS.CODE_BLOCKS.finditer(content)
            if not language or (m.group(1) or "").lower() == language.lower()
        ]
        
        result = {
            "file": file_path,
            "code_blocks": blocks,
            "count": len(blocks),
            "languages": list(set(b["language"] for b in blocks))
        }
        
        performance.cache_result(file_path, "code_blocks", result, cache_params)
        return result
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def find_task_lists(file_path: str, status: str = None):
    """Find task lists with completion tracking."""
    cache_params = {"status": status} if status else None
    cached_result = performance.get_cached_result(file_path, "task_lists", cache_params)
    if cached_result is not None:
        return cached_result
    
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    try:
        content = MarkdownParser.read_file(file_path)
        tasks = []
        
        for m in PATTERNS.TASKS.finditer(content):
            completed = m.group(1) == 'x'
            if not status or (status == 'completed' and completed) or (status == 'incomplete' and not completed):
                tasks.append({
                    "completed": completed,
                    "text": m.group(2),
                    "line": MarkdownParser.get_line_number(content, m.start())
                })
        
        completed = sum(1 for t in tasks if t["completed"])
        result = {
            "file": file_path,
            "tasks": tasks,
            "summary": {
                "total": len(tasks),
                "completed": completed,
                "incomplete": len(tasks) - completed,
                "completion_rate": completed / len(tasks) if tasks else 0
            }
        }
        
        performance.cache_result(file_path, "task_lists", result, cache_params)
        return result
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def analyze_document_structure(file_path: str):
    """Comprehensive markdown document analysis with Obsidian features."""
    cached_result = performance.get_cached_result(file_path, "document_structure")
    if cached_result is not None:
        return cached_result
    
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    try:
        content = MarkdownParser.read_file(file_path)
        
        # Count all elements (standard + Obsidian)
        structure = {
            "headers": len(PATTERNS.HEADERS.findall(content)),
            "wiki_links": len(PATTERNS.WIKI_LINKS.findall(content)),
            "external_links": len(PATTERNS.EXTERNAL_LINKS.findall(content)),
            "code_blocks": len(PATTERNS.CODE_BLOCKS.findall(content)),
            "tasks": len(PATTERNS.TASKS.findall(content)),
            "completed_tasks": len([m for m in PATTERNS.TASKS.finditer(content) if m.group(1) == 'x']),
            "tables": len(PATTERNS.TABLES.findall(content)),
            "tags": len(set(PATTERNS.TAGS.findall(content))),
            
            # Obsidian-specific elements
            "embedded_content": len(PATTERNS.EMBEDDED.findall(content)),
            "block_references": len(PATTERNS.BLOCK_REF.findall(content)),
            "block_links": len(PATTERNS.BLOCK_LINK.findall(content)),
            "header_links": len([m for m in PATTERNS.HEADER_LINK.finditer(content) if '#^' not in m.group(0)]),
            "callouts": len(PATTERNS.CALLOUTS.findall(content)),
            "dataview_fields": len(PATTERNS.DATAVIEW_FIELDS.findall(content)),
            "wiki_aliases": len([m for m in PATTERNS.WIKI_LINKS.finditer(content) if m.group(2)])
        }
        
        # Calculate enhanced complexity score
        obsidian_elements = structure["embedded_content"] + structure["block_references"] + structure["callouts"] + structure["dataview_fields"]
        standard_elements = structure["headers"] + structure["wiki_links"] + structure["code_blocks"] + structure["tasks"] + structure["tables"]
        
        result = {
            "file": file_path,
            "structure": structure,
            "content": {
                "lines": content.count('\n') + 1,
                "words": len(content.split()),
                "characters": len(content)
            },
            "complexity_score": standard_elements + obsidian_elements,
            "obsidian_features": {
                "has_embedded": structure["embedded_content"] > 0,
                "has_block_refs": structure["block_references"] > 0,
                "has_callouts": structure["callouts"] > 0,
                "has_dataview": structure["dataview_fields"] > 0,
                "obsidian_score": obsidian_elements
            }
        }
        
        performance.cache_result(file_path, "document_structure", result)
        return result
        
    except Exception as e:
        return {"error": str(e)}

# Obsidian-specific tools (delegate to obsidian engine)
@mcp.tool
def find_wiki_links(file_path: str, target_link: str = None):
    """Find wiki-style [[internal links]] with Obsidian alias support."""
    return obsidian.find_wiki_links(file_path, target_link)

@mcp.tool
def find_embedded_content(file_path: str, content_type: str = None):
    """Find embedded content using ![[]] syntax (Obsidian transclusion)."""
    return obsidian.find_embedded_content(file_path, content_type)

@mcp.tool
def find_block_references(file_path: str):
    """Find block IDs (^block-id) and block links ([[note#^block]])."""
    return obsidian.find_block_references(file_path)

@mcp.tool
def find_callouts(file_path: str, callout_type: str = None):
    """Find callout/admonition blocks using > [!type] syntax."""
    return obsidian.find_callouts(file_path, callout_type)

@mcp.tool
def parse_obsidian_links(file_path: str):
    """Comprehensive Obsidian link parser for all link types."""
    return obsidian.parse_obsidian_links(file_path)

@mcp.tool
def extract_dataview_fields(file_path: str, field_name: str = None):
    """Extract Dataview inline fields (field:: value)."""
    return obsidian.extract_dataview_fields(file_path, field_name)

@mcp.tool
def build_vault_graph(search_path: str):
    """Build a graph structure of vault connections."""
    return obsidian.build_vault_graph(search_path)

@mcp.tool
def find_cross_references(search_path: str, term: str):
    """Find cross-references to a term across markdown files."""
    return obsidian.find_cross_references(search_path, term)

# Linting tools (delegate to lint engine)
@mcp.tool
def lint_document(file_path: str):
    """Analyze document for common markdown issues and categorize by fixability."""
    return linter.lint_document(file_path)

@mcp.tool
def auto_fix_document(file_path: str, fix_types: list = None):
    """Apply deterministic fixes to markdown document."""
    return linter.auto_fix_document(file_path, fix_types)

# MQ-style selector tools (delegate to MQ engine)
@mcp.tool
def mq_query(file_path: str, selector: str, output_format: str = 'json'):
    """Execute MQ-style query on markdown file (e.g., '.h1', '.code', '.list')."""
    return mq.query(file_path, selector, output_format)

@mcp.tool
def mq_bulk_query(file_paths: list, selector: str):
    """Execute MQ-style query across multiple files with performance optimization."""
    # Use performance engine for bulk operations
    def single_query(file_path):
        return mq.query(file_path, selector, 'json')
    
    return performance.bulk_operation_optimized(
        file_paths, single_query, f"mq_query_{selector}"
    )

@mcp.tool
def analyze_docs(search_path: str):
    """Analyze documentation structure across markdown files (MQ-compatible)."""
    return mq.analyze_docs(search_path)

@mcp.tool
def generate_toc(file_path: str, max_depth: int = 3):
    """Generate table of contents from headers (MQ-compatible)."""
    return mq.generate_toc(file_path, max_depth)

@mcp.tool
def task_stats(search_path: str):
    """Generate task completion statistics (MQ-compatible)."""
    return mq.task_stats(search_path)

@mcp.tool
def validate_spec(file_path: str):
    """Validate markdown specification completeness (MQ-compatible)."""
    return mq.validate_spec(file_path)

# Performance and utility tools
@mcp.tool
def get_performance_stats():
    """Get comprehensive performance statistics for the server."""
    return performance.get_performance_stats()

@mcp.tool
def clear_cache(cache_type: str = "all"):
    """Clear server caches (all, content, results, bulk)."""
    performance.clear_cache(cache_type)
    return {"status": "success", "message": f"Cleared {cache_type} cache"}

@mcp.tool
def bulk_analyze(search_path: str, max_files: int = 100):
    """Perform bulk analysis of markdown files with performance optimization."""
    # Discover files intelligently
    files = performance.intelligent_file_discovery(search_path, "*.md", max_size_mb=50)
    if len(files) > max_files:
        files = files[:max_files]
    
    # Optimize performance for dataset
    avg_file_size = 10  # Assume 10KB average
    performance.optimize_for_dataset(len(files), avg_file_size)
    
    def analyze_single_file(file_path):
        return analyze_document_structure(file_path)
    
    return performance.bulk_operation_optimized(
        files, analyze_single_file, "bulk_analyze", batch_size=20
    )

@mcp.tool
def health_check():
    """Check server health and capabilities."""
    try:
        marksman_available = subprocess.run(["marksman", "--version"], 
                                          capture_output=True, timeout=3).returncode == 0
    except:
        marksman_available = False
        
    return {
        "status": "healthy",
        "marksman_available": marksman_available,
        "capabilities": [
            # Standard markdown
            "document_outline", "wiki_links", "cross_references", 
            "frontmatter_extraction", "code_blocks", "task_lists", "document_analysis",
            # Obsidian-specific
            "embedded_content", "block_references", "callouts", "obsidian_links",
            "dataview_fields", "vault_graph", "nested_tags",
            # Linting capabilities
            "document_linting", "auto_fix_document",
            # MQ-compatible selectors
            "mq_selectors", "bulk_queries", "performance_optimization"
        ],
        "obsidian_features": [
            "transclusion", "block_links", "aliases", "callouts", 
            "dataview", "vault_graph", "nested_tags", "header_links"
        ],
        "mq_selectors": [
            ".h1", ".h2", ".h3", ".h4", ".h5", ".h6",
            ".code", ".list", ".link", ".link.url", ".link.text",
            ".table", ".task", ".tag", ".frontmatter"
        ],
        "performance_features": [
            "intelligent_caching", "bulk_operations", "memory_optimization",
            "file_discovery", "dataset_optimization"
        ],
        "version": "1.0.0-unified",
        "engines": {
            "core": "1.0.0",
            "obsidian": "1.0.0", 
            "lint": "1.0.0",
            "mq": "1.0.0",
            "performance": "1.0.0"
        }
    }

if __name__ == "__main__":
    mcp.run(show_banner=False)