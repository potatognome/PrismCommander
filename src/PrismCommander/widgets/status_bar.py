"""
PrismCommander StatusBar.

Renders a single-line status bar showing:
  - Application name and version
  - Current directory path
  - Number of items in the current listing
  - Available disk space for the active filesystem

Inputs:
    logger    — tUilKit LoggerInterface instance
    path      — optional Path to report status for (default: cwd)
    app_name  — application name string shown in the bar
    version   — version string shown next to the app name

Outputs:
    render()          — prints the status bar line to stdout
    update(path, ...)  — updates status fields and re-renders

Integration points:
    tUilKit: Logger.apply_border, Logger.colour_log
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from tUilKit.interfaces.logger_interface import LoggerInterface


class StatusBar:
    """
    Renders a compact status bar for the PrismCommander application.

    Inputs:
        logger   — tUilKit LoggerInterface for colour output
        path     — directory to report on (default: Path.cwd())
        app_name — name displayed in the bar (default: "PrismCommander")
        version  — version tag displayed next to the name (default: "0.3.0")
    """

    BORDER_PATTERN = {"TOP": "=", "BOTTOM": "=", "LEFT": "|", "RIGHT": "|"}
    FRAME_WIDTH = 72

    def __init__(
        self,
        logger: LoggerInterface,
        path: Optional[Path] = None,
        app_name: str = "PrismCommander",
        version: str = "0.3.0",
    ) -> None:
        self._logger = logger
        self._path = Path(path) if path else Path.cwd()
        self._app_name = app_name
        self._version = version

    def update(
        self,
        path: Optional[Path] = None,
    ) -> None:
        """
        Update the status bar's active path and re-render.

        Inputs:
            path — new directory to report on
        """
        if path is not None:
            self._path = Path(path)
        self.render()

    def render(self) -> None:
        """
        Print the status bar frame to stdout.

        Displays: app name | current path | item count | free disk space.
        """
        item_count = self._count_items()
        free_space = self._free_space_str()

        self._logger.apply_border(
            text=f"  {self._app_name} v{self._version}",
            pattern=self.BORDER_PATTERN,
            total_length=self.FRAME_WIDTH,
            border_rainbow=True,
        )
        self._logger.colour_log(
            "!info", "  Path:",
            "!path", str(self._path),
        )
        self._logger.colour_log(
            "!info", "  Items:", "!int", str(item_count),
            "!info", "   Free:", "!calc", free_space,
        )

    def _count_items(self) -> int:
        """Return the number of entries in the current directory."""
        try:
            return sum(1 for _ in os.scandir(self._path))
        except (PermissionError, FileNotFoundError):
            return 0

    def _free_space_str(self) -> str:
        """Return a human-readable free disk space string for the current path."""
        try:
            usage = shutil.disk_usage(self._path)
            free = usage.free
        except OSError:
            return "?"
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if free < 1024:
                return f"{free:.0f} {unit} free"
            free /= 1024
        return f"{free:.1f} PB free"
