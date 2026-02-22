import sys
import numpy as np
sys.path.insert(0, r"g:\stock portfolio")

from portfolio_optimization.models.black_litterman import BlackLittermanOptimizer

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
opt = BlackLittermanOptimizer(tickers, '2021-01-01', '2026-02-21')

views = {'AAPL': 0.12, 'MSFT': 0.10, 'NVDA': 0.15}
confidence = {'AAPL': 0.60, 'MSFT': 0.50, 'NVDA': 0.65}

returns = opt.historical_mean

# Objective without L2
def sharpe_only(weights):
    ret = np.sum(weights * returns)
    vol = np.sqrt(weights @ opt.cov_matrix @ weights)
    return (ret - 0.03) / vol

print("\n--- Sharpe Component Sizes ---")
weights_eq = np.array([0.2]*5)
weights_max = np.array([0.05, 0.05, 0.05, 0.45, 0.40]) # Example

sharpe_eq = sharpe_only(weights_eq)
sharpe_max = sharpe_only(weights_max)

print(f"Equal Weights Sharpe: {sharpe_eq:.4f}")
print(f"Max NVDA Sharpe: {sharpe_max:.4f}")

l2_eq_05 = 0.5 * np.sum(weights_eq**2)
l2_max_05 = 0.5 * np.sum(weights_max**2)

print(f"L2(0.5) Diff: {l2_max_05 - l2_eq_05:.4f}")
print(f"Sharpe Diff: {sharpe_max - sharpe_eq:.4f}")

l2_eq_2 = 2.0 * np.sum(weights_eq**2)
l2_max_2 = 2.0 * np.sum(weights_max**2)

print(f"L2(2.0) Diff: {l2_max_2 - l2_eq_2:.4f}")
