#!/usr/bin/env python3
"""Compatibility wrapper for the Beats PM Kit bootstrap backend."""

from __future__ import annotations

import sys

from system.scripts.bootstrap import main


if __name__ == "__main__":
    raise SystemExit(main())
