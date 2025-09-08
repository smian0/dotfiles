#!/usr/bin/env -S uv run --script

# /// script
# dependencies = ["fastmcp"]
# ///

"""Single-file marksman MCP server for semantic markdown operations."""

import re
import subprocess
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP()

# Standard markdown patterns
HEADERS = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
CODE_BLOCKS = re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL)
FRONTMATTER = re.compile(r'^---\n(.*?)\n---', re.DOTALL | re.MULTILINE)
TASKS = re.compile(r'^- \[([ x])\]\s+(.+)$', re.MULTILINE)
EXTERNAL_LINKS = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
TABLES = re.compile(r'^\|.*\|$', re.MULTILINE)

# Obsidian-enhanced patterns
WIKI_LINKS = re.compile(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]')  # Support aliases
EMBEDDED = re.compile(r'!\[\[([^\]]+)\]\]')  # Transclusion
BLOCK_REF = re.compile(r'\^([a-zA-Z0-9-]+)')  # Block IDs
BLOCK_LINK = re.compile(r'\[\[([^#]+)#\^([^\]]+)\]\]')  # Block links
HEADER_LINK = re.compile(r'\[\[([^#\]]+)#([^\]]+)\]\]')  # Header links (exclude block links)
NESTED_TAGS = re.compile(r'#([a-zA-Z0-9_/-]+)')  # Hierarchical tags
CALLOUTS = re.compile(r'^>\s*\[!([a-z]+)\](.*)$', re.MULTILINE)  # Admonitions
DATAVIEW_FIELDS = re.compile(r'^([a-zA-Z0-9_-]+)::\s*(.+)$', re.MULTILINE)  # Inline fields
TAGS = NESTED_TAGS  # Use enhanced nested tags

@mcp.tool
def get_document_outline(file_path: str):
    """Extract document outline with headers as navigable symbols."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    headers = [
        {
            "level": len(m.group(1)),
            "title": m.group(2).strip(),
            "line": content[:m.start()].count('\n') + 1,
            "anchor": m.group(2).lower().replace(' ', '-')
        }
        for m in HEADERS.finditer(content)
    ]
    
    return {
        "file": file_path,
        "outline": headers,
        "count": len(headers)
    }

@mcp.tool
def find_wiki_links(file_path: str, target_link: str = None):
    """Find wiki-style [[internal links]] with Obsidian alias support."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    links = []
    
    for m in WIKI_LINKS.finditer(content):
        target = m.group(1)
        alias = m.group(2) if m.group(2) else target
        
        # Check if matches target filter (search both target and alias)
        if not target_link or (target_link.lower() in target.lower() or target_link.lower() in alias.lower()):
            links.append({
                "target": target,
                "alias": alias,
                "display_text": alias,
                "has_alias": bool(m.group(2)),
                "line": content[:m.start()].count('\n') + 1,
                "match": m.group(0)
            })
    
    return {
        "file": file_path,
        "wiki_links": links,
        "count": len(links),
        "aliases_count": sum(1 for link in links if link["has_alias"])
    }

@mcp.tool
def find_embedded_content(file_path: str, content_type: str = None):
    """Find embedded content using ![[]] syntax (Obsidian transclusion)."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    embeds = []
    
    for m in EMBEDDED.finditer(content):
        embed_path = m.group(1)
        is_image = embed_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))
        embed_type = "image" if is_image else "note"
        
        if not content_type or content_type == embed_type:
            embeds.append({
                "path": embed_path,
                "type": embed_type,
                "line": content[:m.start()].count('\n') + 1,
                "match": m.group(0)
            })
    
    return {
        "file": file_path,
        "embedded_content": embeds,
        "count": len(embeds),
        "types": list(set(e["type"] for e in embeds))
    }

@mcp.tool
def find_block_references(file_path: str):
    """Find block IDs (^block-id) and block links ([[note#^block]])."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    block_ids = []
    block_links = []
    
    # Find block IDs in the current file
    for m in BLOCK_REF.finditer(content):
        block_ids.append({
            "block_id": m.group(1),
            "line": content[:m.start()].count('\n') + 1,
            "match": m.group(0)
        })
    
    # Find block links referencing other files
    for m in BLOCK_LINK.finditer(content):
        block_links.append({
            "target_file": m.group(1),
            "block_id": m.group(2),
            "line": content[:m.start()].count('\n') + 1,
            "match": m.group(0)
        })
    
    return {
        "file": file_path,
        "block_ids": block_ids,
        "block_links": block_links,
        "block_id_count": len(block_ids),
        "block_link_count": len(block_links)
    }

@mcp.tool
def find_callouts(file_path: str, callout_type: str = None):
    """Find callout/admonition blocks using > [!type] syntax."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    callouts = []
    
    for m in CALLOUTS.finditer(content):
        c_type = m.group(1)
        c_content = m.group(2).strip()
        
        if not callout_type or callout_type.lower() == c_type.lower():
            callouts.append({
                "type": c_type,
                "content": c_content,
                "line": content[:m.start()].count('\n') + 1,
                "match": m.group(0)
            })
    
    return {
        "file": file_path,
        "callouts": callouts,
        "count": len(callouts),
        "types": list(set(c["type"] for c in callouts))
    }

@mcp.tool
def parse_obsidian_links(file_path: str):
    """Comprehensive Obsidian link parser for all link types."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    results = {
        "wiki_links": [],
        "header_links": [],
        "block_links": [],
        "embedded_content": [],
        "external_links": []
    }
    
    # Parse wiki links with optional aliases
    for m in WIKI_LINKS.finditer(content):
        link = {
            "target": m.group(1),
            "alias": m.group(2) if m.group(2) else m.group(1),
            "line": content[:m.start()].count('\n') + 1,
            "match": m.group(0)
        }
        results["wiki_links"].append(link)
    
    # Parse header links
    for m in HEADER_LINK.finditer(content):
        # Exclude block links (those with ^)
        if '#^' not in m.group(0):
            link = {
                "target_file": m.group(1),
                "header": m.group(2),
                "line": content[:m.start()].count('\n') + 1,
                "match": m.group(0)
            }
            results["header_links"].append(link)
    
    # Parse block links
    for m in BLOCK_LINK.finditer(content):
        link = {
            "target_file": m.group(1),
            "block_id": m.group(2),
            "line": content[:m.start()].count('\n') + 1,
            "match": m.group(0)
        }
        results["block_links"].append(link)
    
    # Parse embedded content
    for m in EMBEDDED.finditer(content):
        embed = {
            "path": m.group(1),
            "type": "image" if m.group(1).lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')) else "note",
            "line": content[:m.start()].count('\n') + 1,
            "match": m.group(0)
        }
        results["embedded_content"].append(embed)
    
    # Parse external links
    for m in EXTERNAL_LINKS.finditer(content):
        link = {
            "text": m.group(1),
            "url": m.group(2),
            "line": content[:m.start()].count('\n') + 1,
            "match": m.group(0)
        }
        results["external_links"].append(link)
    
    # Add counts (create new dict to avoid iteration issues)
    counts = {}
    for key in results:
        counts[f"{key}_count"] = len(results[key])
    
    results.update(counts)
    results["file"] = file_path
    results["total_links"] = sum(len(v) for k, v in results.items() if isinstance(v, list) and not k.endswith('_count'))
    
    return results

@mcp.tool
def extract_dataview_fields(file_path: str, field_name: str = None):
    """Extract Dataview inline fields (field:: value)."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    fields = []
    
    for m in DATAVIEW_FIELDS.finditer(content):
        f_name = m.group(1)
        f_value = m.group(2)
        
        if not field_name or field_name.lower() == f_name.lower():
            fields.append({
                "field": f_name,
                "value": f_value,
                "line": content[:m.start()].count('\n') + 1,
                "match": m.group(0)
            })
    
    return {
        "file": file_path,
        "dataview_fields": fields,
        "count": len(fields),
        "field_names": list(set(f["field"] for f in fields))
    }

@mcp.tool
def build_vault_graph(search_path: str):
    """Build a graph structure of vault connections."""
    path = Path(search_path)
    files = [path] if path.is_file() else list(path.rglob("*.md"))
    
    nodes = []
    edges = []
    
    for file in files:
        try:
            content = file.read_text(encoding='utf-8')
            file_name = file.stem
            
            # Create node
            node = {
                "id": file_name,
                "path": str(file),
                "title": file_name,
                "links_out": 0,
                "links_in": 0
            }
            
            # Count outgoing links
            outgoing_targets = set()
            for m in WIKI_LINKS.finditer(content):
                target = m.group(1).split('|')[0]  # Remove alias part
                if target != file_name:  # Avoid self-links
                    outgoing_targets.add(target)
                    edges.append({
                        "source": file_name,
                        "target": target,
                        "type": "wiki_link"
                    })
            
            node["links_out"] = len(outgoing_targets)
            nodes.append(node)
            
        except Exception:
            continue
    
    # Calculate incoming links
    node_map = {node["id"]: node for node in nodes}
    for edge in edges:
        if edge["target"] in node_map:
            node_map[edge["target"]]["links_in"] += 1
    
    return {
        "vault_path": str(path),
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "avg_connections": len(edges) / len(nodes) if nodes else 0
        }
    }

@mcp.tool
def find_cross_references(search_path: str, term: str):
    """Find cross-references to a term across markdown files."""
    path = Path(search_path)
    files = [path] if path.is_file() else list(path.rglob("*.md"))
    references = []
    
    for file in files:
        try:
            content = file.read_text(encoding='utf-8')
            contexts = []
            
            # Headers, wiki links, text
            for pattern, ref_type in [
                (rf'#{1,6}\s+.*{re.escape(term)}.*', "header"),
                (rf'\[\[.*{re.escape(term)}.*\]\]', "wiki_link"),
                (rf'\b{re.escape(term)}\b', "text")
            ]:
                for m in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content[:m.start()].count('\n') + 1
                    line_text = content.split('\n')[line_num - 1] if ref_type == "text" else m.group(0)
                    contexts.append({"type": ref_type, "line": line_num, "text": line_text.strip()})
            
            if contexts:
                references.append({"file": str(file), "references": contexts})
        except:
            continue
    
    return {
        "term": term,
        "files_searched": len(files),
        "files_with_matches": len(references),
        "cross_references": references
    }

@mcp.tool
def extract_frontmatter(file_path: str):
    """Extract YAML frontmatter metadata."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    match = FRONTMATTER.search(content)
    
    if not match:
        return {"file": file_path, "has_frontmatter": False, "frontmatter": {}}
    
    # Simple key:value parsing
    metadata = {}
    for line in match.group(1).split('\n'):
        if ':' in line and not line.strip().startswith('#'):
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"\'[]')
    
    return {"file": file_path, "has_frontmatter": True, "frontmatter": metadata}

@mcp.tool
def find_code_blocks(file_path: str, language: str = None):
    """Find code blocks, optionally filtered by language."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    blocks = [
        {
            "language": m.group(1) or "text",
            "code": m.group(2),
            "line": content[:m.start()].count('\n') + 1,
            "length": len(m.group(2).split('\n'))
        }
        for m in CODE_BLOCKS.finditer(content)
        if not language or (m.group(1) or "").lower() == language.lower()
    ]
    
    return {
        "file": file_path,
        "code_blocks": blocks,
        "count": len(blocks),
        "languages": list(set(b["language"] for b in blocks))
    }

@mcp.tool
def find_task_lists(file_path: str, status: str = None):
    """Find task lists with completion tracking."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    tasks = []
    
    for m in TASKS.finditer(content):
        completed = m.group(1) == 'x'
        if not status or (status == 'completed' and completed) or (status == 'incomplete' and not completed):
            tasks.append({
                "completed": completed,
                "text": m.group(2),
                "line": content[:m.start()].count('\n') + 1
            })
    
    completed = sum(1 for t in tasks if t["completed"])
    return {
        "file": file_path,
        "tasks": tasks,
        "summary": {
            "total": len(tasks),
            "completed": completed,
            "incomplete": len(tasks) - completed,
            "completion_rate": completed / len(tasks) if tasks else 0
        }
    }

@mcp.tool
def analyze_document_structure(file_path: str):
    """Comprehensive markdown document analysis with Obsidian features."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    
    # Count all elements (standard + Obsidian)
    structure = {
        "headers": len(HEADERS.findall(content)),
        "wiki_links": len(WIKI_LINKS.findall(content)),
        "external_links": len(EXTERNAL_LINKS.findall(content)),
        "code_blocks": len(CODE_BLOCKS.findall(content)),
        "tasks": len(TASKS.findall(content)),
        "completed_tasks": len([m for m in TASKS.finditer(content) if m.group(1) == 'x']),
        "tables": len(TABLES.findall(content)),
        "tags": len(set(NESTED_TAGS.findall(content))),
        
        # Obsidian-specific elements
        "embedded_content": len(EMBEDDED.findall(content)),
        "block_references": len(BLOCK_REF.findall(content)),
        "block_links": len(BLOCK_LINK.findall(content)),
        "header_links": len([m for m in HEADER_LINK.finditer(content) if '#^' not in m.group(0)]),
        "callouts": len(CALLOUTS.findall(content)),
        "dataview_fields": len(DATAVIEW_FIELDS.findall(content)),
        "wiki_aliases": len([m for m in WIKI_LINKS.finditer(content) if m.group(2)])
    }
    
    # Calculate enhanced complexity score
    obsidian_elements = structure["embedded_content"] + structure["block_references"] + structure["callouts"] + structure["dataview_fields"]
    standard_elements = structure["headers"] + structure["wiki_links"] + structure["code_blocks"] + structure["tasks"] + structure["tables"]
    
    return {
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

@mcp.tool
def lint_document(file_path: str):
    """Analyze document for common markdown issues and categorize by fixability."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Issue categorization
    auto_fixable = []
    review_required = []
    
    # Check header level consistency
    headers = list(HEADERS.finditer(content))
    if headers:
        header_issues = _check_header_consistency(headers, content)
        if header_issues:
            auto_fixable.extend(header_issues)
    
    # Check trailing whitespace
    whitespace_issues = _check_whitespace_issues(lines)
    if whitespace_issues:
        auto_fixable.extend(whitespace_issues)
    
    # Check code blocks without language tags
    code_block_issues = _check_code_block_languages(content)
    if code_block_issues:
        review_required.extend(code_block_issues)
    
    # Check wiki-link targets
    wiki_link_issues = _check_wiki_link_targets(file_path, content)
    if wiki_link_issues:
        review_required.extend(wiki_link_issues)
    
    # Check task list formatting
    task_issues = _check_task_formatting(content)
    if task_issues:
        auto_fixable.extend(task_issues)
    
    # Check frontmatter YAML validity
    frontmatter_issues = _check_frontmatter_validity(content)
    if frontmatter_issues:
        review_required.extend(frontmatter_issues)
    
    # Calculate severity scores
    total_issues = len(auto_fixable) + len(review_required)
    severity = "low" if total_issues <= 2 else "medium" if total_issues <= 5 else "high"
    
    return {
        "file": file_path,
        "summary": {
            "total_issues": total_issues,
            "auto_fixable": len(auto_fixable),
            "review_required": len(review_required),
            "severity": severity
        },
        "issues": {
            "auto_fixable": auto_fixable,
            "review_required": review_required
        },
        "recommendations": _generate_fix_recommendations(auto_fixable, review_required)
    }

@mcp.tool
def auto_fix_document(file_path: str, fix_types: list = None):
    """Apply deterministic fixes to markdown document."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    if fix_types is None:
        fix_types = ["headers", "whitespace", "tasks"]
    
    content = path.read_text(encoding='utf-8')
    original_content = content
    applied_fixes = []
    
    # Apply header level fixes
    if "headers" in fix_types:
        content, header_fixes = _fix_header_consistency(content)
        applied_fixes.extend(header_fixes)
    
    # Apply whitespace fixes
    if "whitespace" in fix_types:
        content, whitespace_fixes = _fix_whitespace_issues(content)
        applied_fixes.extend(whitespace_fixes)
    
    # Apply task list fixes
    if "tasks" in fix_types:
        content, task_fixes = _fix_task_formatting(content)
        applied_fixes.extend(task_fixes)
    
    # Write back if changes were made
    if content != original_content:
        path.write_text(content, encoding='utf-8')
        return {
            "file": file_path,
            "status": "fixed",
            "applied_fixes": applied_fixes,
            "changes_made": len(applied_fixes)
        }
    else:
        return {
            "file": file_path,
            "status": "no_changes_needed",
            "applied_fixes": [],
            "changes_made": 0
        }

# Helper functions for linting operations
def _check_header_consistency(headers, content):
    """Check for header level consistency issues."""
    issues = []
    for i, header in enumerate(headers):
        level = len(header.group(1))
        line_num = content[:header.start()].count('\n') + 1
        
        # Check if header levels skip (e.g., H1 -> H3)
        if i > 0:
            prev_level = len(headers[i-1].group(1))
            if level - prev_level > 1:
                issues.append({
                    "type": "header_level_skip",
                    "line": line_num,
                    "message": f"Header level jumps from H{prev_level} to H{level}",
                    "fix": "auto_adjustable"
                })
        
        # Check for level 1 headers in non-root positions
        if level == 1 and i > 0:
            issues.append({
                "type": "misplaced_h1",
                "line": line_num,
                "message": "Multiple H1 headers found - should be unique",
                "fix": "convert_to_h2"
            })
    
    return issues

def _check_whitespace_issues(lines):
    """Check for trailing whitespace and spacing issues."""
    issues = []
    for i, line in enumerate(lines):
        if line.rstrip() != line:
            issues.append({
                "type": "trailing_whitespace",
                "line": i + 1,
                "message": "Line has trailing whitespace",
                "fix": "remove_trailing"
            })
    return issues

def _check_code_block_languages(content):
    """Check for code blocks without language specification."""
    issues = []
    for match in CODE_BLOCKS.finditer(content):
        line_num = content[:match.start()].count('\n') + 1
        if not match.group(1):  # No language specified
            issues.append({
                "type": "missing_code_language",
                "line": line_num,
                "message": "Code block missing language specification",
                "fix": "requires_review"
            })
    return issues

def _check_wiki_link_targets(file_path, content):
    """Check wiki-links for missing targets."""
    issues = []
    base_dir = Path(file_path).parent
    
    for match in WIKI_LINKS.finditer(content):
        target = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        
        # Check if target file exists (basic check)
        target_path = base_dir / f"{target}.md"
        if not target_path.exists():
            issues.append({
                "type": "broken_wiki_link",
                "line": line_num,
                "target": target,
                "message": f"Wiki-link target '{target}' not found",
                "fix": "requires_review"
            })
    
    return issues

def _check_task_formatting(content):
    """Check task list formatting consistency."""
    issues = []
    for match in TASKS.finditer(content):
        line_num = content[:match.start()].count('\n') + 1
        checkbox = match.group(1)
        
        # Check for malformed checkboxes
        if checkbox not in [' ', 'x']:
            issues.append({
                "type": "malformed_task",
                "line": line_num,
                "message": f"Invalid task checkbox '{checkbox}' - should be ' ' or 'x'",
                "fix": "normalize_checkbox"
            })
    
    return issues

def _check_frontmatter_validity(content):
    """Check YAML frontmatter for validity."""
    issues = []
    frontmatter_match = FRONTMATTER.match(content)
    
    if frontmatter_match:
        try:
            import yaml
            yaml.safe_load(frontmatter_match.group(1))
        except ImportError:
            # YAML library not available, skip validation
            pass
        except Exception as e:
            issues.append({
                "type": "invalid_frontmatter",
                "line": 1,
                "message": f"Invalid YAML frontmatter: {str(e)}",
                "fix": "requires_review"
            })
    
    return issues

def _fix_header_consistency(content):
    """Fix header level consistency issues."""
    lines = content.split('\n')
    applied_fixes = []
    
    # Convert level 1 headers after the first one to level 2
    h1_count = 0
    for i, line in enumerate(lines):
        if line.startswith('# ') and not line.startswith('## '):
            h1_count += 1
            if h1_count > 1:
                lines[i] = '##' + line[1:]  # Convert H1 to H2
                applied_fixes.append({
                    "type": "header_level_fix",
                    "line": i + 1,
                    "action": "converted H1 to H2"
                })
    
    return '\n'.join(lines), applied_fixes

def _fix_whitespace_issues(content):
    """Fix trailing whitespace issues."""
    lines = content.split('\n')
    applied_fixes = []
    
    for i, line in enumerate(lines):
        original_line = line
        line = line.rstrip()
        if original_line != line:
            lines[i] = line
            applied_fixes.append({
                "type": "whitespace_fix",
                "line": i + 1,
                "action": "removed trailing whitespace"
            })
    
    return '\n'.join(lines), applied_fixes

def _fix_task_formatting(content):
    """Fix task list formatting issues."""
    applied_fixes = []
    
    def fix_task(match):
        checkbox = match.group(1)
        task_text = match.group(2)
        
        # Normalize checkbox
        if checkbox not in [' ', 'x']:
            normalized = ' ' if checkbox.lower() != 'x' else 'x'
            applied_fixes.append({
                "type": "task_fix",
                "line": content[:match.start()].count('\n') + 1,
                "action": f"normalized checkbox '{checkbox}' to '{normalized}'"
            })
            return f"- [{normalized}] {task_text}"
        
        return match.group(0)
    
    fixed_content = TASKS.sub(fix_task, content)
    return fixed_content, applied_fixes

def _generate_fix_recommendations(auto_fixable, review_required):
    """Generate actionable recommendations for fixes."""
    recommendations = []
    
    if auto_fixable:
        recommendations.append("Run auto_fix_document() to automatically fix deterministic issues")
    
    if any(issue["type"] == "missing_code_language" for issue in review_required):
        recommendations.append("Review code blocks and add appropriate language tags")
    
    if any(issue["type"] == "broken_wiki_link" for issue in review_required):
        recommendations.append("Check wiki-link targets and update broken references")
    
    if any(issue["type"] == "invalid_frontmatter" for issue in review_required):
        recommendations.append("Fix YAML syntax errors in frontmatter")
    
    return recommendations

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
            "document_linting", "auto_fix_document"
        ],
        "obsidian_features": [
            "transclusion", "block_links", "aliases", "callouts", 
            "dataview", "vault_graph", "nested_tags", "header_links"
        ],
        "version": "4.0-obsidian-enhanced"
    }

if __name__ == "__main__":
    mcp.run(show_banner=False)