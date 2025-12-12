FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=vehicles \
    FLASK_ENV=production

WORKDIR /app

# Install runtime deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY . /app

# Ensure instance folder exists
RUN mkdir -p /app/instance

# Gunicorn will listen on port 8000; Nginx (separate container) will proxy on 80
EXPOSE 8000

# Run Gunicorn (production WSGI server)
CMD ["gunicorn", "vehicles:create_app()", "--bind", "0.0.0.0:8000", "--workers", "3"]
