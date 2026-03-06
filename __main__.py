import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(__file__))

# Enable module running capabilities
if __name__ == "__main__":
    print("=========================================================================")
    print(" EMPIRICAL EVALUATION ENGINE: US DEVELOPED, CHINA & INDIA EMERGING")
    print("=========================================================================")
    print("Starting Professional Quantitative Research Platform GUI...")
    from ui.desktop_gui import launch_desktop_gui
    launch_desktop_gui()
