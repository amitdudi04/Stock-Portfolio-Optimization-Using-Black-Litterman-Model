# Regime-Sensitive Black–Litterman Tri-Market Portfolio Allocation Study

**Author:** Amit Kumar Dudi  

## Project Overview
This repository hosts a professional quantitative research pipeline investigating the out-of-sample stability of the Black-Litterman Bayesian allocation framework operating across the United States, China, and India markets. Built for explicit academic reproducibility, the system architecture completely decouples theoretical mathematical models from chronological data manipulation, frictional simulations, and structural statistical validations.

## Research Motivation
Classical unconstrained mean-variance optimization models frequently exhibit severe structural vulnerability out-of-sample due to inherent estimation error maximization and instability during macroeconomic regime transitions. This research system computationally refines and implements a transaction-cost-aware Bayesian asset allocation strategy mapping specifically to emerging markets, further incorporating an isolated empirical sub-study evaluating Chinese State-Owned Enterprises (SOEs) versus Private entities during deep systemic crises.

## Methodology Overview
To bypass forward-looking estimation bias, out-of-sample execution operates strictly utilizing continuous 252-day expanding windows. Mathematical matrices integrate Ledoit-Wolf shrinkage to resolve sample covariance singularity. Unpenalized dynamic allocation decay is evaluated explicitly utilizing an $L_1$-norm **Allocation Stability Index (ASI)**. The statistical engine natively bounds performance distributions internally utilizing Circular Block Bootstrapped confidence testing alongside decoupled Markov Regime Detection arrays.

## Research Pipeline Diagram

```text
Market Data
     ↓
Return Calculation
     ↓
Covariance Estimation (Ledoit–Wolf)
     ↓
Black–Litterman Optimization
     ↓
Rolling Backtest
     ↓
Transaction Cost Adjustment
     ↓
Allocation Stability Index
     ↓
Regime Detection
     ↓
Factor Regression
     ↓
Robustness Testing
     ↓
Results Export
```

## Repository Structure
* `config/`: Central YAML configuration files establishing reproducibility and universal environment arrays.
* `core/`: Base mathematical transformations (data loading, return calculations, matrix shrinkage).
* `models/`: Foundational Black-Litterman and Markowitz theoretical optimization engines.
* `backtesting/`: Frictional environments, rolling out-of-sample execution sequences, and transaction cost modeling.
* `analysis/`: Cross-sectional analytical sweeps including SOE structural comparisons, Markov regime detections, and Ken French factor regressions.
* `pipelines/`: Central orchestration macros mapping specific workflows deterministically.
* `experiments/`: Parameter arrays executing sequential structural boundaries (`tau` scalar sensitivities).
* `results/v1_final_results/`: Designated static export repository mapping exactly to the `.docx` final academic validations.
* `visualization/`: Visual hooks rendering Sharpe decay overlays and probabilistic continuous regime distributions.
* `tests/`: Modular validation architecture.
* `docs/`: Master architectural and finalized compendium methodologies.
* `legacy/`: Complete archival trace of the historical deprecated monolithic scripts.

## Execution Instructions
Before initiating the pipelines, ensure all environmental dependencies are strictly met utilizing Python 3.10+.

```bash
pip install -r requirements.txt
```

To fully regenerate the baseline Tri-Market optimization bounds and empirical regime evaluations:
```bash
python pipelines/run_tri_market_pipeline.py
```

To reconstruct the explicit mathematical boundaries of the Bayesian scalar across independent validation runs:
```bash
python experiments/run_tau_sensitivity.py
```

## Key Results Summary
* **Bayesian Stabilization (ASI)**: The Black-Litterman optimization demonstrated statistically significant advantages regarding structural turnover mitigation and out-of-sample absolute drawdown compression. Portfolio stability was measured utilizing the Allocation Stability Index (ASI)—the average L1 norm distance between consecutive weight vectors. Black–Litterman structurally reduced ASI because Bayesian shrinkage stabilizes expected return estimates over continuous rebalancing.
* **Emerging Market Crisis Frictions**: During the 2020 India Covid dislocation, the Black-Litterman array registered a volatility spike of 0.91x (below unity). This indicates that realized volatility during the crisis window was not higher than the preceding training period, which frequently occurs in emerging markets when crisis dynamics are transmitted through severe liquidity contractions rather than volatility expansions.
* **Structural Ownership Insulation**: The empirical sub-study isolated during the 2015 Chinese liquidity contraction definitively rejected institutional heuristics; Chinese SOEs structurally failed to supply asymmetric downside isolation comparatively against their Private cohort.
* **Regime Conditional Superiority**: Conditional variance modeling via two-state Markov Switching verified Black-Litterman allocations distinctly outperform during high-uncertainty regimes. This occurs precisely due to Bayesian shrinkage anchoring estimates when historical sample variance explodes unpredictably.
* **Fama-French Validation**: Evaluating the out-of-sample data against the Fama-French 4-factor model confirmed that optimization performance is dominated by systematic factor exposure (market beta) rather than pure unobserved alpha ($\alpha \approx 0$).

## Study Limitations
The empirical generalizations presented heavily rely on formalized boundary assumptions. ETF proxies operate as investable baseline representations but inherently suffer from dividend reinvestment friction differences. Frictional constraints heavily utilize linear transaction cost simplifications (0.10%), which do not accurately map the variable illiquidity gaps observed during outright crisis regimes. Structural inferences are also inherently restricted by market microstructure differences across US, Chinese, and Indian clearing operations, alongside sample selection constraints within developing index arrays.

## Visualization Examples
Upon pipeline execution, continuous statistical distributions render natively into `visualization/`:
- `rolling_sharpe.png`: A continuous 252-day lagging stability evaluation.
- `drawdown_comparison.png`: Absolute peak-to-trough systemic loss contours.
- `asi_stability.png`: Aggregated daily $L_1$-norm allocation shifts.
- `tau_sensitivity.png`: Granular Bayesian scalar elasticity measurements.
- `regime_probabilities.png`: Filtered and smoothed Markov market states.
- `regime_performance_comparison.png`: A segmented cross-sectional structural Sharpe analysis.

## Reproducibility Instructions
To universally recreate the documentation tables, raw statistics, and empirical conclusions highlighted within the *Final Research Results Compendium*, identically execute the primary configuration (`config/project_config.yaml`). The framework’s decoupled internal memory guarantees 100% deterministic outputs across identical CPU footprints sequentially executing `run_tri_market_pipeline.py`.
