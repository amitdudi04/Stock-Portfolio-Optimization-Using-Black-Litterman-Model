from portfolio_optimization import BlackLittermanOptimizer
import pandas as pd

def main():
    print("Initializing Robustness Tester for Risk Aversion (λ) Sensitivity...")
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
    
    confidence = {
        'AAPL': 0.60,
        'MSFT': 0.50,
        'GOOGL': 0.40,
        'AMZN': 0.45,
        'NVDA': 0.65
    }
    
    print("\nTriggering Sensitivity Engine for Lambda...")
    df = opt.run_lambda_sensitivity(views, confidence)
    
    # Print numerical results table to terminal
    pd.set_option('display.float_format', '{:.4f}'.format)
    print("\n" + "="*80)
    print("LAMBDA SENSITIVITY DATAFRAME RESULTS")
    print("="*80)
    print(df)
    print("="*80)

if __name__ == "__main__":
    main()
