"""
Privacy-Preserving PDF MCP Server
Extract PDFs with automatic PII redaction for safe LLM analysis
"""
from .extraction_engine import ExtractionEngine
from .redaction_engine import RedactionEngine

__version__ = "1.0.0"
__all__ = ["ExtractionEngine", "RedactionEngine"]
