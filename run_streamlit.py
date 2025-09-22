"""
Run Streamlit Dashboard
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit dashboard"""
    print("Starting Streamlit Dashboard...")
    print("=" * 40)
    
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Streamlit is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Run streamlit app
    streamlit_app_path = os.path.join(os.path.dirname(__file__), "streamlit_app.py")
    
    if os.path.exists(streamlit_app_path):
        print(f"Launching Streamlit app: {streamlit_app_path}")
        subprocess.run([sys.executable, "-m", "streamlit", "run", streamlit_app_path])
    else:
        print(f"Streamlit app not found at: {streamlit_app_path}")
        print("Please make sure streamlit_app.py exists in the project root.")

if __name__ == "__main__":
    main()

