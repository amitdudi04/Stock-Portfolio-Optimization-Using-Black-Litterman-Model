# Desktop GUI - PyQt5 Application

## Overview

Professional PyQt5 desktop application for Black-Litterman portfolio optimization. A native Windows/Mac/Linux GUI for portfolio management without needing to use web browsers.

## Features

### 1. Portfolio Configuration Tab
- ✅ Asset selection (multiple tickers)
- ✅ Historical date range specification
- ✅ Real-time data download from Yahoo Finance
- ✅ One-click optimization

### 2. Investor Views Tab
- ✅ Add/remove investor views dynamically
- ✅ Specify expected returns and confidence levels
- ✅ Interactive table interface
- ✅ Pre-filled example views

### 3. Results Tab
- ✅ Portfolio weight visualization
- ✅ Key metrics (Expected Return, Volatility, Sharpe Ratio, VaR)
- ✅ Metric cards with formatting
- ✅ Export to CSV/Excel

### 4. Analysis Tab
- ✅ Black-Litterman vs Markowitz comparison
- ✅ 20+ risk metrics detailed breakdown
- ✅ Model performance analysis
- ✅ Insights and recommendations

### 5. Advanced Settings
- ✅ Fine-tune Black-Litterman parameters (TAU, Lambda)
- ✅ Risk metrics customization (VaR level)
- ✅ Portfolio constraints
- ✅ Default values

## Quick Start

### Launch the Desktop App

```bash
python run_desktop_gui.py
```

This opens a native PyQt5 window with the full portfolio optimization interface.

### Basic Workflow

1. **Configure Portfolio**
   - Enter tickers (e.g., `AAPL,MSFT,GOOGL,AMZN,NVDA`)
   - Set date range
   - Click "Run Optimization"

2. **Specify Views** (Optional)
   - Go to "Investor Views" tab
   - Add your bullish/bearish views
   - Set confidence levels (0-1)
   - Views update optimization

3. **Review Results**
   - Switch to "Results" tab
   - View recommended portfolio weights
   - See key metrics

4. **Analyze**
   - Go to "Analysis" tab
   - Compare with Markowitz
   - Review detailed risk metrics
   - Export results

## GUI Components

### Main Window (`main_window.py`)

```python
class PortfolioGUI(QMainWindow):
    """Main GUI window with 4 tabs."""
    
    def __init__(self):
        # Initialize UI
    
    def create_config_tab(self):
        # Portfolio configuration
    
    def create_views_tab(self):
        # Investor view specification
    
    def create_results_tab(self):
        # Display optimization results
    
    def create_analysis_tab(self):
        # Risk analysis and comparison
    
    def run_optimization(self):
        # Run in background thread
```

### Background Worker (`main_window.py`)

```python
class OptimizationWorker(QThread):
    """Background thread for optimization."""
    
    def run(self):
        # Initialize BlackLittermanOptimizer
        # Download data from Yahoo Finance
        # Run optimization
        # Emit results signal
```

### Advanced Settings Dialog (`settings_dialog.py`)

```python
class AdvancedSettingsDialog(QDialog):
    """Advanced parameter tuning."""
    
    def __init__(self):
        # TAU parameter
        # Lambda (risk aversion)
        # VaR confidence level
        # Risk-free rate
        # Portfolio constraints
```

## System Requirements

- **Python 3.8+**
- **PyQt5** (automatically installed)
- **4GB RAM minimum**
- **Windows/Mac/Linux**

## Technical Architecture

### Thread Model
- Main thread: UI responsiveness
- Worker thread: Optimization calculations
- Non-blocking: UI stays responsive during long operations

### Integration
- Built on `portfolio_optimization` package
- Uses `BlackLittermanOptimizer` from models
- Leverages `RiskMetricsCalculator` for analysis
- Integrates `PortfolioVisualizer` plotting utilities

### Data Flow
```
Config Input
    ↓
Portfolio Configuration
    ↓
YahooFinance Download
    ↓
BlackLittermanOptimizer
    ↓
RiskMetricsCalculator
    ↓
Results Display
    ↓
Export to CSV/Excel
```

## Advanced Features

### 1. Real-time Optimization
- Background worker thread
- Progress dialog
- Non-blocking UI
- Status bar updates

### 2. Model Comparison
- Black-Litterman weights
- Markowitz weights
- Side-by-side comparison
- Performance metrics

### 3. Risk Analysis
- 20+ metrics calculated
- Detailed breakdown
- Tail risk measures
- Distribution analysis

### 4. Export Functionality
- CSV export
- Excel export
- Multiple sheets
- Professional formatting

## Configuration

### Default Parameters

Located in `portfolio_optimization/config/settings.py`:

```python
# Default assets
TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']

# Black-Litterman
TAU = 0.05          # Uncertainty parameter
LAMBDA_RISK = 2.5   # Risk aversion

# Risk metrics
RISK_FREE_RATE = 0.03
VAR_LEVEL = 0.95
```

### Customize in GUI

- Advanced Settings button (in toolbar)
- Adjust TAU, Lambda, VaR level
- Toggle short-selling
- Set weight constraints
- Save as defaults

## Example Usage

### Portfolio Optimization Step-by-Step

1. **Launch**
   ```bash
   python run_desktop_gui.py
   ```

2. **Configure** (Tab 1)
   - Assets: AAPL, MSFT, GOOGL, AMZN, NVDA
   - Period: 2021-01-01 to today
   - Click "Run Optimization"

3. **Add Views** (Tab 2)
   - AAPL: 12% return, 60% confidence
   - MSFT: 10% return, 50% confidence
   - NVDA: 15% return, 65% confidence

4. **Review Results** (Tab 3)
   - See recommended weights
   - View Sharpe Ratio
   - Export to CSV

5. **Analyze** (Tab 4)
   - Compare with Markowitz
   - Review risk metrics
   - Get insights

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'PyQt5'"
**Solution:**
```bash
pip install PyQt5 PyQt5-sip
```

### Issue: Data download fails
**Solution:**
- Check internet connection
- Verify ticker symbols (e.g., AAPL, not APPLE)
- Ensure date range is valid
- Check: https://finance.yahoo.com

### Issue: Optimization takes too long
**Solution:**
- Reduce number of assets (5-10 optimal)
- Shorter historical period
- Check system resources

### Issue: GUI window doesn't appear
**Solution:**
```bash
# Run with explicit Python interpreter
python run_desktop_gui.py

# Or with python3
python3 run_desktop_gui.py
```

## Performance

| Operation | Time |
|-----------|------|
| Launch GUI | <1 second |
| Download data (5 assets, 3 years) | 5-10 seconds |
| Run optimization | 1-3 seconds |
| Display results | <1 second |
| Export to CSV | <1 second |

## Styling

Professional dark-themed interface:
- Blue accent color (#0066cc)
- Clean, modern design
- High contrast, accessible
- Responsive layout
- Cross-platform fonts

## File Organization

```
portfolio_optimization/gui/
├── __init__.py              # Module initialization
├── main_window.py           # Main GUI window (520+ lines)
└── settings_dialog.py       # Advanced settings dialog (120+ lines)

run_desktop_gui.py           # Launcher script
```

## Future Enhancements

### Planned Features
- ✓ Dark mode toggle
- ✓ Chart visualization (matplotlib embedded)
- ✓ Portfolio comparison charts
- ✓ Backtesting visualization
- ✓ Drag-drop asset weights
- ✓ Scenario analysis
- ✓ Report generation
- ✓ Settings persistence
- ✓ Multi-portfolio management

### Potential Integrations
- Database persistence
- Real-time price updates
- Email alerts
- Integration with brokers (API)
- Mobile synchronization

## API Reference

### Launch Application

```python
python run_desktop_gui.py
```

### Programmatic Usage

```python
from PyQt5.QtWidgets import QApplication
from portfolio_optimization.gui import PortfolioGUI

app = QApplication([])
window = PortfolioGUI()
window.show()
app.exec_()
```

### Access Results

```python
# After optimization, access results via:
window.last_results  # Dictionary with all metrics
```

## Comparison: UI Options

| Feature | Desktop GUI | Streamlit | FastAPI |
|---------|------------|-----------|---------|
| Type | Desktop | Web | API |
| Launch | Native window | Browser | Server |
| Installation | Python package | Streamlit | FastAPI |
| Learning curve | 30 mins | 15 mins | 60 mins |
| Complexity | Advanced | Simple | Intermediate |
| Best for | Power users | Data scientists | Developers |
| Data storage | CSV/Excel | Session | Database |

## Support

For issues or questions:
1. Check [TROUBLESHOOTING](#troubleshooting) section
2. Review code comments in `main_window.py`
3. Check GitHub issues
4. Review the main [README_MASTER.md](../../README_MASTER.md)

## Version

- **Desktop GUI v2.0**
- **Python 3.8+**
- **PyQt5 5.15.x**
- **Compatible**: Windows, macOS, Linux

---

**Enjoy your professional portfolio optimization workflow!** 📊
