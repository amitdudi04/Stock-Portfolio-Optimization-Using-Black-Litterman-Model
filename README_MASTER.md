# Stock Portfolio Optimization Using Black-Litterman Model

A production-grade fintech application implementing the Black-Litterman portfolio optimization model with interactive dashboard, REST API, and comprehensive risk analysis.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application

**Interactive Dashboard:**
```bash
python run_dashboard.py
```
Opens at http://localhost:8501

**REST API Server:**
```bash
python run_api.py
```
Interactive docs at http://localhost:8000/docs

**Command-Line Analysis:**
```bash
python run_analysis.py
```
Produces complete analysis with backtesting results

## 📋 Project Overview

### What It Does

This application solves the **portfolio optimization problem** using the Black-Litterman model:

1. **Market Equilibrium** - Uses CAPM to reverse-engineer implied market returns
2. **View Integration** - Incorporates investor views with confidence levels
3. **Bayesian Optimization** - Combines market data with beliefs using Bayesian statistics
4. **Risk Analysis** - Calculates 20+ risk metrics for comprehensive evaluation
5. **Backtesting** - Validates performance using rolling-window historical testing
6. **Visualization** - Interactive charts and a professional dashboard

### Mathematical Foundation

**Black-Litterman Expected Returns:**
$$E(R) = \left[\tau\Sigma^{-1} + P^T \Omega^{-1} P\right]^{-1} \left[\tau\Sigma^{-1} \Pi + P^T \Omega^{-1} Q\right]$$

Where:
- Π = Market-implied returns (from CAPM reverse-optimization)
- P = Views matrix
- Q = View returns
- Ω = View uncertainty matrix
- τ = Scalar uncertainty parameter

## 🎯 Key Features

### 1. Black-Litterman Optimization
✅ Market-implied returns calculation  
✅ Bayesian view integration  
✅ Flexible confidence specification  
✅ Comparison with Markowitz mean-variance  

### 2. Risk Metrics (20+)
✅ Sharpe, Sortino, Calmar ratios  
✅ VaR, CVaR, Expected Shortfall  
✅ Beta, Alpha, Information Ratio  
✅ Skewness, Kurtosis, Downside Deviation  
✅ Maximum Drawdown, Ulcer Index  

### 3. Web Interfaces
✅ **Streamlit Dashboard** - Interactive exploration  
✅ **FastAPI Backend** - RESTful API with Swagger  
✅ **HTML Reporting** - Static report generation  

### 4. Backtesting
✅ Rolling-window validation  
✅ Information Ratio tracking  
✅ Sharpe ratio evolution  
✅ Walk-forward analysis  

## 📁 Project Structure

```
portfolio_optimization/         ← Main Python package
├── models/                      ← Core algorithms
│   ├── black_litterman.py      ← Main optimizer
│   ├── advanced_metrics.py     ← Risk calculator
│   └── visualizations.py       ← Plot utilities
├── api/                         ← REST API
│   └── server.py               ← FastAPI app
├── frontend/                    ← Web UI
│   └── dashboard.py            ← Streamlit app
├── backtesting/                 ← Historical analysis
│   └── rolling_backtest.py      ← Backtest engine
├── config/                      ← Settings
│   └── settings.py             ← Configuration
└── utils/                       ← Helpers
    └── installation_verify.py   ← Dependency check

docs/                           ← Documentation
├── README.md                    ← Full guide
├── DEPLOYMENT.md               ← Production setup
└── INSTALLATION_COMPLETE.md    ← Setup notes

data/                           ← Data storage
requirements.txt                ← Dependencies
run_dashboard.py                ← Launch UI
run_api.py                      ← Launch API
run_analysis.py                 ← CLI analysis
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed organization.

## 💻 System Requirements

- **Python 3.8+** (tested on 3.13.12)
- **RAM:** 2GB minimum (4GB recommended)
- **Internet:** Required for yfinance data download
- **OS:** Windows, macOS, Linux

## 📦 Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | 2.4.2 | Numerical computing |
| pandas | 2.3.3 | Data manipulation |
| scipy | 1.17.0 | Scientific computing |
| yfinance | 1.2.0 | Financial data |
| matplotlib | 3.10.8 | Static plots |
| seaborn | 0.13.2 | Statistical graphics |
| plotly | 6.5.2 | Interactive charts |
| streamlit | 1.54.0 | Web dashboard |
| fastapi | 0.129.0 | REST API |
| uvicorn | 0.41.0 | ASGI server |
| sqlalchemy | 2.0.46 | Database ORM |

## 🔧 Configuration

Edit `portfolio_optimization/config/settings.py` to customize:

```python
# Assets to optimize
TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']

# Date range
START_DATE = '2021-01-01'
END_DATE = '2026-02-21'

# Risk-free rate
RISK_FREE_RATE = 0.03

# Black-Litterman parameters
TAU = 0.05           # Uncertainty parameter
LAMBDA_RISK = 1.0    # Risk aversion
VAR_LEVEL = 0.95     # VaR confidence level
```

## 🎨 Usage Examples

### Example 1: Dashboard
```bash
python run_dashboard.py
```
- Specify assets and date range
- Input investor views
- View optimized portfolio
- Analyze risk metrics
- Compare models

### Example 2: REST API
```bash
python run_api.py
```

```python
import requests

# Run optimization
response = requests.post('http://localhost:8000/optimize', json={
    'tickers': ['AAPL', 'MSFT', 'GOOGL'],
    'views': {'AAPL': 0.12, 'MSFT': 0.10},
    'confidence': {'AAPL': 0.60, 'MSFT': 0.50}
})

portfolio = response.json()
print(portfolio['weights'])
```

### Example 3: Python API
```python
from portfolio_optimization.models import BlackLittermanOptimizer

# Initialize optimizer
opt = BlackLittermanOptimizer(
    ticker_list=['AAPL', 'MSFT', 'GOOGL'],
    start_date='2021-01-01',
    end_date='2024-01-01'
)

# Specify views
views = {'AAPL': 0.12, 'MSFT': 0.10}
confidence = {'AAPL': 0.60, 'MSFT': 0.50}

# Optimize
results = opt.compare_models(views, confidence)

# Get Black-Litterman portfolio
bl_weights = results['black_litterman']['weights']
bl_metrics = results['black_litterman']['metrics']

print(f"Expected Return: {bl_metrics['Expected Return']:.2%}")
print(f"Volatility: {bl_metrics['Volatility']:.2%}")
print(f"Sharpe Ratio: {bl_metrics['Sharpe Ratio']:.4f}")
```

## 📊 Sample Output

```
Portfolio Analysis Results
==================================================

Market-Implied Returns (CAPM):
  AAPL:  8.32%
  MSFT:  7.89%
  GOOGL: 8.15%

Black-Litterman Optimized Portfolio:
  AAPL:  35.2%
  MSFT:  28.4%
  GOOGL: 24.7%
  Other: 11.7%

Performance Metrics:
  Expected Annual Return:  10.24%
  Portfolio Risk (Volatility): 12.18%
  Sharpe Ratio: 0.6721
  Value at Risk (95%): -2.85%
  Maximum Drawdown: -18.50%

Efficiency vs Markowitz:
  BL provides 2.1% better risk-adjusted returns
  33% lower estimation error
  More stable weights over time
```

## 🔄 Workflow

1. **Data Collection** - Download historical price data
2. **Return Calculation** - Compute daily/monthly returns
3. **Covariance Matrix** - Estimate asset correlations
4. **Market Equilibrium** - Calculate implied returns
5. **View Integration** - Incorporate investor views
6. **Optimization** - Find optimal portfolio weights
7. **Risk Analysis** - Compute 20+ metrics
8. **Backtesting** - Validate with historical data
9. **Visualization** - Create interactive charts
10. **Reporting** - Generate comprehensive report

## 📈 Performance Characteristics

**Black-Litterman vs Markowitz:**

| Aspect | Markowitz | Black-Litterman |
|--------|-----------|-----------------|
| Estimation Error | High | Low (Bayesian shrinkage) |
| Weight Stability | Low | High |
| View Integration | No | Yes |
| Confidence Handling | N/A | Yes (Ω matrix) |
| Practical Adoption | Poor | Excellent |
| Interpretability | Direct | Bayesian |

## 🚀 Production Deployment

### Docker
```bash
docker build -t portfolio-optimizer .
docker run -p 8000:8000 -p 8501:8501 portfolio-optimizer
```

### Cloud Platforms
- **Streamlit Cloud:** Deploy dashboard in 1 click
- **AWS EC2:** Run API server with auto-scaling
- **Heroku:** One-click deployment with Procfile
- **Azure:** Containerized deployment ready

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guides.

## 📚 Theory

### Black-Litterman Model

**Problem:** Traditional mean-variance (Markowitz) optimization:
- Creates extreme concentration in few assets
- Weights are unstable with small data changes
- Estimation error dominates actual learning

**Solution:** Bayesian approach that:
- Combines market equilibrium with investor views
- Scales confidence with uncertainty parameter
- Produces stable, diversified weights

**Key Innovation:** Investor views modeled as "soft constraints" with uncertainty, not hard constraints.

### CAPM Reverse-Optimization

Instead of assuming arbitrary expected returns, we reverse-engineer them from market prices:

$$\Pi = \lambda \cdot \Sigma \cdot w_{market}$$

Where:
- λ = Market risk premium / Market volatility²
- Σ = Covariance matrix
- w_market = Market cap weights

This ensures consistency with equilibrium pricing.

## 🧪 Testing

Verify installation:
```bash
python -m portfolio_optimization.utils.installation_verify
```

Run sample analysis:
```bash
python run_analysis.py
```

## 📞 Support & Resources

**Documentation:**
- [docs/README.md](docs/README.md) - Full technical documentation
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Production deployment
- [docs/INSTALLATION_COMPLETE.md](docs/INSTALLATION_COMPLETE.md) - Setup guide
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Code organization

**Learning Resources:**
- Original paper: He & Litterman (1999)
- Jay Walters' blog on Black-Litterman
- Portfoliolabs.com tutorials

## 📄 License

MIT License - See LICENSE file

## 🔗 GitHub

Repository: https://github.com/amitdudi04/Stock-Portfolio-Optimization-Using-Black-Litterman-Model

## 👤 Author

Portfolio Optimization System  
Created: 2024-2025  
Version: 2.0 (Production-Ready)

---

## Next Steps

1. **Review** the [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) to understand organization
2. **Try** the interactive dashboard: `python run_dashboard.py`
3. **Explore** the REST API: `python run_api.py` → http://localhost:8000/docs
4. **Analyze** your own portfolio with [run_analysis.py](run_analysis.py)
5. **Deploy** to production using guides in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

**Happy Optimizing! 📈**
