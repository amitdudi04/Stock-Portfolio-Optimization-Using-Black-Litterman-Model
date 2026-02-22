import platformdirs
import shutil
import os
import yfinance as yf

for name in ["yfinance", "requests-cache", "requests_cache"]:
    try:
        path = platformdirs.user_cache_dir(name)
        if os.path.exists(path):
            print(f"Deleting {path}")
            shutil.rmtree(path)
            print("Deleted")
    except Exception as e:
        print(f"Error deleting {name}: {e}")

# test again
print("Testing yfinance download after cleanup")
data = yf.download("AAPL", start="2022-01-01", end="2026-02-01", progress=False)
print("Data shape:", data.shape)
if not data.empty:
    print("Success! Columns:", data.columns.tolist())
else:
    print("Failed")
