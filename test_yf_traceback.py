import yfinance as yf
import traceback

try:
    data = yf.download(['AAPL'], start='2022-01-01', end='2026-02-01', progress=False)
except Exception as e:
    traceback.print_exc()
