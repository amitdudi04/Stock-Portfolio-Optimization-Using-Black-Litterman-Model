import sys
import logging
from pipelines.dual_market import evaluate_dual_market, MARKET_CONFIG

logging.basicConfig(level=logging.INFO)

# Validate the dictionary has 3 keys
assert "US" in MARKET_CONFIG
assert "CHINA" in MARKET_CONFIG
assert "INDIA" in MARKET_CONFIG

try:
    print("Initiating test...")
    res = evaluate_dual_market(MARKET_CONFIG)
    print("SUCCESS")
    print("DF Summary lengths:", len(res["summary_df"]))
    print("DF Structural length:", len(res["structural_df"]))
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
