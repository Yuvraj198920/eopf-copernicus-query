# Copernicus Query Web App - Dockerfile
# For deploying on Railway, Render, or any Docker platform

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY copernicus_query_app.py .
COPY .streamlit .streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the app
ENTRYPOINT ["streamlit", "run", "copernicus_query_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
