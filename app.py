from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portfolio_optimization.models.black_litterman import BlackLittermanOptimizer

app = FastAPI(title="Black-Litterman Portfolio Intelligence UI")

# Mount frontend static directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class OptimizationRequest(BaseModel):
    tickers: List[str]
    start_date: str
    end_date: str
    views: Dict[str, float]
    confidence: Dict[str, float]

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

@app.get("/about")
async def read_about():
    return FileResponse('frontend/about.html')

@app.post("/api/optimize")
async def optimize_portfolio(req: OptimizationRequest):
    try:
        # 1. Initialize mathematical optimizer
        optimizer = BlackLittermanOptimizer(
            req.tickers, 
            req.start_date, 
            req.end_date
        )
        
        # 2. Run both models and extract arrays
        # (Compare models automatically outputs Markowitz and Equal Weights for benchmarking alongside the BL results)
        results = optimizer.compare_models(req.views, req.confidence)
        
        # 3. Clean up generic numpy structures so FastAPI can serialize to JSON for the web frontend
        def numpy_to_native(d: dict) -> dict:
            clean = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    clean[k] = numpy_to_native(v)
                elif hasattr(v, 'tolist'):
                    clean[k] = v.tolist()
                elif hasattr(v, 'item'):
                    clean[k] = v.item()
                else:
                    clean[k] = v
            return clean

        return {"status": "success", "data": numpy_to_native(results)}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    print("🚀 Running Black-Litterman Portfolio Web Intelligence Engine")
    print("🌍 Navigate to: http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
