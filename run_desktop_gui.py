#!/usr/bin/env python3
"""
Launch Desktop GUI Application
==============================

Standalone PyQt5 desktop application for Black-Litterman portfolio optimization.

Usage:
    python run_desktop_gui.py

Features:
    • Configure portfolio assets and date range
    • Specify investor views and confidence levels
    • Run Black-Litterman optimization
    • View detailed risk metrics
    • Compare with Markowitz model
    • Export results to CSV/Excel
"""

import sys
import os

# Add portfolio_optimization to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_optimization.gui import PortfolioGUI
from PyQt5.QtWidgets import QApplication


def main():
    """Launch the desktop GUI application."""
    
    print("\n" + "="*70)
    print("Portfolio Optimization System - Desktop GUI")
    print("Black-Litterman Model")
    print("="*70 + "\n")
    
    try:
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = PortfolioGUI()
        window.show()
        
        print("✓ Desktop application launched successfully")
        print("  Window: Portfolio Optimization System (PyQt5)")
        print("\n  Features:")
        print("  • Configure portfolio assets")
        print("  • Specify investor views")
        print("  • Run optimization")
        print("  • Analyze results")
        print("  • Export to CSV/Excel\n")
        
        sys.exit(app.exec_())
    
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
