import yfinance as yf
data = yf.download(['AAPL'], start='2022-01-01', end='2026-02-01', progress=False)
print("Data shape:", data.shape)
if not data.empty:
    print("Columns:", data.columns.tolist())
else:
    print("Data is empty")
