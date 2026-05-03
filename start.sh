#!/bin/bash
# PharmaSentinel — One-click start
# Run: ./start.sh

cd "$(dirname "$0")"

echo ""
echo "======================================"
echo "  PharmaSentinel — Drug Safety Monitor"
echo "======================================"

# Install deps if needed
python3 -m pip install fastapi uvicorn sqlalchemy praw python-dotenv httpx -q

# Copy .env if doesn't exist
if [ ! -f "backend/.env" ] && [ -f ".env.example" ]; then
  cp .env.example backend/.env
fi

echo ""
echo "  Dashboard: http://localhost:8000/frontend/index.html"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop"
echo "======================================"
echo ""

# Start server from backend dir (so relative imports work)
cd backend
python3 -c "
import sys, os
sys.path.insert(0, '.')
from fastapi.staticfiles import StaticFiles
from main import app
app.mount('/frontend', StaticFiles(directory='../frontend', html=True), name='frontend')
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000, log_level='warning')
"
