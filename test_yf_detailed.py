import yfinance as yf
import requests
import traceback

print("Trying with requests.Session()")
try:
    session = requests.Session()
    # Mocking a normal user agent might help if Yahoo is blocking
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    data = yf.download(['AAPL'], start='2022-01-01', end='2026-02-01', session=session, progress=False)
    print("Data shape:", data.shape)
except Exception as e:
    traceback.print_exc()

import appdirs
import os
try:
    print("Cache dir:", appdirs.user_cache_dir("pytickerscache"))
    print("YF Cache dir:", appdirs.user_cache_dir("yfinance"))
except Exception as e:
    pass

import platform
print("Platform:", platform.platform())
