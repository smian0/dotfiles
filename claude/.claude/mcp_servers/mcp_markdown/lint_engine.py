"""
Document linting and auto-fixing engine.

This module provides comprehensive markdown document analysis, issue detection,
and automated fixing capabilities for common formatting problems.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

try:
    from .core import PATTERNS, MarkdownParser, MarkdownError
except ImportError:
    from core import PATTERNS, MarkdownParser, MarkdownError


class LintEngine:
    """Engine for markdown document linting and auto-fixing operations."""
    
    def lint_document(self, file_path: str) -> Dict[str, Any]:
        """Analyze document for common markdown issues and categorize by fixability."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        lines = content.split('\n')
        
        # Issue categorization
        auto_fixable = []
        review_required = []
        
        # Check header level consistency
        headers = list(PATTERNS.HEADERS.finditer(content))
        if headers:
            header_issues = self._check_header_consistency(headers, content)
            if header_issues:
                auto_fixable.extend(header_issues)
        
        # Check trailing whitespace
        whitespace_issues = self._check_whitespace_issues(lines)
        if whitespace_issues:
            auto_fixable.extend(whitespace_issues)
        
        # Check code blocks without language tags
        code_block_issues = self._check_code_block_languages(content)
        if code_block_issues:
            review_required.extend(code_block_issues)
        
        # Check wiki-link targets
        wiki_link_issues = self._check_wiki_link_targets(file_path, content)
        if wiki_link_issues:
            review_required.extend(wiki_link_issues)
        
        # Check task list formatting
        task_issues = self._check_task_formatting(content)
        if task_issues:
            auto_fixable.extend(task_issues)
        
        # Check frontmatter YAML validity
        frontmatter_issues = self._check_frontmatter_validity(content)
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
            "recommendations": self._generate_fix_recommendations(auto_fixable, review_required)
        }

    def auto_fix_document(self, file_path: str, fix_types: List[str] = None) -> Dict[str, Any]:
        """Apply deterministic fixes to markdown document."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        if fix_types is None:
            fix_types = ["headers", "whitespace", "tasks"]
        
        original_content = content
        applied_fixes = []
        
        # Apply header level fixes
        if "headers" in fix_types:
            content, header_fixes = self._fix_header_consistency(content)
            applied_fixes.extend(header_fixes)
        
        # Apply whitespace fixes
        if "whitespace" in fix_types:
            content, whitespace_fixes = self._fix_whitespace_issues(content)
            applied_fixes.extend(whitespace_fixes)
        
        # Apply task list fixes
        if "tasks" in fix_types:
            content, task_fixes = self._fix_task_formatting(content)
            applied_fixes.extend(task_fixes)
        
        # Write back if changes were made
        if content != original_content:
            path = Path(file_path)
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
    def _check_header_consistency(self, headers: List, content: str) -> List[Dict[str, Any]]:
        """Check for header level consistency issues."""
        issues = []
        for i, header in enumerate(headers):
            level = len(header.group(1))
            line_num = MarkdownParser.get_line_number(content, header.start())
            
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

    def _check_whitespace_issues(self, lines: List[str]) -> List[Dict[str, Any]]:
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

    def _check_code_block_languages(self, content: str) -> List[Dict[str, Any]]:
        """Check for code blocks without language specification."""
        issues = []
        for match in PATTERNS.CODE_BLOCKS.finditer(content):
            line_num = MarkdownParser.get_line_number(content, match.start())
            if not match.group(1):  # No language specified
                issues.append({
                    "type": "missing_code_language",
                    "line": line_num,
                    "message": "Code block missing language specification",
                    "fix": "requires_review"
                })
        return issues

    def _check_wiki_link_targets(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check wiki-links for missing targets."""
        issues = []
        base_dir = Path(file_path).parent
        
        for match in PATTERNS.WIKI_LINKS.finditer(content):
            target = match.group(1)
            line_num = MarkdownParser.get_line_number(content, match.start())
            
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

    def _check_task_formatting(self, content: str) -> List[Dict[str, Any]]:
        """Check task list formatting consistency."""
        issues = []
        for match in PATTERNS.TASKS.finditer(content):
            line_num = MarkdownParser.get_line_number(content, match.start())
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

    def _check_frontmatter_validity(self, content: str) -> List[Dict[str, Any]]:
        """Check YAML frontmatter for validity."""
        issues = []
        frontmatter_match = PATTERNS.FRONTMATTER.match(content)
        
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

    def _fix_header_consistency(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
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

    def _fix_whitespace_issues(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
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

    def _fix_task_formatting(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
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
                    "line": MarkdownParser.get_line_number(content, match.start()),
                    "action": f"normalized checkbox '{checkbox}' to '{normalized}'"
                })
                return f"- [{normalized}] {task_text}"
            
            return match.group(0)
        
        fixed_content = PATTERNS.TASKS.sub(fix_task, content)
        return fixed_content, applied_fixes

    def _generate_fix_recommendations(self, auto_fixable: List[Dict], review_required: List[Dict]) -> List[str]:
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