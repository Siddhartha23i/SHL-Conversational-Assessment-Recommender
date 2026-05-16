FROM python:3.11-slim

WORKDIR /app

# Install system deps (needed for faiss-cpu)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Pre-built index and catalog must exist in data/ before building image
# Run: python scripts/preprocess.py && python scripts/build_index.py first

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
