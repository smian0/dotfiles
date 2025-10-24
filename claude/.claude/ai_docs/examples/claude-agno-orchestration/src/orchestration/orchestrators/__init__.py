"""
Orchestration Patterns
=======================

Collection of orchestration patterns for coordinating multiple agents.

Available Orchestrators:
- BaseOrchestrator: Abstract base class
- DirectOrchestrator: Direct function calls (simplest)
"""

from .base import BaseOrchestrator, OrchestrationResult
from .direct import DirectOrchestrator

__all__ = [
    'BaseOrchestrator',
    'OrchestrationResult',
    'DirectOrchestrator',
]
