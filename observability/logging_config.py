"""
Logging configuration for the Financial Agent System.

Provides structured logging with JSON formatting for production
and human-readable formatting for development.
"""
import logging
import sys
from datetime import datetime
from typing import Optional
import os

from config import config


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs for production.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        import json
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "agent_name"):
            log_data["agent_name"] = record.agent_name
        if hasattr(record, "tool_name"):
            log_data["tool_name"] = record.tool_name
        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class DevelopmentFormatter(logging.Formatter):
    """
    Human-readable formatter for development.
    """
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Build the log line
        log_line = (
            f"{color}[{timestamp}] {record.levelname:8}{self.RESET} "
            f"{record.name}: {record.getMessage()}"
        )
        
        # Add context info if present
        extras = []
        if hasattr(record, "user_id"):
            extras.append(f"user={record.user_id}")
        if hasattr(record, "agent_name"):
            extras.append(f"agent={record.agent_name}")
        if hasattr(record, "tool_name"):
            extras.append(f"tool={record.tool_name}")
        if hasattr(record, "latency_ms"):
            extras.append(f"latency={record.latency_ms}ms")
        
        if extras:
            log_line += f" [{', '.join(extras)}]"
        
        return log_line


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_format: bool = False
) -> None:
    """
    Set up logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        json_format: Use JSON formatting (for production)
    """
    level = level or config.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Choose formatter
    if json_format or os.getenv("PRODUCTION", "").lower() == "true":
        formatter = StructuredFormatter()
    else:
        formatter = DevelopmentFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(StructuredFormatter())  # Always JSON for files
        root_logger.addHandler(file_handler)
    
    # Set levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds context to log messages.
    """
    
    def process(self, msg, kwargs):
        # Add extra context to the record
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


def get_context_logger(
    name: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    agent_name: Optional[str] = None
) -> LoggerAdapter:
    """
    Get a logger with pre-configured context.
    
    Args:
        name: Logger name
        user_id: User identifier
        session_id: Session identifier
        agent_name: Agent name
    
    Returns:
        LoggerAdapter with context
    """
    logger = get_logger(name)
    extra = {}
    if user_id:
        extra["user_id"] = user_id
    if session_id:
        extra["session_id"] = session_id
    if agent_name:
        extra["agent_name"] = agent_name
    
    return LoggerAdapter(logger, extra)


# Initialize logging on module import
setup_logging()


"""
Usage Example:

from observability.logging_config import get_logger, get_context_logger

# Simple logging
logger = get_logger(__name__)
logger.info("Processing request")
logger.error("Something went wrong", exc_info=True)

# Context logging
ctx_logger = get_context_logger(
    __name__,
    user_id="user123",
    session_id="sess456",
    agent_name="FinancialAdvisor"
)
ctx_logger.info("Analyzing portfolio")

# With extra fields
logger.info("Tool executed", extra={"tool_name": "get_stock_price", "latency_ms": 150})
"""
