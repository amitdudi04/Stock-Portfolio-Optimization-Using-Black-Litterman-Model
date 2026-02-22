import os
import glob

appdata = os.environ.get('LOCALAPPDATA', '')
print(f"Searching in {appdata}")

# Use glob to find sqlite files in yfinance directories
for root, dirs, files in os.walk(appdata):
    if 'yfinance' in root.lower() or 'pytickerscache' in root.lower() or 'cache' in root.lower():
        for f in files:
            if f.endswith('.sqlite') or f.endswith('.db'):
                if 'yfinance' in root.lower() or 'pytickerscache' in root.lower() or 'yfinance' in f.lower():
                    filepath = os.path.join(root, f)
                    print(f"Found cache db: {filepath}")
                    try:
                        os.remove(filepath)
                        print(f"Deleted {filepath}")
                    except Exception as e:
                        print(f"Failed to delete {filepath}: {e}")
