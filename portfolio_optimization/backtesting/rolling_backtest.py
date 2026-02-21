"""
Backtesting Module for Black-Litterman Portfolio Optimization
==============================================================

Implements rolling window backtesting and performance evaluation.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class PortfolioBacktester:
    """Backtesting framework for portfolio optimization strategies."""
    
    def __init__(self, optimizer, window_size=252, rebalance_freq=63):
        """
        Initialize backtester.
        
        Parameters:
        -----------
        optimizer : BlackLittermanOptimizer
            The optimizer object
        window_size : int
            Training window size in days (252 = 1 year)
        rebalance_freq : int
            Rebalancing frequency in days (63 ≈ 1 quarter)
        """
        self.optimizer = optimizer
        self.window_size = window_size
        self.rebalance_freq = rebalance_freq
        self.returns = optimizer.returns
        
        self.backtest_results = {
            'markowitz': [],
            'black_litterman': [],
            'equal_weight': []
        }
        
        self.rebalance_dates = []
    
    def _calculate_returns_vol(self, returns_window):
        """Calculate expected returns and volatility from returns window."""
        mean_returns = returns_window.mean() * 252
        cov_matrix = returns_window.cov() * 252
        return mean_returns, cov_matrix
    
    def _optimize_weights(self, mean_returns, cov_matrix, method='markowitz'):
        """Optimize portfolio weights."""
        n_assets = len(mean_returns)
        risk_free_rate = self.optimizer.risk_free_rate
        
        def neg_sharpe(weights):
            ret = np.sum(weights * mean_returns)
            vol = np.sqrt(weights @ cov_matrix @ weights)
            return -(ret - risk_free_rate) / vol
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        x0 = np.array([1/n_assets] * n_assets)
        
        result = minimize(neg_sharpe, x0, method='SLSQP', bounds=bounds,
                         constraints=constraints, options={'ftol': 1e-9})
        
        return result.x
    
    def run_backtest(self, views_dict=None):
        """
        Run rolling window backtest.
        
        Parameters:
        -----------
        views_dict : dict
            Investor views for Black-Litterman model
        """
        print("\n" + "="*60)
        print("BACKTESTING: ROLLING WINDOW ANALYSIS")
        print("="*60)
        print(f"Window size: {self.window_size} days")
        print(f"Rebalance frequency: {self.rebalance_freq} days")
        
        # Default views if not provided
        if views_dict is None:
            views_dict = {
                self.optimizer.ticker_list[0]: 0.12,
                self.optimizer.ticker_list[1]: 0.10
            }
        
        markowitz_returns = []
        bl_returns = []
        equal_returns = []
        
        test_dates = []
        
        # Rolling window
        for i in range(self.window_size, len(self.returns), self.rebalance_freq):
            
            # Training window
            train_window = self.returns.iloc[i-self.window_size:i]
            
            if len(train_window) < self.window_size:
                break
            
            # Test window
            test_start = i
            test_end = min(i + self.rebalance_freq, len(self.returns))
            test_window = self.returns.iloc[test_start:test_end]
            
            if len(test_window) == 0:
                break
            
            # Calculate statistics from training window
            mean_returns, cov_matrix = self._calculate_returns_vol(train_window)
            
            # Markowitz optimization
            markowitz_weights = self._optimize_weights(mean_returns, cov_matrix, 
                                                       method='markowitz')
            
            # Equal-weight portfolio
            equal_weights = np.array([1/len(self.optimizer.ticker_list)] * 
                                    len(self.optimizer.ticker_list))
            
            # Simple Black-Litterman (can be enhanced)
            # Adjust expected returns based on views
            bl_returns_adj = mean_returns.copy()
            for ticker, view_return in views_dict.items():
                idx = self.optimizer.ticker_list.index(ticker)
                bl_returns_adj[idx] = 0.7 * mean_returns[idx] + 0.3 * view_return
            
            bl_weights = self._optimize_weights(bl_returns_adj, cov_matrix,
                                               method='black_litterman')
            
            # Calculate returns for test window
            test_ret = test_window.values
            
            markowitz_port_ret = np.sum(markowitz_weights * test_ret.mean()) * 252
            bl_port_ret = np.sum(bl_weights * test_ret.mean()) * 252
            equal_port_ret = np.sum(equal_weights * test_ret.mean()) * 252
            
            markowitz_returns.append(markowitz_port_ret)
            bl_returns.append(bl_port_ret)
            equal_returns.append(equal_port_ret)
            test_dates.append(test_window.index[-1])
        
        self.backtest_results = {
            'markowitz': markowitz_returns,
            'black_litterman': bl_returns,
            'equal_weight': equal_returns,
            'dates': test_dates
        }
        
        print(f"\nBacktest periods: {len(test_dates)}")
        self._print_backtest_summary()
        
        return self.backtest_results
    
    def _print_backtest_summary(self):
        """Print summary statistics from backtest."""
        
        print("\n" + "-"*60)
        print("BACKTEST SUMMARY STATISTICS")
        print("-"*60)
        
        for model_name in ['markowitz', 'black_litterman', 'equal_weight']:
            returns = np.array(self.backtest_results[model_name])
            
            mean_ret = np.mean(returns)
            std_ret = np.std(returns)
            win_rate = np.sum(returns > 0) / len(returns) * 100
            best = np.max(returns)
            worst = np.min(returns)
            
            print(f"\n{model_name.upper().replace('_', ' ')}")
            print(f"  Mean Return:       {mean_ret:8.4%}")
            print(f"  Std Deviation:     {std_ret:8.4%}")
            print(f"  Win Rate:          {win_rate:8.1f}%")
            print(f"  Best Period:       {best:8.4%}")
            print(f"  Worst Period:      {worst:8.4%}")
    
    def calculate_information_ratio(self, benchmark_returns):
        """
        Calculate Information Ratio vs. benchmark.
        
        IR = (Portfolio Return - Benchmark Return) / Tracking Error
        """
        
        results = {}
        
        for model_name in ['markowitz', 'black_litterman']:
            model_returns = np.array(self.backtest_results[model_name])
            benchmark_ret = np.array(benchmark_returns)
            
            active_returns = model_returns - benchmark_ret
            tracking_error = np.std(active_returns)
            
            if tracking_error == 0:
                ir = 0
            else:
                ir = np.mean(active_returns) / tracking_error
            
            results[model_name] = {
                'information_ratio': ir,
                'active_return': np.mean(active_returns),
                'tracking_error': tracking_error
            }
        
        return results
    
    def calculate_sharpe_ratios(self):
        """Calculate Sharpe ratio for each model during backtest."""
        
        results = {}
        risk_free_rate = self.optimizer.risk_free_rate / 252  # Daily
        
        for model_name in ['markowitz', 'black_litterman', 'equal_weight']:
            returns = np.array(self.backtest_results[model_name]) / 252  # Convert to daily
            
            excess_returns = returns - risk_free_rate
            sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
            
            results[model_name] = sharpe
        
        return results


def run_comprehensive_backtest(optimizer, views_dict=None):
    """
    Run comprehensive backtesting analysis.
    
    Parameters:
    -----------
    optimizer : BlackLittermanOptimizer
        The optimizer object
    views_dict : dict
        Investor views for Black-Litterman
    """
    backtester = PortfolioBacktester(optimizer)
    backtest_results = backtester.run_backtest(views_dict)
    
    # Calculate additional metrics
    equal_weight_returns = backtest_results['equal_weight']
    ir_results = backtester.calculate_information_ratio(equal_weight_returns)
    sharpe_results = backtester.calculate_sharpe_ratios()
    
    print("\n" + "="*60)
    print("INFORMATION RATIO (vs Equal-Weight)")
    print("="*60)
    
    for model_name, metrics in ir_results.items():
        print(f"\n{model_name.upper().replace('_', ' ')}")
        print(f"  Information Ratio:  {metrics['information_ratio']:8.4f}")
        print(f"  Active Return:      {metrics['active_return']:8.4%}")
        print(f"  Tracking Error:     {metrics['tracking_error']:8.4%}")
    
    print("\n" + "="*60)
    print("SHARPE RATIOS (Out-of-Sample)")
    print("="*60)
    
    for model_name, sharpe in sharpe_results.items():
        print(f"{model_name.upper().replace('_', ' '):20s}: {sharpe:8.4f}")
    
    return backtest_results, ir_results, sharpe_results
