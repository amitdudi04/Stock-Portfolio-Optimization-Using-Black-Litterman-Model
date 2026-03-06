import os
import sys
import yaml
import numpy as np

sys.path.append(os.path.abspath('.'))

from pipelines.run_tri_market_pipeline import run_rolling_backtest
from core.data_loader import download_market_data
from core.return_calculations import compute_log_returns

prices = download_market_data(['SPY', 'ASHR', 'INDA'], start_date='2005-01-01', end_date='2025-01-01')
returns = compute_log_returns(prices)
initial_weights = np.array([0.4, 0.4, 0.2])

_, weights_df = run_rolling_backtest(returns, initial_weights, 252, model_type='black_litterman')

diffs = weights_df.diff().dropna()
print("Max diff:", diffs.abs().max().max())
print("ASI:", diffs.abs().sum(axis=1).mean())
