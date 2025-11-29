"""
Distributed tracing for the Financial Agent System.

Uses OpenTelemetry for tracing agent execution, tool calls,
and LLM interactions.
"""
from typing import Optional, Dict, Any
from contextlib import contextmanager
from datetime import datetime
import os

from config import config

# Try to import OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None


# Global tracer instance
_tracer: Optional[Any] = None


def setup_tracing(
    service_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    console_export: bool = False
) -> None:
    """
    Set up OpenTelemetry tracing.
    
    Args:
        service_name: Service name for traces
        endpoint: OTLP endpoint for exporting traces
        console_export: Also export traces to console
    """
    global _tracer
    
    if not OTEL_AVAILABLE:
        print("OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk")
        return
    
    service_name = service_name or config.OTEL_SERVICE_NAME
    endpoint = endpoint or config.OTEL_EXPORTER_ENDPOINT
    
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Add console exporter for development
    if console_export:
        provider.add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )
    
    # Add OTLP exporter if endpoint configured
    if endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        except ImportError:
            print("OTLP exporter not available. Install with: pip install opentelemetry-exporter-otlp")
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Get tracer
    _tracer = trace.get_tracer(service_name)


def get_tracer():
    """Get the configured tracer instance."""
    global _tracer
    if _tracer is None and OTEL_AVAILABLE:
        # Initialize with defaults if not set up
        setup_tracing(console_export=False)
    return _tracer


class TracingContext:
    """
    Context manager for creating traced spans.
    """
    
    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        kind: Optional[Any] = None
    ):
        """
        Initialize tracing context.
        
        Args:
            name: Span name
            attributes: Span attributes
            kind: Span kind (INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER)
        """
        self.name = name
        self.attributes = attributes or {}
        self.kind = kind
        self.span = None
        self.token = None
    
    def __enter__(self):
        tracer = get_tracer()
        if tracer:
            span_kind = self.kind or trace.SpanKind.INTERNAL
            self.span = tracer.start_span(
                self.name,
                kind=span_kind,
                attributes=self.attributes
            )
            self.token = trace.use_span(self.span, end_on_exit=True)
            self.token.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                self.span.record_exception(exc_val)
            else:
                self.span.set_status(Status(StatusCode.OK))
            
            if self.token:
                self.token.__exit__(exc_type, exc_val, exc_tb)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        if self.span:
            self.span.set_attribute(key, value)
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the span."""
        if self.span:
            self.span.add_event(name, attributes=attributes)


@contextmanager
def create_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    kind: Optional[str] = None
):
    """
    Create a traced span using context manager.
    
    Args:
        name: Span name
        attributes: Span attributes
        kind: Span kind string (internal, server, client, producer, consumer)
    
    Yields:
        TracingContext instance
    """
    span_kind = None
    if OTEL_AVAILABLE and kind:
        kind_map = {
            "internal": trace.SpanKind.INTERNAL,
            "server": trace.SpanKind.SERVER,
            "client": trace.SpanKind.CLIENT,
            "producer": trace.SpanKind.PRODUCER,
            "consumer": trace.SpanKind.CONSUMER,
        }
        span_kind = kind_map.get(kind.lower())
    
    ctx = TracingContext(name, attributes, span_kind)
    with ctx:
        yield ctx


def trace_agent_execution(agent_name: str, user_id: str, session_id: str):
    """
    Decorator for tracing agent execution.
    
    Args:
        agent_name: Name of the agent
        user_id: User identifier
        session_id: Session identifier
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with create_span(
                f"agent.{agent_name}.execute",
                attributes={
                    "agent.name": agent_name,
                    "user.id": user_id,
                    "session.id": session_id,
                }
            ) as ctx:
                start_time = datetime.now()
                try:
                    result = await func(*args, **kwargs)
                    ctx.set_attribute("agent.success", True)
                    return result
                except Exception as e:
                    ctx.set_attribute("agent.success", False)
                    ctx.set_attribute("agent.error", str(e))
                    raise
                finally:
                    latency = (datetime.now() - start_time).total_seconds() * 1000
                    ctx.set_attribute("agent.latency_ms", latency)
        return wrapper
    return decorator


def trace_tool_call(tool_name: str):
    """
    Decorator for tracing tool calls.
    
    Args:
        tool_name: Name of the tool
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with create_span(
                f"tool.{tool_name}",
                attributes={"tool.name": tool_name}
            ) as ctx:
                start_time = datetime.now()
                try:
                    result = func(*args, **kwargs)
                    ctx.set_attribute("tool.success", True)
                    return result
                except Exception as e:
                    ctx.set_attribute("tool.success", False)
                    ctx.set_attribute("tool.error", str(e))
                    raise
                finally:
                    latency = (datetime.now() - start_time).total_seconds() * 1000
                    ctx.set_attribute("tool.latency_ms", latency)
        return wrapper
    return decorator


"""
Usage Example:

from observability.tracing import setup_tracing, create_span, trace_tool_call

# Initialize tracing
setup_tracing(
    service_name="financial-advisor",
    endpoint="http://localhost:4317",
    console_export=True  # For development
)

# Use context manager
with create_span("analyze_portfolio", {"portfolio.size": 5}) as span:
    result = do_analysis()
    span.set_attribute("analysis.success", True)
    span.add_event("analysis_complete", {"duration_ms": 150})

# Use decorator
@trace_tool_call("get_stock_price")
def get_stock_price(symbol: str):
    return {"price": 100.0}
"""
