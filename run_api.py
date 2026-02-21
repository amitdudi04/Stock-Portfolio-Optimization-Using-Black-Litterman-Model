#!/usr/bin/env python3
"""
Run FastAPI Backend Server
===========================

RESTful API with interactive Swagger documentation.

Usage:
    python run_api.py

Opens: http://localhost:8000/docs (Swagger UI)
       http://localhost:8000/redoc (ReDoc)
"""

import subprocess
import sys


def main():
    """Run the FastAPI server."""
    
    print("\n" + "="*70)
    print("Starting Portfolio Optimization API Server")
    print("="*70)
    print("\nAPI Server documentation available at:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("  - Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Run FastAPI with Uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "portfolio_optimization.api.server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\nAPI server stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting API server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
