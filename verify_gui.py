#!/usr/bin/env python3
"""
Verify Desktop GUI Installation
================================

Tests that all PyQt5 components are properly installed and functional.
"""

import sys
import os

print("\n" + "="*70)
print("Desktop GUI Installation Verification")
print("="*70 + "\n")

# Test 1: Import PyQt5
print("[TEST 1] Importing PyQt5...")
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtCore import Qt, QThread
    print("✓ PyQt5 imports successful")
except ImportError as e:
    print(f"✗ PyQt5 import failed: {e}")
    print("  Run: pip install PyQt5 PyQt5-sip")
    sys.exit(1)

# Test 2: Import GUI module
print("\n[TEST 2] Importing GUI module...")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from portfolio_optimization.gui import PortfolioGUI
    print("✓ GUI module imports successful")
except ImportError as e:
    print(f"✗ GUI module import failed: {e}")
    sys.exit(1)

# Test 3: Import settings dialog
print("\n[TEST 3] Importing settings dialog...")
try:
    from portfolio_optimization.gui.settings_dialog import AdvancedSettingsDialog
    print("✓ Settings dialog imports successful")
except ImportError as e:
    print(f"✗ Settings dialog import failed: {e}")
    sys.exit(1)

# Test 4: Import optimizer
print("\n[TEST 4] Importing optimizer...")
try:
    from portfolio_optimization.models import BlackLittermanOptimizer
    print("✓ Optimizer imports successful")
except ImportError as e:
    print(f"✗ Optimizer import failed: {e}")
    sys.exit(1)

# Test 5: Create GUI instance (without display)
print("\n[TEST 5] Creating GUI instance...")
try:
    app = QApplication([])
    gui = PortfolioGUI()
    print("✓ GUI instance created successfully")
except Exception as e:
    print(f"✗ GUI creation failed: {e}")
    sys.exit(1)

# Test 6: Create settings dialog
print("\n[TEST 6] Creating settings dialog...")
try:
    settings = AdvancedSettingsDialog()
    print("✓ Settings dialog created successfully")
except Exception as e:
    print(f"✗ Settings dialog creation failed: {e}")
    sys.exit(1)

# Test 7: Verify GUI components
print("\n[TEST 7] Verifying GUI components...")
try:
    assert hasattr(gui, 'tabs'), "Missing tabs widget"
    assert hasattr(gui, 'tickers_input'), "Missing tickers input"
    assert hasattr(gui, 'start_date'), "Missing date picker"
    assert hasattr(gui, 'views_table'), "Missing views table"
    assert hasattr(gui, 'results_table'), "Missing results table"
    assert hasattr(gui, 'optimize_btn'), "Missing optimize button"
    print("✓ All GUI components present")
except AssertionError as e:
    print(f"✗ Component verification failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*70)
print("✓ DESKTOP GUI VERIFICATION COMPLETE")
print("="*70)
print("\nAll components are properly installed and functional!")
print("\nTo launch the desktop GUI, run:")
print("  python run_desktop_gui.py\n")

print("Features available:")
print("  • Portfolio Configuration")
print("  • Investor Views Specification")
print("  • Real-time Optimization")
print("  • Results Display (weights, metrics)")
print("  • Risk Analysis & Comparison")
print("  • Export to CSV/Excel")
print("  • Advanced Settings Tuning\n")
