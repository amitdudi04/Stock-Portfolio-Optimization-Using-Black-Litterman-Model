import traceback
from pipelines.dual_market import evaluate_dual_market, MARKET_CONFIG

if __name__ == "__main__":
    try:
        results = evaluate_dual_market({"CHINA": MARKET_CONFIG["CHINA"]})
        with open("stacktrace.txt", "w", encoding='utf-8') as f:
            f.write(f"SOE returned: {results.get('soe_study') is not None}\n")
            f.write(f"Stats returned: {results.get('statistical_tests')}\n")
    except Exception as e:
        with open("stacktrace.txt", "w", encoding='utf-8') as f:
            f.write(traceback.format_exc())
