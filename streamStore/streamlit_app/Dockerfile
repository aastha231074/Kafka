FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for caching)
ADD requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

# Copy all frontend files
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]