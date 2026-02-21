"""
Portfolio Optimization Package
==============================

Black-Litterman Model with Advanced Risk Metrics and Backtesting
"""

__version__ = "1.0.0"
__author__ = "Portfolio Optimization Research Team"
__email__ = "portfolio@optimization.dev"

from .models.black_litterman import BlackLittermanOptimizer
from .models.advanced_metrics import RiskMetricsCalculator
from .backtesting.rolling_backtest import PortfolioBacktester

__all__ = [
    "BlackLittermanOptimizer",
    "RiskMetricsCalculator", 
    "PortfolioBacktester",
]
