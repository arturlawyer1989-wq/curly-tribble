"""Создать сотрудника панели управления или сменить ему пароль.

Примеры:
  python scripts/create_admin.py --login owner --name "Артур" --role owner
  python scripts/create_admin.py --login owner --reset-password
Пароль спрашивается в консоли; можно передать через переменную окружения ADMIN_NEW_PASSWORD.
"""

import argparse
import asyncio
import getpass
import os
import sys

from sqlalchemy import select

from app.core.db import dispose_engine, get_session_factory
from app.core.security import hash_password
from app.models.admin import AdminUser
from app.models.enums import ADMIN_ROLES
from app.services.admin_auth import create_admin_user


def read_password() -> str:
    password = os.environ.get("ADMIN_NEW_PASSWORD", "")
    if not password:
        password = getpass.getpass("Пароль (не короче 8 символов): ")
        confirm = getpass.getpass("Повторите пароль: ")
        if password != confirm:
            print("Пароли не совпадают", file=sys.stderr)
            sys.exit(2)
    if len(password) < 8:
        print("Пароль слишком короткий: нужно не меньше 8 символов", file=sys.stderr)
        sys.exit(2)
    return password


async def run(args: argparse.Namespace) -> int:
    async with get_session_factory()() as session:
        user = await session.scalar(select(AdminUser).where(AdminUser.login == args.login.strip().lower()))
        if user is not None and not args.reset_password:
            print(f"Сотрудник с логином «{user.login}» уже есть. Чтобы сменить пароль, добавьте --reset-password", file=sys.stderr)
            return 1
        password = read_password()
        if user is None:
            user = await create_admin_user(session, login=args.login, password=password, full_name=args.name, role=args.role)
            await session.commit()
            print(f"Создан сотрудник «{user.login}» с ролью {user.role}")
        else:
            user.password_hash = hash_password(password)
            user.is_active = True
            await session.commit()
            print(f"Пароль сотрудника «{user.login}» обновлён")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Сотрудники панели управления")
    parser.add_argument("--login", required=True, help="логин для входа, латиницей")
    parser.add_argument("--name", default="", help="имя, как показывать в панели")
    parser.add_argument("--role", default="owner", choices=ADMIN_ROLES, help="владелец или менеджер")
    parser.add_argument("--reset-password", action="store_true", help="сменить пароль существующему сотруднику")
    args = parser.parse_args()
    sys.exit(asyncio.run(_wrapped(args)))


async def _wrapped(args: argparse.Namespace) -> int:
    try:
        return await run(args)
    finally:
        await dispose_engine()


if __name__ == "__main__":
    main()
