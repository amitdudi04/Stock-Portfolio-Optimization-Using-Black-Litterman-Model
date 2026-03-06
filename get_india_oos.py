import pandas as pd
from core.optimizer import BlackLittermanOptimizer
import copy

def run_oos():
    print("Running India OOS Cost Drag...")
    df = pd.read_csv("data/INDIA_universe.csv")
    tickers = df['Ticker'].tolist()
    
    from pipelines.dual_market import MARKET_CONFIG
    config = MARKET_CONFIG["INDIA"]
    
    # We'll just run evaluate_dual_market and pull out the turn costs via ASI
    # Or just use the already generated turnover
    
    # Cost drag = Turn * 0.001 (10 bps assumption) * rebalances per year
    # Bl Turn = 8.85%. Cost drag annual ~ 8.85% * 0.001 * 12 = 0.0010
    # Mw Turn = 70.37%. Cost drag annual ~ 70.37% * 0.001 * 12 = 0.0084
    
    # To be extremely precise with Table 2 rolling backtests, let's just 
    # generate the exact net/gross from the pipeline metrics
    
    pass

if __name__ == "__main__":
    run_oos()
