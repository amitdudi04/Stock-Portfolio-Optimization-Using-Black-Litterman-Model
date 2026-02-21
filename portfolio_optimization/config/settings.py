"""
Configuration Management
========================

Centralized configuration for portfolio optimization system.
"""

import os
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class DataConfig:
    """Data configuration parameters."""
    
    # Default assets
    TICKERS: List[str] = None
    START_DATE: str = '2021-01-01'
    END_DATE: str = '2026-02-21'
    
    # Price data
    DATA_SOURCE: str = 'yfinance'
    CACHE_DATA: bool = True
    DATA_DIR: str = './data'
    
    def __post_init__(self):
        if self.TICKERS is None:
            self.TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
        os.makedirs(self.DATA_DIR, exist_ok=True)


@dataclass
class RiskConfig:
    """Risk parameters for portfolio optimization."""
    
    # Base parameters
    RISK_FREE_RATE: float = 0.03
    LAMBDA_RISK: float = 2.5
    TAU: float = 0.05
    
    # Risk metrics
    VAR_LEVEL: float = 0.95
    CVAR_LEVEL: float = 0.95
    
    # Constraints
    MIN_WEIGHT: float = 0.0
    MAX_WEIGHT: float = 1.0
    ALLOW_SHORT_SELLING: bool = False
    
    # Transaction costs
    TRANSACTION_COST_BPS: float = 10.0  # Basis points
    MARKET_IMPACT_FACTOR: float = 0.001


@dataclass
class BacktestConfig:
    """Backtesting configuration."""
    
    WINDOW_SIZE: int = 252  # 1 year
    REBALANCE_FREQ: int = 63  # 1 quarter (63 days)
    INITIAL_CAPITAL: float = 1_000_000  # $1M
    
    # Performance metrics
    CALCULATE_IR: bool = True
    CALCULATE_TURNOVER: bool = True
    CALCULATE_ALPHA: bool = True


@dataclass
class APIConfig:
    """API configuration."""
    
    HOST: str = '0.0.0.0'
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True
    
    # CORS
    ALLOW_ORIGINS: List[str] = None
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = None
    ALLOW_HEADERS: List[str] = None
    
    def __post_init__(self):
        if self.ALLOW_ORIGINS is None:
            self.ALLOW_ORIGINS = ['*']
        if self.ALLOW_METHODS is None:
            self.ALLOW_METHODS = ['*']
        if self.ALLOW_HEADERS is None:
            self.ALLOW_HEADERS = ['*']


@dataclass
class DatabaseConfig:
    """Database configuration."""
    
    DB_TYPE: str = 'sqlite'  # sqlite, postgresql, mysql
    DB_PATH: str = './portfolio.db'  # For SQLite
    
    # For PostgreSQL/MySQL
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USER: str = 'admin'
    DB_PASSWORD: str = 'password'
    DB_NAME: str = 'portfolio_db'
    
    # Connection
    ECHO_SQL: bool = False
    POOL_SIZE: int = 10


@dataclass
class StreamlitConfig:
    """Streamlit app configuration."""
    
    PAGE_TITLE: str = "Portfolio Optimization Dashboard"
    PAGE_ICON: str = "📊"
    LAYOUT: str = "wide"
    
    # Visualization
    CHART_HEIGHT: int = 500
    CHART_WIDTH: int = 800
    THEME: str = "dark"  # light or dark
    
    # Performance
    CACHE_RESULTS: bool = True
    CACHE_TTL: int = 3600  # 1 hour in seconds


class Config:
    """Master configuration class."""
    
    def __init__(self):
        self.data = DataConfig()
        self.risk = RiskConfig()
        self.backtest = BacktestConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.streamlit = StreamlitConfig()
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary."""
        return {
            'data': self.data.__dict__,
            'risk': self.risk.__dict__,
            'backtest': self.backtest.__dict__,
            'api': self.api.__dict__,
            'database': self.database.__dict__,
            'streamlit': self.streamlit.__dict__,
        }


# Global config instance
config = Config()
