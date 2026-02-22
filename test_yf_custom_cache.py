import yfinance as yf
import os

custom_cache = "g:\\stock portfolio\\my_yf_cache"
if not os.path.exists(custom_cache):
    os.makedirs(custom_cache)

try:
    yf.set_tz_cache_location(custom_cache)
    print("Set custom cache location to", custom_cache)
except AttributeError:
    print("set_tz_cache_location not found")

try:
    data = yf.download(['AAPL'], start='2022-01-01', end='2026-02-01', progress=False)
    print("Data shape:", data.shape)
    if not data.empty:
        print("Success! Columns:", data.columns.tolist())
    else:
        print("Failed to download")
except Exception as e:
    print("Exception:", e)
