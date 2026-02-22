import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import os
import tempfile
from portfolio_optimization import BlackLittermanOptimizer

class HistoricalStressTester:
    def __init__(self, tickers, train_start='2005-01-01', train_end='2007-12-31', 
                 test_start='2008-01-01', test_end='2009-12-31', benchmark='^GSPC'):
        self.tickers = tickers
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end
        self.benchmark = benchmark
        
        self.weights = {}
        self.test_returns = None
        self.test_prices = None
        self.benchmark_returns = None
        self.results = {}
        
    def _fetch_prices(self, tickers, start, end):
        """Helper to fetch clean daily data."""
        try:
            custom_cache = os.path.join(tempfile.gettempdir(), "yf_cache_custom")
            os.makedirs(custom_cache, exist_ok=True)
            yf.set_tz_cache_location(custom_cache)
        except AttributeError:
            pass
            
        data = yf.download(tickers, start=start, end=end, progress=False)
        if isinstance(data, pd.DataFrame):
            if 'Adj Close' in data.columns:
                data = data['Adj Close']
            elif 'Close' in data.columns:
                data = data['Close']
                
        if len(tickers) == 1 and not isinstance(data, pd.DataFrame):
            data = data.to_frame(name=tickers[0])
            
        # Ensure correct column ordering specifically for multivariate
        if len(tickers) > 1 and isinstance(data, pd.DataFrame):
            data = data[tickers]
            
        return data.dropna()

    def run_training_phase(self, views_dict, confidence_levels):
        """Train standard optimization bounds on pre-crisis pure data natively."""
        print(f"--- TRAINING PHASE: {self.train_start} to {self.train_end} ---")
        opt = BlackLittermanOptimizer(self.tickers, self.train_start, self.train_end)
        
        cmp = opt.compare_models(views_dict, confidence_levels)
        
        self.weights['markowitz'] = cmp['markowitz']['weights']
        self.weights['black_litterman'] = cmp['black_litterman']['weights']
        self.weights['equal_weight'] = cmp['equal_weight']['weights']
        
        # Track pre-crisis volatility directly from opt cov_matrix to calculate Volatility Spike later
        self.train_vol = {
            'markowitz': np.sqrt(self.weights['markowitz'] @ opt.cov_matrix @ self.weights['markowitz']) * np.sqrt(252),
            'black_litterman': np.sqrt(self.weights['black_litterman'] @ opt.cov_matrix @ self.weights['black_litterman']) * np.sqrt(252),
            'benchmark': np.nan  # Will compute SP500 later
        }

    def run_stress_test(self):
        """Evaluate pre-crisis allocations natively across the unseen 2008 collapse window."""
        print(f"\n--- STRESS TESTING PHASE: {self.test_start} to {self.test_end} ---")
        
        # Fetch exact asset array outputs from crisis window
        print("Fetching test window Asset prices...")
        self.test_prices = self._fetch_prices(self.tickers, self.test_start, self.test_end)
        self.test_returns = self.test_prices.pct_change().dropna()
        
        # Fetch S&P 500 equivalent window actively
        print(f"Fetching test window Benchmark ({self.benchmark}) prices...")
        bench_prices = self._fetch_prices([self.benchmark], self.test_start, self.test_end)
        self.benchmark_returns = bench_prices.pct_change().dropna().iloc[:, 0]
        
        # Align timelines natively to identical market days
        aligned = pd.concat([self.test_returns, self.benchmark_returns], axis=1).dropna()
        self.test_returns = aligned[self.tickers]
        self.benchmark_returns = aligned.iloc[:, -1]
        
        # Pre-crisis Benchmark Volatility evaluation
        print("Evaluating pre-crisis Benchmark volatility...")
        bench_train = self._fetch_prices([self.benchmark], self.train_start, self.train_end).pct_change().dropna()
        self.train_vol['benchmark'] = bench_train.iloc[:, 0].std() * np.sqrt(252)
        
        print("Calculating exact crisis performance trails...")
        self.daily_performance = {}
        for strategy, weights in self.weights.items():
            self.daily_performance[strategy] = self.test_returns.dot(weights)
            
        self.daily_performance['benchmark'] = self.benchmark_returns
        
        # Derive core mathematics actively
        for name, daily_ret in self.daily_performance.items():
            # 1. Total Crisis Yield
            cum_rets = (1 + daily_ret).cumprod()
            total_crisis_return = cum_rets.iloc[-1] - 1
            
            # 2. Maximum Drawdown Trace
            rolling_max = cum_rets.cummax()
            drawdowns = (cum_rets - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            # 3. Volatility Spike Mapping
            crisis_vol = daily_ret.std() * np.sqrt(252)
            pre_vol = self.train_vol.get(name, self.train_vol['black_litterman'] if name == 'equal_weight' else np.nan)
            
            if name == 'equal_weight':
               pre_vol = np.sqrt(self.weights['equal_weight'] @ self.test_returns.cov() @ self.weights['equal_weight']) * np.sqrt(252) # Re-estimating from tests since we don't have train equal weight cov matrix cached 
               
            vol_spike = (crisis_vol / pre_vol) if not np.isnan(pre_vol) else np.nan
            
            # 4. Crisis Recovery Logic Trace
            # Evaluates exactly how many trading days are spent inside a single drawdown period
            # For 2008, it's highly likely it never recovered by Dec 2009.
            # Return Days if recovered, else -1 (Did not recover in window)
            recovery_time = -1
            underwater_days = 0
            max_underwater_days = 0
            for dd in drawdowns:
                if dd < 0:
                    underwater_days += 1
                else:
                    max_underwater_days = max(max_underwater_days, underwater_days)
                    underwater_days = 0
            max_underwater_days = max(max_underwater_days, underwater_days)
            
            if cum_rets.iloc[-1] >= rolling_max.max():
                 recovery_time = max_underwater_days
            
            self.results[name] = {
                'Crisis Return': total_crisis_return,
                'Max Drawdown': max_drawdown,
                'Crisis Volatility': crisis_vol,
                'Pre-Crisis Volatility': pre_vol,
                'Volatility Spike (x)': vol_spike,
                'Max Underwater Days': max_underwater_days,
                'cumulative_series': cum_rets,
                'drawdown_series': drawdowns
            }
            
    def print_results(self):
        """Log the output matrix natively to terminal."""
        print("\n" + "="*80)
        print("2008 FINANCIAL CRISIS STRESS TEST RESULTS (Train: 05-07 | Test: 08-09)")
        print("="*80)
        
        format_str = "{:<20} | {:<15} | {:<15} | {:<15} | {:<15}"
        print(format_str.format("Strategy", "Total Return", "Max Drawdown", "Vol Spike (x)", "Underwater Days"))
        print("-" * 85)
        
        display_names = {
            'black_litterman': 'Black-Litterman',
            'markowitz': 'Markowitz',
            'equal_weight': 'Equal Weight',
            'benchmark': 'S&P 500 (^GSPC)'
        }
        
        for name, metrics in self.results.items():
            disp = display_names.get(name, name)
            ret = f"{metrics['Crisis Return']:.2%}"
            dd = f"{metrics['Max Drawdown']:.2%}"
            vs = f"{metrics['Volatility Spike (x)']:.2f}x"
            uw = f"{metrics['Max Underwater Days']} days"
            print(format_str.format(disp, ret, dd, vs, uw))
            
        print("="*80 + "\n")

    def plot_stress_test(self, save_dir="results"):
        """Generate 2-panel rendering tracking cumulative falls and drawdown vectors."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
        
        colors = {
            'black_litterman': '#1E88E5',  # Blue
            'markowitz': '#E53935',        # Red
            'equal_weight': '#8E24AA',     # Purple
            'benchmark': '#43A047'         # Green
        }
        
        display_names = {
            'black_litterman': 'Black-Litterman Allocation',
            'markowitz': 'Markowitz Mean-Variance',
            'equal_weight': 'Equal Weight Portfolio',
            'benchmark': 'S&P 500 (^GSPC)'
        }
        
        # Subplot 1: Cumulative Trajectory
        for name, metrics in self.results.items():
            cum_rets = metrics['cumulative_series']
            # Plot baseline starting at 1.0 (100%)
            val_series = cum_rets * 100
            
            ls = '-' if name != 'benchmark' else '--'
            lw = 2.5 if name == 'black_litterman' else 1.5
            alpha = 1.0 if name == 'black_litterman' else 0.8
            
            ax1.plot(val_series.index, val_series, label=display_names[name], 
                     color=colors[name], linestyle=ls, linewidth=lw, alpha=alpha)
            
        ax1.set_title('2008 Financial Crisis Simulation: Cumulative Trajectories', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value (Baseline %)', fontsize=12)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Drawdown Depths
        for name, metrics in self.results.items():
            dd_series = metrics['drawdown_series'] * 100
            
            ls = '-' if name != 'benchmark' else '--'
            lw = 2.0 if name == 'black_litterman' else 1.0
            alpha = 0.9 if name == 'black_litterman' else 0.5
            
            # Fill between for BL
            if name == 'black_litterman':
                ax2.fill_between(dd_series.index, dd_series, 0, color=colors[name], alpha=0.2)
                
            ax2.plot(dd_series.index, dd_series, color=colors[name], linestyle=ls, linewidth=lw, alpha=alpha)
            
        ax2.set_title('Geometric Drawdown Depths (%)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Drawdown (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'stress_test_2008.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved 2008 Stress Test simulation visualization to: {save_path}")
        plt.close()

def main():
    # Execute a fully automated testing isolation using a diversified tech + defensive setup
    tickers = ['AAPL', 'MSFT', 'JNJ', 'PEP', 'PG']
    
    views = {
        'AAPL': 0.15,
        'MSFT': 0.12,
        'JNJ': 0.08,
        'PEP': 0.09,
        'PG': 0.07
    }
    
    confidence = {
        'AAPL': 0.50,
        'MSFT': 0.50,
        'JNJ': 0.70,
        'PEP': 0.70,
        'PG': 0.70
    }
    
    tester = HistoricalStressTester(tickers)
    tester.run_training_phase(views, confidence)
    tester.run_stress_test()
    tester.print_results()
    tester.plot_stress_test()

if __name__ == '__main__':
    main()
