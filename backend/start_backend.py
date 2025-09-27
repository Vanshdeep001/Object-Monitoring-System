#!/usr/bin/env python3
"""
Simple script to start the FastAPI backend server
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Object Monitoring System Backend...")
    print("=" * 50)
    
    # Use current directory as backend directory
    backend_dir = os.path.dirname(__file__)
    
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        return
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn are installed")
    except ImportError:
        print("❌ FastAPI or Uvicorn not installed. Installing requirements...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], cwd=backend_dir)
    
    # Start the server
    print("🌐 Starting server on http://localhost:8000")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws")
    print("📚 API docs: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        # Run the FastAPI server
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
