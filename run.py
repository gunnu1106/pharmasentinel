#!/usr/bin/env python3
"""
PharmaSentinel startup script for Render Deployment.
"""
import os
import sys
import threading
import time
import importlib.util
from fastapi.staticfiles import StaticFiles

# --- PATH CONFIGURATION ---
# Base directory of the project
base_dir = os.path.dirname(__file__)
backend_dir = os.path.join(base_dir, "backend")
frontend_dir = os.path.join(base_dir, "frontend")

# Ensure backend is in the python path for imports
sys.path.insert(0, backend_dir)

# --- APP INITIALIZATION (Visible to Gunicorn) ---
try:
    # Dynamically load the 'app' from backend/main.py
    spec = importlib.util.spec_from_file_location("main", os.path.join(backend_dir, "main.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    app = mod.app # This is what Gunicorn looks for

    # Mount frontend static files
    # Access via: https://your-app.onrender.com/frontend/index.html
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")
except Exception as e:
    print(f"Error loading application: {e}")
    # Fallback to prevent crash if main.py isn't found during build
    from fastapi import FastAPI
    app = FastAPI()

# --- LOCAL RUN LOGIC ---
def open_browser():
    """Only used for local development"""
    import webbrowser
    time.sleep(2.5)
    print("\n[PharmaSentinel] Opening dashboard...")
    webbrowser.open("http://localhost:8000/frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*50)
    print("  PharmaSentinel — Drug Safety Monitor")
    print("="*50)
    
    # Start browser thread for local use
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
