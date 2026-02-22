"""
Black-Litterman Model Implementation
=====================================

A comprehensive implementation of the Black-Litterman portfolio optimization model
with advanced risk metrics and backtesting capabilities.

Author: Portfolio Optimization Research Team
Date: February 2026
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm
import matplotlib.pyplot as plt
import yfinance as yf
import os
import warnings
warnings.filterwarnings('ignore')


class BlackLittermanOptimizer:
    """
    Implements the Black-Litterman model for portfolio optimization.
    
    The Black-Litterman model combines market-implied returns with investor views
    using Bayesian statistics to create more stable and realistic portfolio weights.
    """
    
    def __init__(self, ticker_list, start_date, end_date, risk_free_rate=0.03):
        """
        Initialize the optimizer with historical data.
        
        Parameters:
        -----------
        ticker_list : list
            List of stock tickers (e.g., ['AAPL', 'MSFT', 'GOOGL'])
        start_date : str
            Start date for historical data (YYYY-MM-DD)
        end_date : str
            End date for historical data (YYYY-MM-DD)
        risk_free_rate : float
            Risk-free rate assumption (default: 3%)
        """
        self.ticker_list = ticker_list
        self.start_date = start_date
        self.end_date = end_date
        self.risk_free_rate = risk_free_rate
        
        # Fetch and process data
        self.prices = self._fetch_data()
        self.returns = self.prices.pct_change().dropna()
        
        # Calculate covariance matrix
        self.cov_matrix = self.returns.cov()
        
        # Historical mean returns (will be overridden by market-implied returns)
        self.historical_mean = self.returns.mean() * 252  # Annualized
        
        # Market weights (initially equal-weight, can be customized)
        self.market_weights = np.array([1/len(ticker_list)] * len(ticker_list))
        
        # Risk aversion coefficient
        self.lambda_risk = 2.5
        
        # Black-Litterman parameters
        self.tau = 0.05  # Scaling factor for uncertainty
        self.bl_views = None
        self.bl_returns = None
        
        print(f"✓ Optimizer initialized with {len(ticker_list)} assets")
        print(f"  Period: {start_date} to {end_date}")
        print(f"  Data shape: {self.prices.shape}")
    
    def _fetch_data(self):
        """Fetch historical price data from Yahoo Finance."""
        print("Fetching historical price data...")
        try:
            # Override yfinance tz cache to avoid disk I/O errors
            import tempfile
            import os
            try:
                custom_cache = os.path.join(tempfile.gettempdir(), "yf_cache_custom")
                if not os.path.exists(custom_cache):
                    os.makedirs(custom_cache, exist_ok=True)
                yf.set_tz_cache_location(custom_cache)
            except AttributeError:
                pass
                
            # Download data with progress disabled
            data = yf.download(self.ticker_list, start=self.start_date, end=self.end_date, 
                              progress=False)
            
            # Handle different return structures based on number of tickers
            if isinstance(data, pd.DataFrame):
                if 'Adj Close' in data.columns:
                    # Multi-index case: result has multi-level columns
                    data = data['Adj Close']
                elif len(self.ticker_list) == 1 and self.ticker_list[0] in data.columns:
                    # Single ticker case where columns are [Open, High, Low, Close, Adj Close, Volume]
                    data = data[['Adj Close']]
                    data.columns = [self.ticker_list[0]]
                else:
                    # Fallback: assume Close prices if Adj Close not available
                    print("Warning: 'Adj Close' not found, using 'Close' as fallback")
                    if 'Close' in data.columns:
                        data = data['Close']
                    else:
                        raise ValueError(f"Could not find price data in columns: {data.columns.tolist()}")
            
            # Ensure proper column structure
            if isinstance(data, pd.Series):
                data = data.to_frame(name=self.ticker_list[0] if len(self.ticker_list) == 1 else 'Price')
            elif len(self.ticker_list) == 1 and not isinstance(data, pd.DataFrame):
                data = data.to_frame(name=self.ticker_list[0])
            
            # Verify data is not empty
            if data.empty:
                raise ValueError(f"No data retrieved for tickers: {self.ticker_list}. Check ticker symbols and date range.")
            
            print(f"✓ Data fetched: {data.shape[0]} rows, {data.shape[1]} columns")
            return data.dropna()
        
        except Exception as e:
            raise RuntimeError(f"Error fetching data for {self.ticker_list}: {str(e)}")

    
    def calculate_market_implied_returns(self):
        """
        Calculate market-implied returns using the CAPM reverse-solving method.
        
        Formula: Π = λ * Σ * w_m
        
        Where:
        - Π = market-implied excess returns
        - λ = risk aversion coefficient
        - Σ = covariance matrix
        - w_m = market weights
        """
        implied_returns = self.lambda_risk * self.cov_matrix.dot(self.market_weights)
        
        print("\n" + "="*60)
        print("MARKET-IMPLIED RETURNS (Π)")
        print("="*60)
        for ticker, ret in zip(self.ticker_list, implied_returns):
            print(f"{ticker:8s}: {ret:8.4%}")
        
        return implied_returns
    
    def set_investor_views(self, views_dict, confidence_levels=None):
        """
        Set investor views for the Black-Litterman model.
        
        Parameters:
        -----------
        views_dict : dict
            Dictionary of views, e.g., {'AAPL': 0.08, 'MSFT': 0.10}
            Values are expected returns (annualized)
        confidence_levels : dict or float
            Confidence in views (0-1). Default: 0.25 for all views
        """
        self.bl_views = views_dict
        
        if confidence_levels is None:
            confidence_levels = {ticker: 0.25 for ticker in views_dict.keys()}
        elif isinstance(confidence_levels, (int, float)):
            confidence_levels = {ticker: confidence_levels for ticker in views_dict.keys()}
        
        print("\n" + "="*60)
        print("INVESTOR VIEWS")
        print("="*60)
        for ticker, ret in views_dict.items():
            conf = confidence_levels.get(ticker, 0.25)
            print(f"{ticker:8s}: {ret:8.4%} (Confidence: {conf:.0%})")
        
        return confidence_levels
    
    def apply_black_litterman(self, views_dict, confidence_levels=None):
        """
        Apply the Black-Litterman model to combine market-implied returns with views.
        
        Formula:
        E(R) = [τΣ^(-1) + P^T Ω^(-1) P]^(-1) [τΣ^(-1) Π + P^T Ω^(-1) Q]
        
        Where:
        - τ = tau (scaling factor)
        - Σ = covariance matrix
        - P = view matrix
        - Q = view return vector
        - Ω = uncertainty matrix (diagonal)
        - Π = market-implied returns
        """
        # Market-implied returns
        implied_returns = self.calculate_market_implied_returns()
        
        # If no views provided, return market-implied returns
        if not views_dict or len(views_dict) == 0:
            print("\n" + "="*60)
            print("BLACK-LITTERMAN RETURNS (No Views - Using Market Equilibrium)")
            print("="*60)
            for ticker, ret in zip(self.ticker_list, implied_returns):
                print(f"{ticker:8s}: {ret:8.4%}")
            self.bl_returns = implied_returns
            return implied_returns
        
        # Investor views
        conf_levels = self.set_investor_views(views_dict, confidence_levels)
        
        # Build view matrix P and view returns Q
        P = np.zeros((len(views_dict), len(self.ticker_list)))
        Q = np.zeros(len(views_dict))
        
        view_tickers = list(views_dict.keys())
        for i, ticker in enumerate(view_tickers):
            idx = self.ticker_list.index(ticker)
            P[i, idx] = 1.0
            Q[i] = views_dict[ticker]
        
        # Uncertainty matrix Ω (diagonal)
        omega = np.zeros((len(views_dict), len(views_dict)))
        for i, ticker in enumerate(view_tickers):
            conf = conf_levels[ticker]
            # Uncertainty is inversely proportional to confidence
            omega[i, i] = (1 - conf) / conf
        
        # Black-Litterman formula
        inv_cov = np.linalg.inv(self.cov_matrix)
        
        left_matrix = np.linalg.inv(
            self.tau * inv_cov + P.T @ np.linalg.inv(omega) @ P
        )
        
        right_vector = (self.tau * inv_cov @ implied_returns + 
                       P.T @ np.linalg.inv(omega) @ Q)
        
        bl_returns = left_matrix @ right_vector
        
        print("\n" + "="*60)
        print("BLACK-LITTERMAN POSTERIOR RETURNS")
        print("="*60)
        for ticker, ret in zip(self.ticker_list, bl_returns):
            hist_ret = self.historical_mean[ticker]
            print(f"{ticker:8s}: {ret:8.4%}  (Historical: {hist_ret:8.4%})")
        
        self.bl_returns = bl_returns
        return bl_returns
    
    def optimize_portfolio(self, expected_returns, min_weight=0, max_weight=1):
        """
        Optimize portfolio weights to maximize Sharpe Ratio.
        
        Objective: max (E(R_p) - R_f) / σ_p
        
        Subject to:
        - Σ w_i = 1
        - min_weight ≤ w_i ≤ max_weight
        """
        n_assets = len(expected_returns)
        
        # Objective: negative Sharpe ratio (minimize) + L2 Regularization
        # Regularization encourages more diversified weights instead of just hugging min/max constraints
        l2_lambda = 20.0  # Strong diversification penalty required to counteract huge historical outperformance of single assets
        
        def objective(weights):
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_vol = np.sqrt(weights @ self.cov_matrix @ weights)
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            
            # L2 penalty: sum of squared weights. Minimizing negative sharpe + l2 penalty 
            # forces the optimizer to prefer smaller, more distributed weights where possible
            l2_penalty = l2_lambda * np.sum(weights**2)
            
            return -sharpe_ratio + l2_penalty
        
        # Constraints
        constraints = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # weights sum to 1
        )
        
        # Bounds
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess
        x0 = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, 
                         constraints=constraints, options={'ftol': 1e-9})
        
        return result.x
    
    def get_portfolio_metrics(self, weights, returns=None):
        """
        Calculate comprehensive portfolio risk metrics.
        
        Returns:
        --------
        dict : Dictionary containing Sharpe ratio, volatility, VaR, CVaR, etc.
        """
        if returns is None:
            returns = self.bl_returns
        
        # Basic metrics
        # Note: If `returns` are daily unannualized (like bl_returns), we must annualize them here
        # to match the scale of the annualized Volatility derived from the covariance matrix.
        # Check an arbitrary asset's expected return to guess if it's already annualized or daily.
        is_annualized = np.mean(returns) > 0.01  # True if average return > 1% (annualized scale)
        annualization_factor = 252 if not is_annualized else 1
        
        portfolio_return = np.sum(weights * returns) * annualization_factor
        portfolio_vol = np.sqrt(weights @ self.cov_matrix @ weights) * np.sqrt(252) # Also annualize Volatility
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
        
        # Calculate portfolio daily returns for risk metrics
        portfolio_daily_returns = (self.returns @ weights).values
        
        # Value at Risk (95%)
        var_95 = np.percentile(portfolio_daily_returns, 5)
        
        # Conditional Value at Risk (95%)
        cvar_95 = portfolio_daily_returns[portfolio_daily_returns <= var_95].mean()
        
        # Maximum Drawdown
        cumulative_returns = (1 + portfolio_daily_returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        metrics = {
            'Expected Return': portfolio_return,
            'Volatility': portfolio_vol,
            'Sharpe Ratio': sharpe_ratio,
            'VaR (95%)': var_95,
            'CVaR (95%)': cvar_95,
            'Max Drawdown': max_drawdown
        }
        
        return metrics
    
    def compare_models(self, views_dict, confidence_levels=None, max_weight=None, min_weight=0.05):
        """
        Compare Markowitz Mean-Variance with Black-Litterman model.
        
        Returns:
        --------
        dict : Comparison results including weights and metrics
        """
        print("\n" + "="*60)
        print("PORTFOLIO COMPARISON")
        print("="*60)
        
        # Set dynamic max weight constraint to prevent 100% allocation to a single asset
        if max_weight is None:
            n_assets = len(self.ticker_list)
            max_weight = min(1.0, max(0.3, 2.0 / n_assets))
            
        print(f"Applying constraints - Min: {min_weight:.1%}, Max: {max_weight:.1%} per asset")
        
        # Markowitz optimization (using historical mean returns)
        markowitz_weights = self.optimize_portfolio(self.historical_mean, min_weight=min_weight, max_weight=max_weight)
        markowitz_metrics = self.get_portfolio_metrics(markowitz_weights, self.historical_mean)
        
        # Black-Litterman optimization
        bl_returns = self.apply_black_litterman(views_dict, confidence_levels)
        bl_weights = self.optimize_portfolio(bl_returns, min_weight=min_weight, max_weight=max_weight)
        bl_metrics = self.get_portfolio_metrics(bl_weights, bl_returns)
        
        # Equal-weight portfolio (benchmark)
        equal_weights = np.array([1/len(self.ticker_list)] * len(self.ticker_list))
        equal_metrics = self.get_portfolio_metrics(equal_weights, bl_returns)
        
        print("\n" + "-"*60)
        print("MARKOWITZ (Mean-Variance) PORTFOLIO")
        print("-"*60)
        for ticker, weight in zip(self.ticker_list, markowitz_weights):
            print(f"{ticker:8s}: {weight:8.2%}")
        print(f"\nSharpe Ratio: {markowitz_metrics['Sharpe Ratio']:.4f}")
        print(f"Volatility:  {markowitz_metrics['Volatility']:.4%}")
        
        print("\n" + "-"*60)
        print("BLACK-LITTERMAN PORTFOLIO")
        print("-"*60)
        for ticker, weight in zip(self.ticker_list, bl_weights):
            print(f"{ticker:8s}: {weight:8.2%}")
        print(f"\nSharpe Ratio: {bl_metrics['Sharpe Ratio']:.4f}")
        print(f"Volatility:  {bl_metrics['Volatility']:.4%}")
        
        print("\n" + "-"*60)
        print("EQUAL-WEIGHT BENCHMARK")
        print("-"*60)
        for ticker, weight in zip(self.ticker_list, equal_weights):
            print(f"{ticker:8s}: {weight:8.2%}")
        print(f"\nSharpe Ratio: {equal_metrics['Sharpe Ratio']:.4f}")
        print(f"Volatility:  {equal_metrics['Volatility']:.4%}")
        
        return {
            'markowitz': {
                'weights': markowitz_weights,
                'metrics': markowitz_metrics
            },
            'black_litterman': {
                'weights': bl_weights,
                'metrics': bl_metrics
            },
            'equal_weight': {
                'weights': equal_weights,
                'metrics': equal_metrics
            }
        }

    def run_tau_sensitivity(self, views_dict, confidence_levels=None, 
                            tau_values=[0.01, 0.03, 0.05, 0.1, 0.2], 
                            max_weight=None, min_weight=0.05, save_dir="results"):
        """
        Run a robustness analysis to track Black-Litterman model sensitivity to Tau (τ).
        
        Parameters:
        -----------
        views_dict : dict
            Investor views.
        confidence_levels : dict
            Confidence in views.
        tau_values : list
            Array of uncertainty scalar constants to iterate across.
        max_weight : float
            Maximum allocation weight per asset.
        min_weight : float
            Minimum allocation weight per asset.
        save_dir : str
            Directory to save the tau sensitivity plot.
            
        Returns:
        --------
        pd.DataFrame : Results of the tau sensitivity analysis.
        """
        print("\n" + "="*60)
        print("RUNNING TAU (τ) SENSITIVITY ANALYSIS")
        print("="*60)
        
        results_list = []
        original_tau = self.tau
        
        if max_weight is None:
            n_assets = len(self.ticker_list)
            max_weight = min(1.0, max(0.3, 2.0 / n_assets))
            
        for t in tau_values:
            # Overwrite the intrinsic param
            self.tau = t
            print(f"Processing τ = {t:.3f} ...")
            
            # Recalculate Posteriors and re-optimize purely off new tau assumption
            bl_returns = self.apply_black_litterman(views_dict, confidence_levels)
            bl_weights = self.optimize_portfolio(bl_returns, min_weight=min_weight, max_weight=max_weight)
            bl_metrics = self.get_portfolio_metrics(bl_weights, bl_returns)
            
            # Record core metrics
            record = {
                'Tau': t,
                'Expected Return': bl_metrics['Expected Return'],
                'Volatility': bl_metrics['Volatility'],
                'Sharpe Ratio': bl_metrics['Sharpe Ratio']
            }
            
            # Extract distinct asset weights
            for ticker, weight in zip(self.ticker_list, bl_weights):
                record[f'Weight_{ticker}'] = weight
                
            results_list.append(record)
            
        # Restore standard optimizer tau condition
        self.tau = original_tau
        
        # Convert the iteration records to a clean dataframe
        df = pd.DataFrame(results_list)
        df.set_index('Tau', inplace=True)
        
        # Build the visualization payload
        os.makedirs(save_dir, exist_ok=True)
        self._plot_tau_sensitivity(df, save_dir)
        
        return df
        
    def _plot_tau_sensitivity(self, df, save_dir):
        """Helper to generate and export the 3-panel Matplotlib graphic for Tau Sensitivity."""
        fig = plt.figure(figsize=(15, 12))
        
        # Subplot 1: Tau vs Sharpe Ratio
        plt.subplot(3, 1, 1)
        plt.plot(df.index, df['Sharpe Ratio'], marker='o', color='green', linewidth=2)
        plt.title('Tau (τ) vs Sharpe Ratio', fontsize=14, fontweight='bold')
        plt.ylabel('Sharpe Ratio', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Subplot 2: Tau vs Volatility vs Expected Return
        plt.subplot(3, 1, 2)
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        
        line1 = ax1.plot(df.index, df['Volatility'] * 100, marker='s', color='orange', label='Volatility')
        line2 = ax2.plot(df.index, df['Expected Return'] * 100, marker='^', color='blue', label='Expected Return')
        
        ax1.set_ylabel('Volatility (%)', fontsize=12, color='orange')
        ax2.set_ylabel('Expected Return (%)', fontsize=12, color='blue')
        plt.title('Tau (τ) vs Expected Return & Volatility', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Add merged legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')
        
        # Subplot 3: Portfolio Weight Drift Mapping
        plt.subplot(3, 1, 3)
        weight_cols = [c for c in df.columns if c.startswith('Weight_')]
        weights_data = df[weight_cols]
        # Clean labels for charting
        labels = [c.replace('Weight_', '') for c in weight_cols]
        
        plt.stackplot(df.index, weights_data.T * 100, labels=labels, alpha=0.8)
        plt.title('Portfolio Weight Distribution vs Tau (τ)', fontsize=14, fontweight='bold')
        plt.xlabel('Tau (τ)', fontsize=12)
        plt.ylabel('Allocation (%)', fontsize=12)
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        save_path = os.path.join(save_dir, 'tau_sensitivity.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nSaved Tau Sensitivity plot to: {save_path}")
        plt.close()

    def run_lambda_sensitivity(self, views_dict, confidence_levels=None, 
                               lambda_values=[1.5, 2.0, 2.5, 3.0, 4.0], 
                               max_weight=None, min_weight=0.05, save_dir="results"):
        """
        Run a robustness analysis to track Black-Litterman model sensitivity to Risk Aversion (λ).
        
        Parameters:
        -----------
        views_dict : dict
            Investor views.
        confidence_levels : dict
            Confidence in views.
        lambda_values : list
            Array of risk aversion coefficients to iterate across.
        max_weight : float
            Maximum allocation weight per asset.
        min_weight : float
            Minimum allocation weight per asset.
        save_dir : str
            Directory to save the lambda sensitivity plot.
            
        Returns:
        --------
        pd.DataFrame : Results of the lambda sensitivity analysis.
        """
        print("\n" + "="*60)
        print("RUNNING RISK AVERSION (λ) SENSITIVITY ANALYSIS")
        print("="*60)
        
        results_list = []
        original_lambda = self.lambda_risk
        
        if max_weight is None:
            n_assets = len(self.ticker_list)
            max_weight = min(1.0, max(0.3, 2.0 / n_assets))
            
        for lmb in lambda_values:
            # Overwrite the intrinsic param
            self.lambda_risk = lmb
            print(f"Processing λ = {lmb:.2f} ...")
            
            # Recalculate Posteriors and re-optimize purely off new risk aversion assumption
            bl_returns = self.apply_black_litterman(views_dict, confidence_levels)
            bl_weights = self.optimize_portfolio(bl_returns, min_weight=min_weight, max_weight=max_weight)
            bl_metrics = self.get_portfolio_metrics(bl_weights, bl_returns)
            
            # Record core metrics
            record = {
                'Lambda': lmb,
                'Expected Return': bl_metrics['Expected Return'],
                'Volatility': bl_metrics['Volatility'],
                'Sharpe Ratio': bl_metrics['Sharpe Ratio']
            }
            
            # Extract distinct asset weights
            for ticker, weight in zip(self.ticker_list, bl_weights):
                record[f'Weight_{ticker}'] = weight
                
            results_list.append(record)
            
        # Restore standard optimizer lambda condition
        self.lambda_risk = original_lambda
        
        # Convert the iteration records to a clean dataframe
        df = pd.DataFrame(results_list)
        df.set_index('Lambda', inplace=True)
        
        # Build the visualization payload
        os.makedirs(save_dir, exist_ok=True)
        self._plot_lambda_sensitivity(df, save_dir)
        
        return df
        
    def _plot_lambda_sensitivity(self, df, save_dir):
        """Helper to generate and export the 2-panel Matplotlib graphic for Lambda Sensitivity."""
        fig = plt.figure(figsize=(15, 10))
        
        # Subplot 1: Lambda vs Sharpe Ratio
        plt.subplot(2, 1, 1)
        plt.plot(df.index, df['Sharpe Ratio'], marker='o', color='purple', linewidth=2)
        plt.title('Risk Aversion (λ) vs Sharpe Ratio', fontsize=14, fontweight='bold')
        plt.ylabel('Sharpe Ratio', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(df.index)
        
        # Subplot 2: Lambda vs Expected Return
        plt.subplot(2, 1, 2)
        plt.plot(df.index, df['Expected Return'] * 100, marker='^', color='teal', linewidth=2)
        plt.title('Risk Aversion (λ) vs Expected Return', fontsize=14, fontweight='bold')
        plt.xlabel('Risk Aversion Coef (λ)', fontsize=12)
        plt.ylabel('Expected Return (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(df.index)
        
        plt.tight_layout()
        save_path = os.path.join(save_dir, 'lambda_sensitivity.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nSaved Lambda Sensitivity plot to: {save_path}")
        plt.close()


def main():
    """Main execution function."""
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    # Configuration
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - relativedelta(years=5)).strftime('%Y-%m-%d')
    risk_free_rate = 0.03
    
    # Initialize optimizer
    optimizer = BlackLittermanOptimizer(tickers, start_date, end_date, risk_free_rate)
    
    # Define investor views
    views = {
        'AAPL': 0.12,   # Expect AAPL to return 12%
        'MSFT': 0.10,   # Expect MSFT to return 10%
        'NVDA': 0.15    # Expect NVDA to return 15%
    }
    
    # Define confidence levels (how sure are we about these views)
    confidence = {
        'AAPL': 0.60,
        'MSFT': 0.50,
        'NVDA': 0.65
    }
    
    # Compare models
    results = optimizer.compare_models(views, confidence)
    
    # Print detailed metrics
    print("\n" + "="*60)
    print("DETAILED RISK METRICS")
    print("="*60)
    
    for model_name, model_data in results.items():
        print(f"\n{model_name.upper().replace('_', ' ')}")
        print("-" * 40)
        for metric_name, metric_value in model_data['metrics'].items():
            if metric_name in ['Expected Return', 'Volatility', 'VaR (95%)', 'Max Drawdown']:
                print(f"{metric_name:20s}: {metric_value:8.4%}")
            else:
                print(f"{metric_name:20s}: {metric_value:8.4f}")


if __name__ == '__main__':
    main()
