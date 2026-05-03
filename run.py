#!/usr/bin/env python3
"""
PharmaSentinel startup script.
Run: python run.py
"""
import subprocess
import sys
import os
import webbrowser
import time
import threading

def check_and_install():
    try:
        import fastapi, uvicorn, sqlalchemy, praw
    except ImportError:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        print("Done.\n")

def open_browser():
    time.sleep(2.5)
    webbrowser.open("http://localhost:8000/frontend/index.html")
    print("\n[PharmaSentinel] Opening dashboard in browser...")

if __name__ == "__main__":
    check_and_install()

    import uvicorn

    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

    # Serve frontend as static files
    sys.path.insert(0, backend_dir)

    # Mount frontend
    from fastapi.staticfiles import StaticFiles
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", os.path.join(backend_dir, "main.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    app = mod.app
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

    threading.Thread(target=open_browser, daemon=True).start()
    print("\n" + "="*50)
    print("  PharmaSentinel — Drug Safety Monitor")
    print("="*50)
    print(f"  API:       http://localhost:8000")
    print(f"  Dashboard: http://localhost:8000/frontend/index.html")
    print(f"  API Docs:  http://localhost:8000/docs")
    print("="*50 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
