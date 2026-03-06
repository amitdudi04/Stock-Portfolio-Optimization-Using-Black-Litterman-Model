import sys
import os
import yaml
import pandas as pd
import pathlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipelines.dual_market import evaluate_dual_market

def run():
    print("Executing Crisis Stress Testing Pipeline...")
    
    # Load Config
    project_root = pathlib.Path(__file__).resolve().parent.parent
    config_path = project_root / 'config' / 'project_config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    results_packet = evaluate_dual_market()
    raw_results = results_packet['raw_results']
    
    records = []
    
    crisis_map = {
        'US': '2008_US_GFC',
        'CHINA': '2015_China_Crash',
        'INDIA': '2020_India_Covid'
    }
    
    for market in ['US', 'CHINA', 'INDIA']:
        if market not in raw_results:
            continue
            
        stress_res = raw_results[market]['stress']
        crisis_name = crisis_map[market]
        market_label = 'United States' if market == 'US' else ('China' if market == 'CHINA' else 'India')
        
        for model in ['black_litterman', 'markowitz']:
            model_name = "Black-Litterman" if model == 'black_litterman' else "Markowitz"
            
            dd = stress_res[model]['Max Drawdown']
            vol_spike = stress_res[model]['Volatility Spike (x)']
            rec_time = stress_res[model]['Max Underwater Days']
            
            records.append({
                'Crisis': crisis_name,
                'Market': market_label,
                'Model': model_name,
                'Max Drawdown': f"{dd*100:.2f}%",
                'Volatility Spike': f"{vol_spike:.2f}x",
                'Recovery Time': f"{rec_time} days"
            })
            
    df = pd.DataFrame(records)
    csv_path = project_root / 'results' / 'v1_final_results' / 'crisis_comparison_tables.csv'
    df.to_csv(csv_path, index=False)
    print("Exporting results to results/v1_final_results/crisis_comparison_tables.csv")

if __name__ == "__main__":
    run()
