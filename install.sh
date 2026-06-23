#!/usr/bin/env bash
# Beats PM Kit installer.
# Usage:
#   git clone https://github.com/officebeats/beats-pm-kit
#   cd beats-pm-kit
#   ./install.sh

set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
  :
else
  echo "Python 3 is required. Install Python 3, then rerun ./install.sh." >&2
  exit 1
fi

python3 system/scripts/bootstrap.py --non-interactive "$@"
