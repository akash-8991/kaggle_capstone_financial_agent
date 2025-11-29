"""
Sub-agents for the Financial Agent System.

This package contains specialized agents for different aspects of
financial decision support:
- Research agents (parallel data gathering)
- Analysis agents (sequential analysis pipeline)
- Recommendation agents (loop-based refinement)
"""

from .research_agent import create_research_agent, parallel_research_agent
from .analysis_agent import create_analysis_pipeline
from .recommendation_agent import create_recommendation_loop

__all__ = [
    "create_research_agent",
    "parallel_research_agent",
    "create_analysis_pipeline",
    "create_recommendation_loop",
]
