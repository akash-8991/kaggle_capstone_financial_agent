"""
Research agents that operate in parallel to gather financial data.

This module demonstrates the ParallelAgent pattern from ADK, where
multiple specialized agents run concurrently to fetch different
types of financial data.
"""
from google.adk.agents import LlmAgent, ParallelAgent
from config import config

# Import tools
from tools.market_tools import (
    get_stock_price,
    get_market_summary,
    get_stock_history,
    search_market_news,
)


def create_research_agent(
    name: str,
    instruction: str,
    description: str,
    tools: list,
    output_key: str
) -> LlmAgent:
    """
    Factory function to create a research sub-agent.
    
    Args:
        name: Agent name
        instruction: Agent instructions
        description: Agent description
        tools: List of tools available to the agent
        output_key: State key where results will be stored
    
    Returns:
        Configured LlmAgent
    """
    return LlmAgent(
        name=name,
        model=config.DEFAULT_MODEL,
        instruction=instruction,
        description=description,
        tools=tools,
        output_key=output_key,
    )


# Market Data Research Agent
market_data_researcher = LlmAgent(
    name="MarketDataResearcher",
    model=config.DEFAULT_MODEL,
    instruction="""You are a market data specialist. Your job is to gather current
    market information including stock prices and market indices.
    
    When asked about specific stocks, use the get_stock_price tool.
    When asked about overall market conditions, use the get_market_summary tool.
    
    Provide concise, data-focused responses with key numbers and trends.
    Focus on: current prices, daily changes, volume, and market indices.
    
    Output format: Structured summary of market data gathered.""",
    description="Gathers current market data including stock prices and indices.",
    tools=[get_stock_price, get_market_summary],
    output_key="market_data_result"
)


# News Research Agent
news_researcher = LlmAgent(
    name="NewsResearcher",
    model=config.DEFAULT_MODEL,
    instruction="""You are a financial news analyst. Your job is to find and
    summarize relevant news and market sentiment.
    
    Use the search_market_news tool to find relevant articles about:
    - Specific companies or stocks
    - Sector trends
    - Economic indicators
    - Market-moving events
    
    Summarize key findings with:
    - Main headlines and themes
    - Overall sentiment (bullish/bearish/neutral)
    - Potential impact on investments
    
    Output format: News summary with sentiment analysis.""",
    description="Researches market news and analyzes sentiment.",
    tools=[search_market_news],
    output_key="news_research_result"
)


# Historical Data Research Agent
historical_researcher = LlmAgent(
    name="HistoricalResearcher",
    model=config.DEFAULT_MODEL,
    instruction="""You are a historical data analyst. Your job is to analyze
    historical price patterns and trends.
    
    Use the get_stock_history tool to retrieve and analyze:
    - Price trends over different time periods
    - Historical volatility
    - Key support and resistance levels
    - Period returns
    
    Compare current prices to historical averages.
    Identify any notable patterns or anomalies.
    
    Output format: Historical analysis with trend interpretation.""",
    description="Analyzes historical price data and trends.",
    tools=[get_stock_history],
    output_key="historical_research_result"
)


# Create the Parallel Research Agent
# This runs all three research agents concurrently
parallel_research_agent = ParallelAgent(
    name="ParallelResearchGathering",
    sub_agents=[
        market_data_researcher,
        news_researcher,
        historical_researcher,
    ],
    description="""Parallel agent that runs multiple research agents concurrently
    to gather market data, news, and historical information simultaneously.
    Results are stored in state keys: market_data_result, news_research_result,
    and historical_research_result."""
)


# Example usage in docstring
"""
Usage Example:

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Create session
session_service = InMemorySessionService()
await session_service.create_session(
    app_name="financial_advisor",
    user_id="user123",
    session_id="session123"
)

# Create runner with parallel agent
runner = InMemoryRunner(
    agent=parallel_research_agent,
    app_name="financial_advisor",
    session_service=session_service
)

# Run research
user_msg = types.Content(
    role="user",
    parts=[types.Part(text="Research AAPL stock")]
)

for event in runner.run(
    user_id="user123",
    session_id="session123",
    new_message=user_msg
):
    if event.is_final_response():
        # Access results from state
        session = await session_service.get_session(
            app_name="financial_advisor",
            user_id="user123",
            session_id="session123"
        )
        market_data = session.state.get("market_data_result")
        news_data = session.state.get("news_research_result")
        historical_data = session.state.get("historical_research_result")
"""
