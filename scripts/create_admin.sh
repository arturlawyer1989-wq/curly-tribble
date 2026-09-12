#!/usr/bin/env bash
# Создать сотрудника панели управления или сменить пароль. Работает при запущенном магазине.
# Примеры:
#   ./scripts/create_admin.sh --login owner --name "Артур" --role owner
#   ./scripts/create_admin.sh --login owner --reset-password
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose exec backend python scripts/create_admin.py "$@"
