ARG PYTHON_VERSION=3.13.7
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# PYTHONPATH musi widzieć /app, bo tam trafi biblioteka
ENV PYTHONPATH="/app"

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Instalujemy zależności (z pliku lokalnego w API)
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY --from=lib . /app/image_processing/

COPY . /app/API/


USER appuser
EXPOSE 8000

# Startujemy z folderu /app/API
CMD ["gunicorn", "--chdir", "/app/API", "app.main:api", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]