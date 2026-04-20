"""
PrismCommander OpsPane.

Provides a file-operation menu for the currently selected path:
  copy, move, delete, rename, and mkdir.

All destructive operations require confirmation via CLIMenuHandler.confirm().
All actions are logged through the tUilKit Logger.

Inputs:
    logger       — tUilKit LoggerInterface instance
    menu_handler — tUilKit CLIMenuInterface instance
    target       — optional Path to operate on (can be set later)

Outputs:
    render()     — prints the OpsPane menu frame to stdout
    run()        — runs the interactive operations loop; returns control
                   when the user selects 'back'

Integration points:
    tUilKit: Logger.apply_border, Logger.colour_log,
             CLIMenuHandler.show_numbered_menu, CLIMenuHandler.confirm,
             CLIMenuHandler.prompt_with_default
"""

import shutil
import os
from pathlib import Path
from typing import Optional

from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.interfaces.cli_menu_interface import CLIMenuInterface


class OpsPane:
    """
    Renders and drives a file-operations menu for a target path.

    Inputs:
        logger       — tUilKit LoggerInterface for colour output and logging
        menu_handler — tUilKit CLIMenuInterface for interactive prompts
        target       — Path to operate on (may be None)
    """

    TITLE = "Operations"
    BORDER_PATTERN = {"TOP": "=", "BOTTOM": "=", "LEFT": "|", "RIGHT": "|"}
    FRAME_WIDTH = 72

    _MENU_OPTIONS = [
        {"key": "copy",   "label": "Copy",              "icon": "📋"},
        {"key": "move",   "label": "Move / Rename",     "icon": "✂️ "},
        {"key": "delete", "label": "Delete",             "icon": "🗑️ "},
        {"key": "mkdir",  "label": "New Directory",      "icon": "📁"},
    ]

    def __init__(
        self,
        logger: LoggerInterface,
        menu_handler: CLIMenuInterface,
        target: Optional[Path] = None,
    ) -> None:
        self._logger = logger
        self._menu = menu_handler
        self._target: Optional[Path] = Path(target) if target else None

    @property
    def target(self) -> Optional[Path]:
        """The path currently targeted for operations."""
        return self._target

    @target.setter
    def target(self, path: Optional[Path]) -> None:
        self._target = Path(path) if path else None

    def render(self) -> None:
        """
        Print the OpsPane header frame showing the current target path.
        """
        target_str = str(self._target) if self._target else "(none)"
        self._logger.apply_border(
            text=f"  {self.TITLE}  —  {target_str}",
            pattern=self.BORDER_PATTERN,
            total_length=self.FRAME_WIDTH,
            border_rainbow=True,
        )
        for opt in self._MENU_OPTIONS:
            self._logger.colour_log("!list", f"  {opt['icon']}  {opt['label']}")

    def run(self) -> None:
        """
        Launch the interactive file-operations menu loop.

        Continues prompting until the user selects 'back' or 'quit'.
        Each operation confirms before execution and logs the result.
        """
        while True:
            self.render()
            choice = self._menu.show_numbered_menu(
                title=self.TITLE,
                options=self._MENU_OPTIONS,
                allow_back=True,
                allow_quit=True,
            )
            if choice in (None, "back", "quit"):
                break

            handler = {
                "copy":   self._do_copy,
                "move":   self._do_move,
                "delete": self._do_delete,
                "mkdir":  self._do_mkdir,
            }.get(choice)

            if handler:
                handler()

    def _do_copy(self) -> None:
        """Interactively copy the target to a destination chosen by the user."""
        if not self._target:
            self._logger.colour_log("!warn", "  No target selected.")
            return

        dest_str = self._menu.prompt_with_default(
            prompt=f"Copy '{self._target.name}' to (full destination path)",
            default=str(self._target.parent),
        )
        if dest_str is None:
            return

        dest = Path(dest_str)
        if dest.is_dir():
            dest = dest / self._target.name

        if not self._menu.confirm(f"Copy '{self._target}' → '{dest}'?", default=False):
            return

        try:
            if self._target.is_dir():
                shutil.copytree(self._target, dest)
            else:
                shutil.copy2(self._target, dest)
            self._logger.colour_log("!done", "  Copied:", "!path", str(dest))
        except Exception as exc:
            self._logger.colour_log("!error", f"  Copy failed: {exc}")

    def _do_move(self) -> None:
        """Interactively move or rename the target."""
        if not self._target:
            self._logger.colour_log("!warn", "  No target selected.")
            return

        dest_str = self._menu.prompt_with_default(
            prompt=f"Move/rename '{self._target.name}' to (full destination path)",
            default=str(self._target),
        )
        if dest_str is None:
            return

        dest = Path(dest_str)
        if not self._menu.confirm(f"Move '{self._target}' → '{dest}'?", default=False):
            return

        try:
            shutil.move(str(self._target), dest)
            self._logger.colour_log("!done", "  Moved:", "!path", str(dest))
            self._target = dest
        except Exception as exc:
            self._logger.colour_log("!error", f"  Move failed: {exc}")

    def _do_delete(self) -> None:
        """Interactively delete the target after confirmation."""
        if not self._target:
            self._logger.colour_log("!warn", "  No target selected.")
            return

        if not self._menu.confirm(
            f"Permanently delete '{self._target}'? This cannot be undone.",
            default=False,
        ):
            return

        try:
            if self._target.is_dir():
                shutil.rmtree(self._target)
            else:
                self._target.unlink()
            self._logger.colour_log("!delete", "  Deleted:", "!path", str(self._target))
            self._target = None
        except Exception as exc:
            self._logger.colour_log("!error", f"  Delete failed: {exc}")

    def _do_mkdir(self) -> None:
        """Interactively create a new directory inside (or alongside) the target."""
        base = self._target if self._target and self._target.is_dir() else (
            self._target.parent if self._target else Path.cwd()
        )
        name = self._menu.prompt_with_default(
            prompt=f"New directory name inside '{base}'",
        )
        if not name:
            return

        new_dir = base / name
        try:
            new_dir.mkdir(parents=True, exist_ok=True)
            self._logger.colour_log("!create", "  Created:", "!path", str(new_dir))
        except Exception as exc:
            self._logger.colour_log("!error", f"  mkdir failed: {exc}")
