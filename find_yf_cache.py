import yfinance
print(yfinance.__file__)
import os
import sqlite3

# find all sqlite3 files created recently or with yfinance in the path
home = os.environ.get('USERPROFILE', '')
appdata = os.environ.get('LOCALAPPDATA', '')

def find_sqlite(base):
    if not os.path.exists(base): return
    for root, dirs, files in os.walk(base):
        if 'yfinance' in root.lower() or 'pytickerscache' in root.lower() or 'yahoo' in root.lower():
            for f in files:
                print(os.path.join(root, f))

find_sqlite(appdata)

try:
    import platformdirs
    print("platformdirs:", platformdirs.user_cache_dir("yfinance"))
except Exception as e:
    print(e)
