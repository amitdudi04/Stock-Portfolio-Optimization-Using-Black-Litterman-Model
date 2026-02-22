import sys
import os
sys.path.insert(0, r"g:\stock portfolio")

from portfolio_optimization.models.black_litterman import BlackLittermanOptimizer

print("Initializing optimizer...")
opt = BlackLittermanOptimizer(['AAPL'], '2022-01-01', '2026-02-01')
print("Returns shape:", opt.returns.shape)
