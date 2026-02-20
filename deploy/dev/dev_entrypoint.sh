#!/usr/bin/env bash
set -euo pipefail

# абсолютный путь к самому скрипту (с учётом симлинков)
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

# поднимаемся на два уровня вверх (из deploy/tests → в корень проекта)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export ENVIRONMENT_SLUG=dev

echo "Running from: $(pwd)"

exec poetry run uvicorn src.mount:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level debug
