"""
Recommendation agents that use loops for iterative refinement.

This module demonstrates the LoopAgent pattern from ADK, where
agents iterate to refine their output until a quality threshold
is met or maximum iterations are reached.
"""
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext
from google.adk.events import Event, EventActions
from typing import AsyncGenerator
from config import config

# Import tools
from tools.portfolio_tools import suggest_rebalancing


# Exit loop tool - called when recommendation meets quality criteria
async def approve_recommendation(
    tool_context: ToolContext,
    quality_score: int,
    final_recommendation: str
) -> dict:
    """
    Approve the recommendation and exit the refinement loop.
    
    This tool should be called when the recommendation meets quality criteria:
    - Quality score >= 8 out of 10
    - All key aspects are addressed
    - Actionable steps are included
    
    Args:
        tool_context: ADK tool context for accessing actions
        quality_score: Quality score from 1-10
        final_recommendation: The approved recommendation text
    
    Returns:
        Confirmation of approval
    """
    if quality_score >= 8:
        # Signal to exit the loop
        tool_context.actions.escalate = True
        return {
            "status": "approved",
            "quality_score": quality_score,
            "message": "Recommendation approved and finalized",
            "recommendation": final_recommendation[:200] + "..."  # Truncate for confirmation
        }
    else:
        return {
            "status": "needs_improvement",
            "quality_score": quality_score,
            "message": f"Quality score {quality_score} is below threshold of 8. Continue refining."
        }


# Recommendation Generator Agent
recommendation_generator = LlmAgent(
    name="RecommendationGenerator",
    model=config.DEFAULT_MODEL,
    instruction="""You are a financial recommendation specialist. Generate
    investment recommendations based on the analysis provided.
    
    Use all available analysis from context:
    - Performance Evaluation: {performance_evaluation_result}
    - Risk Assessment: {risk_assessment_result}
    - Portfolio Analysis: {portfolio_analysis_result}
    - Market Data: {market_data_result}
    - News: {news_research_result}
    
    Previous criticism (if any): {recommendation_criticism}
    Previous recommendation (if any): {current_recommendation}
    
    If this is a refinement iteration, address ALL criticisms raised.
    
    Use suggest_rebalancing tool if portfolio changes are needed.
    
    Generate a comprehensive recommendation covering:
    
    1. EXECUTIVE SUMMARY
       - One paragraph overview of key recommendations
    
    2. SPECIFIC ACTIONS (numbered, actionable)
       - Buy/Sell/Hold decisions with reasoning
       - Allocation changes with percentages
       - Timeline for actions
    
    3. RISK CONSIDERATIONS
       - Key risks to monitor
       - Stop-loss or exit criteria
    
    4. EXPECTED OUTCOMES
       - Target returns
       - Time horizon
       - Success metrics
    
    Be specific, actionable, and data-driven.""",
    description="Generates investment recommendations based on analysis.",
    tools=[suggest_rebalancing],
    output_key="current_recommendation"
)


# Recommendation Critic Agent
recommendation_critic = LlmAgent(
    name="RecommendationCritic",
    model=config.DEFAULT_MODEL,
    instruction="""You are a critical reviewer of investment recommendations.
    Your job is to evaluate the quality of recommendations and identify
    areas for improvement.
    
    Review the current recommendation:
    {current_recommendation}
    
    Against the analysis context:
    - Performance Evaluation: {performance_evaluation_result}
    - Risk Assessment: {risk_assessment_result}
    
    Evaluate on these criteria (score each 1-10):
    
    1. COMPLETENESS: Does it address all key areas?
    2. ACTIONABILITY: Are steps specific and executable?
    3. DATA SUPPORT: Are recommendations backed by analysis?
    4. RISK AWARENESS: Are risks adequately addressed?
    5. CLARITY: Is the recommendation clear and unambiguous?
    
    Calculate OVERALL SCORE (average of all criteria).
    
    If OVERALL SCORE >= 8:
       - Call approve_recommendation with the score and recommendation
       - This will finalize and exit the loop
    
    If OVERALL SCORE < 8:
       - Provide specific, constructive criticism
       - List exactly what needs improvement
       - The generator will use this to improve
    
    Output format:
    SCORES:
    - Completeness: X/10
    - Actionability: X/10
    - Data Support: X/10
    - Risk Awareness: X/10
    - Clarity: X/10
    - OVERALL: X/10
    
    CRITICISM (if score < 8):
    [Specific improvements needed]
    
    If approved, call the approve_recommendation tool.""",
    description="Critically evaluates recommendations for quality.",
    tools=[approve_recommendation],
    output_key="recommendation_criticism"
)


def create_recommendation_loop() -> LoopAgent:
    """
    Create the recommendation refinement loop.
    
    This loop iterates between:
    1. Generator - Creates/refines recommendations
    2. Critic - Evaluates and either approves or requests improvements
    
    The loop exits when:
    - Critic approves (quality score >= 8)
    - Maximum iterations reached (default: 3)
    
    Returns:
        LoopAgent configured for recommendation refinement
    """
    return LoopAgent(
        name="RecommendationRefinementLoop",
        sub_agents=[
            recommendation_generator,
            recommendation_critic,
        ],
        max_iterations=config.MAX_LOOP_ITERATIONS,  # Default: 3
        description="""Loop agent that iteratively refines recommendations
        until they meet quality criteria. Generator creates recommendations,
        critic evaluates them. Loop exits on approval or max iterations."""
    )


# Pre-configured instance
recommendation_loop = create_recommendation_loop()


# Complete recommendation pipeline including synthesis
recommendation_synthesizer = LlmAgent(
    name="RecommendationSynthesizer",
    model=config.DEFAULT_MODEL,
    instruction="""You are the final synthesizer of financial recommendations.
    
    Take the refined recommendation from the loop:
    {current_recommendation}
    
    And present it in a polished, client-ready format:
    
    ═══════════════════════════════════════════════════════
    FINANCIAL RECOMMENDATION REPORT
    ═══════════════════════════════════════════════════════
    
    Date: [Today's date]
    Prepared for: [User]
    
    EXECUTIVE SUMMARY
    ─────────────────
    [Concise overview]
    
    RECOMMENDED ACTIONS
    ─────────────────
    1. [Action 1]
    2. [Action 2]
    3. [Action 3]
    
    RISK MANAGEMENT
    ─────────────────
    [Key risks and mitigation]
    
    EXPECTED OUTCOMES
    ─────────────────
    [Projections and timeline]
    
    DISCLAIMER
    ─────────────────
    This is an AI-generated recommendation for informational
    purposes only. Please consult a licensed financial advisor
    before making investment decisions.
    ═══════════════════════════════════════════════════════
    
    Make it professional, clear, and actionable.""",
    description="Synthesizes final recommendation into polished report.",
    output_key="final_recommendation"
)


def create_full_recommendation_pipeline() -> SequentialAgent:
    """
    Create the complete recommendation pipeline.
    
    Combines the refinement loop with final synthesis.
    
    Returns:
        SequentialAgent with loop and synthesizer
    """
    return SequentialAgent(
        name="FullRecommendationPipeline",
        sub_agents=[
            recommendation_loop,
            recommendation_synthesizer,
        ],
        description="Complete recommendation pipeline with iterative refinement and final synthesis."
    )


# Pre-configured full pipeline
full_recommendation_pipeline = create_full_recommendation_pipeline()


"""
Usage Example:

# The recommendation pipeline expects analysis results in state
# It should be run after the analysis pipeline

from google.adk.agents import SequentialAgent

# Create complete financial advisory workflow
complete_workflow = SequentialAgent(
    name="CompleteFinancialAdvisor",
    sub_agents=[
        parallel_research_agent,    # Gather data in parallel
        analysis_pipeline,          # Sequential analysis
        full_recommendation_pipeline # Loop refinement + synthesis
    ]
)

# This represents the full workflow:
# 1. Parallel: Market data, News, Historical data (concurrent)
# 2. Sequential: Risk -> Portfolio -> Performance evaluation
# 3. Loop: Generate -> Critique -> Refine (up to 3 times)
# 4. Final: Synthesize polished recommendation

# State keys after completion:
# - market_data_result
# - news_research_result
# - historical_research_result
# - risk_assessment_result
# - portfolio_analysis_result
# - performance_evaluation_result
# - current_recommendation
# - recommendation_criticism
# - final_recommendation  <- The polished output
"""
