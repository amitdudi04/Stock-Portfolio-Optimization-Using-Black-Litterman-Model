import yfinance as yf
import requests

session = requests.Session()
data = yf.download(['AAPL'], start='2022-01-01', end='2026-02-01', session=session, progress=False)
print("Data shape with session:", data.shape)

from yfinance import cache
try:
    print("Cache path:", cache.get_cache_dir())
except Exception as e:
    pass
