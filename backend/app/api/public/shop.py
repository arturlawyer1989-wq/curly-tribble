"""Публичные данные магазина для шапки, подвала и контактов."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.schemas.shop import ShopPublic
from app.services.shop import defaults_from_settings, get_shop

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Магазин"])


@router.get("/shop", response_model=ShopPublic, summary="Реквизиты и контакты магазина")
async def read_shop(session: AsyncSession = Depends(get_session)) -> ShopPublic:
    shop = await get_shop(session)
    if shop is None:
        # Строка появляется при первом запуске; до этого витрина работает на значениях из .env
        logger.warning("Настройки магазина ещё не созданы, отдаём значения по умолчанию")
        return ShopPublic(**defaults_from_settings(get_settings()))
    return ShopPublic.model_validate(shop)
