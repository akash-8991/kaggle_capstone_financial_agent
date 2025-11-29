"""
Analysis agents that operate in sequence for thorough financial analysis.

This module demonstrates the SequentialAgent pattern from ADK, where
agents run one after another, with each agent building on the work
of the previous one through shared session state.
"""
from google.adk.agents import LlmAgent, SequentialAgent
from config import config

# Import tools
from tools.portfolio_tools import (
    analyze_portfolio,
    calculate_portfolio_metrics,
)
from tools.risk_tools import (
    calculate_var,
    assess_risk_profile,
    run_stress_test,
)
from tools.calculation_tools import (
    calculate_sharpe_ratio,
    calculate_diversification_score,
)


# Step 1: Risk Assessment Agent
risk_assessment_agent = LlmAgent(
    name="RiskAssessmentAgent",
    model=config.DEFAULT_MODEL,
    instruction="""You are a risk assessment specialist. Your job is to evaluate
    the risk profile of investments and portfolios.
    
    Based on the research results available in context:
    - {market_data_result}
    - {news_research_result}
    - {historical_research_result}
    
    Perform risk analysis:
    1. Use calculate_var to compute Value at Risk
    2. Use assess_risk_profile if investor details are provided
    3. Use run_stress_test to evaluate downside scenarios
    
    Provide a clear risk assessment with:
    - Risk level (Low/Medium/High)
    - Key risk factors identified
    - VaR and stress test results
    
    Output a structured risk assessment that the next agent can use.""",
    description="Assesses risk using VaR, stress tests, and risk profiling.",
    tools=[calculate_var, assess_risk_profile, run_stress_test],
    output_key="risk_assessment_result"
)


# Step 2: Portfolio Analysis Agent
portfolio_analysis_agent = LlmAgent(
    name="PortfolioAnalysisAgent",
    model=config.DEFAULT_MODEL,
    instruction="""You are a portfolio analysis expert. Your job is to analyze
    portfolio composition and performance metrics.
    
    Use the risk assessment from the previous step:
    - {risk_assessment_result}
    
    And the research data:
    - {market_data_result}
    - {historical_research_result}
    
    Perform portfolio analysis:
    1. Use analyze_portfolio to evaluate composition
    2. Use calculate_portfolio_metrics for performance metrics
    3. Use calculate_diversification_score to assess diversification
    
    Provide analysis covering:
    - Portfolio composition (sector allocation, concentration)
    - Performance metrics (Sharpe ratio, beta, alpha)
    - Diversification quality
    - Comparison to benchmarks
    
    Output a structured analysis for the performance evaluation agent.""",
    description="Analyzes portfolio composition, metrics, and diversification.",
    tools=[analyze_portfolio, calculate_portfolio_metrics, calculate_diversification_score],
    output_key="portfolio_analysis_result"
)


# Step 3: Performance Evaluation Agent
performance_evaluation_agent = LlmAgent(
    name="PerformanceEvaluationAgent",
    model=config.DEFAULT_MODEL,
    instruction="""You are a performance evaluation specialist. Your job is to
    synthesize all analysis and provide a comprehensive evaluation.
    
    Review all previous analysis:
    - Risk Assessment: {risk_assessment_result}
    - Portfolio Analysis: {portfolio_analysis_result}
    - Market Data: {market_data_result}
    - News: {news_research_result}
    - Historical Data: {historical_research_result}
    
    Use calculate_sharpe_ratio if you need to compute risk-adjusted returns.
    
    Provide a comprehensive evaluation:
    
    1. OVERALL HEALTH SCORE (1-100)
       - Weight: Risk (30%), Performance (30%), Diversification (20%), Market Position (20%)
    
    2. STRENGTHS
       - List 2-3 key portfolio strengths
    
    3. WEAKNESSES
       - List 2-3 areas of concern
    
    4. KEY METRICS SUMMARY
       - Risk level, expected return, Sharpe ratio, diversification score
    
    5. MARKET CONTEXT
       - How does the portfolio fare in current market conditions?
    
    This evaluation will be used by the recommendation agent.""",
    description="Evaluates overall portfolio performance and health.",
    tools=[calculate_sharpe_ratio],
    output_key="performance_evaluation_result"
)


def create_analysis_pipeline() -> SequentialAgent:
    """
    Create the sequential analysis pipeline.
    
    This pipeline runs three agents in sequence:
    1. Risk Assessment - Evaluates portfolio risk
    2. Portfolio Analysis - Analyzes composition and metrics
    3. Performance Evaluation - Synthesizes everything into evaluation
    
    Each agent reads from state keys written by previous agents
    and writes its results to its own output_key.
    
    Returns:
        SequentialAgent configured with the analysis pipeline
    """
    return SequentialAgent(
        name="AnalysisPipeline",
        sub_agents=[
            risk_assessment_agent,
            portfolio_analysis_agent,
            performance_evaluation_agent,
        ],
        description="""Sequential pipeline that performs comprehensive
        portfolio analysis in three stages: risk assessment, portfolio
        analysis, and performance evaluation. Each stage builds on
        the previous stage's results."""
    )


# Pre-configured instance
analysis_pipeline = create_analysis_pipeline()


"""
Usage Example:

# The analysis pipeline expects research results to be in state
# It should be run after the parallel research agent

from google.adk.agents import SequentialAgent
from google.adk.runners import InMemoryRunner

# Create a combined workflow
full_analysis_workflow = SequentialAgent(
    name="FullAnalysisWorkflow",
    sub_agents=[
        parallel_research_agent,  # From research_agent.py
        analysis_pipeline,         # This module
    ]
)

# Run the complete workflow
runner = InMemoryRunner(
    agent=full_analysis_workflow,
    app_name="financial_advisor",
    session_service=session_service
)

# After running, state will contain:
# - market_data_result
# - news_research_result  
# - historical_research_result
# - risk_assessment_result
# - portfolio_analysis_result
# - performance_evaluation_result
"""
