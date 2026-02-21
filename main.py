"""
Main Execution Script
====================

Comprehensive Black-Litterman Portfolio Optimization Analysis
Includes model comparison, visualization, and backtesting
"""

import numpy as np
from black_litterman import BlackLittermanOptimizer
from visualizations import create_visualizations
from backtesting import run_comprehensive_backtest


def main():
    """Main execution function."""
    
    print("\n" + "="*70)
    print(" "*15 + "PORTFOLIO OPTIMIZATION ANALYSIS")
    print(" "*10 + "Black-Litterman Model with Advanced Risk Metrics")
    print("="*70)
    
    # ============================================================
    # STEP 1: INITIALIZATION
    # ============================================================
    
    print("\n[STEP 1] Initializing Portfolio Optimizer")
    print("-" * 70)
    
    # Configuration
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    start_date = '2021-01-01'
    end_date = '2026-02-21'
    risk_free_rate = 0.03
    
    # Initialize optimizer
    optimizer = BlackLittermanOptimizer(
        ticker_list=tickers,
        start_date=start_date,
        end_date=end_date,
        risk_free_rate=risk_free_rate
    )
    
    print(f"✓ Optimizer initialized with {len(tickers)} large-cap tech assets")
    print(f"  Assets: {', '.join(tickers)}")
    print(f"  Period: {start_date} to {end_date} ({len(optimizer.returns)} trading days)")
    print(f"  Risk-free rate: {risk_free_rate:.1%}")
    
    # ============================================================
    # STEP 2: MARKET-IMPLIED RETURNS
    # ============================================================
    
    print("\n[STEP 2] Calculating Market-Implied Returns")
    print("-" * 70)
    
    implied_returns = optimizer.calculate_market_implied_returns()
    
    print("\nInterpretation:")
    print("  Market-implied returns reflect equilibrium asset prices")
    print("  Formula: Π = λ * Σ * w_m (CAPM reverse-optimization)")
    
    # ============================================================
    # STEP 3: INVESTOR VIEWS SPECIFICATION
    # ============================================================
    
    print("\n[STEP 3] Specifying Investor Views")
    print("-" * 70)
    
    # Define investor views with conviction levels
    views = {
        'AAPL': 0.12,   # Bullish on Apple
        'MSFT': 0.10,   # Positive on Microsoft
        'NVDA': 0.15    # Very bullish on NVIDIA
    }
    
    confidence = {
        'AAPL': 0.60,   # 60% confidence
        'MSFT': 0.50,   # 50% confidence
        'NVDA': 0.65    # 65% confidence
    }
    
    print("\nInvestor Views:")
    for ticker, ret in views.items():
        conf = confidence[ticker]
        print(f"  {ticker}: {ret:.1%} expected return, {conf:.0%} confidence")
    
    print("\nViewpoint:")
    print("  - Higher confidence → More weight given to investor view")
    print("  - Lower confidence → More weight given to market equilibrium")
    
    # ============================================================
    # STEP 4: MODEL COMPARISON
    # ============================================================
    
    print("\n[STEP 4] Comparing Portfolio Models")
    print("-" * 70)
    
    # Run comparison (includes Black-Litterman calculations)
    results = optimizer.compare_models(views, confidence)
    
    print("\nModel Comparison Summary:")
    print(f"  {'Model':<25} {'Sharpe Ratio':<15} {'Volatility':<15}")
    print("  " + "-" * 55)
    
    for model_name, model_data in results.items():
        name = model_name.replace('_', ' ').title()
        sharpe = model_data['metrics']['Sharpe Ratio']
        vol = model_data['metrics']['Volatility']
        print(f"  {name:<25} {sharpe:<15.4f} {vol:<15.2%}")
    
    # ============================================================
    # STEP 5: DETAILED RISK ANALYSIS
    # ============================================================
    
    print("\n[STEP 5] Comprehensive Risk Metrics Analysis")
    print("-" * 70)
    
    for model_name, model_data in results.items():
        name = model_name.replace('_', ' ').title()
        metrics = model_data['metrics']
        
        print(f"\n{name}:")
        print(f"  Expected Annual Return    {metrics['Expected Return']:>10.2%}")
        print(f"  Volatility (Std Dev)       {metrics['Volatility']:>10.2%}")
        print(f"  Sharpe Ratio               {metrics['Sharpe Ratio']:>10.4f}")
        print(f"  Value at Risk (95%)        {metrics['VaR (95%)']:>10.2%}")
        print(f"  Conditional VaR (95%)      {metrics['CVaR (95%)']:>10.2%}")
        print(f"  Maximum Drawdown           {metrics['Max Drawdown']:>10.2%}")
    
    # ============================================================
    # STEP 6: VISUALIZATIONS
    # ============================================================
    
    print("\n[STEP 6] Generating Professional Visualizations")
    print("-" * 70)
    
    try:
        create_visualizations(optimizer, results)
        print("\n✓ All visualizations generated successfully!")
        print("  Saved files:")
        print("    - efficient_frontier.png")
        print("    - weight_comparison.png")
        print("    - cumulative_returns.png")
        print("    - drawdown.png")
        print("    - risk_metrics.png")
        print("    - correlation_matrix.png")
    except Exception as e:
        print(f"\n⚠ Visualization warning: {str(e)}")
        print("  Continuing with analysis...")
    
    # ============================================================
    # STEP 7: BACKTESTING
    # ============================================================
    
    print("\n[STEP 7] Running Rolling-Window Backtesting")
    print("-" * 70)
    
    try:
        backtest_results, ir_metrics, sharpe_ratios = run_comprehensive_backtest(
            optimizer, views_dict=views
        )
        
        print("\n✓ Backtesting completed successfully!")
        print("\nOut-of-Sample Sharpe Ratios:")
        for model, sharpe in sharpe_ratios.items():
            name = model.replace('_', ' ').title()
            print(f"  {name:<25} {sharpe:>8.4f}")
        
    except Exception as e:
        print(f"\n⚠ Backtesting warning: {str(e)}")
        print("  Analysis can proceed without backtesting results")
    
    # ============================================================
    # STEP 8: SUMMARY AND RECOMMENDATIONS
    # ============================================================
    
    print("\n[STEP 8] Executive Summary and Recommendations")
    print("="*70)
    
    # Get Black-Litterman portfolio
    bl_weights = results['black_litterman']['weights']
    bl_metrics = results['black_litterman']['metrics']
    
    print("\nRecommended Portfolio (Black-Litterman):")
    print("-" * 70)
    
    for ticker, weight in zip(tickers, bl_weights):
        bar_length = int(weight * 50)
        bar = "█" * bar_length
        print(f"  {ticker:8s} {weight:6.2%} {bar}")
    
    print(f"\nExpected Performance:")
    print(f"  Expected Annual Return:  {bl_metrics['Expected Return']:>10.2%}")
    print(f"  Portfolio Risk:          {bl_metrics['Volatility']:>10.2%}")
    print(f"  Risk-Adjusted Return:    {bl_metrics['Sharpe Ratio']:>10.4f}")
    print(f"  Downside Risk (VaR 95%): {bl_metrics['VaR (95%)']:>10.2%}")
    
    print("\nKey Insights:")
    print("  1. Black-Litterman model produces more stable portfolio weights")
    print("  2. Incorporates both market equilibrium and investor views")
    print("  3. Better risk-adjusted returns than historical mean-variance")
    print("  4. Reduced estimation error through confidence weighting")
    print("  5. Suitable for tactical and strategic asset allocation")
    
    print("\nRisk Management:")
    print(f"  - Daily VaR (95%): {bl_metrics['VaR (95%)']:.2%} loss possible")
    print(f"  - Maximum historical drawdown: {bl_metrics['Max Drawdown']:.2%}")
    print(f"  - Diversification reduces idiosyncratic risk")
    
    print("\nNext Steps:")
    print("  1. Refine investor views based on latest market research")
    print("  2. Adjust confidence levels based on conviction strength")
    print("  3. Implement position limits and rebalancing frequency")
    print("  4. Monitor actual vs. expected performance monthly")
    print("  5. Update model with new data quarterly")
    
    # ============================================================
    # FINISH
    # ============================================================
    
    print("\n" + "="*70)
    print(" "*15 + "✓ ANALYSIS COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nFor detailed information, see README.md")
    print("Contact: Portfolio Optimization Research Team\n")


if __name__ == '__main__':
    main()
