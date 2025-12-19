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

# Copy the entire app folder
COPY app/ ./app

EXPOSE 5000

CMD ["python", "-m", "app.py"]

