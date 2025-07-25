"""
Main entry point for the Google AI Studio Proxy
"""

import os
import sys
import subprocess
import uvicorn
from run_proxy import main as run_main

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed")
    except subprocess.CalledProcessError:
        print("✗ Failed to install requirements")

def main():
    """Main function"""
    # Install requirements if needed
    try:
        import fastapi
        import uvicorn
    except ImportError:
        install_requirements()
    
    # Run the proxy
    run_main()

if __name__ == '__main__':
    main()
