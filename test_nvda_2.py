import sys
import pandas as pd
import numpy as np

sys.path.insert(0, r"g:\stock portfolio")

from portfolio_optimization.models.black_litterman import BlackLittermanOptimizer

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
start_date = '2021-01-01'
end_date = '2026-02-21'

opt = BlackLittermanOptimizer(tickers, start_date, end_date)
views = {'AAPL': 0.12, 'MSFT': 0.10, 'NVDA': 0.15}
confidence = {'AAPL': 0.60, 'MSFT': 0.50, 'NVDA': 0.65}

# Print the market implied returns
print("\nHistorical Returns:")
print(opt.historical_mean)

implied_returns = opt.calculate_market_implied_returns()

print("\nPosterior Returns:")
post = opt.apply_black_litterman(views, confidence)

print("\nMarkowitz Weights:")
mw = opt.optimize_portfolio(opt.historical_mean)
for t, w in zip(tickers, mw): print(f"{t}: {w:.4f}")

print("\nBL Weights:")
blw = opt.optimize_portfolio(post)
for t, w in zip(tickers, blw): print(f"{t}: {w:.4f}")

print("\nBL Weights (max 0.3):")
blw_capped = opt.optimize_portfolio(post, max_weight=0.3)
for t, w in zip(tickers, blw_capped): print(f"{t}: {w:.4f}")
