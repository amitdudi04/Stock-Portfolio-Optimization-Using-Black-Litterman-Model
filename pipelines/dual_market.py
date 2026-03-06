import os
import pandas as pd
import numpy as np
import logging
import warnings
warnings.filterwarnings('ignore')
from typing import Dict, Any, List, Optional, Tuple

from core.optimizer import BlackLittermanOptimizer
from core.backtester import run_comprehensive_backtest
from core.stress_testing import HistoricalStressTester
from core.robustness import run_tau_sensitivity, run_lambda_sensitivity
from core.soe_private_analysis import run_china_soe_pipeline, run_china_private_pipeline, _hypothesis_tests
from core.statistical_tests import bootstrap_sharpe_diff, jobson_korkie_test

logger = logging.getLogger(__name__)

# 1. Add Chinese Equity Universe (Academic Structure: Pre-2005 Blue Chips)
CHINA_UNIVERSE = {
    "Kweichow Moutai Co., Ltd.": {"ticker": "600519.SS", "sector": "Consumer Staples"},
    "China Vanke Co., Ltd.": {"ticker": "000002.SZ", "sector": "Real Estate"},
    "China Merchants Bank Co., Ltd.": {"ticker": "600036.SS", "sector": "Banking"},
    "Shanghai Pudong Development Bank": {"ticker": "600000.SS", "sector": "Banking"},
    "Gree Electric Appliances, Inc.": {"ticker": "000651.SZ", "sector": "Consumer Discretionary"},
    "Wuliangye Yibin Co., Ltd.": {"ticker": "000858.SZ", "sector": "Consumer Staples"},
    "Jiangsu Hengrui Pharmaceuticals Co., Ltd.": {"ticker": "600276.SS", "sector": "Healthcare"},
    "Wanhua Chemical Group Co., Ltd.": {"ticker": "600309.SS", "sector": "Industrial Materials"}
}

# 2. Add Indian Equity Universe (Academic Structure: Pre-2005 Blue Chips)
INDIA_UNIVERSE = {
    "Reliance Industries": {"ticker": "RELIANCE.NS", "sector": "Energy"},
    "Tata Consultancy Services": {"ticker": "TCS.NS", "sector": "Technology"},
    "HDFC Bank": {"ticker": "HDFCBANK.NS", "sector": "Banking"},
    "Infosys": {"ticker": "INFY.NS", "sector": "Technology"},
    "ICICI Bank": {"ticker": "ICICIBANK.NS", "sector": "Banking"},
    "Hindustan Unilever": {"ticker": "HINDUNILVR.NS", "sector": "Consumer"},
    "ITC Limited": {"ticker": "ITC.NS", "sector": "Consumer"},
    "Larsen & Toubro": {"ticker": "LT.NS", "sector": "Industrial"}
}

china_tickers = [v["ticker"] for v in CHINA_UNIVERSE.values()]
india_tickers = [v["ticker"] for v in INDIA_UNIVERSE.values()]

TICKER_NAME_MAP = {v["ticker"]: k.split(" ")[0] for k, v in CHINA_UNIVERSE.items()}
TICKER_NAME_MAP.update({v["ticker"]: k.split(" ")[0] for k, v in INDIA_UNIVERSE.items()})
TICKER_NAME_MAP.update({'AAPL': 'Apple', 'MSFT': 'Microsoft', 'GOOGL': 'Alphabet', 'AMZN': 'Amazon', 'NVDA': 'NVIDIA'})

TICKER_TO_SECTOR = {v["ticker"]: v["sector"] for v in CHINA_UNIVERSE.values()}
TICKER_TO_SECTOR.update({v["ticker"]: v["sector"] for v in INDIA_UNIVERSE.values()})
TICKER_TO_SECTOR.update({'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Consumer Cyclical', 'NVDA': 'Technology'})


MARKET_CONFIG = {
    "US": {
        "tickers": ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
        "benchmark": '^GSPC',
        "start": '2010-01-01',
        "end": '2025-01-01',
        "stress_train_start": '2005-01-01',
        "stress_train_end": '2007-12-31',
        "stress_test_start": '2008-01-01',
        "stress_test_end": '2009-12-31',
        "stress_tickers": ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
        "views": {'AAPL': 0.12, 'MSFT': 0.10, 'GOOGL': 0.11, 'AMZN': 0.14, 'NVDA': 0.15},
        "confidence": {'AAPL': 0.60, 'MSFT': 0.50, 'GOOGL': 0.40, 'AMZN': 0.45, 'NVDA': 0.65}
    },
    "CHINA": {
        "tickers": china_tickers,
        "benchmark": '000001.SS',
        "start": '2010-01-01',
        "end": '2025-01-01',
        "stress_train_start": '2012-01-01',
        "stress_train_end": '2014-12-31',
        "stress_test_start": '2015-01-01',
        "stress_test_end": '2016-06-30',
        "stress_tickers": china_tickers,
        "views": {t: 0.12 for t in china_tickers},
        "confidence": {t: 0.50 for t in china_tickers}
    },
    "INDIA": {
        "tickers": india_tickers,
        "benchmark": '^BSESN',
        "start": '2010-01-01',
        "end": '2025-01-01',
        "stress_train_start": '2005-01-01',
        "stress_train_end": '2007-12-31',
        "stress_test_start": '2008-01-01',
        "stress_test_end": '2009-12-31',
        "stress_tickers": india_tickers,
        "views": {t: 0.12 for t in india_tickers},
        "confidence": {t: 0.50 for t in india_tickers}
    }
}

def extract_metrics(res_dict: Dict[str, Any], model_key: str) -> Tuple[float, float, float, float, float, float]:
    daily_net = res_dict[model_key]['net']
    ann_ret = daily_net.mean() * 252
    ann_vol = daily_net.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    
    cum_rets = (1 + daily_net).cumprod()
    drawdowns = (cum_rets - cum_rets.cummax()) / cum_rets.cummax()
    max_dd = drawdowns.min()
    
    var_95 = np.percentile(daily_net, 5)
    cvar_95 = daily_net[daily_net <= var_95].mean()
    
    turnover = res_dict.get('turnover', {}).get(model_key, [])
    avg_turnover = np.mean(turnover) if len(turnover) > 0 else 0.0
    
    return ann_ret, ann_vol, sharpe, max_dd, cvar_95, avg_turnover

def run_market_pipeline(market_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"[{market_name}] COMMENCING EMPIRICAL PIPELINE EVALUATION")
    
    opt = BlackLittermanOptimizer(
        config["tickers"], 
        config["start"], 
        config["end"], 
        use_market_cap_weights=True
    )
    
    # Apply dynamic UI Parameter overrides before calculating
    if "tau_override" in config:
        opt.tau = float(config["tau_override"])
    if "lambda_override" in config:
        opt.lambda_risk = float(config["lambda_override"])
    
    # We also apply frictionless override if passed (for base backtest)
    fric_val = float(config.get("trade_cost_override", 0.001))
    rebal_freq = int(config.get("rebalance_days_override", 63))
    
    logger.info(f"Synthesizing Baseline Cross-Model Allocation (Tau={opt.tau}, Lam={opt.lambda_risk})...")
    baseline_comparison = opt.compare_models(config["views"], config["confidence"])
    
    logger.info("Launching Frictional Rolling Backtest...")
    bt_results, _, _ = run_comprehensive_backtest(
        opt, 
        config["views"], 
        transaction_cost=fric_val, 
        rebalance_freq=rebal_freq
    )
    
    bl_ret, bl_vol, bl_sharpe, bl_dd, bl_cvar, bl_turn = extract_metrics(bt_results, 'black_litterman')
    mw_ret, mw_vol, mw_sharpe, mw_dd, mw_cvar, mw_turn = extract_metrics(bt_results, 'markowitz')
    
    if config["benchmark"] == '^GSPC':
        bench_key = 'sp500'
    elif config["benchmark"] in ['000001.SS', '399300.SZ']:
        bench_key = 'csi300'
    else:
        bench_key = 'sensex'
        
    bench_returns = bt_results[bench_key]
    bench_ann_ret = bench_returns.mean() * 252
    bench_ann_vol = bench_returns.std() * np.sqrt(252)
    bench_cum = (1 + bench_returns).cumprod()
    bench_dd = ((bench_cum - bench_cum.cummax()) / bench_cum.cummax()).min()
    bench_sharpe = bench_ann_ret / bench_ann_vol if bench_ann_vol > 0 else 0
    
    bl_active = bt_results['black_litterman']['net'] - bench_returns
    mw_active = bt_results['markowitz']['net'] - bench_returns
    
    bl_ir = (bl_active.mean() * 252) / (bl_active.std() * np.sqrt(252)) if bl_active.std() > 0 else 0
    mw_ir = (mw_active.mean() * 252) / (mw_active.std() * np.sqrt(252)) if mw_active.std() > 0 else 0
    
    logger.info("Running Robustness Sensitivity Checks...")
    df_tau = run_tau_sensitivity(opt, config["views"], config["confidence"], tau_values=[0.01, 0.2])
    df_lambda = run_lambda_sensitivity(opt, config["views"], config["confidence"], lambda_values=[1.5, 4.0])
    
    logger.info(f"Executing Deep Stress Crisis Regime ({config['stress_test_start']} to {config['stress_test_end']})...")
    tester = HistoricalStressTester(
        config["stress_tickers"],
        train_start=config["stress_train_start"],
        train_end=config["stress_train_end"],
        test_start=config["stress_test_start"],
        test_end=config["stress_test_end"],
        benchmark=config["benchmark"]
    )
    s_views = {t: config["views"][t] for t in config["stress_tickers"]}
    s_conf = {t: config["confidence"][t] for t in config["stress_tickers"]}
    tester.run_training_phase(s_views, s_conf)
    tester.run_stress_test()
    
    return {
        "baseline": baseline_comparison,
        "backtest_series": {
            "bl_cum": (1 + bt_results['black_litterman']['net']).cumprod(),
            "mw_cum": (1 + bt_results['markowitz']['net']).cumprod(),
            "bench_cum": bench_cum
        },
        "performance": {
            "bl_ret": bl_ret, "bl_vol": bl_vol, "bl_sharpe": bl_sharpe, "bl_dd": bl_dd, "bl_cvar": bl_cvar, "bl_turn": bl_turn, "bl_ir": bl_ir,
            "mw_ret": mw_ret, "mw_vol": mw_vol, "mw_sharpe": mw_sharpe, "mw_dd": mw_dd, "mw_cvar": mw_cvar, "mw_turn": mw_turn, "mw_ir": mw_ir,
            "bench_ret": bench_ann_ret, "bench_vol": bench_ann_vol, "bench_sharpe": bench_sharpe, "bench_dd": bench_dd
        },
        "stress": tester.results,
        "tau": df_tau,
        "lambda": df_lambda,
        "daily_returns": {
            "bl_net": bt_results['black_litterman']['net'],
            "mw_net": bt_results['markowitz']['net']
        }
    }

def generate_cross_market_summary(all_results: Dict[str, Any]) -> pd.DataFrame:
    records = []
    for market, data in all_results.items():
        perf = data["performance"]
        records.extend([
            {
                "Market": market, "Model": "Black-Litterman",
                "Annualized Net Return": f"{perf['bl_ret']*100:.2f}%",
                "Annualized Volatility": f"{perf['bl_vol']*100:.2f}%",
                "Sharpe Ratio": f"{perf['bl_sharpe']:.3f}",
                "Information Ratio": f"{perf['bl_ir']:.3f}",
                "Max Drawdown": f"{perf['bl_dd']*100:.2f}%",
                "Average Turnover": f"{perf['bl_turn']*100:.2f}%"
            },
            {
                "Market": market, "Model": "Markowitz",
                "Annualized Net Return": f"{perf['mw_ret']*100:.2f}%",
                "Annualized Volatility": f"{perf['mw_vol']*100:.2f}%",
                "Sharpe Ratio": f"{perf['mw_sharpe']:.3f}",
                "Information Ratio": f"{perf['mw_ir']:.3f}",
                "Max Drawdown": f"{perf['mw_dd']*100:.2f}%",
                "Average Turnover": f"{perf['mw_turn']*100:.2f}%"
            },
            {
                "Market": market, "Model": "Benchmark",
                "Annualized Net Return": f"{perf['bench_ret']*100:.2f}%",
                "Annualized Volatility": f"{perf['bench_vol']*100:.2f}%",
                "Sharpe Ratio": f"{perf['bench_sharpe']:.3f}",
                "Information Ratio": "N/A",
                "Max Drawdown": f"{perf['bench_dd']*100:.2f}%",
                "Average Turnover": "N/A"
            }
        ])
    return pd.DataFrame(records)

def generate_structural_analysis(all_results: Dict[str, Any]) -> pd.DataFrame:
    records = []
    has_us = "US" in all_results
    has_cn = "CHINA" in all_results
    has_in = "INDIA" in all_results
    
    models = ['black_litterman', 'markowitz']
    
    for model in models:
        mkey = "bl_" if model == 'black_litterman' else "mw_"
        
        row_vol = {"Structural Metric": f"Average Realized Volatility ({model})"}
        row_turn = {"Structural Metric": f"Average Turnover Constraints ({model})"}
        row_spike = {"Structural Metric": f"Stress-Test Volatility Spike Multiple ({model})"}
        row_dd = {"Structural Metric": f"Max Crisis Drawdown ({model})"}
        row_rec = {"Structural Metric": f"Crisis Recovery Duration ({model})"}

        if has_us:
            row_vol["US Market"] = f"{all_results['US']['performance'][mkey+'vol']*100:.2f}%"
            row_turn["US Market"] = f"{all_results['US']['performance'][mkey+'turn']*100:.2f}%"
            row_spike["US Market"] = f"{all_results['US']['stress'][model]['Volatility Spike (x)']:.2f}x (2008)"
            row_dd["US Market"] = f"{all_results['US']['stress'][model]['Max Drawdown']*100:.2f}% (2008)"
            row_rec["US Market"] = f"{all_results['US']['stress'][model]['Max Underwater Days']} days"

        if has_cn:
            row_vol["China Market"] = f"{all_results['CHINA']['performance'][mkey+'vol']*100:.2f}%"
            row_turn["China Market"] = f"{all_results['CHINA']['performance'][mkey+'turn']*100:.2f}%"
            row_spike["China Market"] = f"{all_results['CHINA']['stress'][model]['Volatility Spike (x)']:.2f}x (2015)"
            row_dd["China Market"] = f"{all_results['CHINA']['stress'][model]['Max Drawdown']*100:.2f}% (2015)"
            row_rec["China Market"] = f"{all_results['CHINA']['stress'][model]['Max Underwater Days']} days"

        if has_in:
            row_vol["India Market"] = f"{all_results['INDIA']['performance'][mkey+'vol']*100:.2f}%"
            row_turn["India Market"] = f"{all_results['INDIA']['performance'][mkey+'turn']*100:.2f}%"
            row_spike["India Market"] = f"{all_results['INDIA']['stress'][model]['Volatility Spike (x)']:.2f}x (2008)"
            row_dd["India Market"] = f"{all_results['INDIA']['stress'][model]['Max Drawdown']*100:.2f}% (2008)"
            row_rec["India Market"] = f"{all_results['INDIA']['stress'][model]['Max Underwater Days']} days"

        records.extend([row_vol, row_turn, row_spike, row_dd, row_rec])
        
    return pd.DataFrame(records)

def evaluate_dual_market(custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    logger.info("EMPIRICAL EVALUATION ENGINE: US DEVELOPED, CHINA & INDIA EMERGING")
    
    config = custom_config if custom_config else MARKET_CONFIG
    all_results = {}
    for market_name, cfg in config.items():
        all_results[market_name] = run_market_pipeline(market_name, cfg)
        
    summary_df = generate_cross_market_summary(all_results)
    structural_df = generate_structural_analysis(all_results)
    
    # 1. Add China Structural Ownership Study if China was run
    soe_study = None
    if "CHINA" in all_results:
        logger.info("Running parallel China SOE vs Private Sub-Study...")
        # To run the pipelines we need raw prices. For simplicity in the GUI orchestrator, 
        # we can fetch the prices or pass the cached prices from the optimizer. 
        # The optimizer for CHINA is not saved globally here, so we will download the data once.
        import yfinance as yf
        from core.ownership_classification import SOE_TICKERS, PRIVATE_TICKERS
        all_cn_tickers = list(set(SOE_TICKERS + PRIVATE_TICKERS))
        
        try:
            data = yf.download(all_cn_tickers, start=config["CHINA"]["start"], end=config["CHINA"]["end"], auto_adjust=True, progress=False)
            
            if isinstance(data.columns, pd.MultiIndex):
                level_0 = data.columns.get_level_values(0)
                level_1 = data.columns.get_level_values(1)
                if "Adj Close" in level_0:
                    prices = data["Adj Close"]
                elif "Close" in level_0:
                    prices = data["Close"]
                elif "Adj Close" in level_1:
                    prices = data.xs("Adj Close", axis=1, level=1)
                elif "Close" in level_1:
                    prices = data.xs("Close", axis=1, level=1)
                else:
                    raise ValueError(f"No valid price column for {all_cn_tickers}")
            else:
                if "Adj Close" in data.columns:
                    prices = data["Adj Close"]
                elif "Close" in data.columns:
                    prices = data["Close"]
                else:
                    raise ValueError(f"No valid price column for {all_cn_tickers}")
            
            assert prices.shape[0] > 0, "Downloaded DataFrame is empty (rows)"
            assert prices.shape[1] > 0, "Downloaded DataFrame is empty (columns)"
            
            missing_soe = [t for t in SOE_TICKERS if t not in prices.columns]
            missing_private = [t for t in PRIVATE_TICKERS if t not in prices.columns]
            print("China DF shape:", prices.shape)
            print("SOE tickers missing:", missing_soe)
            print("Private tickers missing:", missing_private)
            
            soe_res = run_china_soe_pipeline(prices, start_date=config["CHINA"]["start"], end_date=config["CHINA"]["end"], tc_rate=config["CHINA"].get("trade_cost_override", 0.001))
            priv_res = run_china_private_pipeline(prices, start_date=config["CHINA"]["start"], end_date=config["CHINA"]["end"], tc_rate=config["CHINA"].get("trade_cost_override", 0.001))
            
            assert len(soe_res.get('returns', pd.DataFrame()).columns) > 0 if isinstance(soe_res.get('returns'), pd.DataFrame) else True, "Empty SOE returns subset"
            assert len(priv_res.get('returns', pd.DataFrame()).columns) > 0 if isinstance(priv_res.get('returns'), pd.DataFrame) else True, "Empty Private returns subset"
            
            tests = _hypothesis_tests(soe_res, priv_res)
            soe_study = {
                "soe": soe_res,
                "private": priv_res,
                "tests": tests
            }
        except Exception as e:
            logger.error(f"Failed to run SOE sub-study: {e}")
            raise e

    # 2. Add Formal Statistical Validation (Bootstrap P-Values) for BL vs MW
    statistical_tests = {}
    for market_name, m_res in all_results.items():
        try:
            bl_net = m_res["daily_returns"]["bl_net"]
            mw_net = m_res["daily_returns"]["mw_net"]
            
            # Align indices
            common = bl_net.index.intersection(mw_net.index)
            r_A = bl_net.loc[common]
            r_B = mw_net.loc[common]
            
            p_boot = bootstrap_sharpe_diff(r_A, r_B, n_bootstrap=1000)[1]
            p_jk = jobson_korkie_test(r_A, r_B)['p_value']
            
            statistical_tests[market_name] = {
                "bootstrap_p": p_boot,
                "jobson_korkie_p": p_jk
            }
        except Exception as e:
            logger.error(f"Failed to run stats for {market_name}: {e}")
    
    return {
        "raw_results": all_results,
        "summary_df": summary_df,
        "structural_df": structural_df,
        "soe_study": soe_study,
        "statistical_tests": statistical_tests
    }
