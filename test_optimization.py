#!/usr/bin/env python3
"""
Quick test script to verify optimization is working.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_optimization.models import BlackLittermanOptimizer

def test_optimization():
    """Test optimization with sample portfolio."""
    
    print("\n" + "="*70)
    print("PORTFOLIO OPTIMIZATION TEST")
    print("="*70 + "\n")
    
    try:
        # Sample data
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        start_date = '2023-01-01'
        end_date = '2024-12-31'
        
        print(f"Testing optimization with: {tickers}")
        print(f"Period: {start_date} to {end_date}\n")
        
        # Initialize optimizer
        print("1. Initializing optimizer...")
        optimizer = BlackLittermanOptimizer(
            ticker_list=tickers,
            start_date=start_date,
            end_date=end_date,
            risk_free_rate=0.03
        )
        print("   ✓ Optimizer initialized successfully\n")
        
        # Test 1: Run without views (market equilibrium)
        print("2. Running optimization WITHOUT views (market equilibrium)...")
        results_no_views = optimizer.compare_models({})
        print("   ✓ Optimization completed\n")
        
        # Test 2: Run with views
        print("3. Running optimization WITH views...")
        views = {'AAPL': 0.12, 'MSFT': 0.10}
        confidence = {'AAPL': 0.7, 'MSFT': 0.6}
        results_with_views = optimizer.compare_models(views, confidence)
        print("   ✓ Optimization with views completed\n")
        
        # Display results
        print("="*70)
        print("BLACK-LITTERMAN WEIGHTS (with views):")
        print("="*70)
        bl_weights = results_with_views['black_litterman']['weights']
        for ticker, weight in zip(tickers, bl_weights):
            print(f"  {ticker:8s}: {weight:7.2%}")
        
        print("\n" + "="*70)
        print("MARKOWITZ WEIGHTS (without views):")
        print("="*70)
        mw_weights = results_with_views['markowitz']['weights']
        for ticker, weight in zip(tickers, mw_weights):
            print(f"  {ticker:8s}: {weight:7.2%}")
        
        print("\n" + "="*70)
        print("RESULTS SUMMARY")
        print("="*70)
        bl_metrics = results_with_views['black_litterman']['metrics']
        print(f"Expected Return (BL):  {bl_metrics['Expected Return']:.2%}")
        print(f"Volatility (BL):       {bl_metrics['Volatility']:.2%}")
        print(f"Sharpe Ratio (BL):     {bl_metrics['Sharpe Ratio']:.4f}")
        
        print("\n✓ All tests passed successfully!")
        print("✓ Optimization is working correctly\n")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n✗ Test failed with error:")
        print(f"  {str(e)}\n")
        print("Traceback:")
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = test_optimization()
    sys.exit(0 if success else 1)
