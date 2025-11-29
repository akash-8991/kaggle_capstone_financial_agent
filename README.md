# Multi-Agent Financial Decision Support System

A comprehensive financial decision support system built with Google's Agent Development Kit (ADK). This system demonstrates multiple advanced agent concepts to help users make informed financial decisions.

## 🎯 Concepts Implemented

This project implements **8 key concepts** from the ADK framework:

### 1. Multi-Agent System
- **LLM-Powered Agents**: Specialized agents for different financial domains
- **Parallel Agents**: Concurrent data fetching from multiple sources
- **Sequential Agents**: Ordered workflow for analysis pipeline
- **Loop Agents**: Iterative refinement of recommendations

### 2. Tools
- **Custom Tools**: Financial calculations, risk assessment, portfolio analysis
- **MCP Integration**: Model Context Protocol for extensible tool ecosystem
- **Built-in Tools**: Google Search for market news and research

### 3. Sessions & Memory
- **InMemorySessionService**: Session state management for conversations
- **Long-term Memory**: User preference and portfolio history storage
- **State Management**: Tracking analysis progress and user context

### 4. Context Engineering
- **Context Compaction**: Efficient handling of large financial datasets
- **State Key Templates**: Dynamic prompt injection for personalization

### 5. Observability
- **Logging**: Comprehensive logging throughout the system
- **Tracing**: OpenTelemetry-based distributed tracing
- **Metrics**: Performance and usage metrics collection

### 6. Agent Evaluation
- **Evaluation Sets**: Predefined test cases for agent behavior
- **Tool Trajectory Scoring**: Verification of correct tool usage
- **Response Quality Metrics**: Assessment of recommendation quality

### 7. A2A Protocol
- **Agent Cards**: Capability discovery for remote agents
- **Inter-Agent Communication**: Standardized agent-to-agent messaging

### 8. Agent Deployment
- **FastAPI Integration**: Production-ready API server
- **Cloud Run Ready**: Containerized deployment support

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Financial Advisor (Root Agent)                │
│                   Orchestrates all sub-agents                    │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐    ┌───────────────────┐    ┌───────────────────┐
│   Research    │    │    Analysis       │    │  Recommendation   │
│    Agent      │    │     Pipeline      │    │      Agent        │
│  (Parallel)   │    │  (Sequential)     │    │    (Loop)         │
└───────────────┘    └───────────────────┘    └───────────────────┘
        │                       │                       │
   ┌────┼────┐            ┌─────┼─────┐           ┌─────┼─────┐
   │    │    │            │     │     │           │     │     │
   ▼    ▼    ▼            ▼     ▼     ▼           ▼     ▼     ▼
┌────┐┌────┐┌────┐   ┌─────┐┌─────┐┌─────┐   ┌─────┐┌─────┐┌─────┐
│Mkt ││News││Econ│   │Risk ││Port ││Perf │   │Gen  ││Crit ││Ref  │
│Data││Res ││Ind │   │Anal ││Anal ││Eval │   │Rec  ││Eval ││ine  │
└────┘└────┘└────┘   └─────┘└─────┘└─────┘   └─────┘└─────┘└─────┘
```

## 📁 Project Structure

```
financial_agent_system/
├── README.md
├── requirements.txt
├── .env.example
├── __init__.py
├── agent.py                    # Main agent definition (root_agent)
├── config.py                   # Configuration settings
│
├── agents/                     # Sub-agent definitions
│   ├── __init__.py
│   ├── research_agent.py       # Parallel research agents
│   ├── analysis_agent.py       # Sequential analysis pipeline
│   └── recommendation_agent.py # Loop-based recommendation refiner
│
├── tools/                      # Custom tools
│   ├── __init__.py
│   ├── market_tools.py         # Market data tools
│   ├── portfolio_tools.py      # Portfolio analysis tools
│   ├── risk_tools.py           # Risk assessment tools
│   └── calculation_tools.py    # Financial calculations
│
├── mcp/                        # MCP Server integration
│   ├── __init__.py
│   └── financial_mcp_server.py # MCP server for financial tools
│
├── memory/                     # Memory and session management
│   ├── __init__.py
│   └── memory_service.py       # Custom memory implementation
│
├── observability/              # Logging, tracing, metrics
│   ├── __init__.py
│   ├── logging_config.py       # Logging setup
│   ├── tracing.py              # OpenTelemetry tracing
│   └── metrics.py              # Metrics collection
│
├── evaluation/                 # Agent evaluation
│   ├── __init__.py
│   ├── financial_advisor_eval.evalset.json
│   └── test_agents.py          # pytest evaluation tests
│
├── a2a/                        # A2A Protocol support
│   ├── __init__.py
│   ├── agent_card.json         # Agent capability card
│   └── a2a_server.py           # A2A server wrapper
│
└── deployment/                 # Deployment configurations
    ├── Dockerfile
    ├── docker-compose.yml
    └── deploy_api.py           # FastAPI deployment
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Google Cloud Project (for Gemini API)
- API keys for financial data providers (optional)

### Installation

1. Clone the repository:
```bash
cd financial_agent_system
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Running the Agent

**Development UI:**
```bash
adk web .
```

**API Server:**
```bash
adk api_server .
```

**With A2A Protocol:**
```bash
adk api_server . --a2a
```

## 💡 Usage Examples

### Basic Financial Query
```
User: "Should I invest in tech stocks right now?"
Agent: [Researches market conditions, analyzes risk, provides recommendation]
```

### Portfolio Analysis
```
User: "Analyze my portfolio: 40% AAPL, 30% GOOGL, 20% MSFT, 10% cash"
Agent: [Calculates metrics, assesses diversification, suggests rebalancing]
```

### Risk Assessment
```
User: "What's my risk exposure if the market drops 20%?"
Agent: [Runs stress tests, calculates VaR, provides risk mitigation strategies]
```

## 🧪 Running Evaluations

**Via CLI:**
```bash
adk eval . evaluation/financial_advisor_eval.evalset.json
```

**Via pytest:**
```bash
pytest evaluation/test_agents.py -v
```

**Via Web UI:**
1. Run `adk web .`
2. Navigate to Eval tab
3. Load evaluation set
4. Run evaluations

## 📊 Observability

### Viewing Traces
- **Local**: Use ADK Web UI's trace viewer
- **Cloud**: Enable Cloud Trace with `--trace_to_cloud`

### Metrics
- Agent response latency
- Tool call success rates
- Memory usage statistics

### Logging
Logs are written to `logs/financial_agent.log` with configurable levels.

## 🔒 Security Considerations

- API keys stored in environment variables
- Input validation on all financial calculations
- Rate limiting on external API calls
- No storage of sensitive financial data

## 📝 License

Apache 2.0 License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.
