# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY app/requirements.txt .

# Install python dependencies
RUN pip install --upgrade pip && \
    pip install \
    --default-timeout=300 \
    --retries 10 \
    --no-cache-dir \
    -r requirements.txt

# Install gunicorn for production
RUN pip install gunicorn

# Copy the entire app folder
COPY app/ ./app

# Lets add a health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app.app:app"]

