import pandas as pd
from core.stress_testing import HistoricalStressTester
from pipelines.dual_market import MARKET_CONFIG

def run_india_crisis():
    # Load India universe
    tickers = MARKET_CONFIG['INDIA']['tickers']
    
    # Configure COVID crisis windows for India
    # Train 2017-2019
    # Test 2020
    tester = HistoricalStressTester(
        ticker_list=tickers,
        train_start='2017-01-01',
        train_end='2019-12-31',
        test_start='2020-01-01',
        test_end='2020-12-31',
        benchmark='^BSESN', # BSE Sensex as benchmark for India
        name_mapping=None
    )
    
    # Needs views for BL
    # Let's extract prior historical views from 2017-2019 using simple moving averages
    # But wait, MARKET_CONFIG['INDIA']['views'] handles views. 
    # Or we can just use dummy views or naively set them to the long term returns of the training set.
    # Actually, HistoricalStressTester expects `views_dict` and `confidence_levels` directly in run_training_phase.
    
    # We will simulate views based on 2017-2019 returns
    train_prices = tester._fetch_prices(tickers, '2017-01-01', '2019-12-31')
    train_rets = train_prices.pct_change().dropna()
    avg_annual_rets = train_rets.mean() * 252
    
    views_dict = avg_annual_rets.to_dict()
    confidence_levels = {t: 0.5 for t in tickers}
    
    tester.run_training_phase(views_dict, confidence_levels)
    tester.run_stress_test()
    with open("results/india_crisis.txt", "w") as f:
        for strategy, res in tester.results.items():
            f.write(f"\n--- {strategy.upper()} ---\n")
            f.write(f"Max Drawdown: {res['Max Drawdown']:.2%}\n")
            f.write(f"Pre Vol: {res['Pre-Crisis Volatility']:.4f}\n")
            f.write(f"Crisis Vol: {res['Crisis Volatility']:.4f}\n")
            f.write(f"Vol Spike: {res['Volatility Spike (x)']:.2f}x\n")
            f.write(f"Recovery Days (Underwater): {res['Max Underwater Days']} days\n")

if __name__ == "__main__":
    run_india_crisis()
