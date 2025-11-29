"""
Financial calculation tools for various investment computations.
"""
from typing import Optional, List
from datetime import datetime
import math


def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12,
    monthly_contribution: float = 0
) -> dict:
    """
    Calculate compound interest with optional regular contributions.
    
    Args:
        principal: Initial investment amount
        annual_rate: Annual interest rate as percentage (e.g., 7 for 7%)
        years: Investment duration in years
        compounds_per_year: Number of times interest compounds per year (default: 12)
        monthly_contribution: Optional monthly contribution amount
    
    Returns:
        Dictionary containing calculation results and projections
    """
    rate = annual_rate / 100
    n = compounds_per_year
    t = years
    
    # Calculate future value of principal
    # FV = P(1 + r/n)^(nt)
    fv_principal = principal * math.pow(1 + rate/n, n*t)
    
    # Calculate future value of contributions (if any)
    # FV_contributions = PMT × (((1 + r/n)^(nt) - 1) / (r/n))
    if monthly_contribution > 0 and rate > 0:
        monthly_rate = rate / 12
        total_months = years * 12
        fv_contributions = monthly_contribution * ((math.pow(1 + monthly_rate, total_months) - 1) / monthly_rate)
    else:
        fv_contributions = monthly_contribution * years * 12
    
    total_future_value = fv_principal + fv_contributions
    total_contributions = principal + (monthly_contribution * 12 * years)
    total_interest_earned = total_future_value - total_contributions
    
    # Generate yearly breakdown
    yearly_breakdown = []
    running_balance = principal
    running_contributions = principal
    
    for year in range(1, years + 1):
        # Calculate year-end balance
        year_start_balance = running_balance
        
        # Add monthly contributions and compound interest
        for month in range(12):
            running_balance = running_balance * (1 + rate/12)
            if monthly_contribution > 0:
                running_balance += monthly_contribution
                running_contributions += monthly_contribution
        
        yearly_breakdown.append({
            "year": year,
            "balance": round(running_balance, 2),
            "year_growth": round(running_balance - year_start_balance - (monthly_contribution * 12), 2),
            "total_contributions": round(running_contributions, 2)
        })
    
    return {
        "inputs": {
            "principal": principal,
            "annual_rate": f"{annual_rate}%",
            "years": years,
            "compounds_per_year": compounds_per_year,
            "monthly_contribution": monthly_contribution
        },
        "results": {
            "future_value": round(total_future_value, 2),
            "total_contributions": round(total_contributions, 2),
            "total_interest_earned": round(total_interest_earned, 2),
            "effective_annual_rate": round((math.pow(1 + rate/n, n) - 1) * 100, 3)
        },
        "yearly_breakdown": yearly_breakdown[-5:] if len(yearly_breakdown) > 5 else yearly_breakdown,
        "summary": f"Investing ${principal:,.2f} at {annual_rate}% for {years} years with ${monthly_contribution:,.2f}/month contributions yields ${total_future_value:,.2f}",
        "timestamp": datetime.now().isoformat()
    }


def calculate_roi(
    initial_investment: float,
    final_value: float,
    holding_period_years: Optional[float] = None,
    dividends_received: float = 0
) -> dict:
    """
    Calculate Return on Investment (ROI) and related metrics.
    
    Args:
        initial_investment: Initial investment amount
        final_value: Current/final value of investment
        holding_period_years: Optional holding period for annualized returns
        dividends_received: Total dividends received during holding period
    
    Returns:
        Dictionary containing ROI calculations
    """
    # Calculate total return
    total_return = (final_value + dividends_received - initial_investment)
    roi_percentage = (total_return / initial_investment) * 100
    
    result = {
        "inputs": {
            "initial_investment": initial_investment,
            "final_value": final_value,
            "dividends_received": dividends_received
        },
        "returns": {
            "total_return_dollars": round(total_return, 2),
            "total_return_percentage": round(roi_percentage, 2),
            "capital_gain": round(final_value - initial_investment, 2),
            "dividend_return": dividends_received
        }
    }
    
    # Calculate annualized return if holding period provided
    if holding_period_years and holding_period_years > 0:
        # CAGR = (FV/PV)^(1/n) - 1
        total_value = final_value + dividends_received
        cagr = (math.pow(total_value / initial_investment, 1 / holding_period_years) - 1) * 100
        
        result["annualized"] = {
            "holding_period_years": holding_period_years,
            "cagr": round(cagr, 2),
            "average_annual_return": round(roi_percentage / holding_period_years, 2)
        }
        
        # Performance context
        if cagr >= 15:
            performance = "Excellent - significantly above market average"
        elif cagr >= 10:
            performance = "Good - above historical market average"
        elif cagr >= 7:
            performance = "Acceptable - near historical market average"
        elif cagr >= 0:
            performance = "Below average - underperforming market"
        else:
            performance = "Poor - negative returns"
        
        result["performance_assessment"] = performance
    
    return result


def calculate_sharpe_ratio(
    portfolio_return: float,
    risk_free_rate: float,
    portfolio_volatility: float
) -> dict:
    """
    Calculate the Sharpe Ratio for risk-adjusted returns.
    
    Args:
        portfolio_return: Expected/actual portfolio return as percentage
        risk_free_rate: Risk-free rate as percentage (e.g., Treasury yield)
        portfolio_volatility: Portfolio standard deviation as percentage
    
    Returns:
        Dictionary containing Sharpe ratio and interpretation
    """
    if portfolio_volatility <= 0:
        return {"error": "Volatility must be greater than 0"}
    
    # Sharpe Ratio = (Rp - Rf) / σp
    excess_return = portfolio_return - risk_free_rate
    sharpe_ratio = excess_return / portfolio_volatility
    
    # Interpretation
    if sharpe_ratio >= 2:
        interpretation = "Excellent - very strong risk-adjusted returns"
        rating = "★★★★★"
    elif sharpe_ratio >= 1:
        interpretation = "Good - returns adequately compensate for risk"
        rating = "★★★★☆"
    elif sharpe_ratio >= 0.5:
        interpretation = "Average - moderate risk-adjusted returns"
        rating = "★★★☆☆"
    elif sharpe_ratio >= 0:
        interpretation = "Below Average - poor risk compensation"
        rating = "★★☆☆☆"
    else:
        interpretation = "Poor - negative excess returns; risk-free better"
        rating = "★☆☆☆☆"
    
    return {
        "inputs": {
            "portfolio_return": f"{portfolio_return}%",
            "risk_free_rate": f"{risk_free_rate}%",
            "portfolio_volatility": f"{portfolio_volatility}%"
        },
        "sharpe_ratio": round(sharpe_ratio, 3),
        "excess_return": round(excess_return, 2),
        "interpretation": interpretation,
        "rating": rating,
        "context": {
            "typical_sp500_sharpe": "0.4 - 0.6 (long-term)",
            "typical_hedge_fund": "0.5 - 1.5",
            "excellent_fund": "> 1.0"
        },
        "timestamp": datetime.now().isoformat()
    }


def calculate_diversification_score(
    holdings: dict,
    correlation_data: Optional[dict] = None
) -> dict:
    """
    Calculate a diversification score for a portfolio.
    
    Args:
        holdings: Dictionary of holdings with percentages
        correlation_data: Optional correlation matrix between holdings
    
    Returns:
        Dictionary containing diversification analysis
    """
    # Sector mappings
    sector_mapping = {
        "AAPL": "Technology", "GOOGL": "Technology", "MSFT": "Technology",
        "NVDA": "Technology", "META": "Communication Services", "AMZN": "Consumer Discretionary",
        "TSLA": "Consumer Discretionary", "JPM": "Financials", "V": "Financials",
        "JNJ": "Healthcare", "UNH": "Healthcare", "PG": "Consumer Staples",
        "XOM": "Energy", "CVX": "Energy", "CASH": "Cash"
    }
    
    # Market cap categories (simplified)
    cap_mapping = {
        "AAPL": "Large", "GOOGL": "Large", "MSFT": "Large", "NVDA": "Large",
        "META": "Large", "AMZN": "Large", "TSLA": "Large", "JPM": "Large",
        "V": "Large", "JNJ": "Large"
    }
    
    # Calculate sector distribution
    sector_weights = {}
    for symbol, pct in holdings.items():
        sector = sector_mapping.get(symbol.upper(), "Other")
        sector_weights[sector] = sector_weights.get(sector, 0) + pct
    
    # Calculate metrics
    num_holdings = len([v for v in holdings.values() if v > 0])
    num_sectors = len([s for s in sector_weights if sector_weights[s] > 0])
    
    # Concentration metrics
    max_position = max(holdings.values()) if holdings else 0
    max_sector = max(sector_weights.values()) if sector_weights else 0
    
    # Herfindahl-Hirschman Index (HHI) - lower is better
    hhi = sum((pct/100)**2 for pct in holdings.values())
    effective_positions = 1 / hhi if hhi > 0 else 0
    
    # Calculate diversification score (0-100)
    scores = {
        "num_holdings_score": min(num_holdings * 5, 25),  # Max 25 pts for 5+ holdings
        "sector_score": min(num_sectors * 5, 25),  # Max 25 pts for 5+ sectors
        "concentration_score": max(0, 25 - (max_position - 10) * 1),  # Penalize >10% positions
        "sector_concentration_score": max(0, 25 - (max_sector - 25) * 0.5)  # Penalize >25% sectors
    }
    
    total_score = sum(scores.values())
    
    # Determine grade
    if total_score >= 85:
        grade = "A"
        assessment = "Excellent diversification"
    elif total_score >= 70:
        grade = "B"
        assessment = "Good diversification with minor concentration"
    elif total_score >= 55:
        grade = "C"
        assessment = "Moderate diversification - consider rebalancing"
    elif total_score >= 40:
        grade = "D"
        assessment = "Poor diversification - significant concentration risk"
    else:
        grade = "F"
        assessment = "Very poor diversification - high concentration risk"
    
    # Recommendations
    recommendations = []
    if num_holdings < 10:
        recommendations.append(f"Consider adding {10 - num_holdings} more positions")
    if num_sectors < 5:
        recommendations.append(f"Add exposure to {5 - num_sectors} more sectors")
    if max_position > 25:
        recommendations.append(f"Reduce largest position from {max_position}% to under 25%")
    if max_sector > 40:
        recommendations.append(f"Reduce largest sector from {max_sector}% to under 40%")
    
    return {
        "diversification_score": round(total_score, 1),
        "grade": grade,
        "assessment": assessment,
        "score_breakdown": scores,
        "portfolio_stats": {
            "number_of_holdings": num_holdings,
            "number_of_sectors": num_sectors,
            "largest_position_pct": round(max_position, 1),
            "largest_sector_pct": round(max_sector, 1),
            "effective_positions": round(effective_positions, 1),
            "hhi": round(hhi, 4)
        },
        "sector_distribution": sector_weights,
        "recommendations": recommendations if recommendations else ["Portfolio is well-diversified"],
        "ideal_targets": {
            "min_holdings": 10,
            "min_sectors": 5,
            "max_position": "20-25%",
            "max_sector": "30-40%"
        },
        "timestamp": datetime.now().isoformat()
    }
