import sys
import json
sys.path.insert(0, r"g:\stock portfolio")

from portfolio_optimization.models.black_litterman import BlackLittermanOptimizer

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
start_date = '2021-01-01'
end_date = '2026-02-21'

opt = BlackLittermanOptimizer(tickers, start_date, end_date)
views = {'AAPL': 0.12, 'MSFT': 0.10, 'NVDA': 0.15}

res = opt.compare_models(views)

output = {
    "bl": res['black_litterman']['metrics'].get('Expected Return'),
    "bl_vol": res['black_litterman']['metrics'].get('Volatility'),
    "mw": res['markowitz']['metrics'].get('Expected Return'),
    "eq": res['equal_weight']['metrics'].get('Expected Return')
}

with open("metrics_out.json", "w") as f:
    json.dump(output, f)

print("Wrote to metrics_out.json")
