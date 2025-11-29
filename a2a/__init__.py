"""
A2A Protocol support for the Financial Agent System.

This package provides Agent-to-Agent (A2A) protocol integration,
allowing the Financial Advisor to communicate with other agents
in a standardized way.
"""

from .a2a_server import create_a2a_app, run_a2a_server

__all__ = ["create_a2a_app", "run_a2a_server"]
