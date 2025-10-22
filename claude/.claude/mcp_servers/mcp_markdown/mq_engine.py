"""
MQ-style selector engine for markdown processing.

This module provides jq-like selectors for structural markdown extraction,
compatible with the MQ (Markdown Query) tool syntax and patterns.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

try:
    from .core import PATTERNS, MarkdownParser, MarkdownError
except ImportError:
    from core import PATTERNS, MarkdownParser, MarkdownError


class MQEngine:
    """Engine for MQ-compatible markdown selectors and queries."""
    
    def __init__(self):
        """Initialize MQ engine with selector mappings."""
        self.selector_map = {
            '.h1': self._extract_h1,
            '.h2': self._extract_h2,
            '.h3': self._extract_h3,
            '.h4': self._extract_h4,
            '.h5': self._extract_h5,
            '.h6': self._extract_h6,
            '.code': self._extract_code,
            '.list': self._extract_list,
            '.link': self._extract_links,
            '.link.url': self._extract_link_urls,
            '.link.text': self._extract_link_text,
            '.table': self._extract_tables,
            '.task': self._extract_tasks,
            '.tag': self._extract_tags,
            '.frontmatter': self._extract_frontmatter_data,
        }
    
    def query(self, file_path: str, selector: str, output_format: str = 'json') -> Union[str, Dict[str, Any]]:
        """Execute MQ-style query on markdown file.

        Supports field-specific queries like:
        - frontmatter.status:active
        - frontmatter.priority:5
        - frontmatter.para-type:project
        """
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}

        # Normalize selector
        selector = selector.strip()

        # Check for field-specific frontmatter queries
        if selector.startswith('frontmatter.') and ':' in selector:
            # Parse field query: frontmatter.FIELD:VALUE
            field_query = selector[len('frontmatter.'):]
            if ':' in field_query:
                field_name, field_value = field_query.split(':', 1)
                field_name = field_name.strip()
                field_value = field_value.strip()

                # Extract frontmatter
                frontmatter = self._extract_frontmatter_data(content)

                # Filter by field
                if field_name in frontmatter:
                    actual_value = str(frontmatter[field_name]).strip()
                    matches = (actual_value.lower() == field_value.lower())

                    if output_format.lower() == 'json':
                        return {
                            "file": file_path,
                            "selector": selector,
                            "matched": matches,
                            "field": field_name,
                            "value": frontmatter[field_name] if matches else None,
                            "results": frontmatter if matches else {}
                        }
                    else:
                        return str(frontmatter[field_name]) if matches else ""
                else:
                    if output_format.lower() == 'json':
                        return {
                            "file": file_path,
                            "selector": selector,
                            "matched": False,
                            "field": field_name,
                            "error": f"Field '{field_name}' not found in frontmatter"
                        }
                    else:
                        return ""

        # Check if selector is in standard map
        if selector not in self.selector_map:
            return {"error": f"Unsupported selector: {selector}"}

        # Execute selector function
        try:
            results = self.selector_map[selector](content)

            if output_format.lower() == 'json':
                return {
                    "file": file_path,
                    "selector": selector,
                    "results": results,
                    "count": len(results) if isinstance(results, list) else 1
                }
            else:
                # Return as markdown/text format
                if isinstance(results, list):
                    return '\n'.join(str(item) for item in results)
                else:
                    return str(results)

        except Exception as e:
            return {"error": f"Query execution failed: {str(e)}"}
    
    def bulk_query(self, file_paths: List[str], selector: str, compact: bool = True) -> Dict[str, Any]:
        """Execute MQ-style query across multiple files.

        Args:
            file_paths: List of file paths to query
            selector: Query selector string
            compact: If True, only return matched file paths for field queries (default: True)
        """
        results = {}
        total_matches = 0
        matched_files = []
        is_field_query = selector.startswith('frontmatter.') and ':' in selector

        for file_path in file_paths:
            file_result = self.query(file_path, selector, 'json')
            if 'error' not in file_result:
                # Handle field-specific queries differently
                if 'matched' in file_result:
                    if file_result['matched']:
                        matched_files.append(file_path)
                        total_matches += 1
                        # Only store full results if not compact mode
                        if not compact:
                            results[file_path] = file_result['results']
                else:
                    # Standard query - always include results
                    results[file_path] = file_result['results']
                    total_matches += file_result.get('count', 0)
            else:
                results[file_path] = {"error": file_result['error']}

        response = {
            "selector": selector,
            "files_processed": len(file_paths),
            "total_matches": total_matches,
        }

        # For field queries in compact mode, only return matched file list
        if is_field_query and compact:
            response['matched_files'] = matched_files
            response['note'] = 'Compact mode: only matched file paths returned. Use compact=False for full results.'
        else:
            # Include full results
            response['results'] = results
            if matched_files:
                response['matched_files'] = matched_files

        return response
    
    def analyze_docs(self, search_path: str) -> Dict[str, Any]:
        """Analyze documentation structure across markdown files (MQ-compatible)."""
        path = Path(search_path)
        files = list(path.rglob("*.md")) if path.is_dir() else [path]
        
        stats = {
            "files_analyzed": len(files),
            "headers": {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0},
            "code_blocks": 0,
            "lists": 0,
            "links": 0,
            "tasks": {"total": 0, "completed": 0, "incomplete": 0},
            "tables": 0,
            "tags": 0
        }
        
        file_details = []
        
        for file_path in files:
            try:
                content = MarkdownParser.read_file(str(file_path))
                
                file_stats = {
                    "file": str(file_path),
                    "headers": {
                        "h1": len(PATTERNS.H1.findall(content)),
                        "h2": len(PATTERNS.H2.findall(content)),
                        "h3": len(PATTERNS.H3.findall(content)),
                        "h4": len(PATTERNS.H4.findall(content)),
                        "h5": len(PATTERNS.H5.findall(content)),
                        "h6": len(PATTERNS.H6.findall(content))
                    },
                    "code_blocks": len(PATTERNS.CODE_BLOCKS.findall(content)),
                    "lists": len(PATTERNS.LIST_ITEMS.findall(content)),
                    "links": len(PATTERNS.EXTERNAL_LINKS.findall(content)),
                    "tasks": len(PATTERNS.TASKS.findall(content)),
                    "tables": len(PATTERNS.TABLES.findall(content)),
                    "tags": len(set(PATTERNS.TAGS.findall(content)))
                }
                
                # Update totals
                for level in stats["headers"]:
                    stats["headers"][level] += file_stats["headers"][level]
                
                stats["code_blocks"] += file_stats["code_blocks"]
                stats["lists"] += file_stats["lists"]
                stats["links"] += file_stats["links"]
                stats["tables"] += file_stats["tables"]
                stats["tags"] += file_stats["tags"]
                
                # Count completed vs incomplete tasks
                for match in PATTERNS.TASKS.finditer(content):
                    stats["tasks"]["total"] += 1
                    if match.group(1) == 'x':
                        stats["tasks"]["completed"] += 1
                    else:
                        stats["tasks"]["incomplete"] += 1
                
                file_details.append(file_stats)
                
            except Exception:
                continue
        
        return {
            "summary": stats,
            "file_details": file_details
        }
    
    def generate_toc(self, file_path: str, max_depth: int = 3) -> Dict[str, Any]:
        """Generate table of contents from headers (MQ-compatible)."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        headers = []
        for match in PATTERNS.HEADERS.finditer(content):
            level = len(match.group(1))
            if level <= max_depth:
                title = match.group(2).strip()
                anchor = MarkdownParser.normalize_anchor(title)
                line_num = MarkdownParser.get_line_number(content, match.start())
                
                headers.append({
                    "level": level,
                    "title": title,
                    "anchor": anchor,
                    "line": line_num
                })
        
        # Generate markdown TOC
        toc_lines = []
        for header in headers:
            indent = "  " * (header["level"] - 1)
            toc_lines.append(f"{indent}- [{header['title']}](#{header['anchor']})")
        
        return {
            "file": file_path,
            "toc_markdown": "\n".join(toc_lines),
            "headers": headers,
            "max_depth": max_depth
        }
    
    def task_stats(self, search_path: str) -> Dict[str, Any]:
        """Generate task completion statistics (MQ-compatible)."""
        path = Path(search_path)
        files = list(path.rglob("*.md")) if path.is_dir() else [path]
        
        total_tasks = 0
        completed_tasks = 0
        file_breakdown = []
        
        for file_path in files:
            try:
                content = MarkdownParser.read_file(str(file_path))
                file_total = 0
                file_completed = 0
                
                for match in PATTERNS.TASKS.finditer(content):
                    file_total += 1
                    if match.group(1) == 'x':
                        file_completed += 1
                
                if file_total > 0:
                    file_breakdown.append({
                        "file": str(file_path),
                        "total": file_total,
                        "completed": file_completed,
                        "incomplete": file_total - file_completed,
                        "completion_rate": file_completed / file_total
                    })
                
                total_tasks += file_total
                completed_tasks += file_completed
                
            except Exception:
                continue
        
        return {
            "summary": {
                "total_files": len(files),
                "files_with_tasks": len(file_breakdown),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "incomplete_tasks": total_tasks - completed_tasks,
                "overall_completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
            },
            "file_breakdown": file_breakdown
        }
    
    def validate_spec(self, file_path: str) -> Dict[str, Any]:
        """Validate markdown specification completeness (MQ-compatible)."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        validation_results = {
            "file": file_path,
            "checks": {},
            "score": 0,
            "issues": []
        }
        
        # Check for H1 header (title)
        h1_headers = PATTERNS.H1.findall(content)
        validation_results["checks"]["has_title"] = len(h1_headers) == 1
        if len(h1_headers) != 1:
            validation_results["issues"].append("Document should have exactly one H1 title")
        
        # Check for structured headers
        headers = list(PATTERNS.HEADERS.finditer(content))
        validation_results["checks"]["has_structure"] = len(headers) >= 2
        if len(headers) < 2:
            validation_results["issues"].append("Document should have multiple headers for structure")
        
        # Check for code examples
        code_blocks = PATTERNS.CODE_BLOCKS.findall(content)
        validation_results["checks"]["has_code_examples"] = len(code_blocks) > 0
        if len(code_blocks) == 0:
            validation_results["issues"].append("Specification should include code examples")
        
        # Check for links (references)
        links = PATTERNS.EXTERNAL_LINKS.findall(content)
        validation_results["checks"]["has_references"] = len(links) > 0
        if len(links) == 0:
            validation_results["issues"].append("Specification should include external references")
        
        # Check for task lists (requirements)
        tasks = PATTERNS.TASKS.findall(content)
        validation_results["checks"]["has_requirements"] = len(tasks) > 0
        if len(tasks) == 0:
            validation_results["issues"].append("Specification should include requirement checklists")
        
        # Calculate score
        total_checks = len(validation_results["checks"])
        passed_checks = sum(1 for check in validation_results["checks"].values() if check)
        validation_results["score"] = passed_checks / total_checks if total_checks > 0 else 0
        
        return validation_results
    
    # Selector implementation functions
    def _extract_h1(self, content: str) -> List[str]:
        """Extract H1 headers."""
        return [match.strip() for match in PATTERNS.H1.findall(content)]
    
    def _extract_h2(self, content: str) -> List[str]:
        """Extract H2 headers."""
        return [match.strip() for match in PATTERNS.H2.findall(content)]
    
    def _extract_h3(self, content: str) -> List[str]:
        """Extract H3 headers."""
        return [match.strip() for match in PATTERNS.H3.findall(content)]
    
    def _extract_h4(self, content: str) -> List[str]:
        """Extract H4 headers."""
        return [match.strip() for match in PATTERNS.H4.findall(content)]
    
    def _extract_h5(self, content: str) -> List[str]:
        """Extract H5 headers."""
        return [match.strip() for match in PATTERNS.H5.findall(content)]
    
    def _extract_h6(self, content: str) -> List[str]:
        """Extract H6 headers.""" 
        return [match.strip() for match in PATTERNS.H6.findall(content)]
    
    def _extract_code(self, content: str) -> List[str]:
        """Extract code blocks with language and content."""
        blocks = []
        for match in PATTERNS.CODE_BLOCKS.finditer(content):
            language = match.group(1) or "text"
            code_content = match.group(2)
            blocks.append(f"```{language}\n{code_content}\n```")
        return blocks
    
    def _extract_list(self, content: str) -> List[str]:
        """Extract list items."""
        return [match.strip() for match in PATTERNS.LIST_ITEMS.findall(content)]
    
    def _extract_links(self, content: str) -> List[str]:
        """Extract all links in [text](url) format."""
        return [match[0] for match in PATTERNS.EXTERNAL_LINKS.findall(content)]
    
    def _extract_link_urls(self, content: str) -> List[str]:
        """Extract link URLs only."""
        return [match[1] for match in PATTERNS.EXTERNAL_LINKS.findall(content)]
    
    def _extract_link_text(self, content: str) -> List[str]:
        """Extract link text only."""
        return [match[0] for match in PATTERNS.EXTERNAL_LINKS.findall(content)]
    
    def _extract_tables(self, content: str) -> List[str]:
        """Extract table rows."""
        return [match.strip() for match in PATTERNS.TABLES.findall(content)]
    
    def _extract_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Extract task list items with completion status."""
        tasks = []
        for match in PATTERNS.TASKS.finditer(content):
            tasks.append({
                "completed": match.group(1) == 'x',
                "text": match.group(2),
                "checkbox": match.group(1)
            })
        return tasks
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract hashtags."""
        return list(set(PATTERNS.TAGS.findall(content)))
    
    def _extract_frontmatter_data(self, content: str) -> Dict[str, Any]:
        """Extract frontmatter as structured data."""
        match = PATTERNS.FRONTMATTER.search(content)
        if not match:
            return {}
        
        # Simple key:value parsing (compatible with MQ expectations)
        metadata = {}
        for line in match.group(1).split('\n'):
            if ':' in line and not line.strip().startswith('#'):
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'[]')
        
        return metadata