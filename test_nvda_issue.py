import sys
sys.path.insert(0, r"g:\stock portfolio")

from portfolio_optimization.models.black_litterman import BlackLittermanOptimizer

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
start_date = '2021-01-01'
end_date = '2026-02-21'

opt = BlackLittermanOptimizer(tickers, start_date, end_date)
views = {'AAPL': 0.12, 'MSFT': 0.10}
confidence = {'AAPL': 0.60, 'MSFT': 0.50}

res = opt.compare_models(views, confidence)

print("\n--- Markowitz Weights ---")
for t, w in zip(tickers, res['markowitz']['weights']):
    print(f"{t}: {w:.4f}")

print("\n--- Black-Litterman Weights ---")
for t, w in zip(tickers, res['black_litterman']['weights']):
    print(f"{t}: {w:.4f}")

print("\n--- Equal Weights ---")
for t, w in zip(tickers, res['equal_weight']['weights']):
    print(f"{t}: {w:.4f}")
