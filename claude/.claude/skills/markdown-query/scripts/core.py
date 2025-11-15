"""
Core utilities and patterns for markdown processing.

This module provides shared regex patterns and utilities used across
all markdown processing engines.
"""

import re
import signal
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable


# Default timeout for regex operations (from environment or 5 seconds)
import os
REGEX_TIMEOUT_SECONDS = int(os.environ.get('MCP_REGEX_TIMEOUT', '5'))

class TimeoutError(Exception):
    """Raised when a regex operation times out."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for regex timeout."""
    raise TimeoutError("Regex operation timed out")


def safe_regex_operation(func: Callable, *args, timeout: int = REGEX_TIMEOUT_SECONDS, **kwargs):
    """Execute a regex operation with timeout protection."""
    try:
        # Set up signal handler for timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Always clean up the alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
            
    except TimeoutError:
        return []  # Return empty list for timed out operations
    except Exception:
        return []  # Return empty list for any other errors


def safe_findall(pattern: re.Pattern, content: str, timeout: int = REGEX_TIMEOUT_SECONDS) -> List:
    """Safe regex findall with timeout protection."""
    return safe_regex_operation(pattern.findall, content, timeout=timeout)


def safe_finditer(pattern: re.Pattern, content: str, timeout: int = REGEX_TIMEOUT_SECONDS):
    """Safe regex finditer with timeout protection."""
    return safe_regex_operation(pattern.finditer, content, timeout=timeout)


def safe_search(pattern: re.Pattern, content: str, timeout: int = REGEX_TIMEOUT_SECONDS):
    """Safe regex search with timeout protection."""
    return safe_regex_operation(pattern.search, content, timeout=timeout)


class PATTERNS:
    """Compiled regex patterns for markdown elements."""
    
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
    
    # MQ-compatible patterns for simple extraction
    H1 = re.compile(r'^# [^#].*$', re.MULTILINE)
    H2 = re.compile(r'^## [^#].*$', re.MULTILINE)
    H3 = re.compile(r'^### [^#].*$', re.MULTILINE)
    H4 = re.compile(r'^#### [^#].*$', re.MULTILINE)
    H5 = re.compile(r'^##### [^#].*$', re.MULTILINE)
    H6 = re.compile(r'^###### [^#].*$', re.MULTILINE)
    LIST_ITEMS = re.compile(r'^[\s]*[-*+] .*$', re.MULTILINE)


class MarkdownParser:
    """Shared markdown parsing utilities."""
    
    @staticmethod
    def read_file(file_path: Union[str, Path]) -> str:
        """Read markdown file content with UTF-8 encoding."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path.read_text(encoding='utf-8')
    
    @staticmethod
    def get_line_number(content: str, match_start: int) -> int:
        """Get line number for a regex match position."""
        return content[:match_start].count('\n') + 1
    
    @staticmethod
    def extract_header_level(header_text: str) -> int:
        """Extract header level from header text."""
        return len(header_text) - len(header_text.lstrip('#'))
    
    @staticmethod
    def normalize_anchor(text: str) -> str:
        """Convert header text to GitHub-style anchor."""
        return text.lower().replace(' ', '-').replace('_', '-')
    
    @staticmethod
    def is_image_path(path: str) -> bool:
        """Check if path is an image file."""
        return path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))
    
    @staticmethod
    def split_lines(content: str) -> List[str]:
        """Split content into lines preserving line endings."""
        return content.split('\n')
    
    @staticmethod
    def count_elements(content: str, pattern: re.Pattern, timeout: int = REGEX_TIMEOUT_SECONDS) -> int:
        """Count occurrences of a pattern in content with timeout protection."""
        results = safe_findall(pattern, content, timeout=timeout)
        return len(results)


class MarkdownError(Exception):
    """Base exception for markdown processing errors."""
    pass


class FileNotFoundError(MarkdownError):
    """Raised when a markdown file is not found."""
    pass


class ParseError(MarkdownError):
    """Raised when parsing fails."""
    pass


# Utility functions for common operations
def get_file_stats(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Get basic statistics about a markdown file."""
    content = MarkdownParser.read_file(file_path)
    
    return {
        "file": str(file_path),
        "content": {
            "lines": content.count('\n') + 1,
            "words": len(content.split()),
            "characters": len(content),
            "bytes": len(content.encode('utf-8'))
        },
        "elements": {
            "headers": MarkdownParser.count_elements(content, PATTERNS.HEADERS),
            "code_blocks": MarkdownParser.count_elements(content, PATTERNS.CODE_BLOCKS),
            "wiki_links": MarkdownParser.count_elements(content, PATTERNS.WIKI_LINKS),
            "external_links": MarkdownParser.count_elements(content, PATTERNS.EXTERNAL_LINKS),
            "tasks": MarkdownParser.count_elements(content, PATTERNS.TASKS),
            "tables": MarkdownParser.count_elements(content, PATTERNS.TABLES)
        }
    }


def validate_selector(selector: str) -> bool:
    """Validate if a selector is supported."""
    valid_selectors = {'.h1', '.h2', '.h3', '.h4', '.h5', '.h6', '.code', '.list', '.link', '.table'}
    valid_modifiers = {'.lang', '.url', '.text'}
    
    # Handle complex selectors like .code.lang or .link.url
    parts = selector.split('.')
    if len(parts) == 2:
        return f'.{parts[1]}' in valid_selectors
    elif len(parts) == 3:
        return f'.{parts[1]}' in valid_selectors and f'.{parts[2]}' in valid_modifiers
    
    return False


def normalize_output_format(format_type: str) -> str:
    """Normalize output format specification."""
    format_type = format_type.lower().strip()
    if format_type in ['markdown', 'md', 'text', 'raw']:
        return 'markdown'
    elif format_type in ['json', 'structured', 'data']:
        return 'json'
    else:
        return 'markdown'  # Default to markdown