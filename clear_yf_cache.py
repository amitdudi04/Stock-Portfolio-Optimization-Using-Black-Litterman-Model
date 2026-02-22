import os
import shutil

cache_dirs = [
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'yfinance'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'pytickerscache')
]

for d in cache_dirs:
    if os.path.exists(d):
        print(f"Found {d}")
        try:
            shutil.rmtree(d)
            print("Successfully deleted")
        except Exception as e:
            print(f"Failed to delete {d}: {e}")
