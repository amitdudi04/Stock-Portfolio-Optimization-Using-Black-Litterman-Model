import logging
logging.basicConfig(level=logging.INFO)
try:
    from pipelines.dual_market import evaluate_dual_market
    print('Starting eval...')
    res = evaluate_dual_market()
    print('Done.')
except Exception as e:
    import traceback
    traceback.print_exc()
