# Use official lightweight Python image
FROM python:3.11-slim

WORKDIR /app

# copy only requirements first for cache efficiency
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY app/ ./app

# use env
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=5000

EXPOSE 5000

# run using gunicorn for production-like environment
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.app:app"]
