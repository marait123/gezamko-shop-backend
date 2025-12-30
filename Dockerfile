FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs /app/media /app/staticfiles

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Run migrations, seed DB, collect static, then start Gunicorn
CMD sh -c "python manage.py migrate && \
           python manage.py seed_database && \
           python manage.py collectstatic --noinput && \
           gunicorn gezamko.wsgi:application --bind 0.0.0.0:8000 --workers 4"
