FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy praw python-dotenv httpx

COPY backend/ ./backend/
COPY frontend/ ./frontend/

WORKDIR /app/backend

RUN python3 -c "
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
from database import SessionLocal
from main import _seed_database
db = SessionLocal()
_seed_database(db)
db.close()
print('DB seeded')
"

EXPOSE 8000

CMD ["python3", "-c", "
import sys, os
sys.path.insert(0, '.')
from fastapi.staticfiles import StaticFiles
from main import app
app.mount('/frontend', StaticFiles(directory='../frontend', html=True), name='frontend')
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000, log_level='warning')
"]
