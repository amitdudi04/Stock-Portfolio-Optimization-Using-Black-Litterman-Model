import pandas as pd
import numpy as np
from core.covariance_estimators import estimate_covariance
from models.black_litterman_model import compute_implied_equilibrium_returns, compute_black_litterman_posterior
from models.optimizer import compute_black_litterman_weights, compute_mean_variance_weights

def run_rolling_backtest(returns_df, initial_weights, window_size=252, rebalance_freq=63, model_type=None, tau=0.05):
    """
    Perform rolling out-of-sample portfolio simulation.
    Iteratively recalibrates portfolio constraints using standard historic look-back windows.
    Returns the out-of-sample equity curve and the rolling history of portfolio weights.
    """
    T = len(returns_df)
    portfolio_returns = []
    weights_history = []
    
    # Extract values for safe numpy operations if Series
    current_weight = initial_weights.values if isinstance(initial_weights, pd.Series) else initial_weights
    
    # Executing localized out-of-sample optimizations
    for i in range(window_size, T):
        # Lookback slice
        train_data = returns_df.iloc[i-window_size:i]
        test_return = returns_df.iloc[i]
        
        # Recalibrate every `rebalance_freq` days
        if model_type is not None and (i - window_size) % rebalance_freq == 0 and (i - window_size) > 0:
            cov_matrix = estimate_covariance(train_data)
            expected_returns = train_data.mean() * 252
            
            if model_type == 'markowitz':
                res = compute_mean_variance_weights(expected_returns, cov_matrix)
                current_weight = res.values if isinstance(res, pd.Series) else res
            elif model_type == 'black_litterman':
                n_assets = len(train_data.columns)
                market_weights = [1/n_assets] * n_assets
                pi = compute_implied_equilibrium_returns(cov_matrix, market_weights, lambda_risk_aversion=3.0)
                bl_posterior = compute_black_litterman_posterior(pi, cov_matrix, P=None, Q=None, Omega=None, tau=tau)
                res = compute_black_litterman_weights(bl_posterior, cov_matrix)
                current_weight = res.values if isinstance(res, pd.Series) else res
        
        # Realized performance
        step_return = np.dot(current_weight, test_return)
        
        portfolio_returns.append(step_return)
        weights_history.append(current_weight.copy() if hasattr(current_weight, 'copy') else current_weight)
        
    # Translate list to DataFrame Series matching the out-of-sample dates
    oos_dates = returns_df.index[window_size:]
    oos_series = pd.Series(portfolio_returns, index=oos_dates, name='Strategy Return')
    
    # Gather weights history into a structured DataFrame
    weights_history_df = pd.DataFrame(weights_history, index=oos_dates)
    if isinstance(initial_weights, pd.Series):
        weights_history_df.columns = initial_weights.index
        
    return oos_series, weights_history_df
