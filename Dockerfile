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
RUN pip install --default-timeout=200 --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the entire app folder
COPY app/ ./

EXPOSE 5000

CMD ["python", "app.py"]

