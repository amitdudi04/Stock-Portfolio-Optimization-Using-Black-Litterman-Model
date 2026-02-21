# 📊 Bayesian Portfolio Optimization Using the Black-Litterman Model

**A research-grade implementation of advanced portfolio optimization with Bayesian investor views, advanced risk metrics, and comprehensive backtesting.**

---

## 🎯 Project Overview

This project implements the **Black-Litterman portfolio optimization model**, a sophisticated framework that combines:

- **Market-Implied Returns** using the CAPM reverse-solving approach
- **Investor Views** integrated through Bayesian updating
- **Portfolio Optimization** maximizing the Sharpe ratio
- **Advanced Risk Metrics** including VaR, CVaR, and maximum drawdown
- **Comprehensive Backtesting** using rolling-window analysis
- **Professional Visualizations** for decision-making

The Black-Litterman model addresses key limitations of the classic Mean-Variance (Markowitz) approach by incorporating:
1. Market equilibrium conditions
2. Investor's subjective views with confidence levels
3. More stable and realistic portfolio weights
4. Reduced estimation errors in expected returns

---

## 📈 Mathematical Framework

### 1. Market-Implied Returns

Using the reverse-optimization principle:

$$\Pi = \lambda \Sigma w_m$$

Where:
- $\Pi$ = vector of market-implied excess returns
- $\lambda$ = risk aversion coefficient (typically 2.5)
- $\Sigma$ = covariance matrix of asset returns
- $w_m$ = market portfolio weights

### 2. Black-Litterman Posterior Returns

Combining market views with investor views using Bayesian updating:

$$E(R) = \left[(\tau \Sigma)^{-1} + P^T \Omega^{-1} P\right]^{-1} \left[(\tau \Sigma)^{-1} \Pi + P^T \Omega^{-1} Q\right]$$

Where:
- $P$ = view matrix (identifying which assets have views)
- $Q$ = vector of view returns
- $\Omega$ = uncertainty matrix (inverse proportional to confidence)
- $\tau$ = scaling factor for market estimates (typically 0.05)

### 3. Portfolio Optimization

Maximize the Sharpe ratio:

$$\max \frac{E(R_p) - R_f}{\sigma_p}$$

Subject to:
- $\sum w_i = 1$ (weights sum to unity)
- $0 \leq w_i \leq 1$ (no short selling)

### 4. Risk Metrics

**Volatility (Annual Standard Deviation)**
$$\sigma_p = \sqrt{w^T \Sigma w}$$

**Value at Risk (VaR, 95%)**
- The worst expected loss with 95% confidence

**Conditional Value at Risk (CVaR, 95%)**
- Average loss beyond the 95% VaR threshold

**Maximum Drawdown**
$$\text{DD} = \frac{\text{Min Cumulative Return} - \text{Peak Cumulative Return}}{\text{Peak Cumulative Return}}$$

---

## 📦 Project Structure

```
stock-portfolio-optimization/
│
├── black_litterman.py          # Core Black-Litterman implementation
├── visualizations.py            # Portfolio visualization module
├── backtesting.py               # Backtesting and performance analysis
├── main.py                      # Main execution script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
└── results/
    ├── efficient_frontier.png
    ├── weight_comparison.png
    ├── cumulative_returns.png
    ├── drawdown.png
    ├── risk_metrics.png
    └── correlation_matrix.png
```

---

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/amitdudi04/Stock-Portfolio-Optimization-Using-Black-Litterman-Model.git
   cd Stock-Portfolio-Optimization-Using-Black-Litterman-Model
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the main analysis:**
   ```bash
   python main.py
   ```

---

## 💻 Usage Guide

### Basic Example

```python
from black_litterman import BlackLittermanOptimizer
from visualizations import create_visualizations
from backtesting import run_comprehensive_backtest

# Initialize optimizer with historical data
optimizer = BlackLittermanOptimizer(
    ticker_list=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
    start_date='2021-01-01',
    end_date='2026-02-21',
    risk_free_rate=0.03
)

# Define investor views with confidence levels
views = {
    'AAPL': 0.12,   # Expect 12% annual return
    'MSFT': 0.10,   # Expect 10% annual return
    'NVDA': 0.15    # Expect 15% annual return
}

confidence = {
    'AAPL': 0.60,   # 60% confidence in this view
    'MSFT': 0.50,   # 50% confidence
    'NVDA': 0.65    # 65% confidence
}

# Compare models
results = optimizer.compare_models(views, confidence)

# Generate visualizations
create_visualizations(optimizer, results)

# Run backtesting
backtest_results, ir_metrics, sharpe_ratios = run_comprehensive_backtest(
    optimizer, views_dict=views
)
```

### Advanced Features

#### Setting Custom Market Weights
```python
optimizer.market_weights = np.array([0.30, 0.25, 0.20, 0.15, 0.10])
```

#### Adjusting Risk Aversion
```python
optimizer.lambda_risk = 3.0  # More conservative
```

#### Modifying Confidence Levels
```python
confidence = {
    'AAPL': 0.80,  # High confidence
    'MSFT': 0.40   # Low confidence
}
```

---

## 📊 Output Metrics

The optimizer provides comprehensive metrics for each portfolio:

| Metric | Description | Formula |
|--------|-------------|---------|
| Expected Return | Annual portfolio return | $\sum w_i E(R_i)$ |
| Volatility | Annual standard deviation | $\sqrt{w^T \Sigma w}$ |
| Sharpe Ratio | Return per unit of risk | $(R_p - R_f) / \sigma_p$ |
| VaR (95%) | Max loss with 95% confidence | Percentile at 5% |
| CVaR (95%) | Average loss beyond VaR | Mean of worst 5% |
| Max Drawdown | Peak-to-trough decline | Min cumulative return |

---

## 📈 Results Interpretation

### Example Portfolio Comparison

```
MARKOWITZ (Mean-Variance) PORTFOLIO
AAPL:     25.3%
MSFT:     22.1%
GOOGL:    18.5%
AMZN:     20.0%
NVDA:     14.1%

Sharpe Ratio: 1.2345
Volatility: 18.50%

---

BLACK-LITTERMAN PORTFOLIO
AAPL:     15.2%
MSFT:     18.3%
GOOGL:    12.4%
AMZN:     25.1%
NVDA:     29.0%

Sharpe Ratio: 1.3567
Volatility: 17.80%
```

**Interpretation:**
- Black-Litterman produces more **balanced weights** across assets
- Higher **Sharpe ratio** indicates better risk-adjusted returns
- Lower **volatility** demonstrates reduced estimation risk
- Weights reflect both market equilibrium and investor insights

---

## 🧮 Key Concepts

### Black-Litterman vs Markowitz

| Aspect | Markowitz | Black-Litterman |
|--------|-----------|-----------------|
| **Input** | Historical mean returns | Market-implied + views |
| **Stability** | Unstable weights | More stable weights |
| **Estimation Risk** | High | Reduced |
| **Incorporates Views** | No | Yes |
| **Confidence** | Not modeled | Explicitly modeled |
| **Practical Use** | Limited | Widely used (institutional) |

### Understanding Confidence Levels

- **High Confidence (0.7-1.0)**: Strong conviction, large influence on posterior
- **Medium Confidence (0.4-0.7)**: Moderate view, balanced with market
- **Low Confidence (0.0-0.4)**: Weak view, little influence on weights

---

## 🔬 Backtesting Methodology

The backtesting framework uses:

1. **Rolling Window (252 days)**: Train on 1 year of data
2. **Rebalancing Frequency (63 days)**: Quarterly portfolio rebalancing
3. **Out-of-Sample Testing**: Evaluate performance on unseen data
4. **Performance Metrics**:
   - Sharpe Ratio
   - Information Ratio (vs. benchmark)
   - Tracking Error
   - Win Rate

---

## 📊 Visualizations

The project generates six professional visualizations:

1. **Efficient Frontier**
   - Scatter plot of random portfolios
   - Optimal portfolios for each model
   - Sharpe ratio visualization via color

2. **Weight Comparison**
   - Side-by-side bar charts
   - Comparison across models
   - Asset allocation insights

3. **Cumulative Returns**
   - Performance over time
   - Relative outperformance
   - Drawdown context

4. **Drawdown Analysis**
   - Maximum drawdown visualization
   - Risk exposure over time
   - Comparative smoothness

5. **Risk Metrics**
   - Return, volatility, Sharpe ratio
   - VaR and CVaR comparison
   - Comprehensive risk view

6. **Correlation Matrix**
   - Asset correlation heatmap
   - Diversification assessment
   - Risk factor identification

---

## 🎓 Academic Foundation

This implementation is based on:

- **Black, F., & Litterman, R. (1992).** "Global Portfolio Optimization." *Financial Analysts Journal*, 48(5), 28-43.

- **He, G., & Litterman, R. (1999).** "The Intuition Behind Black-Litterman Model Portfolios."

- **Idzorek, T. (2005).** "A Step-by-Step Guide to the Black-Litterman Model."

---

## 🔧 Configuration

### Default Parameters

```python
# Data
ticker_list = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
start_date = '2021-01-01'
end_date = '2026-02-21'

# Risk parameters
risk_free_rate = 0.03
lambda_risk = 2.5
tau = 0.05

# Backtesting
window_size = 252    # 1 year
rebalance_freq = 63  # 1 quarter
```

### Customization

Modify these in `main.py` to adjust:
- Asset universe
- Historical period
- Risk preferences
- Backtesting frequency

---

## 📋 Requirements

- Python 3.8+
- pandas
- numpy
- scipy
- matplotlib
- seaborn
- yfinance

See `requirements.txt` for specific versions.

---

## 🚨 Limitations and Disclaimers

1. **Past Performance**: Historical backtests do not guarantee future results
2. **View Formation**: Quality depends on accuracy of investor views
3. **Estimation Risk**: Covariance matrices can be unstable with small samples
4. **Market Assumptions**: Assumes efficient markets and frictionless trading
5. **Constraints**: Default implementation does not include transaction costs
6. **Rebalancing**: Assumes costless rebalancing (unrealistic in practice)

---

## 🔮 Extensions and Enhancements

Potential improvements for advanced users:

### 1. Multi-Factor Models
```python
# Include Fama-French factors
factors = get_fama_french_factors()
returns_adj = optimizer.returns - factors
```

### 2. Transaction Costs
```python
# Add penalty for portfolio turnover
transaction_cost = 0.001 * sum(abs(new_weights - old_weights))
```

### 3. Constraints
```python
# Add sector or position limits
constraints['sector_limit'] = 0.30
constraints['max_position'] = 0.25
```

### 4. Machine Learning Views
```python
# Use ML predictions for view formation
ml_predictions = train_return_predictor(returns)
views = ml_predictions
```

### 5. Stress Testing
```python
# Monte Carlo simulation
stressed_returns = monte_carlo_simulation(returns, scenarios=1000)
```

---

## 📞 Support and Contact

For questions, issues, or suggestions:

- **GitHub Issues**: [Create an issue](https://github.com/amitdudi04/Stock-Portfolio-Optimization-Using-Black-Litterman-Model/issues)
- **Discussions**: [Start a discussion](https://github.com/amitdudi04/Stock-Portfolio-Optimization-Using-Black-Litterman-Model/discussions)

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👨‍💼 Author

**Portfolio Optimization Research Team**  
February 2026

---

## 🙏 Acknowledgments

- Black, F. and Litterman, R. for the foundational model
- Idzorek, T. for clear explanations
- The open-source Python community

---

## 📚 References

1. **Black-Litterman Model Overview**
   - He, G., & Litterman, R. (1999)
   - Concept, assumptions, and practical applications

2. **Implementation Guides**
   - Idzorek, T. (2005) - Step-by-step guide
   - Walters, J., & Irurozki, G. (2012) - Practical aspects

3. **Risk Metrics**
   - Jorion, P. (2006) - Value at Risk
   - Dowd, K. (2007) - Measuring market risk

4. **Portfolio Optimization**
   - Markowitz, H. (1952) - Original mean-variance model
   - Fabozzi, F. J., et al. (2007) - Encyclopedia of quantitative finance

---

**Happy optimizing! 🚀📊**
