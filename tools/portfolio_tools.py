"""
Portfolio analysis tools for evaluating and optimizing investment portfolios.
"""
from typing import Optional
from datetime import datetime


def analyze_portfolio(holdings: dict) -> dict:
    """
    Analyze a portfolio's composition and characteristics.
    
    Args:
        holdings: Dictionary of holdings with format {'SYMBOL': percentage, ...}
                  Example: {'AAPL': 40, 'GOOGL': 30, 'MSFT': 20, 'CASH': 10}
    
    Returns:
        Dictionary containing portfolio analysis results
    """
    # Sector mappings for common stocks
    sector_mapping = {
        "AAPL": "Technology",
        "GOOGL": "Technology",
        "MSFT": "Technology",
        "AMZN": "Consumer Discretionary",
        "NVDA": "Technology",
        "TSLA": "Consumer Discretionary",
        "META": "Communication Services",
        "JPM": "Financials",
        "V": "Financials",
        "JNJ": "Healthcare",
        "UNH": "Healthcare",
        "PG": "Consumer Staples",
        "XOM": "Energy",
        "CVX": "Energy",
        "HD": "Consumer Discretionary",
        "BAC": "Financials",
        "PFE": "Healthcare",
        "KO": "Consumer Staples",
        "DIS": "Communication Services",
        "NFLX": "Communication Services",
        "CASH": "Cash",
    }
    
    # Risk profiles for sectors
    sector_risk = {
        "Technology": "High",
        "Healthcare": "Medium",
        "Financials": "Medium",
        "Consumer Discretionary": "High",
        "Consumer Staples": "Low",
        "Energy": "High",
        "Utilities": "Low",
        "Real Estate": "Medium",
        "Materials": "Medium",
        "Industrials": "Medium",
        "Communication Services": "Medium-High",
        "Cash": "Very Low",
    }
    
    # Calculate sector allocation
    sector_allocation = {}
    unknown_holdings = []
    
    for symbol, percentage in holdings.items():
        symbol = symbol.upper()
        sector = sector_mapping.get(symbol, "Unknown")
        if sector == "Unknown":
            unknown_holdings.append(symbol)
        sector_allocation[sector] = sector_allocation.get(sector, 0) + percentage
    
    # Validate total allocation
    total = sum(holdings.values())
    
    # Determine portfolio type
    tech_weight = sector_allocation.get("Technology", 0)
    cash_weight = sector_allocation.get("Cash", 0)
    
    if tech_weight > 50:
        portfolio_type = "Aggressive Growth"
    elif cash_weight > 30:
        portfolio_type = "Conservative"
    elif tech_weight > 30:
        portfolio_type = "Growth"
    else:
        portfolio_type = "Balanced"
    
    # Calculate concentration metrics
    allocation_values = list(holdings.values())
    max_position = max(allocation_values) if allocation_values else 0
    num_holdings = len([v for v in allocation_values if v > 0])
    
    return {
        "portfolio_summary": {
            "total_allocation": round(total, 2),
            "number_of_holdings": num_holdings,
            "portfolio_type": portfolio_type,
            "largest_position": round(max_position, 2),
            "cash_allocation": round(cash_weight, 2)
        },
        "sector_allocation": sector_allocation,
        "sector_risks": {s: sector_risk.get(s, "Unknown") for s in sector_allocation.keys()},
        "concentration_analysis": {
            "is_concentrated": max_position > 25,
            "concentration_warning": "High single-stock concentration" if max_position > 40 else None,
            "diversification_score": min(100, num_holdings * 10 + (100 - max_position))
        },
        "unknown_holdings": unknown_holdings if unknown_holdings else None,
        "timestamp": datetime.now().isoformat()
    }


def calculate_portfolio_metrics(
    holdings: dict,
    benchmark: str = "SPY"
) -> dict:
    """
    Calculate key portfolio performance metrics.
    
    Args:
        holdings: Dictionary of holdings with percentages
        benchmark: Benchmark symbol for comparison (default: SPY for S&P 500)
    
    Returns:
        Dictionary containing portfolio metrics
    """
    import random
    
    # Simulated metrics for demonstration
    # In production, these would be calculated from actual historical data
    
    # Calculate weighted metrics based on holdings
    num_holdings = len(holdings)
    
    # Simulated returns and risk metrics
    portfolio_return = random.uniform(5, 25)
    benchmark_return = random.uniform(8, 15)
    portfolio_volatility = random.uniform(12, 30)
    benchmark_volatility = 18.5
    
    # Calculate Sharpe Ratio (assuming 4% risk-free rate)
    risk_free_rate = 4.0
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
    
    # Calculate Beta
    beta = portfolio_volatility / benchmark_volatility * random.uniform(0.8, 1.2)
    
    # Calculate Alpha
    alpha = portfolio_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))
    
    # Calculate Sortino Ratio (using downside volatility)
    downside_volatility = portfolio_volatility * random.uniform(0.6, 0.9)
    sortino_ratio = (portfolio_return - risk_free_rate) / downside_volatility
    
    return {
        "performance_metrics": {
            "portfolio_return_ytd": round(portfolio_return, 2),
            "benchmark_return_ytd": round(benchmark_return, 2),
            "excess_return": round(portfolio_return - benchmark_return, 2),
            "portfolio_volatility": round(portfolio_volatility, 2),
            "benchmark_volatility": round(benchmark_volatility, 2)
        },
        "risk_adjusted_metrics": {
            "sharpe_ratio": round(sharpe_ratio, 3),
            "sortino_ratio": round(sortino_ratio, 3),
            "beta": round(beta, 3),
            "alpha": round(alpha, 2),
            "information_ratio": round(random.uniform(-0.5, 1.5), 3)
        },
        "risk_metrics": {
            "max_drawdown": round(random.uniform(-15, -5), 2),
            "value_at_risk_95": round(random.uniform(-3, -1), 2),
            "tracking_error": round(random.uniform(2, 8), 2)
        },
        "benchmark": benchmark,
        "interpretation": {
            "sharpe": "Good" if sharpe_ratio > 1 else "Below average" if sharpe_ratio > 0.5 else "Poor",
            "beta": "Aggressive" if beta > 1.2 else "Market-like" if beta > 0.8 else "Defensive",
            "alpha": "Outperforming" if alpha > 0 else "Underperforming"
        },
        "timestamp": datetime.now().isoformat()
    }


def suggest_rebalancing(
    current_holdings: dict,
    target_allocation: Optional[dict] = None,
    risk_tolerance: str = "moderate"
) -> dict:
    """
    Suggest portfolio rebalancing actions.
    
    Args:
        current_holdings: Current portfolio holdings with percentages
        target_allocation: Target allocation (optional, will suggest if not provided)
        risk_tolerance: Risk tolerance level ('conservative', 'moderate', 'aggressive')
    
    Returns:
        Dictionary containing rebalancing recommendations
    """
    # Default target allocations based on risk tolerance
    default_targets = {
        "conservative": {
            "Stocks": 40,
            "Bonds": 40,
            "Cash": 15,
            "Alternatives": 5
        },
        "moderate": {
            "Stocks": 60,
            "Bonds": 25,
            "Cash": 10,
            "Alternatives": 5
        },
        "aggressive": {
            "Stocks": 80,
            "Bonds": 10,
            "Cash": 5,
            "Alternatives": 5
        }
    }
    
    if target_allocation is None:
        target_allocation = default_targets.get(risk_tolerance.lower(), default_targets["moderate"])
    
    # Analyze current allocation
    current_analysis = analyze_portfolio(current_holdings)
    sector_allocation = current_analysis.get("sector_allocation", {})
    
    # Calculate current asset class allocation
    tech_sectors = ["Technology", "Communication Services"]
    defensive_sectors = ["Consumer Staples", "Utilities", "Healthcare"]
    
    current_allocation = {
        "Stocks": 100 - sector_allocation.get("Cash", 0),
        "Cash": sector_allocation.get("Cash", 0),
        "Bonds": 0,  # Assuming no bonds in simple stock portfolio
        "Alternatives": 0
    }
    
    # Generate rebalancing actions
    actions = []
    
    for asset_class, target_pct in target_allocation.items():
        current_pct = current_allocation.get(asset_class, 0)
        diff = target_pct - current_pct
        
        if abs(diff) > 2:  # Only suggest changes > 2%
            action = "Buy" if diff > 0 else "Sell"
            actions.append({
                "asset_class": asset_class,
                "action": action,
                "current_allocation": round(current_pct, 1),
                "target_allocation": target_pct,
                "adjustment_needed": round(abs(diff), 1),
                "priority": "High" if abs(diff) > 10 else "Medium" if abs(diff) > 5 else "Low"
            })
    
    # Specific stock suggestions
    stock_suggestions = []
    
    # Check for over-concentration
    for symbol, pct in current_holdings.items():
        if pct > 25 and symbol.upper() != "CASH":
            stock_suggestions.append({
                "symbol": symbol,
                "action": "Reduce",
                "reason": f"Position size ({pct}%) exceeds recommended 25% maximum",
                "suggested_target": 20
            })
    
    # Check for under-diversification
    if len(current_holdings) < 10:
        stock_suggestions.append({
            "action": "Diversify",
            "reason": f"Portfolio has only {len(current_holdings)} holdings. Consider adding more positions.",
            "suggestions": ["Consider adding exposure to underrepresented sectors"]
        })
    
    return {
        "risk_tolerance": risk_tolerance,
        "current_allocation": current_allocation,
        "target_allocation": target_allocation,
        "rebalancing_actions": actions,
        "stock_specific_suggestions": stock_suggestions,
        "summary": {
            "total_adjustments_needed": len(actions),
            "urgency": "High" if any(a["priority"] == "High" for a in actions) else "Moderate",
            "estimated_trades": len([a for a in actions if abs(a["adjustment_needed"]) > 5])
        },
        "tax_considerations": "Consider tax implications of selling positions with gains",
        "timestamp": datetime.now().isoformat()
    }
