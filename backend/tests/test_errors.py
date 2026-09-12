"""Ошибки API отдаются в едином формате с русскими сообщениями."""

import pytest
from fastapi import APIRouter
from httpx import AsyncClient
from pydantic import BaseModel, Field

from app.main import app


class _Payload(BaseModel):
    name: str
    qty: int = Field(ge=1)


_router = APIRouter(prefix="/api/v1/_test")


@_router.post("/validate")
async def _validate(payload: _Payload) -> dict[str, str]:
    return {"ok": payload.name}


@_router.get("/boom")
async def _boom() -> None:
    raise RuntimeError("секретная техническая подробность")


@pytest.fixture(scope="module", autouse=True)
def _test_routes() -> None:
    """Тестовые маршруты нужны, чтобы проверить обработчики ошибок на реальном приложении."""
    app.include_router(_router)


async def test_unknown_route_returns_russian_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/nothing-here")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert "нет" in body["error"]["message"]
    assert "Not Found" not in body["error"]["message"]


async def test_method_not_allowed_is_russian(client: AsyncClient) -> None:
    response = await client.post("/api/v1/health")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"
    assert "Method" not in response.json()["error"]["message"]


async def test_validation_error_lists_fields(client: AsyncClient) -> None:
    response = await client.post("/api/v1/_test/validate", json={"qty": 0})
    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "validation_error"
    fields = {item["field"]: item["message"] for item in body["fields"]}
    assert fields["name"] == "Обязательное поле"
    assert fields["qty"] == "Значение слишком маленькое"


async def test_validation_error_on_broken_json(client: AsyncClient) -> None:
    response = await client.post("/api/v1/_test/validate", content=b"{oops", headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


async def test_unhandled_error_hides_details(client: AsyncClient) -> None:
    response = await client.get("/api/v1/_test/boom")
    assert response.status_code == 500
    body = response.json()["error"]
    assert body["code"] == "server_error"
    assert "секретная" not in response.text
    assert "Traceback" not in response.text
