"""
Observability package for the Financial Agent System.

This package provides:
- Structured logging with configurable levels
- OpenTelemetry-based distributed tracing
- Metrics collection and reporting
"""

from .logging_config import setup_logging, get_logger
from .tracing import setup_tracing, create_span, TracingContext
from .metrics import MetricsCollector, track_latency, track_tool_call

__all__ = [
    "setup_logging",
    "get_logger",
    "setup_tracing",
    "create_span",
    "TracingContext",
    "MetricsCollector",
    "track_latency",
    "track_tool_call",
]
