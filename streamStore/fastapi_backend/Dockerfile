FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for caching)
ADD requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

# Copy all files from fastapi_backend.py folder
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]