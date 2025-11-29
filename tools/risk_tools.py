"""
Risk assessment tools for evaluating portfolio and market risks.
"""
from typing import Optional
from datetime import datetime
import random
import math


def calculate_var(
    portfolio_value: float,
    holdings: dict,
    confidence_level: float = 0.95,
    time_horizon_days: int = 1
) -> dict:
    """
    Calculate Value at Risk (VaR) for a portfolio.
    
    Args:
        portfolio_value: Total portfolio value in dollars
        holdings: Dictionary of holdings with percentages
        confidence_level: Confidence level (default 0.95 for 95%)
        time_horizon_days: Time horizon in days (default 1)
    
    Returns:
        Dictionary containing VaR calculations and analysis
    """
    # Simulated volatilities for different assets
    asset_volatilities = {
        "AAPL": 0.25,
        "GOOGL": 0.28,
        "MSFT": 0.24,
        "AMZN": 0.32,
        "NVDA": 0.45,
        "TSLA": 0.55,
        "META": 0.35,
        "JPM": 0.22,
        "V": 0.20,
        "JNJ": 0.15,
        "CASH": 0.0,
    }
    
    # Calculate portfolio volatility (simplified - assumes no correlation)
    portfolio_variance = 0
    for symbol, percentage in holdings.items():
        symbol = symbol.upper()
        weight = percentage / 100
        vol = asset_volatilities.get(symbol, 0.30)  # Default 30% volatility
        portfolio_variance += (weight * vol) ** 2
    
    portfolio_volatility = math.sqrt(portfolio_variance)
    
    # Z-scores for different confidence levels
    z_scores = {
        0.90: 1.28,
        0.95: 1.65,
        0.99: 2.33
    }
    z_score = z_scores.get(confidence_level, 1.65)
    
    # Calculate VaR
    # VaR = Portfolio Value × Z-score × Volatility × sqrt(time)
    daily_var = portfolio_value * z_score * portfolio_volatility * math.sqrt(time_horizon_days / 252)
    var_percentage = (daily_var / portfolio_value) * 100
    
    # Calculate CVaR (Conditional VaR / Expected Shortfall)
    cvar = daily_var * 1.25  # Simplified approximation
    
    return {
        "var_analysis": {
            "portfolio_value": portfolio_value,
            "confidence_level": f"{confidence_level * 100}%",
            "time_horizon_days": time_horizon_days,
            "value_at_risk_dollars": round(daily_var, 2),
            "value_at_risk_percentage": round(var_percentage, 2),
            "conditional_var_dollars": round(cvar, 2),
            "conditional_var_percentage": round((cvar / portfolio_value) * 100, 2)
        },
        "interpretation": {
            "var_meaning": f"There is a {(1-confidence_level)*100}% chance of losing more than ${daily_var:,.2f} over {time_horizon_days} day(s)",
            "cvar_meaning": f"If losses exceed VaR, the expected loss is approximately ${cvar:,.2f}"
        },
        "portfolio_risk_metrics": {
            "annualized_volatility": round(portfolio_volatility * 100, 2),
            "daily_volatility": round(portfolio_volatility * 100 / math.sqrt(252), 2)
        },
        "risk_assessment": "High" if var_percentage > 3 else "Moderate" if var_percentage > 1.5 else "Low",
        "timestamp": datetime.now().isoformat()
    }


def assess_risk_profile(
    age: int,
    investment_horizon_years: int,
    annual_income: float,
    liquid_net_worth: float,
    risk_capacity_score: Optional[int] = None
) -> dict:
    """
    Assess an investor's risk profile based on their characteristics.
    
    Args:
        age: Investor's age
        investment_horizon_years: Investment time horizon in years
        annual_income: Annual income in dollars
        liquid_net_worth: Liquid net worth in dollars
        risk_capacity_score: Optional self-assessed risk score (1-10)
    
    Returns:
        Dictionary containing risk profile assessment and recommendations
    """
    # Calculate risk capacity based on factors
    
    # Age factor (younger = more risk capacity)
    if age < 30:
        age_factor = 10
    elif age < 40:
        age_factor = 8
    elif age < 50:
        age_factor = 6
    elif age < 60:
        age_factor = 4
    else:
        age_factor = 2
    
    # Time horizon factor
    if investment_horizon_years >= 20:
        horizon_factor = 10
    elif investment_horizon_years >= 10:
        horizon_factor = 8
    elif investment_horizon_years >= 5:
        horizon_factor = 6
    elif investment_horizon_years >= 3:
        horizon_factor = 4
    else:
        horizon_factor = 2
    
    # Income stability factor (simplified)
    income_to_expenses_ratio = min(annual_income / 50000, 2)  # Normalized
    income_factor = income_to_expenses_ratio * 5
    
    # Net worth factor
    if liquid_net_worth >= 1_000_000:
        networth_factor = 10
    elif liquid_net_worth >= 500_000:
        networth_factor = 8
    elif liquid_net_worth >= 250_000:
        networth_factor = 6
    elif liquid_net_worth >= 100_000:
        networth_factor = 4
    else:
        networth_factor = 2
    
    # Calculate composite score
    objective_score = (age_factor * 0.25 + horizon_factor * 0.35 + 
                       income_factor * 0.20 + networth_factor * 0.20)
    
    # Adjust with self-assessed score if provided
    if risk_capacity_score:
        final_score = (objective_score * 0.7) + (risk_capacity_score * 0.3)
    else:
        final_score = objective_score
    
    # Determine risk profile
    if final_score >= 8:
        risk_profile = "Aggressive"
        stock_allocation = "80-100%"
        bond_allocation = "0-20%"
    elif final_score >= 6:
        risk_profile = "Moderately Aggressive"
        stock_allocation = "60-80%"
        bond_allocation = "20-40%"
    elif final_score >= 4:
        risk_profile = "Moderate"
        stock_allocation = "40-60%"
        bond_allocation = "40-60%"
    elif final_score >= 2:
        risk_profile = "Moderately Conservative"
        stock_allocation = "20-40%"
        bond_allocation = "60-80%"
    else:
        risk_profile = "Conservative"
        stock_allocation = "0-20%"
        bond_allocation = "80-100%"
    
    return {
        "risk_profile": risk_profile,
        "risk_score": round(final_score, 1),
        "score_breakdown": {
            "age_factor": round(age_factor, 1),
            "horizon_factor": round(horizon_factor, 1),
            "income_factor": round(income_factor, 1),
            "networth_factor": round(networth_factor, 1),
            "self_assessment": risk_capacity_score
        },
        "recommended_allocation": {
            "stocks": stock_allocation,
            "bonds": bond_allocation,
            "alternatives": "0-10%",
            "cash": "5-10%"
        },
        "key_considerations": [
            f"Your investment horizon of {investment_horizon_years} years {'allows' if investment_horizon_years >= 10 else 'limits'} exposure to volatile assets",
            f"At age {age}, you have {'significant' if age < 40 else 'limited'} time to recover from market downturns",
            "Consider rebalancing annually to maintain target allocation"
        ],
        "timestamp": datetime.now().isoformat()
    }


def run_stress_test(
    portfolio_value: float,
    holdings: dict,
    scenario: str = "market_crash"
) -> dict:
    """
    Run stress tests on a portfolio under various market scenarios.
    
    Args:
        portfolio_value: Total portfolio value in dollars
        holdings: Dictionary of holdings with percentages
        scenario: Stress test scenario ('market_crash', 'tech_bubble', 'inflation_spike', 
                  'interest_rate_hike', 'recession', 'custom')
    
    Returns:
        Dictionary containing stress test results and analysis
    """
    # Define scenario impacts by sector
    scenario_impacts = {
        "market_crash": {
            "description": "Broad market decline similar to 2008 or March 2020",
            "impacts": {
                "Technology": -35,
                "Financials": -45,
                "Consumer Discretionary": -40,
                "Healthcare": -20,
                "Consumer Staples": -15,
                "Energy": -50,
                "Utilities": -10,
                "Communication Services": -30,
                "Real Estate": -35,
                "Materials": -40,
                "Industrials": -35,
                "Cash": 0
            }
        },
        "tech_bubble": {
            "description": "Technology sector collapse similar to 2000-2002",
            "impacts": {
                "Technology": -60,
                "Communication Services": -55,
                "Consumer Discretionary": -25,
                "Financials": -15,
                "Healthcare": -5,
                "Consumer Staples": 0,
                "Energy": 5,
                "Utilities": 5,
                "Cash": 0
            }
        },
        "inflation_spike": {
            "description": "Rapid inflation increase (>8% annual)",
            "impacts": {
                "Technology": -25,
                "Financials": -10,
                "Consumer Discretionary": -20,
                "Healthcare": -5,
                "Consumer Staples": -10,
                "Energy": 15,
                "Utilities": -15,
                "Communication Services": -20,
                "Real Estate": -25,
                "Materials": 10,
                "Cash": -8  # Purchasing power loss
            }
        },
        "interest_rate_hike": {
            "description": "Rapid interest rate increases (300+ bps)",
            "impacts": {
                "Technology": -30,
                "Financials": 10,
                "Consumer Discretionary": -20,
                "Healthcare": -10,
                "Consumer Staples": -5,
                "Energy": -10,
                "Utilities": -25,
                "Real Estate": -35,
                "Communication Services": -25,
                "Cash": 3  # Higher rates benefit
            }
        },
        "recession": {
            "description": "Economic recession with GDP contraction",
            "impacts": {
                "Technology": -25,
                "Financials": -30,
                "Consumer Discretionary": -35,
                "Healthcare": -10,
                "Consumer Staples": -5,
                "Energy": -30,
                "Utilities": -5,
                "Communication Services": -20,
                "Real Estate": -25,
                "Industrials": -30,
                "Cash": 0
            }
        }
    }
    
    # Get scenario parameters
    scenario_data = scenario_impacts.get(scenario.lower(), scenario_impacts["market_crash"])
    impacts = scenario_data["impacts"]
    
    # Sector mappings
    sector_mapping = {
        "AAPL": "Technology", "GOOGL": "Technology", "MSFT": "Technology",
        "NVDA": "Technology", "META": "Communication Services", "AMZN": "Consumer Discretionary",
        "TSLA": "Consumer Discretionary", "JPM": "Financials", "V": "Financials",
        "JNJ": "Healthcare", "CASH": "Cash"
    }
    
    # Calculate portfolio impact
    total_impact = 0
    position_impacts = []
    
    for symbol, percentage in holdings.items():
        symbol = symbol.upper()
        sector = sector_mapping.get(symbol, "Technology")  # Default to Tech
        sector_impact = impacts.get(sector, -20)  # Default -20%
        
        position_value = portfolio_value * (percentage / 100)
        position_loss = position_value * (sector_impact / 100)
        total_impact += position_loss
        
        position_impacts.append({
            "symbol": symbol,
            "sector": sector,
            "current_value": round(position_value, 2),
            "scenario_impact_pct": sector_impact,
            "projected_loss": round(position_loss, 2),
            "projected_value": round(position_value + position_loss, 2)
        })
    
    # Sort by impact
    position_impacts.sort(key=lambda x: x["projected_loss"])
    
    portfolio_impact_pct = (total_impact / portfolio_value) * 100
    
    return {
        "scenario": scenario,
        "scenario_description": scenario_data["description"],
        "portfolio_summary": {
            "initial_value": portfolio_value,
            "projected_value": round(portfolio_value + total_impact, 2),
            "total_impact_dollars": round(total_impact, 2),
            "total_impact_percentage": round(portfolio_impact_pct, 2)
        },
        "position_analysis": position_impacts,
        "most_vulnerable_positions": [p for p in position_impacts[:3]],
        "most_resilient_positions": [p for p in position_impacts[-3:]],
        "risk_assessment": {
            "severity": "Severe" if portfolio_impact_pct < -30 else "High" if portfolio_impact_pct < -20 else "Moderate",
            "recovery_estimate": "12-24 months" if portfolio_impact_pct < -30 else "6-12 months" if portfolio_impact_pct < -20 else "3-6 months"
        },
        "recommendations": [
            "Consider increasing cash allocation for protection" if portfolio_impact_pct < -25 else "Portfolio shows reasonable resilience",
            "Review sector concentration in vulnerable areas",
            "Consider hedging strategies for high-risk positions"
        ],
        "timestamp": datetime.now().isoformat()
    }
