# Project Structure & Organization

## Directory Layout

```
stock portfolio/
├── portfolio_optimization/          # Main package
│   ├── __init__.py                 # Package initialization
│   ├── models/                     # Core algorithms
│   │   ├── __init__.py             # Models package init
│   │   ├── black_litterman.py      # Black-Litterman optimizer (384 lines)
│   │   ├── advanced_metrics.py     # Risk metrics calculator (500+ lines)
│   │   └── visualizations.py       # Visualization utilities (400 lines)
│   ├── api/                        # REST API backend
│   │   ├── __init__.py             # API package init
│   │   └── server.py               # FastAPI application (11.4 KB)
│   ├── frontend/                   # Web UI
│   │   ├── __init__.py             # Frontend package init
│   │   └── dashboard.py            # Streamlit dashboard (18.8 KB)
│   ├── backtesting/                # Historical analysis
│   │   ├── __init__.py             # Backtesting package init
│   │   └── rolling_backtest.py     # Rolling window analyzer (9.8 KB)
│   ├── config/                     # Settings management
│   │   ├── __init__.py             # Config package init
│   │   └── settings.py             # Configuration dataclasses (3.8 KB)
│   ├── utils/                      # Helper functions
│   │   ├── __init__.py             # Utils package init
│   │   └── installation_verify.py  # Dependency checker (2.5 KB)
│   └── tests/                      # Unit tests
│       └── __init__.py             # Tests package init
├── docs/                           # Documentation
│   ├── README.md                   # Main project documentation
│   ├── DEPLOYMENT.md               # Production deployment guide
│   ├── INSTALLATION_COMPLETE.md    # Setup instructions
│   └── SETUP_GUIDE.py              # Installation helper
├── data/                           # Data directory
│   └── (downloadable data will be cached here)
├── requirements.txt                # Python dependencies
├── run_dashboard.py                # Launch Streamlit UI
├── run_api.py                      # Launch FastAPI server
├── run_analysis.py                 # Run complete analysis
└── (root Python modules - being phased out)
```

## Module Organization

### Portfolio Optimization Core (`portfolio_optimization/models/`)

**black_litterman.py** - Main optimization engine
- `BlackLittermanOptimizer` class
  - `calculate_market_implied_returns()` - CAPM reverse-optimization
  - `apply_black_litterman()` - View integration
  - `optimize_portfolio()` - Final optimization
  - `compare_models()` - Markowitz vs Black-Litterman comparison
- Mathematical foundation: 
  - CAPM: Π = λ * Σ * w_market
  - Black-Litterman: E(R) = [τΣ^(-1) + P^T Ω^(-1) P]^(-1) [τΣ^(-1) Π + P^T Ω^(-1) Q]

**advanced_metrics.py** - Comprehensive risk assessment
- `RiskMetricsCalculator` class
- 20+ metrics:
  - Basic: Sharpe, Sortino, Calmar ratios
  - Advanced: Information Ratio, Beta, Alpha
  - Tail Risk: VaR, CVaR, Expected Shortfall
  - Distribution: Skewness, Kurtosis, Downside Deviation
  - Drawdown: Maximum, Ulcer Index, Recovery Duration

**visualizations.py** - Chart generation
- `PortfolioVisualizer` class
- Plot types:
  - Efficient Frontier (all 2D combinations)
  - Weight Comparison (model comparison)
  - Cumulative Returns (performance over time)
  - Drawdown Analysis (underwater plots)
  - Correlation Heatmap
  - Risk-Return Scatter

### REST API (`portfolio_optimization/api/`)

**server.py** - FastAPI application
- 7 RESTful endpoints:
  - `POST /optimize` - Run optimization with custom views
  - `GET /efficient-frontier` - Get frontier data
  - `GET /risk-metrics` - Compute risk metrics
  - `POST /backtest` - Rolling window backtest
  - `GET /health` - Service status check
  - `GET /config` - Current configuration
  - `GET /assets` - Available assets
- Auto-generated documentation:
  - Swagger UI: `/docs`
  - ReDoc: `/redoc`

### Interactive Dashboard (`portfolio_optimization/frontend/`)

**dashboard.py** - Streamlit web UI
- 5 tabs:
  1. Overview - Configuration and setup
  2. Allocations - Portfolio weight visualization
  3. Performance - Returns and risk analysis
  4. Risk Metrics - Detailed 20+ metrics
  5. Analysis - Model comparison and insights
- Real-time reactivity to user inputs
- Interactive Plotly charts
- Export capability

### Backtesting Engine (`portfolio_optimization/backtesting/`)

**rolling_backtest.py** - Historical validation
- `PortfolioBacktester` class
- Rolling window analysis:
  - 252-day training window
  - Daily rebalancing
  - Walk-forward validation
- Metrics:
  - Information Ratio vs Market
  - Sharpe Ratio evolution
  - Rolling returns and volatility
  - Cumulative performance

### Configuration Management (`portfolio_optimization/config/`)

**settings.py** - Centralized configuration
- 6 config dataclasses:
  - `DataConfig` - Asset list, date range
  - `RiskConfig` - Risk parameters
  - `BacktestConfig` - Backtest settings
  - `APIConfig` - Server parameters
  - `DatabaseConfig` - Data persistence
  - `StreamlitConfig` - UI settings

## Python Imports

### From Root
```python
# Run analysis
from portfolio_optimization.models import BlackLittermanOptimizer

# Use API
from portfolio_optimization.api.server import app

# Launch UI
from portfolio_optimization.frontend.dashboard import main

# Backtest
from portfolio_optimization.backtesting import run_comprehensive_backtest
```

### Within Package
```python
# In dashboard.py
from portfolio_optimization.config import config
from portfolio_optimization.models import BlackLittermanOptimizer

# In api/server.py
from portfolio_optimization.models import BlackLittermanOptimizer, RiskMetricsCalculator
from portfolio_optimization.config import config

# In backtesting/rolling_backtest.py
from portfolio_optimization.models import BlackLittermanOptimizer
```

## Running the Application

### 1. Interactive Dashboard
```bash
python run_dashboard.py
# Opens http://localhost:8501
```

### 2. REST API Server
```bash
python run_api.py
# Opens http://localhost:8000/docs
```

### 3. Command-Line Analysis
```bash
python run_analysis.py
# Prints comprehensive report + backtesting results
```

## Dependencies

**Core Numerical:**
- numpy 2.4.2 - Numerical computing
- scipy 1.17.0 - Scientific functions
- pandas 2.3.3 - Data manipulation

**Data:**
- yfinance 1.2.0 - Yahoo Finance data

**Web Frameworks:**
- fastapi 0.129.0 - REST API
- uvicorn 0.41.0 - ASGI server
- streamlit 1.54.0 - Interactive UI

**Visualization:**
- matplotlib 3.10.8 - Static plots
- seaborn 0.13.2 - Statistical graphics
- plotly 6.5.2 - Interactive charts

**Database:**
- sqlalchemy 2.0.46 - ORM (future PostgreSQL support)

## Design Patterns

### 1. Package Structure
- Separates concerns into modules
- Enables selective imports
- Supports testing isolation
- Professional deployment structure

### 2. Configuration Management
- Centralized in `config/settings.py`
- Dataclass-based for type safety
- Easy override for different environments
- Supports cloud deployment

### 3. API Design
- RESTful principles
- Pydantic models for validation
- Auto-generated documentation
- CORS-enabled for cross-origin requests

### 4. Visualization
- Matplotlib for static reports
- Plotly for interactive exploration
- Streamlit for reactive UI
- Consistent styling across tools

## File Organization Philosophy

**Why This Structure?**

1. **Modularity** - Each component is independent
2. **Scalability** - Easy to add new models/metrics/backends
3. **Testability** - Clear unit testing boundaries
4. **Maintainability** - Logical organization reduces cognitive load
5. **Professionalism** - Industry-standard Python package layout
6. **Deployment** - Ready for Docker/cloud containerization

**Comparison:**

❌ **Bad (Monolithic):**
```
stock_portfolio/
├── black_litterman.py
├── api.py
├── dashboard.py
├── metrics.py
└── lots_of_other_files.py
```

✅ **Good (Modular):**
```
stock_portfolio/
├── portfolio_optimization/
│   ├── models/
│   ├── api/
│   ├── frontend/
│   ├── backtesting/
│   ├── config/
│   └── utils/
```

## Next Steps

1. **Extend Models**
   - Add multi-period asset-liability matching
   - Implement constraint optimization
   - Support factor models

2. **Enhanced Backtesting**
   - Transaction costs
   - Slippage modeling
   - Regime detection

3. **Advanced Metrics**
   - Performance attribution
   - Risk decomposition
   - Style analysis

4. **Database Integration**
   - Cache optimized portfolios
   - Store user preferences
   - Track historical changes

5. **Cloud Deployment**
   - Docker containerization
   - AWS/GCP/Azure deployment
   - Streamlit Cloud hosting
