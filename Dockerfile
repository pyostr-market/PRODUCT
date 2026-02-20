# syntax=docker/dockerfile:1.7

############################
# 1️⃣ Base image
############################
FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=2.2.1

WORKDIR /code

############################
# Builder stage
############################
FROM base AS builder

# системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    ca-certificates \
    libmagic1 \
    libmagic-mgc \
 && rm -rf /var/lib/apt/lists/*

# установка poetry с кешем pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "poetry==$POETRY_VERSION"

# копируем только файлы зависимостей (важно для кеша)
COPY pyproject.toml poetry.lock ./

# установка зависимостей
RUN --mount=type=cache,target=/root/.cache/pip \
    poetry config virtualenvs.create false \
 && poetry install \
      --no-interaction \
      --no-ansi \
      --no-root \
      --without dev


############################
# Runtime stage
############################
FROM base AS runtime

# только runtime пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libmagic-mgc \
    curl \
 && rm -rf /var/lib/apt/lists/*


# копируем установленные пакеты из builder
COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /usr/local/bin /usr/local/bin

# создаём пользователя (без root)
RUN useradd -m appuser
USER appuser

WORKDIR /code

# копируем проект
COPY --chown=appuser:appuser . .

# права на скрипты
RUN chmod +x /code/deploy/prod/*.sh

EXPOSE 8001

