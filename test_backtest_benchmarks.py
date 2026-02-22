from portfolio_optimization import BlackLittermanOptimizer
from backtesting import run_comprehensive_backtest

def main():
    print("Initializing BlackLittermanOptimizer for 5 years back...")
    opt = BlackLittermanOptimizer(
        ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
        '2018-01-01',
        '2024-01-01'
    )
    
    views = {
        'AAPL': 0.12,
        'MSFT': 0.10,
        'GOOGL': 0.11,
        'AMZN': 0.14,
        'NVDA': 0.15
    }
    
    print("\nTriggering Enhanced Backtester Matrix...")
    run_comprehensive_backtest(opt, views)

if __name__ == "__main__":
    main()
