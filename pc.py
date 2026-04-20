#!/usr/bin/env python
"""
pc.py
Convenience entry point for running PrismCommander from the project root.
Handles module path setup automatically.
"""

import sys
import os
from pathlib import Path

# Add src to path so PrismCommander can be imported as a module
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import PrismCommander.main
PrismCommander.main.main()
