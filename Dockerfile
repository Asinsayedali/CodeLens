FROM python:3.11-slim

WORKDIR /app

# git is needed by GitPython when cloning repos for analysis
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source + pre-seeded database
COPY backend/ /app/

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
