"""
MCP Server implementation for Financial Tools.

This server exposes financial analysis tools via the Model Context Protocol,
allowing other AI systems to use these tools in a standardized way.

Run with: python -m mcp.financial_mcp_server
"""
import asyncio
import json
from typing import Any, Dict, Optional

# Import tools
from tools.market_tools import (
    get_stock_price,
    get_market_summary,
    get_stock_history,
    search_market_news,
)
from tools.portfolio_tools import (
    analyze_portfolio,
    calculate_portfolio_metrics,
    suggest_rebalancing,
)
from tools.risk_tools import (
    calculate_var,
    assess_risk_profile,
    run_stress_test,
)
from tools.calculation_tools import (
    calculate_compound_interest,
    calculate_roi,
    calculate_sharpe_ratio,
    calculate_diversification_score,
)


# Tool definitions for MCP
TOOLS = {
    "financial_get_stock_price": {
        "description": "Get current stock price and basic info for a given symbol",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL', 'GOOGL')"
                }
            },
            "required": ["symbol"]
        },
        "function": get_stock_price,
        "readOnlyHint": True,
        "destructiveHint": False
    },
    "financial_get_market_summary": {
        "description": "Get overall market summary including major indices and sentiment",
        "inputSchema": {
            "type": "object",
            "properties": {}
        },
        "function": get_market_summary,
        "readOnlyHint": True,
        "destructiveHint": False
    },
    "financial_get_stock_history": {
        "description": "Get historical price data for a stock",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "period": {
                    "type": "string",
                    "description": "Time period: 1W, 1M, 3M, 6M, 1Y, 5Y",
                    "default": "1M"
                }
            },
            "required": ["symbol"]
        },
        "function": get_stock_history,
        "readOnlyHint": True,
        "destructiveHint": False
    },
    "financial_search_news": {
        "description": "Search for market news and analysis",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        },
        "function": search_market_news,
        "readOnlyHint": True,
        "destructiveHint": False
    },
    "financial_analyze_portfolio": {
        "description": "Analyze portfolio composition and characteristics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "holdings": {
                    "type": "object",
                    "description": "Holdings with format {'SYMBOL': percentage}",
                    "additionalProperties": {"type": "number"}
                }
            },
            "required": ["holdings"]
        },
        "function": analyze_portfolio,
        "readOnlyHint": True,
        "destructiveHint": False
    },
    "financial_calculate_var": {
        "description": "Calculate Value at Risk for a portfolio",
        "inputSchema": {
            "type": "object",
            "properties": {
                "portfolio_value": {
                    "type": "number",
                    "description": "Total portfolio value in dollars"
                },
                "holdings": {
                    "type": "object",
                    "description": "Holdings with percentages"
                },
                "confidence_level": {
                    "type": "number",
                    "description": "Confidence level (default 0.95)",
                    "default": 0.95
                },
                "time_horizon_days": {
                    "type": "integer",
                    "description": "Time horizon in days",
                    "default": 1
                }
            },
            "required": ["portfolio_value", "holdings"]
        },
        "function": calculate_var,
        "readOnlyHint": True,
        "destructiveHint": False
    },
    "financial_stress_test": {
        "description": "Run stress tests on a portfolio",
        "inputSchema": {
            "type": "object",
            "properties": {
                "portfolio_value": {
                    "type": "number",
                    "description": "Portfolio value"
                },
                "holdings": {
                    "type": "object",
                    "description": "Holdings"
                },
                "scenario": {
                    "type": "string",
                    "description": "Scenario: market_crash, tech_bubble, inflation_spike, interest_rate_hike, recession",
                    "default": "market_crash"
                }
            },
            "required": ["portfolio_value", "holdings"]
        },
        "function": run_stress_test,
        "readOnlyHint": True,
        "destructiveHint": False
    },
    "financial_compound_interest": {
        "description": "Calculate compound interest with optional contributions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "principal": {
                    "type": "number",
                    "description": "Initial investment"
                },
                "annual_rate": {
                    "type": "number",
                    "description": "Annual rate as percentage"
                },
                "years": {
                    "type": "integer",
                    "description": "Investment duration"
                },
                "monthly_contribution": {
                    "type": "number",
                    "description": "Monthly contribution",
                    "default": 0
                }
            },
            "required": ["principal", "annual_rate", "years"]
        },
        "function": calculate_compound_interest,
        "readOnlyHint": True,
        "destructiveHint": False
    },
    "financial_diversification_score": {
        "description": "Calculate portfolio diversification score",
        "inputSchema": {
            "type": "object",
            "properties": {
                "holdings": {
                    "type": "object",
                    "description": "Holdings with percentages"
                }
            },
            "required": ["holdings"]
        },
        "function": calculate_diversification_score,
        "readOnlyHint": True,
        "destructiveHint": False
    }
}


class FinancialMCPServer:
    """
    MCP Server for Financial Tools.
    
    This server can be run standalone or integrated with ADK agents.
    """
    
    def __init__(self):
        """Initialize the MCP server."""
        self.tools = TOOLS
        self.server_info = {
            "name": "financial-tools-mcp",
            "version": "1.0.0",
            "description": "Financial analysis tools via MCP"
        }
    
    def list_tools(self) -> list:
        """
        List all available tools.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": name,
                "description": tool["description"],
                "inputSchema": tool["inputSchema"],
                "annotations": {
                    "readOnlyHint": tool.get("readOnlyHint", False),
                    "destructiveHint": tool.get("destructiveHint", True)
                }
            }
            for name, tool in self.tools.items()
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool with the given arguments.
        
        Args:
            name: Tool name
            arguments: Tool arguments
        
        Returns:
            Tool result
        """
        if name not in self.tools:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}]
            }
        
        tool = self.tools[name]
        func = tool["function"]
        
        try:
            # Call the tool function
            result = func(**arguments)
            
            # Format result
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, default=str)
                    }
                ]
            }
        except Exception as e:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error calling {name}: {str(e)}"
                    }
                ]
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP JSON-RPC request.
        
        Args:
            request: JSON-RPC request
        
        Returns:
            JSON-RPC response
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "serverInfo": self.server_info,
                    "capabilities": {
                        "tools": {"listChanged": False}
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.list_tools()}
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Run async call
            result = asyncio.run(self.call_tool(tool_name, arguments))
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }


# Server instance
mcp_server = FinancialMCPServer()


def run_stdio_server():
    """Run the MCP server using stdio transport."""
    import sys
    
    print("Financial MCP Server started (stdio mode)", file=sys.stderr)
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            response = mcp_server.handle_request(request)
            
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    run_stdio_server()


"""
Usage with ADK:

# In your agent.py, you can connect to MCP servers:
from google.adk.tools.mcp_tool import MCPTool

mcp_tool = MCPTool(
    server_command=["python", "-m", "mcp.financial_mcp_server"],
    tool_filter=["financial_get_stock_price", "financial_analyze_portfolio"]
)

agent = LlmAgent(
    name="FinancialAgent",
    tools=[mcp_tool]  # Include MCP tools
)

# Or run standalone:
# python -m mcp.financial_mcp_server
"""
