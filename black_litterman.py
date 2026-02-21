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
import yfinance as yf
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
        data = yf.download(self.ticker_list, start=self.start_date, end=self.end_date, 
                          progress=False)['Adj Close']
        
        if len(self.ticker_list) == 1:
            data = data.to_frame(name=self.ticker_list[0])
        
        return data.dropna()
    
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
        
        # Objective: negative Sharpe ratio (minimize)
        def neg_sharpe(weights):
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_vol = np.sqrt(weights @ self.cov_matrix @ weights)
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe_ratio
        
        # Constraints
        constraints = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # weights sum to 1
        )
        
        # Bounds
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess
        x0 = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(neg_sharpe, x0, method='SLSQP', bounds=bounds, 
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
        portfolio_return = np.sum(weights * returns)
        portfolio_vol = np.sqrt(weights @ self.cov_matrix @ weights)
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
    
    def compare_models(self, views_dict, confidence_levels=None):
        """
        Compare Markowitz Mean-Variance with Black-Litterman model.
        
        Returns:
        --------
        dict : Comparison results including weights and metrics
        """
        print("\n" + "="*60)
        print("PORTFOLIO COMPARISON")
        print("="*60)
        
        # Markowitz optimization (using historical mean returns)
        markowitz_weights = self.optimize_portfolio(self.historical_mean)
        markowitz_metrics = self.get_portfolio_metrics(markowitz_weights, self.historical_mean)
        
        # Black-Litterman optimization
        bl_returns = self.apply_black_litterman(views_dict, confidence_levels)
        bl_weights = self.optimize_portfolio(bl_returns)
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


def main():
    """Main execution function."""
    
    # Configuration
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    start_date = '2021-01-01'
    end_date = '2026-02-21'
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
