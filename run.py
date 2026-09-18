#!/usr/bin/env python3
"""Switcheroo launcher script."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from switcheroo.app import main

if __name__ == "__main__":
    main()
