FROM python:3.12-slim-bookworm

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    PIP_REQUESTS_TIMEOUT=1200 \
    POETRY_REQUESTS_TIMEOUT=1200 \
    POETRY_VERSION=1.8.2 \
    PATH="/home/work/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-cache --no-root

COPY prism /app/prism

CMD ["python3", "-m", "prism.app"]
