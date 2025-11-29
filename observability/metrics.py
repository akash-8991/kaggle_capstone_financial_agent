"""
Metrics collection for the Financial Agent System.

Provides lightweight metrics collection for monitoring
agent performance, tool usage, and system health.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import time
from functools import wraps

from config import config


class MetricsCollector:
    """
    Thread-safe metrics collector for agent observability.
    
    Collects:
    - Counters: Cumulative counts (requests, errors, tool calls)
    - Gauges: Current values (active sessions, queue size)
    - Histograms: Distribution of values (latencies)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for global metrics access."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._histogram_max_size = 1000  # Keep last 1000 values
        self._lock = threading.Lock()
        self._start_time = datetime.now()
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Increment value
            tags: Optional tags for the metric
        """
        key = self._make_key(name, tags)
        with self._lock:
            self._counters[key] += value
    
    def decrement(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Decrement a counter metric."""
        self.increment(name, -value, tags)
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge metric.
        
        Args:
            name: Metric name
            value: Gauge value
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        with self._lock:
            self._gauges[key] = value
    
    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a histogram value.
        
        Args:
            name: Metric name
            value: Value to record
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        with self._lock:
            self._histograms[key].append(value)
            # Limit size
            if len(self._histograms[key]) > self._histogram_max_size:
                self._histograms[key] = self._histograms[key][-self._histogram_max_size:]
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Create a unique key from name and tags."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> int:
        """Get counter value."""
        key = self._make_key(name, tags)
        return self._counters.get(key, 0)
    
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get gauge value."""
        key = self._make_key(name, tags)
        return self._gauges.get(key)
    
    def get_histogram_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """
        Get histogram statistics.
        
        Returns:
            Dictionary with count, min, max, avg, p50, p90, p99
        """
        key = self._make_key(name, tags)
        values = self._histograms.get(key, [])
        
        if not values:
            return {"count": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": sum(values) / count,
            "p50": sorted_values[int(count * 0.50)],
            "p90": sorted_values[int(count * 0.90)] if count >= 10 else sorted_values[-1],
            "p99": sorted_values[int(count * 0.99)] if count >= 100 else sorted_values[-1],
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics as a dictionary.
        
        Returns:
            Dictionary containing all metrics
        """
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        histogram_stats = {}
        for key in self._histograms:
            histogram_stats[key] = self.get_histogram_stats(key.split("[")[0])
        
        return {
            "uptime_seconds": uptime,
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": histogram_stats,
            "collected_at": datetime.now().isoformat(),
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._start_time = datetime.now()


# Global metrics instance
metrics = MetricsCollector()


def track_latency(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """
    Decorator to track function latency.
    
    Args:
        metric_name: Name for the latency metric
        tags: Optional tags
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                metrics.increment(f"{metric_name}.success", tags=tags)
                return result
            except Exception as e:
                metrics.increment(f"{metric_name}.error", tags=tags)
                raise
            finally:
                latency_ms = (time.time() - start) * 1000
                metrics.histogram(f"{metric_name}.latency_ms", latency_ms, tags=tags)
        return wrapper
    return decorator


def track_latency_async(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """
    Async decorator to track function latency.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                metrics.increment(f"{metric_name}.success", tags=tags)
                return result
            except Exception as e:
                metrics.increment(f"{metric_name}.error", tags=tags)
                raise
            finally:
                latency_ms = (time.time() - start) * 1000
                metrics.histogram(f"{metric_name}.latency_ms", latency_ms, tags=tags)
        return wrapper
    return decorator


def track_tool_call(tool_name: str):
    """
    Track a tool call.
    
    Args:
        tool_name: Name of the tool
    """
    tags = {"tool": tool_name}
    metrics.increment("tool.calls", tags=tags)


def track_agent_request(agent_name: str, user_id: str):
    """
    Track an agent request.
    
    Args:
        agent_name: Name of the agent
        user_id: User identifier
    """
    metrics.increment("agent.requests", tags={"agent": agent_name})
    metrics.increment("user.requests", tags={"user": user_id})


def track_active_sessions(count: int):
    """Track number of active sessions."""
    metrics.gauge("sessions.active", count)


def track_llm_tokens(prompt_tokens: int, completion_tokens: int, model: str):
    """
    Track LLM token usage.
    
    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        model: Model name
    """
    tags = {"model": model}
    metrics.increment("llm.prompt_tokens", prompt_tokens, tags=tags)
    metrics.increment("llm.completion_tokens", completion_tokens, tags=tags)
    metrics.increment("llm.total_tokens", prompt_tokens + completion_tokens, tags=tags)


class MetricsEndpoint:
    """
    Simple metrics endpoint for Prometheus-style scraping.
    """
    
    @staticmethod
    def format_prometheus() -> str:
        """
        Format metrics in Prometheus exposition format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        all_metrics = metrics.get_all_metrics()
        
        # Counters
        for name, value in all_metrics["counters"].items():
            clean_name = name.replace(".", "_").replace("[", "{").replace("]", "}")
            lines.append(f"financial_advisor_{clean_name} {value}")
        
        # Gauges
        for name, value in all_metrics["gauges"].items():
            clean_name = name.replace(".", "_").replace("[", "{").replace("]", "}")
            lines.append(f"financial_advisor_{clean_name} {value}")
        
        # Histograms (simplified - just avg and p99)
        for name, stats in all_metrics["histograms"].items():
            clean_name = name.replace(".", "_").replace("[", "{").replace("]", "}")
            if "avg" in stats:
                lines.append(f"financial_advisor_{clean_name}_avg {stats['avg']:.2f}")
            if "p99" in stats:
                lines.append(f"financial_advisor_{clean_name}_p99 {stats['p99']:.2f}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_json() -> Dict[str, Any]:
        """
        Format metrics as JSON.
        
        Returns:
            Metrics dictionary
        """
        return metrics.get_all_metrics()


"""
Usage Example:

from observability.metrics import metrics, track_latency, track_tool_call

# Direct metric recording
metrics.increment("requests.total")
metrics.gauge("active.users", 42)
metrics.histogram("request.latency_ms", 150.5)

# Using decorators
@track_latency("portfolio_analysis", tags={"type": "full"})
def analyze_portfolio(holdings):
    # ... analysis logic
    return result

# Track tool calls
track_tool_call("get_stock_price")

# Get metrics
all_metrics = metrics.get_all_metrics()
print(all_metrics)

# Prometheus format
from observability.metrics import MetricsEndpoint
prometheus_output = MetricsEndpoint.format_prometheus()
"""
