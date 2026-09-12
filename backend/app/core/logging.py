"""Единый формат логов для API и фоновых задач."""

import logging

_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


class _PlainUvicornName(logging.Filter):
    """Логгер uvicorn называется «uvicorn.error» даже для обычных сообщений о запуске.
    В логах слово error сбивает с толку, поэтому показываем просто «uvicorn»."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name == "uvicorn.error":
            record.name = "uvicorn"
        return True


def setup_logging(level: str) -> None:
    """Настроить корневой логгер один раз. Повторный вызов только меняет уровень."""
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_FORMAT))
        handler.addFilter(_PlainUvicornName())
        root.addHandler(handler)
    root.setLevel(level.upper())
    # Логи uvicorn идут через тот же формат
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True
