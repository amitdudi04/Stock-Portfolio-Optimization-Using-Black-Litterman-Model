import sys
sys.path.insert(0, r"g:\stock portfolio")

from portfolio_optimization.models.black_litterman import BlackLittermanOptimizer

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
start_date = '2021-01-01'
end_date = '2026-02-21'

opt = BlackLittermanOptimizer(tickers, start_date, end_date)
views = {'AAPL': 0.12, 'MSFT': 0.10, 'NVDA': 0.15}

res = opt.compare_models(views)

print("---")
print("BL Return:", res['black_litterman']['metrics'].get('Expected Return'))
print("MW Return:", res['markowitz']['metrics'].get('Expected Return'))
print("EQ Return:", res['equal_weight']['metrics'].get('Expected Return'))
