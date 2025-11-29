"""
Market data tools for fetching stock prices, market summaries, and news.
"""
from typing import Optional
from datetime import datetime, timedelta
import random


def get_stock_price(symbol: str) -> dict:
    """
    Get current stock price and basic info for a given symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
        
    Returns:
        Dictionary containing price, change, and volume information
    """
    # Simulated data for demonstration
    # In production, this would call a real API like yfinance or Alpha Vantage
    mock_prices = {
        "AAPL": {"price": 178.50, "change": 2.35, "change_pct": 1.33, "volume": 58_000_000},
        "GOOGL": {"price": 141.20, "change": -0.80, "change_pct": -0.56, "volume": 22_000_000},
        "MSFT": {"price": 378.90, "change": 4.20, "change_pct": 1.12, "volume": 25_000_000},
        "AMZN": {"price": 178.25, "change": 1.50, "change_pct": 0.85, "volume": 45_000_000},
        "NVDA": {"price": 495.50, "change": 12.30, "change_pct": 2.55, "volume": 52_000_000},
        "TSLA": {"price": 248.75, "change": -5.25, "change_pct": -2.07, "volume": 98_000_000},
        "META": {"price": 505.30, "change": 8.40, "change_pct": 1.69, "volume": 18_000_000},
        "JPM": {"price": 195.80, "change": 1.20, "change_pct": 0.62, "volume": 12_000_000},
        "V": {"price": 280.45, "change": 2.10, "change_pct": 0.75, "volume": 8_000_000},
        "JNJ": {"price": 158.30, "change": -0.45, "change_pct": -0.28, "volume": 7_500_000},
    }
    
    symbol = symbol.upper()
    
    if symbol in mock_prices:
        data = mock_prices[symbol]
        return {
            "symbol": symbol,
            "price": data["price"],
            "change": data["change"],
            "change_percent": data["change_pct"],
            "volume": data["volume"],
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    else:
        # Generate random data for unknown symbols
        base_price = random.uniform(50, 500)
        change = random.uniform(-10, 10)
        return {
            "symbol": symbol,
            "price": round(base_price, 2),
            "change": round(change, 2),
            "change_percent": round((change / base_price) * 100, 2),
            "volume": random.randint(1_000_000, 100_000_000),
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "note": "Data simulated for demonstration"
        }


def get_market_summary() -> dict:
    """
    Get overall market summary including major indices.
    
    Returns:
        Dictionary containing major market indices and their performance
    """
    return {
        "indices": {
            "S&P 500": {
                "value": 5021.84,
                "change": 25.30,
                "change_pct": 0.51,
                "status": "up"
            },
            "NASDAQ": {
                "value": 15990.66,
                "change": 145.80,
                "change_pct": 0.92,
                "status": "up"
            },
            "DOW": {
                "value": 38996.39,
                "change": -45.20,
                "change_pct": -0.12,
                "status": "down"
            },
            "Russell 2000": {
                "value": 2052.30,
                "change": 12.45,
                "change_pct": 0.61,
                "status": "up"
            }
        },
        "market_sentiment": "bullish",
        "volatility_index": 13.45,
        "fear_greed_index": 68,  # 0-100, higher = greed
        "sector_performance": {
            "Technology": 1.25,
            "Healthcare": 0.45,
            "Financials": 0.32,
            "Consumer Discretionary": 0.88,
            "Energy": -0.75,
            "Utilities": -0.22,
            "Real Estate": 0.15,
            "Materials": 0.42,
            "Industrials": 0.55,
            "Communication Services": 0.95,
            "Consumer Staples": 0.18
        },
        "timestamp": datetime.now().isoformat()
    }


def get_stock_history(
    symbol: str, 
    period: str = "1M"
) -> dict:
    """
    Get historical price data for a stock.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period ('1W', '1M', '3M', '6M', '1Y', '5Y')
        
    Returns:
        Dictionary containing historical price data and statistics
    """
    symbol = symbol.upper()
    
    # Define period in days
    period_days = {
        "1W": 7,
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "1Y": 365,
        "5Y": 1825
    }
    
    days = period_days.get(period, 30)
    
    # Generate simulated historical data
    base_price = random.uniform(100, 400)
    prices = []
    current_price = base_price
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        daily_change = random.uniform(-0.03, 0.035) * current_price
        current_price = max(current_price + daily_change, 10)
        prices.append({
            "date": date,
            "close": round(current_price, 2),
            "volume": random.randint(5_000_000, 80_000_000)
        })
    
    # Calculate statistics
    close_prices = [p["close"] for p in prices]
    
    return {
        "symbol": symbol,
        "period": period,
        "data_points": len(prices),
        "history": prices[-10:],  # Last 10 data points for brevity
        "statistics": {
            "period_high": round(max(close_prices), 2),
            "period_low": round(min(close_prices), 2),
            "period_avg": round(sum(close_prices) / len(close_prices), 2),
            "period_return": round(((prices[-1]["close"] - prices[0]["close"]) / prices[0]["close"]) * 100, 2),
            "volatility": round(random.uniform(15, 45), 2)
        },
        "timestamp": datetime.now().isoformat()
    }


def search_market_news(
    query: str, 
    max_results: int = 5
) -> dict:
    """
    Search for market news and analysis related to a query.
    
    Args:
        query: Search query (e.g., 'AAPL earnings', 'tech sector outlook')
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary containing relevant news articles and summaries
    """
    # Simulated news data for demonstration
    sample_news = [
        {
            "title": f"Market Analysis: {query} Shows Strong Momentum",
            "source": "Financial Times",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": f"Analysts are optimistic about {query} as recent data shows positive trends. Key indicators suggest continued growth in the near term.",
            "sentiment": "positive",
            "relevance_score": 0.95
        },
        {
            "title": f"What Investors Need to Know About {query}",
            "source": "Bloomberg",
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "summary": f"A comprehensive look at {query} and its implications for investors. Experts weigh in on potential risks and opportunities.",
            "sentiment": "neutral",
            "relevance_score": 0.88
        },
        {
            "title": f"Breaking: New Developments in {query}",
            "source": "Reuters",
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "summary": f"Recent announcements regarding {query} have caught market attention. Trading volume has increased significantly.",
            "sentiment": "positive",
            "relevance_score": 0.82
        },
        {
            "title": f"Expert Opinion: {query} Faces Challenges",
            "source": "Wall Street Journal",
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "summary": f"Some analysts express caution regarding {query} citing macroeconomic headwinds and regulatory concerns.",
            "sentiment": "negative",
            "relevance_score": 0.75
        },
        {
            "title": f"Long-term Outlook for {query}",
            "source": "CNBC",
            "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "summary": f"A look at the long-term prospects for {query}. Historical patterns suggest potential for growth despite short-term volatility.",
            "sentiment": "positive",
            "relevance_score": 0.70
        }
    ]
    
    return {
        "query": query,
        "results_count": min(max_results, len(sample_news)),
        "articles": sample_news[:max_results],
        "overall_sentiment": "mixed",
        "timestamp": datetime.now().isoformat()
    }
