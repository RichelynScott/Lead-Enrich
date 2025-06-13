#!/usr/bin/env python3
"""
Quick script to start the Python backend server.
"""

import subprocess
import sys
import os

def main():
    print("🔥 Starting Fire Enrich Python Backend...")
    print("📍 Advanced CrewAI multi-agent system")
    print("🚀 Starting server on http://127.0.0.1:8000")
    print()
    
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if virtual environment should be activated
    if os.path.exists('venv') or os.path.exists('.venv'):
        print("💡 Tip: Make sure your virtual environment is activated!")
        print("   Run: source venv/bin/activate  # or source .venv/bin/activate")
        print()
    
    try:
        # Start the FastAPI server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "src.api_server:app", 
            "--reload", 
            "--port", "8000",
            "--host", "127.0.0.1"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        print()
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set environment variables in .env file:")
        print("   OPENAI_API_KEY=your_key_here")
        print("   FIRECRAWL_API_KEY=your_key_here")
        print("3. Check if port 8000 is available")
        sys.exit(1)

if __name__ == "__main__":
    main()