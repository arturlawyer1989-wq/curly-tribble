# Образ бэкенда: FastAPI и Celery на Python 3.12
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Зависимости ставятся отдельным слоем: при изменении кода они не пересобираются.
# Секрет proxy_ca нужен только при сборке в закрытой сети через прокси; при обычной сборке его нет и шаг идёт как есть.
COPY requirements.txt ./
RUN --mount=type=secret,id=proxy_ca,required=false \
    sh -c 'if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; pip install -r requirements.txt'

COPY . .
RUN chmod +x scripts/*.sh \
    && useradd --create-home --uid 10001 app \
    && chown -R app:app /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 CMD ["python", "-m", "app.healthcheck"]
CMD ["scripts/start-api.sh"]
