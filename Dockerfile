FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    POETRY_VERSION=2.1.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PATH="/opt/poetry/bin:$PATH"

RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev \
        postgresql-dev \
    && pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-ansi

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python scripts/migrate.py && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
