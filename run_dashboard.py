#!/usr/bin/env python3
"""
Run Streamlit Dashboard
=======================

Interactive web UI for portfolio optimization.

Usage:
    python run_dashboard.py

Opens: http://localhost:8501
"""

import subprocess
import sys
import os


def main():
    """Run the Streamlit dashboard."""
    
    print("\n" + "="*70)
    print("Starting Portfolio Optimization Dashboard")
    print("="*70)
    print("\nStreamlit server will open at: http://localhost:8501")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "portfolio_optimization/frontend/dashboard.py",
            "--logger.level=error"
        ])
    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
