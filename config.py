"""
Configuration settings for the Financial Agent System.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Application settings
    APP_NAME: str = os.getenv("APP_NAME", "financial_advisor")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
    
    # Google AI Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    USE_VERTEX_AI: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Financial API Keys
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    
    # Observability
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "financial-agent-system")
    OTEL_EXPORTER_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # A2A Configuration
    A2A_SERVER_PORT: int = int(os.getenv("A2A_SERVER_PORT", "8001"))
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_MEMORY_ITEMS: int = 100
    
    # Agent Configuration
    MAX_LOOP_ITERATIONS: int = 3
    PARALLEL_TIMEOUT_SECONDS: int = 30
    

config = Config()
