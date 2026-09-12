# Образ бэкенда: FastAPI и Celery на Python 3.12. Сборка в два этапа:
# на первом ставятся зависимости, во второй попадает только готовое, без кеша pip.
FROM python:3.12-slim AS builder
# Таймаут побольше: PyPI из России бывает медленным
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1 PIP_DEFAULT_TIMEOUT=60
WORKDIR /build
COPY requirements.txt ./
# Секрет proxy_ca нужен только при сборке в закрытой сети через прокси; при обычной сборке его нет и шаг идёт как есть.
RUN --mount=type=secret,id=proxy_ca,required=false \
    sh -c 'if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; pip install --prefix=/install -r requirements.txt'

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN chmod +x scripts/*.sh \
    && useradd --create-home --uid 10001 app \
    && chown -R app:app /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 CMD ["python", "-m", "app.healthcheck"]
CMD ["scripts/start-api.sh"]
