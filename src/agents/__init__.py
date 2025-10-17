"""
Agent Architecture 3.0 - Unified Agent Framework
The foundation for all 140+ agents in the Autonomous Enterprise Builder
"""

from .base_agent import BaseAgent, MockStateManager, MockToolRegistry

__version__ = "3.0.0"
__all__ = ["BaseAgent", "MockStateManager", "MockToolRegistry"]
