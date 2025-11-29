"""
Custom financial tools for the agent system.
"""

from .market_tools import (
    get_stock_price,
    get_market_summary,
    get_stock_history,
    search_market_news,
)
from .portfolio_tools import (
    analyze_portfolio,
    calculate_portfolio_metrics,
    suggest_rebalancing,
)
from .risk_tools import (
    calculate_var,
    assess_risk_profile,
    run_stress_test,
)
from .calculation_tools import (
    calculate_compound_interest,
    calculate_roi,
    calculate_sharpe_ratio,
    calculate_diversification_score,
)

__all__ = [
    # Market tools
    "get_stock_price",
    "get_market_summary",
    "get_stock_history",
    "search_market_news",
    # Portfolio tools
    "analyze_portfolio",
    "calculate_portfolio_metrics",
    "suggest_rebalancing",
    # Risk tools
    "calculate_var",
    "assess_risk_profile",
    "run_stress_test",
    # Calculation tools
    "calculate_compound_interest",
    "calculate_roi",
    "calculate_sharpe_ratio",
    "calculate_diversification_score",
]
