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

EXPOSE 5000

# Start the Flask development server. For production consider using gunicorn.
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
