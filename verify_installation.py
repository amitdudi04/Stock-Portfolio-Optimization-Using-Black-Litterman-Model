#!/usr/bin/env python3
"""
Installation Verification Script
===================================

Verifies that all required packages are installed and working.
"""

import sys

def verify_packages():
    """Verify all required packages are installed."""
    
    packages = {
        'pandas': 'Data manipulation',
        'numpy': 'Numerical computing',
        'scipy': 'Scientific computing',
        'matplotlib': 'Plotting library',
        'seaborn': 'Statistical visualization',
        'yfinance': 'Financial data API',
        'streamlit': 'Web dashboard framework',
        'fastapi': 'REST API framework',
        'uvicorn': 'ASGI server',
        'plotly': 'Interactive charts',
        'sqlalchemy': 'Database ORM',
    }
    
    print("\n" + "="*70)
    print("PORTFOLIO OPTIMIZATION PROJECT - INSTALLATION VERIFICATION")
    print("="*70 + "\n")
    
    failed = []
    success = []
    
    for package_name, description in packages.items():
        try:
            module = __import__(package_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"[OK] {package_name:20s} - {version:15s} {description}")
            success.append(package_name)
        except Exception as e:
            error_msg = str(e)[:50]  # Truncate long errors
            print(f"[ERROR] {package_name:20s} - {error_msg}")
            failed.append((package_name, error_msg))
    
    print("\n" + "="*70)
    
    if failed:
        print(f"INSTALLATION INCOMPLETE: {len(failed)} package(s) failed\n")
        for pkg, error in failed:
            print(f"  - {pkg}: {error}")
        return False
    else:
        print(f"SUCCESS: All {len(success)} required packages installed!\n")
        print("Your project is ready to use:")
        print("\n1. STREAMLIT DASHBOARD (Interactive Web UI):")
        print("   Command: streamlit run dashboard.py")
        print("   Opens:   http://localhost:8501")
        print("\n2. FASTAPI BACKEND (REST API with Swagger docs):")
        print("   Command: python api.py")
        print("   Opens:   http://localhost:8000/docs")
        print("\n3. FULL ANALYSIS (Command-line execution):")
        print("   Command: python main.py")
        print("\n" + "="*70)
        print("NO ADDITIONAL SETUP REQUIRED - Ready for deployment! 🚀")
        print("="*70 + "\n")
        return True


if __name__ == "__main__":
    success = verify_packages()
    sys.exit(0 if success else 1)
