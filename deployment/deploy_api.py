"""
FastAPI deployment wrapper for the Financial Agent System.

This module provides a production-ready FastAPI application that
can be deployed to Cloud Run, Kubernetes, or any container platform.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import config
from observability.logging_config import setup_logging, get_logger
from observability.metrics import MetricsEndpoint, metrics

# Initialize logging
setup_logging(log_file="logs/financial_agent.log")
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    # Try to use ADK's FastAPI helper
    try:
        from google.adk.cli.fast_api import get_fast_api_app
        
        # Get the agent directory
        agent_dir = Path(__file__).parent.parent
        
        # Create app with ADK helper
        app = get_fast_api_app(
            agents_dir=str(agent_dir),
            web=True,  # Enable web UI
            trace_to_cloud=os.getenv("TRACE_TO_CLOUD", "").lower() == "true"
        )
        
        logger.info("Created FastAPI app using ADK helper")
        
    except ImportError:
        logger.warning("ADK FastAPI helper not available, using fallback")
        app = create_fallback_app()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom routes
    add_custom_routes(app)
    
    return app


def create_fallback_app() -> FastAPI:
    """
    Create a fallback FastAPI app when ADK helper is not available.
    """
    from agent import root_agent
    
    app = FastAPI(
        title="Financial Advisor API",
        description="AI-powered financial decision support system",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        return {
            "name": "Financial Advisor",
            "status": "running",
            "agent": root_agent.name
        }
    
    @app.post("/chat")
    async def chat(request: Request):
        """Simple chat endpoint."""
        body = await request.json()
        message = body.get("message", "")
        
        # In fallback mode, return a placeholder
        return {
            "response": f"Received: {message}. Please use 'adk web' for full functionality.",
            "agent": root_agent.name
        }
    
    return app


def add_custom_routes(app: FastAPI) -> None:
    """
    Add custom routes to the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint for load balancers."""
        return {
            "status": "healthy",
            "service": config.APP_NAME,
            "version": "1.0.0"
        }
    
    @app.get("/ready")
    async def readiness_check():
        """Readiness check for Kubernetes."""
        return {"status": "ready"}
    
    @app.get("/metrics")
    async def get_metrics():
        """Prometheus-compatible metrics endpoint."""
        return JSONResponse(
            content=MetricsEndpoint.format_json(),
            media_type="application/json"
        )
    
    @app.get("/metrics/prometheus")
    async def get_prometheus_metrics():
        """Prometheus text format metrics."""
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=MetricsEndpoint.format_prometheus(),
            media_type="text/plain"
        )
    
    @app.post("/feedback")
    async def submit_feedback(request: Request):
        """Endpoint for collecting user feedback."""
        body = await request.json()
        
        # Log feedback
        logger.info(f"Feedback received: {body}")
        metrics.increment("feedback.received")
        
        return {"status": "received", "message": "Thank you for your feedback"}
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        metrics.increment("errors.unhandled")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if os.getenv("DEBUG") else "An error occurred"
            }
        )


# Create the application
app = create_app()


def main():
    """Main entry point for running the server."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    
    logger.info(f"Starting Financial Advisor API on {host}:{port}")
    
    uvicorn.run(
        "deployment.deploy_api:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "").lower() == "true",
        workers=int(os.getenv("WORKERS", "1"))
    )


if __name__ == "__main__":
    main()


"""
Usage:

1. Run directly:
   python deployment/deploy_api.py

2. Run with uvicorn:
   uvicorn deployment.deploy_api:app --host 0.0.0.0 --port 8080

3. Run with gunicorn (production):
   gunicorn deployment.deploy_api:app -w 4 -k uvicorn.workers.UvicornWorker

4. Environment variables:
   - HOST: Server host (default: 0.0.0.0)
   - PORT: Server port (default: 8080)
   - DEBUG: Enable debug mode (default: false)
   - WORKERS: Number of workers (default: 1)
   - TRACE_TO_CLOUD: Enable cloud tracing (default: false)
"""
