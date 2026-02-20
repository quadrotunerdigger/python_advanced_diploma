# Этап 1: Базовый образ с зависимостями
FROM python:3.11-slim as base

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Этап 2: Установка Python зависимостей
FROM base as dependencies

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt


# Этап 3: Production образ
FROM dependencies as production

# Создаём непривилегированного пользователя
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Копируем код приложения
COPY --chown=appuser:appgroup ./app ./app
COPY --chown=appuser:appgroup ./migrations ./migrations
COPY --chown=appuser:appgroup ./alembic.ini .

# Создаём директорию для медиафайлов
RUN mkdir -p /app/static/media && chown -R appuser:appgroup /app/static

# Переключаемся на непривилегированного пользователя
USER appuser

# Порт приложения
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Запуск приложения
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


# Этап 4: Development образ (опционально)
FROM dependencies as development

# Копируем dev зависимости
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Копируем весь проект включая тесты
COPY . .

# Создаём директорию для медиафайлов
RUN mkdir -p /app/static/media

# Запуск с hot-reload для разработки
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]