"""Проверка для Docker: отвечает ли API. Код выхода 0 означает «жив».

Запуск: python -m app.healthcheck
"""

import sys
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/api/v1/health"


def main() -> int:
    try:
        with urllib.request.urlopen(URL, timeout=4) as response:
            return 0 if response.status == 200 else 1
    except urllib.error.HTTPError as exc:
        # 503 значит, что API отвечает, но база или Redis недоступны: сам контейнер живой
        return 0 if exc.code == 503 else 1
    except Exception:  # noqa: BLE001 - любая другая ошибка означает, что API не отвечает
        return 1


if __name__ == "__main__":
    sys.exit(main())
