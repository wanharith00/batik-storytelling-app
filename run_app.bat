import os
import sys
import subprocess

print("Starting Batik Storytelling Platform...")
print("Opening at: http://localhost:8501")

# Install requirements if needed
try:
    import streamlit
    import PIL
    from gtts import gTTS
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "pillow", "gtts"])

# Run Streamlit
os.system("streamlit run batik_web_app.py")