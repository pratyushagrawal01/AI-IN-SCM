import subprocess
import webbrowser
import time
import os
import sys

print("🚀 Starting Contract Bot...")

# Kill old streamlit
os.system("taskkill /f /im streamlit.exe >nul 2>&1")

# Start streamlit
cmd = [sys.executable, "-m", "streamlit", "run", "chat.py", "--server.headless=true"]
process = subprocess.Popen(cmd)

time.sleep(3)
webbrowser.open("http://localhost:8501")

print("✅ Browser opened! Close this window to stop.")
input("Press Enter to stop...")