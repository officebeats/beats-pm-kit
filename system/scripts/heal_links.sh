#!/bin/bash

# Beats PM Kit - Runtime adapter healing
# Keeps .agent/ canonical and regenerates local ignored adapters.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Regenerating local runtime adapters from .agent/..."
python3 system/scripts/sync_cli_adapters.py
echo "Runtime adapters are synchronized."
