import os
import sys
import subprocess

# Get correct path to app.py
base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
app_file = os.path.join(base_path, "app.py")

# Run Streamlit in a subprocess (so the exe doesn’t exit)
subprocess.run(f'streamlit run "{app_file}"', shell=True)
