"""
Pytest-based evaluation tests for the Financial Advisor agent.

Run with: pytest evaluation/test_agents.py -v
"""
import pytest
import asyncio
import json
from pathlib import Path

# Import ADK evaluation utilities
try:
    from google.adk.evaluation import run_test_file, EvalResult
    ADK_EVAL_AVAILABLE = True
except ImportError:
    ADK_EVAL_AVAILABLE = False
    run_test_file = None
    EvalResult = None

# Import the agent
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import root_agent


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def agent():
    """Provide the root agent for testing."""
    return root_agent


@pytest.fixture
def evalset_path():
    """Path to the evaluation set JSON file."""
    return Path(__file__).parent / "financial_advisor_eval.evalset.json"


@pytest.fixture
def evalset(evalset_path):
    """Load the evaluation set."""
    with open(evalset_path) as f:
        return json.load(f)


# ============================================================================
# UNIT TESTS - Tool Functionality
# ============================================================================

class TestToolFunctionality:
    """Test individual tool functions work correctly."""
    
    def test_get_stock_price(self):
        """Test stock price retrieval."""
        from tools.market_tools import get_stock_price
        
        result = get_stock_price("AAPL")
        
        assert result["status"] == "success"
        assert result["symbol"] == "AAPL"
        assert "price" in result
        assert "change" in result
        assert "change_percent" in result
        assert isinstance(result["price"], (int, float))
    
    def test_get_market_summary(self):
        """Test market summary retrieval."""
        from tools.market_tools import get_market_summary
        
        result = get_market_summary()
        
        assert "indices" in result
        assert "S&P 500" in result["indices"]
        assert "market_sentiment" in result
        assert "sector_performance" in result
    
    def test_analyze_portfolio(self):
        """Test portfolio analysis."""
        from tools.portfolio_tools import analyze_portfolio
        
        holdings = {"AAPL": 40, "GOOGL": 30, "MSFT": 20, "CASH": 10}
        result = analyze_portfolio(holdings)
        
        assert "portfolio_summary" in result
        assert "sector_allocation" in result
        assert result["portfolio_summary"]["total_allocation"] == 100
        assert result["portfolio_summary"]["number_of_holdings"] == 4
    
    def test_calculate_var(self):
        """Test VaR calculation."""
        from tools.risk_tools import calculate_var
        
        result = calculate_var(
            portfolio_value=100000,
            holdings={"AAPL": 50, "MSFT": 50},
            confidence_level=0.95
        )
        
        assert "var_analysis" in result
        assert "value_at_risk_dollars" in result["var_analysis"]
        assert result["var_analysis"]["confidence_level"] == "95.0%"
    
    def test_calculate_compound_interest(self):
        """Test compound interest calculation."""
        from tools.calculation_tools import calculate_compound_interest
        
        result = calculate_compound_interest(
            principal=10000,
            annual_rate=7,
            years=20
        )
        
        assert "results" in result
        assert result["results"]["future_value"] > 10000  # Should grow
        assert result["results"]["total_interest_earned"] > 0
    
    def test_run_stress_test(self):
        """Test stress testing."""
        from tools.risk_tools import run_stress_test
        
        result = run_stress_test(
            portfolio_value=100000,
            holdings={"AAPL": 50, "MSFT": 50},
            scenario="market_crash"
        )
        
        assert "scenario" in result
        assert "portfolio_summary" in result
        assert result["portfolio_summary"]["total_impact_dollars"] < 0  # Should show loss
    
    def test_diversification_score(self):
        """Test diversification scoring."""
        from tools.calculation_tools import calculate_diversification_score
        
        # Concentrated portfolio
        concentrated = calculate_diversification_score({"AAPL": 90, "CASH": 10})
        
        # Diversified portfolio
        diversified = calculate_diversification_score({
            "AAPL": 15, "GOOGL": 15, "MSFT": 15, "JPM": 15,
            "JNJ": 15, "XOM": 15, "CASH": 10
        })
        
        assert diversified["diversification_score"] > concentrated["diversification_score"]


# ============================================================================
# INTEGRATION TESTS - Agent Behavior
# ============================================================================

class TestAgentBehavior:
    """Test agent responses to various queries."""
    
    @pytest.mark.skipif(not ADK_EVAL_AVAILABLE, reason="ADK evaluation not available")
    def test_simple_query_uses_tools(self, agent):
        """Test that simple queries trigger appropriate tool calls."""
        # This would use ADK's evaluation framework
        pass
    
    def test_agent_has_required_tools(self, agent):
        """Test that agent has all required tools configured."""
        tool_names = [tool.__name__ if callable(tool) else str(tool) 
                      for tool in agent.tools]
        
        required_tools = [
            "get_stock_price",
            "get_market_summary",
            "analyze_portfolio",
            "calculate_var",
        ]
        
        for required in required_tools:
            assert any(required in name for name in tool_names), \
                f"Missing required tool: {required}"
    
    def test_agent_has_sub_agents(self, agent):
        """Test that agent has sub-agents configured."""
        assert hasattr(agent, 'sub_agents'), "Agent should have sub_agents"
        assert len(agent.sub_agents) > 0, "Agent should have at least one sub-agent"


# ============================================================================
# EVALUATION SET TESTS
# ============================================================================

class TestEvaluationSet:
    """Test using the evaluation set."""
    
    def test_evalset_loads(self, evalset):
        """Test that evaluation set loads correctly."""
        assert "test_cases" in evalset
        assert len(evalset["test_cases"]) > 0
    
    def test_evalset_has_required_fields(self, evalset):
        """Test evaluation set structure."""
        required_fields = ["eval_set_id", "name", "test_cases", "evaluation_metrics"]
        for field in required_fields:
            assert field in evalset, f"Missing required field: {field}"
    
    def test_all_test_cases_valid(self, evalset):
        """Test that all test cases have required structure."""
        for test_case in evalset["test_cases"]:
            assert "test_id" in test_case
            assert "session" in test_case
            assert "turns" in test_case["session"]
            
            for turn in test_case["session"]["turns"]:
                assert "user_content" in turn
                assert "expected_tool_use" in turn
    
    @pytest.mark.skipif(not ADK_EVAL_AVAILABLE, reason="ADK evaluation not available")
    @pytest.mark.asyncio
    async def test_run_evaluation_set(self, agent, evalset_path):
        """Run the full evaluation set."""
        # This would use ADK's evaluation runner
        # result = await run_eval_set(agent, evalset_path)
        # assert result.overall_score > 0.7  # 70% threshold
        pass


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test agent performance characteristics."""
    
    def test_tool_response_time(self):
        """Test that tools respond within acceptable time."""
        import time
        from tools.market_tools import get_stock_price
        
        start = time.time()
        get_stock_price("AAPL")
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Tool took too long: {elapsed}s"
    
    def test_portfolio_analysis_scalability(self):
        """Test portfolio analysis with large portfolio."""
        from tools.portfolio_tools import analyze_portfolio
        
        # Create large portfolio
        holdings = {f"STOCK{i}": 100/50 for i in range(50)}
        
        import time
        start = time.time()
        result = analyze_portfolio(holdings)
        elapsed = time.time() - start
        
        assert elapsed < 2.0, f"Analysis took too long: {elapsed}s"
        assert result["portfolio_summary"]["number_of_holdings"] == 50


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_unknown_stock_symbol(self):
        """Test handling of unknown stock symbols."""
        from tools.market_tools import get_stock_price
        
        result = get_stock_price("UNKNOWNXYZ123")
        
        # Should still return a result (with simulated data)
        assert result["status"] == "success"
        assert "note" in result  # Should indicate simulated data
    
    def test_empty_portfolio(self):
        """Test handling of empty portfolio."""
        from tools.portfolio_tools import analyze_portfolio
        
        result = analyze_portfolio({})
        
        assert result["portfolio_summary"]["number_of_holdings"] == 0
    
    def test_invalid_var_inputs(self):
        """Test VaR with edge case inputs."""
        from tools.risk_tools import calculate_var
        
        # Very small portfolio
        result = calculate_var(
            portfolio_value=100,
            holdings={"AAPL": 100},
            confidence_level=0.99
        )
        
        assert result["var_analysis"]["value_at_risk_dollars"] >= 0
    
    def test_negative_returns_calculation(self):
        """Test ROI with negative returns."""
        from tools.calculation_tools import calculate_roi
        
        result = calculate_roi(
            initial_investment=10000,
            final_value=8000  # Loss scenario
        )
        
        assert result["returns"]["total_return_percentage"] < 0


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
