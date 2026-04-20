"""
PrismCommander widgets package.

Exports the top-level UI chrome widgets:
  - StatusBar     — one-line status line showing path, counts, and disk usage
  - CommandStrip  — function-key command reference strip
"""

from PrismCommander.widgets.status_bar import StatusBar
from PrismCommander.widgets.command_strip import CommandStrip

__all__ = ["StatusBar", "CommandStrip"]
