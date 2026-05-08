#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

cat <<'EOS'

Virtual environment created at .venv
Activate it with:
  source .venv/bin/activate

Deactivate with:
  deactivate
EOS
