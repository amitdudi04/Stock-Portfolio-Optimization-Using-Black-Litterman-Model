import pandas as pd
from pipelines.dual_market import evaluate_dual_market, MARKET_CONFIG
import copy

def run():
    print("Running evaluate_dual_market for INDIA only...")
    config = copy.deepcopy(MARKET_CONFIG)
    eval_config = {"INDIA": config["INDIA"]}
    
    results = evaluate_dual_market(eval_config)
    
    # Extract India Performance
    in_res = results["raw_results"]["INDIA"]
    p = in_res["performance"]
    
    print("\nINDIA METRICS:")
    print(f"BL Return: {p['bl_ret']*100:.2f}%")
    print(f"BL Vol: {p['bl_vol']*100:.2f}%")
    print(f"BL Sharpe: {p['bl_sharpe']:.3f}")
    print(f"BL Turnover: {p['bl_turn']*100:.2f}%")
    print(f"BL Max DD: {p['bl_dd']*100:.2f}%")
    print("---")
    print(f"MW Return: {p['mw_ret']*100:.2f}%")
    print(f"MW Vol: {p['mw_vol']*100:.2f}%")
    print(f"MW Sharpe: {p['mw_sharpe']:.3f}")
    print(f"MW Turnover: {p['mw_turn']*100:.2f}%")
    print(f"MW Max DD: {p['mw_dd']*100:.2f}%")
    print("---")
    print(f"Bench Return: {p['bench_ret']*100:.2f}%")
    print(f"Bench Vol: {p['bench_vol']*100:.2f}%")
    print(f"Bench Sharpe: {p['bench_sharpe']:.3f}")
    print(f"Bench Max DD: {p['bench_dd']*100:.2f}%")

if __name__ == "__main__":
    run()
