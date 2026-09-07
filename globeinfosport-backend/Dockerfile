FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements/ ./requirements/
RUN pip install -r requirements/production.txt
COPY . .

FROM base AS development
RUN pip install -r requirements/development.txt
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base AS production
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
