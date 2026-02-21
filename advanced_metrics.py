"""
Advanced Risk Metrics
====================

Comprehensive risk metrics and performance analytics.
"""

import numpy as np
import pandas as pd
from scipy import stats


class RiskMetricsCalculator:
    """Advanced portfolio risk metrics calculation."""
    
    def __init__(self, risk_free_rate=0.03):
        """Initialize calculator with risk-free rate."""
        self.risk_free_rate = risk_free_rate
        self.risk_free_rate_daily = risk_free_rate / 252
    
    def sharpe_ratio(self, returns, daily=False):
        """
        Calculate Sharpe Ratio.
        
        Formula: (E[R] - Rf) / σ
        """
        if daily:
            excess_returns = returns - self.risk_free_rate_daily
            return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        else:
            excess_returns = returns - self.risk_free_rate
            return np.mean(excess_returns) / np.std(excess_returns)
    
    def sortino_ratio(self, returns, target_return=None, daily=False):
        """
        Calculate Sortino Ratio (downside risk only).
        
        Formula: (E[R] - Rf) / σ_downside
        """
        if target_return is None:
            target_return = self.risk_free_rate_daily if daily else self.risk_free_rate
        
        excess_returns = returns - target_return
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return np.inf
        
        downside_std = np.std(downside_returns)
        
        if daily:
            return np.mean(excess_returns) / downside_std * np.sqrt(252)
        else:
            return np.mean(excess_returns) / downside_std
    
    def calmar_ratio(self, returns):
        """
        Calculate Calmar Ratio.
        
        Formula: CAGR / Maximum Drawdown
        """
        cumulative_returns = (1 + returns).cumprod()
        cagr = (cumulative_returns.iloc[-1] ** (252 / len(returns)) - 1) * 252
        max_dd = self.maximum_drawdown(returns)
        
        if max_dd == 0:
            return np.inf
        
        return -cagr / max_dd  # Note: max_dd is negative
    
    def information_ratio(self, portfolio_returns, benchmark_returns):
        """
        Calculate Information Ratio.
        
        Formula: (E[R_p] - E[R_b]) / σ_tracking_error
        """
        active_returns = portfolio_returns - benchmark_returns
        tracking_error = np.std(active_returns)
        
        if tracking_error == 0:
            return 0
        
        return np.mean(active_returns) / tracking_error
    
    def maximum_drawdown(self, returns):
        """
        Calculate Maximum Drawdown.
        
        Formula: (Min Cumulative Return - Peak) / Peak
        """
        cumulative_returns = (1 + returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        
        return np.min(drawdown)
    
    def calmar_drawer(self, returns):
        """Return (cagr, max_drawdown) tuple."""
        cumulative_returns = (1 + returns).cumprod()
        cagr = (cumulative_returns.iloc[-1] ** (252 / len(returns)) - 1) * 252
        max_dd = self.maximum_drawdown(returns)
        
        return cagr, max_dd
    
    def value_at_risk(self, returns, confidence=0.95):
        """
        Calculate Value at Risk (parametric method).
        
        VaR = μ - z_α * σ
        """
        z_score = stats.norm.ppf(1 - confidence)
        var = np.mean(returns) - z_score * np.std(returns)
        return var
    
    def conditional_value_at_risk(self, returns, confidence=0.95):
        """
        Calculate Conditional Value at Risk (Expected Shortfall).
        
        CVaR = E[L | L > VaR]
        """
        var = self.value_at_risk(returns, confidence)
        return returns[returns <= var].mean()
    
    def beta(self, returns, market_returns):
        """
        Calculate Beta (systematic risk).
        
        Formula: Cov(R, R_m) / Var(R_m)
        """
        covariance = np.cov(returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 0
        
        return covariance / market_variance
    
    def alpha(self, returns, market_returns, capm_return=None):
        """
        Calculate Jensen's Alpha (risk-adjusted excess return).
        
        Formula: R - [Rf + β(R_m - Rf)]
        """
        if capm_return is None:
            capm_return = self.risk_free_rate
        
        beta = self.beta(returns, market_returns)
        market_excess_return = np.mean(market_returns) - self.risk_free_rate
        expected_return = capm_return + beta * market_excess_return
        
        return np.mean(returns) - expected_return
    
    def tracking_error(self, returns, benchmark_returns):
        """
        Calculate Tracking Error.
        
        Formula: σ(R - R_b)
        """
        active_returns = returns - benchmark_returns
        return np.std(active_returns)
    
    def volatility(self, returns, annualized=True):
        """Calculate volatility (standard deviation)."""
        vol = np.std(returns)
        return vol * np.sqrt(252) if annualized else vol
    
    def variance(self, returns, annualized=True):
        """Calculate variance."""
        var = np.var(returns)
        return var * 252 if annualized else var
    
    def skewness(self, returns):
        """Calculate return skewness (tail risk)."""
        return stats.skew(returns)
    
    def kurtosis(self, returns):
        """Calculate return kurtosis (tail heaviness)."""
        return stats.kurtosis(returns)
    
    def cagr(self, returns):
        """
        Calculate Compound Annual Growth Rate.
        
        Formula: (Final Value / Initial Value) ^ (1 / Years) - 1
        """
        cumulative_returns = (1 + returns).cumprod()
        years = len(returns) / 252
        
        return (cumulative_returns.iloc[-1] ** (1 / years) - 1)
    
    def recovery_factor(self, returns):
        """
        Calculate Recovery Factor.
        
        Formula: CAGR / |Maximum Drawdown|
        """
        cagr_val = self.cagr(returns)
        max_dd = self.maximum_drawdown(returns)
        
        if max_dd == 0:
            return np.inf
        
        return -cagr_val / max_dd
    
    def profit_factor(self, returns):
        """
        Calculate Profit Factor.
        
        Formula: |Sum of Gains| / |Sum of Losses|
        """
        gains = returns[returns > 0].sum()
        losses = returns[returns < 0].sum()
        
        if losses == 0:
            return np.inf if gains > 0 else 0
        
        return -gains / losses
    
    def win_rate(self, returns):
        """Calculate percentage of positive returns."""
        return (returns > 0).sum() / len(returns)
    
    def payoff_ratio(self, returns):
        """
        Calculate Payoff Ratio.
        
        Formula: |Avg Gain| / |Avg Loss|
        """
        gains = returns[returns > 0]
        losses = returns[returns < 0]
        
        if len(losses) == 0:
            return np.inf
        
        avg_gain = gains.mean() if len(gains) > 0 else 0
        avg_loss = losses.mean()
        
        return -avg_gain / avg_loss if avg_loss != 0 else np.inf
    
    def comprehensive_analysis(self, portfolio_returns, benchmark_returns=None, 
                             market_returns=None):
        """
        Calculate comprehensive risk metrics package.
        
        Returns:
        --------
        dict : All relevant risk metrics
        """
        metrics = {
            # Central tendency
            'Mean Return': np.mean(portfolio_returns),
            'Median Return': np.median(portfolio_returns),
            
            # Volatility metrics
            'Volatility (Daily)': self.volatility(portfolio_returns, annualized=False),
            'Volatility (Annual)': self.volatility(portfolio_returns, annualized=True),
            'Variance': self.variance(portfolio_returns),
            
            # Risk-adjusted returns
            'Sharpe Ratio': self.sharpe_ratio(portfolio_returns),
            'Sortino Ratio': self.sortino_ratio(portfolio_returns),
            'Calmar Ratio': self.calmar_ratio(portfolio_returns),
            
            # Drawdown metrics
            'Maximum Drawdown': self.maximum_drawdown(portfolio_returns),
            'CAGR': self.cagr(portfolio_returns),
            'Recovery Factor': self.recovery_factor(portfolio_returns),
            
            # Value at Risk
            'VaR (95%)': self.value_at_risk(portfolio_returns, confidence=0.95),
            'CVaR (95%)': self.conditional_value_at_risk(portfolio_returns, confidence=0.95),
            
            # Return distribution
            'Skewness': self.skewness(portfolio_returns),
            'Kurtosis': self.kurtosis(portfolio_returns),
            
            # Trading metrics
            'Win Rate': self.win_rate(portfolio_returns),
            'Profit Factor': self.profit_factor(portfolio_returns),
            'Payoff Ratio': self.payoff_ratio(portfolio_returns),
        }
        
        # Conditional metrics
        if benchmark_returns is not None:
            metrics['Information Ratio'] = self.information_ratio(
                portfolio_returns, benchmark_returns
            )
            metrics['Tracking Error'] = self.tracking_error(
                portfolio_returns, benchmark_returns
            )
        
        # CAPM metrics
        if market_returns is not None:
            metrics['Beta'] = self.beta(portfolio_returns, market_returns)
            metrics['Alpha'] = self.alpha(portfolio_returns, market_returns)
        
        return metrics


def calculate_portfolio_metrics(portfolio_returns, weights=None, 
                               cov_matrix=None, risk_free_rate=0.03):
    """
    Convenience function for calculating portfolio metrics.
    
    Parameters:
    -----------
    portfolio_returns : pd.Series or np.ndarray
        Portfolio returns
    weights : np.ndarray, optional
        Portfolio weights
    cov_matrix : np.ndarray, optional
        Asset covariance matrix
    risk_free_rate : float
        Risk-free rate
    
    Returns:
    --------
    dict : Portfolio metrics
    """
    calculator = RiskMetricsCalculator(risk_free_rate=risk_free_rate)
    return calculator.comprehensive_analysis(portfolio_returns)
