"""Схемы панели управления: вход, сотрудник, сводка."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=200)


class AdminUserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    full_name: str
    role: str
    is_active: bool
    last_login_at: datetime | None


class LoginResponse(BaseModel):
    user: AdminUserPublic
    access_expires_at: datetime


class OverviewSection(BaseModel):
    key: str
    title: str
    count: int


class OverviewResponse(BaseModel):
    sections: list[OverviewSection]
    orders_by_status: dict[str, int]
