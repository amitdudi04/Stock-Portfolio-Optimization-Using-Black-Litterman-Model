# Research Pipeline Architecture

Market Data (yfinance)
        │
        ▼
Return Calculation
(core/return_calculations.py)
        │
        ▼
Covariance Estimation
(Ledoit–Wolf Shrinkage)
(core/covariance_estimators.py)
        │
        ▼
Black–Litterman Optimization
(models/black_litterman_model.py)
        │
        ▼
Portfolio Optimization
(models/optimizer.py)
        │
        ▼
Rolling Out-of-Sample Backtest
(backtesting/rolling_backtest.py)
        │
        ▼
Transaction Cost Adjustment
(backtesting/transaction_costs.py)
        │
        ▼
Crisis Freeze Stress Testing
(backtesting/crisis_freeze.py)
        │
        ▼
SOE vs Private Structural Study
(analysis/soe_private_analysis.py)
        │
        ▼
Statistical Validation
(analysis/statistical_tests.py)
        │
        ▼
Export Results
(results/v1_final_results)
