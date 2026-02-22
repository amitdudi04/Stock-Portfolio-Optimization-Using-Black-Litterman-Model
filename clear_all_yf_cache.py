import os
import shutil

cache_dirs = [
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'yfinance'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'pytickerscache'),
    os.path.expanduser('~/.cache/yfinance'),
    os.path.expanduser('~/.cache/pytickerscache'),
    os.path.join(os.environ.get('APPDATA', ''), 'yfinance'),
    os.path.join(os.environ.get('APPDATA', ''), 'Local', 'yfinance')
]

found = False
for d in cache_dirs:
    if d and os.path.exists(d):
        print(f"Found cache dir: {d}")
        found = True
        try:
            shutil.rmtree(d)
            print(f"Successfully deleted {d}")
        except Exception as e:
            print(f"Failed to delete {d}: {e}")

if not found:
    print("No cache dirs found!")
