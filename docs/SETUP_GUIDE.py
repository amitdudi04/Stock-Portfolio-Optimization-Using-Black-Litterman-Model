#!/usr/bin/env python3
"""
Installation and Setup Guide
=============================

Complete setup instructions for the Portfolio Optimization System
"""

import subprocess
import sys
import os


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print formatted section."""
    print(f"\n✓ {text}")
    print("-" * 70)


def install_dependencies():
    """Install required dependencies."""
    print_section("Installing Dependencies")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"
        ])
        print("✓ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {str(e)}")
        return False


def print_usage_guide():
    """Print usage guide."""
    
    print_header("PORTFOLIO OPTIMIZATION SYSTEM - USAGE GUIDE")
    
    print("""
🚀 LAUNCHING THE SYSTEM
=======================

1. STREAMLIT DASHBOARD (Interactive Frontend)
   ✓ Beautiful web UI for portfolio optimization
   ✓ Real-time model comparison
   ✓ Interactive efficient frontier
   ✓ Risk analysis & recommendations
   
   TO RUN:
   $ streamlit run dashboard.py
   
   Then open: http://localhost:8501

2. FASTAPI BACKEND (REST API)
   ✓ Production-ready API endpoints
   ✓ Swagger documentation
   ✓ JSON request/response format
   ✓ Scalable architecture
   
   TO RUN:
   $ python api.py
   
   Then visit: http://localhost:8000/docs

3. COMMAND-LINE ANALYSIS
   ✓ Full analysis with visualizations
   ✓ Comprehensive reporting
   ✓ Backtesting
   
   TO RUN:
   $ python main.py

""")
    
    print_section("API ENDPOINTS")
    
    print("""
Health Check:
  GET /health
  
Optimization:
  POST /optimize
  Request body:
  {
    "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
    "start_date": "2021-01-01",
    "end_date": "2026-02-21",
    "risk_free_rate": 0.03,
    "lambda_risk": 2.5,
    "views": [
      {
        "ticker": "AAPL",
        "expected_return": 0.12,
        "confidence": 0.60
      }
    ]
  }

Efficient Frontier:
  POST /efficient-frontier
  (Same request body as /optimize)

Risk Metrics:
  POST /risk-metrics
  (Same request body as /optimize)

Backtesting:
  POST /backtest
  (Same request body as /optimize)

Configuration:
  GET /config

Assets:
  GET /assets
  
Interactive Docs:
  GET /docs (Swagger UI)
  GET /redoc (ReDoc)
""")
    
    print_section("CONFIGURATION")
    
    print("""
Edit 'config.py' to customize:

1. Data Configuration:
   - TICKERS: List of assets
   - START_DATE, END_DATE: Historical period
   - DATA_SOURCE: 'yfinance' or 'csv'

2. Risk Parameters:
   - RISK_FREE_RATE: Risk-free rate assumption
   - LAMBDA_RISK: Risk aversion coefficient
   - TAU: Black-Litterman scaling factor
   - VAR_LEVEL: For Value at Risk calculation
   - TRANSACTION_COST_BPS: Basis points cost

3. Backtesting:
   - WINDOW_SIZE: Training window (252 days = 1 year)
   - REBALANCE_FREQ: Rebalancing frequency
   - INITIAL_CAPITAL: Starting capital

4. API:
   - HOST, PORT: API server settings
   - CORS settings
   - Debug mode

5. Streamlit:
   - Page layout and theme
   - Chart dimensions
   - Performance settings
""")
    
    print_section("DEPLOYMENT")
    
    print("""
For Production Deployment:

1. Streamlit Cloud (Free):
   $ git push your-repo
   Set up on https://share.streamlit.io
   
2. AWS/GCP/Azure:
   - Use Docker container
   - Deploy FastAPI on serverless platform
   - Use managed database (PostgreSQL)
   
3. Local Server:
   - Use Gunicorn for FastAPI
   - Enable HTTPS/SSL
   - Set up reverse proxy (nginx)
   
4. Docker Compose:
   - Run Streamlit + FastAPI + Database together
   - Easy scaling and deployment
""")
    
    print_section("TROUBLESHOOTING")
    
    print("""
Issue: "No module named 'yfinance'"
Solution: 
  $ pip install yfinance

Issue: "Connection refused" when accessing API
Solution:
  - Ensure API is running: python api.py
  - Check port 8000 is not in use
  - Try: python api.py --port 9000

Issue: "Streamlit not found"
Solution:
  $ pip install streamlit

Issue: "Data loading is slow"
Solution:
  - Check internet connection
  - Use shorter date range
  - Enable DATA_CACHE in config.py

Issue: "ModuleNotFoundError"
Solution:
  - Activate virtual environment
  - Reinstall dependencies: pip install -r requirements.txt
  - Check PYTHONPATH includes project directory
""")
    
    print_section("PROJECT STRUCTURE")
    
    print("""
portfolio_optimization/
│
├── black_litterman.py          # Core BL model implementation
├── advanced_metrics.py         # Advanced risk metrics
├── visualizations.py           # Matplotlib visualizations
├── backtesting.py              # Backtesting framework
├── config.py                   # Configuration management
├── main.py                     # CLI execution
│
├── dashboard.py                # Streamlit dashboard (NEW)
├── api.py                      # FastAPI backend (NEW)
│
├── requirements.txt            # Dependencies
├── README.md                   # Full documentation
└── setup.py                    # Installation script
""")
    
    print_section("NEXT STEPS")
    
    print("""
1. Install dependencies:
   $ pip install -r requirements.txt

2. Try the Streamlit dashboard:
   $ streamlit run dashboard.py

3. Explore the API:
   $ python api.py
   Then visit: http://localhost:8000/docs

4. Run full analysis:
   $ python main.py

5. Customize settings:
   Edit config.py for your needs

6. Deploy to production:
   See deployment section above
""")
    
    print_header("Ready to Optimize! 🚀📊")


def main():
    """Main setup function."""
    
    print_header("PORTFOLIO OPTIMIZATION SYSTEM - SETUP")
    
    # Install dependencies
    if not install_dependencies():
        print("\nPlease install dependencies manually:")
        print("  $ pip install -r requirements.txt")
        sys.exit(1)
    
    # Print usage guide
    print_usage_guide()
    
    print("\n✓ Setup complete! You can now run the applications.\n")


if __name__ == "__main__":
    main()
