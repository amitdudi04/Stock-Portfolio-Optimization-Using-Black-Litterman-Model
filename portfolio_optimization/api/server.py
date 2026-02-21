"""
FastAPI Backend for Portfolio Optimization
===========================================

RESTful API for Black-Litterman portfolio optimization.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import numpy as np
from datetime import datetime

from portfolio_optimization.models import BlackLittermanOptimizer, RiskMetricsCalculator
from portfolio_optimization.config import config


# Pydantic models
class InvestorView(BaseModel):
    """Investor view specification."""
    ticker: str = Field(..., description="Asset ticker")
    expected_return: float = Field(..., description="Expected annual return")
    confidence: float = Field(..., description="Confidence level (0-1)")


class OptimizationRequest(BaseModel):
    """Portfolio optimization request."""
    tickers: List[str] = Field(default=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'])
    start_date: str = Field(default='2021-01-01')
    end_date: str = Field(default='2026-02-21')
    risk_free_rate: float = Field(default=0.03)
    lambda_risk: float = Field(default=2.5)
    views: List[InvestorView] = Field(default_factory=list)


class PortfolioWeights(BaseModel):
    """Portfolio weights response."""
    model: str
    tickers: List[str]
    weights: List[float]
    total: float = 1.0


class RiskMetrics(BaseModel):
    """Risk metrics response."""
    expected_return: float
    volatility: float
    sharpe_ratio: float
    var_95: float
    cvar_95: float
    max_drawdown: float


class OptimizationResponse(BaseModel):
    """Optimization response."""
    timestamp: str
    models: Dict[str, Dict]
    correlation_matrix: List[List[float]]


class EfficientFrontierData(BaseModel):
    """Efficient frontier data."""
    volatilities: List[float]
    returns: List[float]
    sharpe_ratios: List[float]
    optimal_portfolios: Dict[str, Dict]


# Initialize FastAPI app
app = FastAPI(
    title="Portfolio Optimization API",
    description="Black-Litterman Model with Advanced Risk Metrics",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.ALLOW_ORIGINS,
    allow_credentials=config.api.ALLOW_CREDENTIALS,
    allow_methods=config.api.ALLOW_METHODS,
    allow_headers=config.api.ALLOW_HEADERS,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_portfolio(request: OptimizationRequest):
    """
    Optimize portfolio using Black-Litterman model.
    
    Parameters:
    -----------
    request : OptimizationRequest
        Portfolio optimization parameters
    
    Returns:
    --------
    OptimizationResponse : Optimization results
    """
    try:
        # Initialize optimizer
        optimizer = BlackLittermanOptimizer(
            ticker_list=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date,
            risk_free_rate=request.risk_free_rate
        )
        
        optimizer.lambda_risk = request.lambda_risk
        
        # Convert views to dictionary
        views_dict = {v.ticker: v.expected_return for v in request.views}
        confidence_dict = {v.ticker: v.confidence for v in request.views}
        
        # Run optimization
        results = optimizer.compare_models(views_dict, confidence_dict)
        
        # Prepare response
        response_data = {
            'timestamp': datetime.now().isoformat(),
            'models': {}
        }
        
        for model_name, model_data in results.items():
            response_data['models'][model_name] = {
                'weights': (model_data['weights'] * 100).tolist(),
                'metrics': {
                    key: float(val) if isinstance(val, (np.floating, np.integer)) else val
                    for key, val in model_data['metrics'].items()
                }
            }
        
        # Add correlation matrix
        response_data['correlation_matrix'] = optimizer.returns.corr().values.tolist()
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/efficient-frontier")
async def get_efficient_frontier(request: OptimizationRequest):
    """
    Generate efficient frontier data.
    
    Returns interactive frontier visualization data.
    """
    try:
        optimizer = BlackLittermanOptimizer(
            ticker_list=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date,
            risk_free_rate=request.risk_free_rate
        )
        
        optimizer.lambda_risk = request.lambda_risk
        
        # Generate random portfolios
        np.random.seed(42)
        volatilities = []
        returns = []
        sharpe_ratios = []
        
        for _ in range(500):
            weights = np.random.random(len(optimizer.ticker_list))
            weights /= np.sum(weights)
            
            port_return = np.sum(weights * optimizer.bl_returns)
            port_vol = np.sqrt(weights @ optimizer.cov_matrix @ weights)
            sharpe = (port_return - optimizer.risk_free_rate) / port_vol
            
            volatilities.append(float(port_vol))
            returns.append(float(port_return))
            sharpe_ratios.append(float(sharpe))
        
        # Views for optimization
        views_dict = {v.ticker: v.expected_return for v in request.views}
        confidence_dict = {v.ticker: v.confidence for v in request.views}
        
        # Optimal portfolios
        results = optimizer.compare_models(views_dict, confidence_dict)
        
        optimal_portfolios = {}
        for model_name, model_data in results.items():
            vol = float(np.sqrt(model_data['weights'] @ optimizer.cov_matrix @ model_data['weights']))
            ret = float(model_data['metrics']['Expected Return'])
            
            optimal_portfolios[model_name] = {
                'volatility': vol,
                'return': ret,
                'weights': (model_data['weights'] * 100).tolist()
            }
        
        return {
            'volatilities': volatilities,
            'returns': returns,
            'sharpe_ratios': sharpe_ratios,
            'optimal_portfolios': optimal_portfolios
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/risk-metrics")
async def calculate_risk_metrics(request: OptimizationRequest):
    """
    Calculate comprehensive risk metrics.
    
    Returns advanced risk analytics.
    """
    try:
        optimizer = BlackLittermanOptimizer(
            ticker_list=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date,
            risk_free_rate=request.risk_free_rate
        )
        
        views_dict = {v.ticker: v.expected_return for v in request.views}
        confidence_dict = {v.ticker: v.confidence for v in request.views}
        
        results = optimizer.compare_models(views_dict, confidence_dict)
        
        # Calculate advanced metrics
        calculator = RiskMetricsCalculator(risk_free_rate=request.risk_free_rate)
        
        metrics_response = {}
        
        for model_name, model_data in results.items():
            weights = model_data['weights']
            portfolio_returns = (optimizer.returns @ weights).values
            
            comprehensive_metrics = calculator.comprehensive_analysis(portfolio_returns)
            
            # Convert numpy types to Python types
            metrics_response[model_name] = {
                key: float(val) if isinstance(val, (np.floating, np.integer)) else val
                for key, val in comprehensive_metrics.items()
            }
        
        return metrics_response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/assets")
async def get_available_assets():
    """Get list of available assets."""
    return {
        "default_assets": config.data.TICKERS,
        "description": "List of default assets in portfolio optimization"
    }


@app.get("/config")
async def get_configuration():
    """Get API configuration."""
    return {
        "risk_free_rate": config.risk.RISK_FREE_RATE,
        "lambda_risk": config.risk.LAMBDA_RISK,
        "tau": config.risk.TAU,
        "var_level": config.risk.VAR_LEVEL,
        "cvar_level": config.risk.CVAR_LEVEL,
        "transaction_cost_bps": config.risk.TRANSACTION_COST_BPS
    }


@app.post("/backtest")
async def run_backtest(request: OptimizationRequest):
    """
    Run backtesting analysis.
    
    Returns out-of-sample performance metrics.
    """
    try:
        from backtesting import run_comprehensive_backtest
        
        optimizer = BlackLittermanOptimizer(
            ticker_list=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date,
            risk_free_rate=request.risk_free_rate
        )
        
        views_dict = {v.ticker: v.expected_return for v in request.views}
        
        backtest_results, ir_metrics, sharpe_ratios = run_comprehensive_backtest(
            optimizer, views_dict=views_dict
        )
        
        return {
            'sharpe_ratios': {k: float(v) for k, v in sharpe_ratios.items()},
            'information_ratios': {
                k: {
                    'ir': float(v['information_ratio']),
                    'active_return': float(v['active_return']),
                    'tracking_error': float(v['tracking_error'])
                }
                for k, v in ir_metrics.items()
            },
            'periods': len(backtest_results['dates']),
            'window_size': config.backtest.WINDOW_SIZE,
            'rebalance_frequency': config.backtest.REBALANCE_FREQ
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Portfolio Optimization API",
        "version": "1.0.0",
        "description": "Black-Litterman Model with Advanced Risk Metrics",
        "endpoints": {
            "health": "/health",
            "optimize": "POST /optimize",
            "efficient_frontier": "POST /efficient-frontier",
            "risk_metrics": "POST /risk-metrics",
            "backtest": "POST /backtest",
            "assets": "GET /assets",
            "config": "GET /config"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.api.HOST,
        port=config.api.PORT,
        debug=config.api.DEBUG,
        reload=config.api.RELOAD
    )
