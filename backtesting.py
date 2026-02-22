"""
Backtesting Module for Black-Litterman Portfolio Optimization
==============================================================

Implements rolling window backtesting and performance evaluation.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import yfinance as yf
import os
import warnings
warnings.filterwarnings('ignore')


class PortfolioBacktester:
    """Backtesting framework for portfolio optimization strategies."""
    
    def __init__(self, optimizer, window_size=252, rebalance_freq=63, 
                 transaction_cost_rate=0.001, slippage_rate=0.0005):
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
        transaction_cost_rate : float
            Fixed proportional cost per trade (default: 10 bps)
        slippage_rate : float
            Estimated slippage per trade (default: 5 bps)
        """
        self.optimizer = optimizer
        self.window_size = window_size
        self.rebalance_freq = rebalance_freq
        self.tc_rate = transaction_cost_rate
        self.slip_rate = slippage_rate
        self.total_trade_cost_rate = self.tc_rate + self.slip_rate
        self.returns = optimizer.returns
        
        self.backtest_results = {
            'markowitz': {'gross': [], 'net': []},
            'black_litterman': {'gross': [], 'net': []},
            'equal_weight': {'gross': [], 'net': []},
            'turnover': {
                'markowitz': [],
                'black_litterman': [],
                'equal_weight': []
            },
            'cost_impact': {}
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
        
        # Store entire daily trajectory logic, not single averaged numbers per period
        # Tracking both Gross (Before Fees) and Net (After Fees)
        markowitz_daily_gross = pd.Series(dtype=float)
        markowitz_daily_net = pd.Series(dtype=float)
        
        bl_daily_gross = pd.Series(dtype=float)
        bl_daily_net = pd.Series(dtype=float)
        
        equal_daily_gross = pd.Series(dtype=float)
        equal_daily_net = pd.Series(dtype=float)
        
        # Track the raw weights over time for deeper turnover analysis
        prev_mw_weights = None
        prev_bl_weights = None
        prev_eq_weights = None
        
        mw_turnover_history = []
        bl_turnover_history = []
        eq_turnover_history = []
        
        test_dates = []
        rebalance_dates = []
        
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
            
            # Calculate Turnover vs Previous Weights
            # If first period, turnover is 100% (cash to fully invested) -> 1.0 (or 2.0 based on sum(abs) standard, we'll use sum(abs(w_new - 0)))
            if prev_mw_weights is None:
                mw_turnover = np.sum(np.abs(markowitz_weights))
                bl_turnover = np.sum(np.abs(bl_weights))
                eq_turnover = np.sum(np.abs(equal_weights))
            else:
                # In a hyper-realistic rig, we would calculate weight drift over the rebalance period.
                # For this standard test, we use target-to-target differencing.
                mw_turnover = np.sum(np.abs(markowitz_weights - prev_mw_weights))
                bl_turnover = np.sum(np.abs(bl_weights - prev_bl_weights))
                eq_turnover = np.sum(np.abs(equal_weights - prev_eq_weights))
                
            mw_turnover_history.append(mw_turnover)
            bl_turnover_history.append(bl_turnover)
            eq_turnover_history.append(eq_turnover)
            
            # Save state for next rolling window
            prev_mw_weights = markowitz_weights
            prev_bl_weights = bl_weights
            prev_eq_weights = equal_weights
            
            # Calculate Transaction Costs
            mw_cost = mw_turnover * self.total_trade_cost_rate
            bl_cost = bl_turnover * self.total_trade_cost_rate
            eq_cost = eq_turnover * self.total_trade_cost_rate
            
            # Calculate ACTUAL out-of-sample daily returns instead of purely average means
            # Dot product of daily asset returns matrix (periods x assets) with weights (assets)
            mw_daily = test_window.dot(markowitz_weights)
            bl_daily = test_window.dot(bl_weights)
            eq_daily = test_window.dot(equal_weights)
            
            # Copy to Net and systematically deduct the rebalance cost from the FIRST DAY of the window
            mw_daily_net = mw_daily.copy()
            bl_daily_net = bl_daily.copy()
            eq_daily_net = eq_daily.copy()
            
            mw_daily_net.iloc[0] -= mw_cost
            bl_daily_net.iloc[0] -= bl_cost
            eq_daily_net.iloc[0] -= eq_cost
            
            # Append pandas Series maintaining index dates
            markowitz_daily_gross = pd.concat([markowitz_daily_gross, mw_daily])
            markowitz_daily_net = pd.concat([markowitz_daily_net, mw_daily_net])
            
            bl_daily_gross = pd.concat([bl_daily_gross, bl_daily])
            bl_daily_net = pd.concat([bl_daily_net, bl_daily_net])
            
            equal_daily_gross = pd.concat([equal_daily_gross, eq_daily])
            equal_daily_net = pd.concat([equal_daily_net, eq_daily_net])
            
            test_dates.append(test_window.index[-1])
            rebalance_dates.append(test_window.index[0])
        
        self.backtest_results = {
            'markowitz': {
                'gross': markowitz_daily_gross.loc[~markowitz_daily_gross.index.duplicated(keep='last')], 
                'net': markowitz_daily_net.loc[~markowitz_daily_net.index.duplicated(keep='last')]
            },
            'black_litterman': {
                'gross': bl_daily_gross.loc[~bl_daily_gross.index.duplicated(keep='last')], 
                'net': bl_daily_net.loc[~bl_daily_net.index.duplicated(keep='last')]
            },
            'equal_weight': {
                'gross': equal_daily_gross.loc[~equal_daily_gross.index.duplicated(keep='last')], 
                'net': equal_daily_net.loc[~equal_daily_net.index.duplicated(keep='last')]
            },
            'turnover': {
                'markowitz': pd.Series(mw_turnover_history, index=rebalance_dates),
                'black_litterman': pd.Series(bl_turnover_history, index=rebalance_dates),
                'equal_weight': pd.Series(eq_turnover_history, index=rebalance_dates)
            },
            'cost_impact': {},
            'dates': test_dates,
            'overall_dates': markowitz_daily_gross.loc[~markowitz_daily_gross.index.duplicated(keep='last')].index # Expose the full timeline
        }
        
        print(f"\nBacktest periods: {len(test_dates)}")
        self._print_backtest_summary()
        
        return self.backtest_results
    
    def _print_backtest_summary(self):
        """Print summary statistics from backtest based on daily return series."""
        
        print("\n" + "-"*60)
        print("BACKTEST SUMMARY STATISTICS (Net Annualized)")
        print("-"*60)
        
        for model_name in ['markowitz', 'black_litterman', 'equal_weight']:
            daily_gross = self.backtest_results[model_name]['gross']
            daily_net = self.backtest_results[model_name]['net']
            
            # Annualize metrics
            mean_gross = daily_gross.mean() * 252
            mean_net = daily_net.mean() * 252
            std_net = daily_net.std() * np.sqrt(252)
            
            # Cost Impact
            annual_cost_drag = mean_gross - mean_net
            self.backtest_results['cost_impact'][model_name] = annual_cost_drag
            
            # Drawdown calculation
            cum_returns = (1 + daily_net).cumprod()
            rolling_max = cum_returns.cummax()
            drawdowns = (cum_returns - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            win_rate = (daily_net > 0).sum() / len(daily_net) * 100
            
            # Turnover
            avg_turnover = self.backtest_results['turnover'][model_name].mean()
            
            print(f"\n{model_name.upper().replace('_', ' ')}")
            print(f"  Gross Annual Return: {mean_gross:8.4%}")
            print(f"  Net Annual Return:   {mean_net:8.4%}")
            print(f"  Annual Volatility:   {std_net:8.4%}")
            print(f"  Cost Drag (bps/yr):  {annual_cost_drag * 10000:8.1f}")
            print(f"  Avg Rebal Turnover:  {avg_turnover:8.4%}")
            print(f"  Max Drawdown:        {max_drawdown:8.4%}")
            print(f"  Daily Win Rate:      {win_rate:8.1f}%")
    
    def calculate_information_ratio(self, benchmark_returns):
        """
        Calculate Information Ratio vs. benchmark using daily net series.
        
        IR = (Portfolio Return - Benchmark Return) / Tracking Error
        (Annualized)
        """
        
        results = {}
        
        for model_name in ['markowitz', 'black_litterman']:
            model_returns = self.backtest_results[model_name]['net']
            
            # Align indices in case of missing data
            aligned = pd.concat([model_returns, benchmark_returns], axis=1).dropna()
            mod_ret = aligned.iloc[:, 0]
            bench_ret = aligned.iloc[:, 1]
            
            active_returns = mod_ret - bench_ret
            # Annualize tracking error
            tracking_error = active_returns.std() * np.sqrt(252)
            
            if tracking_error == 0:
                ir = 0
            else:
                # Annualized active return over annualized tracking error
                annual_active_ret = active_returns.mean() * 252
                ir = annual_active_ret / tracking_error
            
            results[model_name] = {
                'information_ratio': ir,
                'active_return': active_returns.mean() * 252,
                'tracking_error': tracking_error
            }
        
        return results
    
    def calculate_sharpe_ratios(self):
        """Calculate Sharpe ratio for each model during backtest (Annualized)."""
        
        results = {}
        risk_free_rate_daily = self.optimizer.risk_free_rate / 252 
        
        for model_name in ['markowitz', 'black_litterman', 'equal_weight']:
            daily_returns = self.backtest_results[model_name]['net']
            
            excess_returns = daily_returns - risk_free_rate_daily
            # Annualize Sharpe: Multiply daily Sharpe by sqrt(252)
            sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
            
            results[model_name] = sharpe
        
        return results

    def fetch_and_align_benchmarks(self):
        """Fetch ^GSPC and 000300.SS from yfinance and align to backtest dates."""
        start_date = self.backtest_results['overall_dates'][0].strftime('%Y-%m-%d')
        end_date = self.backtest_results['overall_dates'][-1].strftime('%Y-%m-%d')
        
        print("\nFetching benchmark data (S&P 500, CSI 300)...")
        # Add 1 day buffer to end_date for yf to catch the last day
        fetch_end = (self.backtest_results['overall_dates'][-1] + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        bench_data = yf.download(['^GSPC', '000300.SS'], start=start_date, end=fetch_end, progress=False)
        
        # Calculate daily returns
        if 'Adj Close' in bench_data.columns:
            bench_prices = bench_data['Adj Close']
        else:
            bench_prices = bench_data['Close']
            
        bench_prices.fillna(method='ffill', inplace=True)
        bench_returns = bench_prices.pct_change().dropna()
        
        # Align to our portfolio out-of-sample timeline exactly
        sp500 = bench_returns['^GSPC'].reindex(self.backtest_results['overall_dates']).fillna(0)
        csi300 = bench_returns['000300.SS'].reindex(self.backtest_results['overall_dates']).fillna(0)
        
        self.backtest_results['sp500'] = sp500
        self.backtest_results['csi300'] = csi300
        return sp500, csi300


    def plot_benchmark_comparison(self, save_dir="results"):
        """Plot cumulative returns of models against benchmarks and save plot."""
        os.makedirs(save_dir, exist_ok=True)
        
        plt.figure(figsize=(12, 7))
        
        # Calculate cumulative returns
        models = {
            'MW (Net)': self.backtest_results['markowitz']['net'],
            'MW (Gross)': self.backtest_results['markowitz']['gross'],
            'BL (Net)': self.backtest_results['black_litterman']['net'],
            'BL (Gross)': self.backtest_results['black_litterman']['gross'],
            'Equal-Weight (Net)': self.backtest_results['equal_weight']['net'],
            'S&P 500 (^GSPC)': self.backtest_results['sp500'],
            'CSI 300 (000300.SS)': self.backtest_results['csi300']
        }
        
        colors = {
            'MW (Net)': '#ff7f0e',
            'MW (Gross)': '#ffbb78', # Lighter tint
            'BL (Net)': '#1f77b4',
            'BL (Gross)': '#aec7e8', # Lighter tint
            'Equal-Weight (Net)': '#2ca02c',
            'S&P 500 (^GSPC)': '#d62728',
            'CSI 300 (000300.SS)': '#9467bd'
        }
        
        for name, returns in models.items():
            cum_rets = (1 + returns).cumprod() - 1
            ls = '--' if 'Gross' in name else '-'
            alpha = 0.5 if 'Gross' in name else 1.0
            plt.plot(cum_rets.index, cum_rets * 100, label=name, color=colors[name], 
                     linewidth=2.0, linestyle=ls, alpha=alpha)
            
        plt.title('Out-of-Sample Cumulative Returns vs Benchmarks (Gross/Net)', fontsize=14, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Cumulative Return (%)', fontsize=12)
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        save_path = os.path.join(save_dir, 'benchmark_comparison.png')
        plt.savefig(save_path, dpi=300)
        print(f"\nSaved benchmark comparison plot to: {save_path}")
        plt.close()

    def plot_turnover_history(self, save_dir="results"):
        """Plot turnover rates at each rebalance period over time."""
        os.makedirs(save_dir, exist_ok=True)
        
        plt.figure(figsize=(12, 5))
        
        models = {
            'Markowitz': self.backtest_results['turnover']['markowitz'],
            'Black-Litterman': self.backtest_results['turnover']['black_litterman'],
            'Equal-Weight': self.backtest_results['turnover']['equal_weight'],
        }
        
        colors = {
            'Markowitz': '#ff7f0e',
            'Black-Litterman': '#1f77b4',
            'Equal-Weight': '#2ca02c',
        }
        
        for name, turnover in models.items():
            # Bar width approx 10 days for visibility depending on freq
            plt.bar(turnover.index, turnover * 100, label=name, color=colors[name], 
                    alpha=0.6, width=15)
            
        plt.title('Portfolio Asset Turnover at Rolling Rebalances', fontsize=14, fontweight='bold')
        plt.xlabel('Rebalance Date', fontsize=12)
        plt.ylabel('Turnover Weight Transacted (%)', fontsize=12)
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        save_path = os.path.join(save_dir, 'turnover_history.png')
        plt.savefig(save_path, dpi=300)
        print(f"Saved turnover history plot to: {save_path}")
        plt.close()


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
    
    # Fetch real-world benchmarks
    sp500, csi300 = backtester.fetch_and_align_benchmarks()
    
    # Calculate additional metrics against SP500 instead of equal weight
    ir_results = backtester.calculate_information_ratio(sp500)
    sharpe_results = backtester.calculate_sharpe_ratios()
    
    print("\n" + "="*60)
    print("INFORMATION RATIO (vs S&P 500)")
    print("="*60)
    
    for model_name, metrics in ir_results.items():
        print(f"\n{model_name.upper().replace('_', ' ')}")
        print(f"  Information Ratio:  {metrics['information_ratio']:8.4f}")
        print(f"  Active Return:      {metrics['active_return']:8.4%}")
        print(f"  Tracking Error:     {metrics['tracking_error']:8.4%}")
    
    print("\n" + "="*60)
    print("SHARPE RATIOS (Out-of-Sample, Annualized)")
    print("="*60)
    
    for model_name, sharpe in sharpe_results.items():
        print(f"{model_name.upper().replace('_', ' '):20s}: {sharpe:8.4f}")
        
    backtester.plot_benchmark_comparison()
    backtester.plot_turnover_history()
    
    return backtest_results, ir_results, sharpe_results
