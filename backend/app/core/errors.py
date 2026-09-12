"""Обработка ошибок: покупатель всегда видит понятное русское сообщение, а не технический текст."""

import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

# Сообщения для стандартных HTTP-ошибок
STATUS_MESSAGES: dict[int, tuple[str, str]] = {
    400: ("bad_request", "Запрос составлен неверно. Обновите страницу и попробуйте снова."),
    401: ("unauthorized", "Нужно войти, чтобы выполнить это действие."),
    403: ("forbidden", "У вас нет доступа к этому действию."),
    404: ("not_found", "Такой страницы или данных нет. Возможно, ссылка устарела."),
    405: ("method_not_allowed", "Этот способ запроса не поддерживается."),
    409: ("conflict", "Данные уже изменились. Обновите страницу и повторите действие."),
    413: ("too_large", "Файл слишком большой."),
    429: ("too_many_requests", "Слишком много запросов. Подождите минуту и попробуйте снова."),
    503: ("unavailable", "Сервис временно недоступен. Попробуйте через несколько минут."),
}
GENERIC_MESSAGE = "На сайте произошла ошибка, мы уже знаем о ней. Обновите страницу или позвоните нам."

# Сообщения для ошибок заполнения полей по типу ошибки Pydantic
FIELD_MESSAGES: dict[str, str] = {
    "missing": "Обязательное поле",
    "string_too_short": "Слишком короткое значение",
    "string_too_long": "Слишком длинное значение",
    "string_type": "Ожидается текст",
    "int_parsing": "Ожидается целое число",
    "int_type": "Ожидается целое число",
    "float_parsing": "Ожидается число",
    "greater_than_equal": "Значение слишком маленькое",
    "less_than_equal": "Значение слишком большое",
    "bool_parsing": "Ожидается «да» или «нет»",
    "enum": "Недопустимое значение",
    "literal_error": "Недопустимое значение",
    "json_invalid": "Неверный формат данных",
    "value_error": "Неверное значение",
}


def error_body(code: str, message: str, **extra: object) -> dict[str, object]:
    """Единый формат тела ошибки: {"error": {"code": ..., "message": ...}}."""
    return {"error": {"code": code, "message": message, **extra}}


def _field_name(loc: tuple[int | str, ...]) -> str:
    # Убираем служебные части пути вроде body / query
    parts = [str(p) for p in loc if p not in ("body", "query", "path", "header", "cookie")]
    return ".".join(parts) or "body"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code, default_message = STATUS_MESSAGES.get(exc.status_code, ("error", GENERIC_MESSAGE))
        # Стандартную английскую фразу («Not Found», «Method Not Allowed») заменяем на русскую.
        # Если же код специально передал своё понятное сообщение, показываем его.
        try:
            english_phrase = HTTPStatus(exc.status_code).phrase
        except ValueError:
            english_phrase = ""
        if isinstance(exc.detail, dict) and "message" in exc.detail:
            # Код и сообщение заданы явно, например {"code": "session_expired", "message": "..."}
            code = str(exc.detail.get("code", code))
            message = str(exc.detail["message"])
        else:
            custom = isinstance(exc.detail, str) and exc.detail and exc.detail != english_phrase and exc.status_code < 500
            message = exc.detail if custom else default_message
        return JSONResponse(status_code=exc.status_code, content=error_body(code, message), headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        fields = [
            {"field": _field_name(tuple(err.get("loc", ()))), "message": FIELD_MESSAGES.get(str(err.get("type")), "Неверное значение")}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_body("validation_error", "Проверьте правильность заполнения полей.", fields=fields),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Необработанная ошибка на %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(status_code=500, content=error_body("server_error", GENERIC_MESSAGE))
