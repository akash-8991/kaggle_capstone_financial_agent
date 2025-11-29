"""
Main agent definition for the Financial Decision Support System.

This file defines the root_agent which is the main entry point for
the ADK application. It orchestrates all sub-agents and provides
the primary interface for users.
"""
import os
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools import google_search

# Set up environment
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

from config import config

# Import all tools
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

# Import sub-agents
from agents.research_agent import parallel_research_agent
from agents.analysis_agent import analysis_pipeline
from agents.recommendation_agent import full_recommendation_pipeline


# ============================================================================
# SPECIALIZED SUB-AGENTS
# ============================================================================

# Quick Query Agent - For simple questions
quick_query_agent = LlmAgent(
    name="QuickQueryAgent",
    model=config.DEFAULT_MODEL,
    instruction="""You handle simple, quick financial queries that don't require
    comprehensive analysis. Use tools directly to answer questions about:
    
    - Current stock prices (use get_stock_price)
    - Market summary (use get_market_summary)
    - Simple calculations (use calculation tools)
    - Quick portfolio checks (use analyze_portfolio)
    
    Provide concise, direct answers. For complex analysis requests,
    indicate that a full analysis would be more appropriate.""",
    description="Handles quick financial queries with direct tool usage.",
    tools=[
        get_stock_price,
        get_market_summary,
        get_stock_history,
        calculate_compound_interest,
        calculate_roi,
        analyze_portfolio,
    ]
)


# Full Analysis Agent - Orchestrates complete analysis
full_analysis_agent = SequentialAgent(
    name="FullAnalysisWorkflow",
    sub_agents=[
        parallel_research_agent,
        analysis_pipeline,
        full_recommendation_pipeline,
    ],
    description="""Complete financial analysis workflow that:
    1. Gathers data in parallel (market, news, historical)
    2. Performs sequential analysis (risk, portfolio, performance)
    3. Generates refined recommendations through iterative loop"""
)


# ============================================================================
# ROOT AGENT - Main Entry Point
# ============================================================================

root_agent = LlmAgent(
    name="FinancialAdvisor",
    model=config.DEFAULT_MODEL,
    instruction="""You are an AI-powered Financial Advisor assistant. Your role is
    to help users make informed financial decisions through comprehensive analysis
    and personalized recommendations.
    
    ## YOUR CAPABILITIES
    
    1. **Quick Queries**: Answer simple questions about stock prices, market
       conditions, or basic calculations directly using your tools.
    
    2. **Portfolio Analysis**: Analyze investment portfolios for composition,
       risk, diversification, and performance.
    
    3. **Risk Assessment**: Evaluate risk profiles, calculate Value at Risk,
       and run stress tests.
    
    4. **Investment Recommendations**: Provide data-driven recommendations
       based on thorough analysis.
    
    5. **Financial Calculations**: Compute compound interest, ROI, Sharpe ratios,
       and other financial metrics.
    
    6. **Market Research**: Search for market news, analyze sentiment, and
       track historical trends.
    
    ## AVAILABLE TOOLS
    
    Market Tools:
    - get_stock_price: Get current price for a stock symbol
    - get_market_summary: Get overall market indices and sentiment
    - get_stock_history: Get historical price data
    - search_market_news: Search for relevant financial news
    - google_search: Search the web for current information
    
    Portfolio Tools:
    - analyze_portfolio: Analyze portfolio composition
    - calculate_portfolio_metrics: Calculate performance metrics
    - suggest_rebalancing: Get rebalancing recommendations
    
    Risk Tools:
    - calculate_var: Calculate Value at Risk
    - assess_risk_profile: Assess investor risk profile
    - run_stress_test: Run portfolio stress tests
    
    Calculation Tools:
    - calculate_compound_interest: Project investment growth
    - calculate_roi: Calculate return on investment
    - calculate_sharpe_ratio: Calculate risk-adjusted returns
    - calculate_diversification_score: Evaluate portfolio diversification
    
    ## HOW TO RESPOND
    
    1. For simple queries (prices, quick calculations):
       - Use tools directly and provide concise answers
    
    2. For analysis requests:
       - Gather relevant data using multiple tools
       - Synthesize findings into clear insights
       - Provide actionable recommendations
    
    3. For portfolio reviews:
       - Request portfolio holdings if not provided
       - Use analysis tools comprehensively
       - Address risk, performance, and optimization
    
    4. Always:
       - Be data-driven and cite specific numbers
       - Explain your reasoning
       - Highlight risks alongside opportunities
       - Include appropriate disclaimers
    
    ## IMPORTANT DISCLAIMER
    
    Always remind users that you provide information for educational purposes
    only and recommend consulting licensed financial advisors for major
    investment decisions.
    
    ## USER CONTEXT
    
    If available, use information from:
    - User preferences: {user:preferences}
    - Previous analysis: {app:last_analysis}
    - Session context: {current_topic}""",
    
    description="""AI Financial Advisor that helps users make informed financial
    decisions through market research, portfolio analysis, risk assessment,
    and personalized recommendations.""",
    
    tools=[
        # Market tools
        get_stock_price,
        get_market_summary,
        get_stock_history,
        search_market_news,
        # Portfolio tools
        analyze_portfolio,
        calculate_portfolio_metrics,
        suggest_rebalancing,
        # Risk tools
        calculate_var,
        assess_risk_profile,
        run_stress_test,
        # Calculation tools
        calculate_compound_interest,
        calculate_roi,
        calculate_sharpe_ratio,
        calculate_diversification_score,
        # Google search for current information
        google_search,
    ],
    
    # Sub-agents for delegation
    sub_agents=[
        quick_query_agent,
        full_analysis_agent,
    ],
)


# ============================================================================
# CALLBACKS FOR OBSERVABILITY
# ============================================================================

async def before_agent_callback(callback_context):
    """
    Callback executed before the agent processes a request.
    Used for logging and metrics.
    """
    import logging
    logger = logging.getLogger("financial_advisor")
    
    user_message = callback_context.user_content
    logger.info(f"Processing request: {str(user_message)[:100]}...")
    
    # Store timestamp in state for latency tracking
    from datetime import datetime
    callback_context.state["request_start_time"] = datetime.now().isoformat()


async def after_agent_callback(callback_context):
    """
    Callback executed after the agent completes a request.
    Used for logging, metrics, and memory management.
    """
    import logging
    logger = logging.getLogger("financial_advisor")
    
    logger.info("Request completed")
    
    # Calculate latency
    from datetime import datetime
    start_time = callback_context.state.get("request_start_time")
    if start_time:
        start = datetime.fromisoformat(start_time)
        latency = (datetime.now() - start).total_seconds()
        logger.info(f"Request latency: {latency:.2f} seconds")
    
    # Save analysis to app state for continuity
    if callback_context.state.get("performance_evaluation_result"):
        callback_context.state["app:last_analysis"] = callback_context.state.get(
            "performance_evaluation_result"
        )


# Apply callbacks to root agent
root_agent.before_agent_callback = before_agent_callback
root_agent.after_agent_callback = after_agent_callback


# ============================================================================
# FOR ADK CLI COMPATIBILITY
# ============================================================================

# ADK expects to find 'root_agent' when discovering agents
# This is already defined above, but explicitly export it
__all__ = ["root_agent"]


"""
Running the Agent:

1. Development UI:
   adk web .

2. API Server:
   adk api_server .

3. With A2A Protocol:
   adk api_server . --a2a

4. Programmatically:
   from google.adk.runners import InMemoryRunner
   from google.adk.sessions import InMemorySessionService
   from google.genai import types
   
   session_service = InMemorySessionService()
   await session_service.create_session(
       app_name="financial_advisor",
       user_id="user123",
       session_id="session123"
   )
   
   runner = InMemoryRunner(
       agent=root_agent,
       app_name="financial_advisor",
       session_service=session_service
   )
   
   user_msg = types.Content(
       role="user",
       parts=[types.Part(text="What's the current price of AAPL?")]
   )
   
   for event in runner.run(
       user_id="user123",
       session_id="session123",
       new_message=user_msg
   ):
       if event.is_final_response():
           print(event.content.parts[0].text)
"""
