"""
A2A Server for the Financial Advisor Agent.

This module exposes the Financial Advisor agent via the A2A protocol,
allowing other agents to discover and interact with it.
"""
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

from config import config
from observability.logging_config import get_logger

logger = get_logger(__name__)


def load_agent_card() -> Dict[str, Any]:
    """Load the agent card from JSON file."""
    card_path = Path(__file__).parent / "agent_card.json"
    with open(card_path) as f:
        return json.load(f)


def create_a2a_app(agent, port: int = None):
    """
    Create an A2A-enabled FastAPI application.
    
    This wraps the ADK agent with A2A protocol support.
    
    Args:
        agent: The ADK agent to expose
        port: Port to run on (default from config)
    
    Returns:
        FastAPI application with A2A routes
    """
    try:
        from google.adk.a2a import to_a2a
        
        # Convert ADK agent to A2A-compatible server
        a2a_app = to_a2a(agent)
        
        logger.info(f"Created A2A application for agent: {agent.name}")
        return a2a_app
        
    except ImportError:
        logger.warning("A2A support not available. Using fallback implementation.")
        return create_fallback_a2a_app(agent)


def create_fallback_a2a_app(agent):
    """
    Create a fallback A2A implementation using FastAPI.
    
    This is used when the google.adk.a2a module is not available.
    """
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    
    app = FastAPI(
        title="Financial Advisor A2A Server",
        description="A2A protocol server for the Financial Advisor agent"
    )
    
    agent_card = load_agent_card()
    
    @app.get("/.well-known/agent.json")
    async def get_agent_card():
        """Serve the agent card for discovery."""
        return JSONResponse(content=agent_card)
    
    @app.get("/.well-known/agent-card.json")
    async def get_agent_card_alt():
        """Alternative endpoint for agent card."""
        return JSONResponse(content=agent_card)
    
    @app.post("/tasks/send")
    async def send_task(request: Request):
        """
        Handle incoming A2A task requests.
        
        This is the main endpoint for agent-to-agent communication.
        """
        try:
            body = await request.json()
            
            # Extract message from A2A format
            params = body.get("params", {})
            message = params.get("message", {})
            task_id = params.get("id", "unknown")
            
            # Extract text content
            parts = message.get("parts", [])
            text_content = ""
            for part in parts:
                if part.get("kind") == "text":
                    text_content += part.get("text", "")
                elif "text" in part:
                    text_content += part["text"]
            
            logger.info(f"Received A2A task {task_id}: {text_content[:100]}...")
            
            # Process with agent
            # In a full implementation, this would use the ADK runner
            response_text = f"Financial Advisor received: {text_content}. " \
                           f"(A2A fallback mode - connect via ADK for full functionality)"
            
            # Format A2A response
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "id": task_id,
                    "status": {
                        "state": "completed"
                    },
                    "artifacts": [
                        {
                            "parts": [
                                {
                                    "kind": "text",
                                    "text": response_text
                                }
                            ]
                        }
                    ]
                }
            })
            
        except Exception as e:
            logger.error(f"Error processing A2A task: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id") if 'body' in dir() else None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
            )
    
    @app.post("/tasks/sendSubscribe")
    async def send_subscribe_task(request: Request):
        """Handle streaming A2A tasks (not fully implemented in fallback)."""
        # Redirect to non-streaming endpoint
        return await send_task(request)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "agent": agent.name}
    
    return app


def run_a2a_server(
    agent=None,
    host: str = "0.0.0.0",
    port: Optional[int] = None
):
    """
    Run the A2A server.
    
    Args:
        agent: ADK agent to expose (defaults to root_agent)
        host: Host to bind to
        port: Port to run on
    """
    import uvicorn
    
    if agent is None:
        from agent import root_agent
        agent = root_agent
    
    port = port or config.A2A_SERVER_PORT
    
    app = create_a2a_app(agent, port)
    
    # Update agent card URL
    agent_card = load_agent_card()
    agent_card["url"] = f"http://{host}:{port}"
    
    logger.info(f"Starting A2A server at http://{host}:{port}")
    logger.info(f"Agent card available at http://{host}:{port}/.well-known/agent.json")
    
    uvicorn.run(app, host=host, port=port)


# Entry point for running standalone
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Financial Advisor A2A Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=config.A2A_SERVER_PORT, help="Port to run on")
    
    args = parser.parse_args()
    
    run_a2a_server(host=args.host, port=args.port)


"""
Usage:

1. Run standalone A2A server:
   python -m a2a.a2a_server --port 8001

2. Use with ADK (recommended):
   adk api_server . --a2a

3. From another agent, connect to this agent:
   
   from google.adk.agents import RemoteA2aAgent
   
   financial_advisor = RemoteA2aAgent(
       name="FinancialAdvisor",
       url="http://localhost:8001"
   )
   
   # Now use as sub-agent
   coordinator = LlmAgent(
       name="Coordinator",
       sub_agents=[financial_advisor]
   )

4. Inspect agent capabilities:
   curl http://localhost:8001/.well-known/agent.json
"""
