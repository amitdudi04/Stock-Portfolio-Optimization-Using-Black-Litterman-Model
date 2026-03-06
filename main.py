import sys
import logging

# Configure root logger to output engine info locally if needed
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    from ui.desktop_gui import launch_desktop_gui
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"\n[ERROR] Failed to load the Quantitative Research Platform GUI.")
    print(f"Details: {e}")
    print("\nPlease ensure all dependencies are installed.")
    print("If the error is about a missing module, install it via pip (e.g., pip install <module_name>)")
    sys.exit(1)

if __name__ == "__main__":
    print("=========================================================================")
    print(" EMPIRICAL EVALUATION ENGINE: US DEVELOPED, CHINA & INDIA EMERGING")
    print("=========================================================================")
    print("Starting Professional Quantitative Research Platform GUI...")
    launch_desktop_gui()
