# GUI Usage Quick Reference

## How to Use the Portfolio Optimization System GUI

### Step 1: Enter Portfolio Assets
1. In the **Portfolio Setup** tab, enter stock tickers in the input field
2. Format: `AAPL, MSFT, GOOGL` (comma-separated)
3. Example valid tickers:
   - Tech: `AAPL, MSFT, GOOGL, NVDA`
   - Finance: `JPM, BAC, GS`
   - Mixed: `AAPL, MSFT, XOM, JNJ`

### Step 2: Select Date Range
1. Click on **Start Date** calendar icon
2. Select start date (recommend 1-3 years of historical data)
3. Click on **End Date** calendar icon  
4. Select end date (today's date recommended)

### Step 3 (Optional): Add Investor Views
Views are optional! The system works with or without them.

**To add a view:**
1. In "Add Investor View" section, type an asset ticker
2. Set expected return percentage (e.g., 10% means you expect 10% annual return)
3. Set confidence level (0-100%, where 100% = very confident)
4. Click **Add View**
5. Repeat for additional views

**Examples:**
- "I think AAPL will return 15% next year - 80% confident" → AAPL, 15%, 80%
- "MSFT will outperform by 10% - 60% confident" → MSFT, 10%, 60%

### Step 4: Run Optimization
1. Click **Run Optimization** button
2. Wait for progress dialog to complete (usually <2 seconds)
3. Results automatically appear on **Results** tab

### Step 5: View Results
**Results Tab shows:**
- Black-Litterman weights (incorporates your views)
- Markowitz weights (market-based)
- Detailed allocation table
- Visual pie chart

**Risk Analysis Tab shows:**
- Expected annual return
- Volatility (risk)
- Sharpe ratio
- Value-at-Risk (VaR)
- Maximum drawdown

### Step 6: Export Results
**Export to CSV:**
- Click **Export to CSV** button
- Choose save location
- Contains: Tickers and optimal weights

**Export to PDF:**
- Click **Export to PDF** button
- Professional report with:
  - Portfolio configuration
  - Key metrics
  - Allocation table
  - Generated timestamp

---

## Troubleshooting

### "Invalid ticker" Error
✓ Check ticker symbols are valid (e.g., AAPL not APPLE)
✓ Verify ticker is listed on Yahoo Finance
✓ Try single ticker first to test: `AAPL`

### No optimization results appear
✓ Check date range is valid (end date after start date)
✓ Ensure at least 1 year of data is available
✓ Try with fewer assets first (3-5 assets)

### PDF Export fails
✓ Make sure you have write permissions to save location
✓ Try saving to Desktop or Documents folder

### Slow optimization
✓ Normal: first run takes 1-2 seconds
✓ Subsequent runs are faster
✓ Using 5-20 assets is optimal

---

## Tips for Best Results

### Asset Selection
- **Minimum:** 2-3 assets
- **Optimal:** 5-15 assets
- **Maximum:** 20+ (may be slow)
- **Diverse:** Mix different sectors/classes

### Historical Data
- **1 year:** Recent conditions
- **2-3 years:** Includes market cycles (recommended)
- **5+ years:** Includes recovery periods but older data

### Investor Views
- **Realistic:** Expect 5-15% alpha (outperformance)
- **Confident:** Use 70-90% confidence for strong convictions
- **Conservative:** Use 50-70% for moderate views
- **No views:** Leave empty for market-based allocation

### Interpreting Weights
- **0-5%:** Minimal holding (diversification)
- **5-20%:** Core position
- **20%+:** Major concentration bet

---

## Understand the Models

### Black-Litterman (With Views)
Your opinion + Market consensus = Better portfolio
- Combines what markets know with what you believe
- More stable weights than pure theory
- **Best for:** Investors with market insights

### Markowitz (Market-Based)
Pure mathematical optimization
- Based on historical returns and correlations
- No investor opinions included
- **Best for:** Passive/index-based strategies

---

## Example Workflows

### Workflow 1: Basic Optimization (No Views)
```
1. Enter: AAPL, MSFT, GOOGL, AMZN, NVDA
2. Set dates: 2023-01-01 to 2024-12-31
3. Skip views (leave empty)
4. Run optimization
5. Use Markowitz weights (left side)
6. Export to CSV
```

### Workflow 2: Optimization With Convictions
```
1. Enter: AAPL, MSFT, GOOGL, AMZN
2. Set dates: 2022-01-01 to 2024-12-31
3. Add view: AAPL → 12% return, 80% confidence
4. Add view: MSFT → 10% return, 70% confidence
5. Run optimization
6. Use Black-Litterman weights (right side)
7. Export PDF report
```

### Workflow 3: Competitor Analysis
```
1. Enter competitor stocks in your industry
2. Add view for leader, neutral for others
3. Run optimization
4. Compare weights to market cap weights
5. Adjust conviction based on results
```

---

## Key Metrics Explained

| Metric | Meaning | What's Good? |
|--------|---------|--------------|
| Expected Return | Projected annual return | Higher is better |
| Volatility | Risk/standard deviation | Lower is better |
| Sharpe Ratio | Return per unit of risk | Higher is better |
| VaR (95%) | 95% worst-case loss | Less negative is better |
| Max Drawdown | Largest peak-to-trough decline | Less negative is better |

---

## Advanced Tips

### Customize Settings
- Menu → Settings (optional)
- Adjust risk-free rate
- Adjust market risk premium
- Save preferences

### Run Multiple Scenarios
- Save results from different view sets
- Compare outcomes in Excel
- Identify most impactful views

### Use Equal-Weight as Baseline
- Compare your optimized weights to equal-weight
- If similar, maybe reconsider views
- If very different, ensure convictions are strong

---

**Ready to optimize your portfolio?** 🚀

Start with the GUI, enter some assets, and run optimization. The system will guide you through the process!

If you have questions, check the error messages in the console or refer to the USER_MANUAL.md for detailed information.
