import sys
sys.path.insert(0, r"g:\stock portfolio")

from portfolio_optimization.models.black_litterman import BlackLittermanOptimizer

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
start_date = '2021-01-01'
end_date = '2026-02-21'

opt = BlackLittermanOptimizer(tickers, start_date, end_date)
views = {'AAPL': 0.12, 'MSFT': 0.10, 'NVDA': 0.15}
confidence = {'AAPL': 0.60, 'MSFT': 0.50, 'NVDA': 0.65}

res = opt.compare_models(views, confidence)

print("\n--- Model Metrics Used by Chart ---")
print("Black-Litterman Expected Return:", res['black_litterman']['metrics'].get('Expected Return', 'Missing'))
print("Black-Litterman Volatility:", res['black_litterman']['metrics'].get('Volatility', 'Missing'))
print("Markowitz Expected Return:", res['markowitz']['metrics'].get('Expected Return', 'Missing'))
print("Markowitz Volatility:", res['markowitz']['metrics'].get('Volatility', 'Missing'))
