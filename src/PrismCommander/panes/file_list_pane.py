"""
PrismCommander FileListPane.

Lists the contents of a directory (directories first, then files) with
colour-coded entries and interactive selection.

Inputs:
    logger       — tUilKit LoggerInterface instance
    menu_handler — tUilKit CLIMenuInterface instance
    directory    — Path of the directory to list

Outputs:
    render()     — prints a colour-coded file listing frame to stdout
    select()     — runs an interactive selection loop; returns chosen Path

Integration points:
    tUilKit: Logger.apply_border, Logger.colour_log, Logger.colour_log_text,
             CLIMenuHandler.select_from_list
"""

import os
from pathlib import Path
from typing import Optional, List

from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.interfaces.cli_menu_interface import CLIMenuInterface


class FileListPane:
    """
    Renders a directory file listing and supports interactive selection.

    Inputs:
        logger       — tUilKit LoggerInterface for colour output
        menu_handler — tUilKit CLIMenuInterface for selection interaction
        directory    — directory whose contents are displayed
    """

    TITLE = "Files"
    BORDER_PATTERN = {"TOP": "=", "BOTTOM": "=", "LEFT": "|", "RIGHT": "|"}
    FRAME_WIDTH = 72
    MAX_PREVIEW_ROWS = 24

    def __init__(
        self,
        logger: LoggerInterface,
        menu_handler: CLIMenuInterface,
        directory: Optional[Path] = None,
    ) -> None:
        self._logger = logger
        self._menu = menu_handler
        self._directory = Path(directory) if directory else Path.cwd()

    @property
    def directory(self) -> Path:
        """The directory currently shown in this pane."""
        return self._directory

    @directory.setter
    def directory(self, path: Path) -> None:
        self._directory = Path(path)

    def _scan(self) -> tuple[List[Path], List[Path]]:
        """
        Return (dirs, files) for the current directory, sorted alphabetically.
        Skips entries that raise PermissionError.
        """
        dirs: List[Path] = []
        files: List[Path] = []
        try:
            with os.scandir(self._directory) as it:
                for entry in it:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            dirs.append(Path(entry.path))
                        else:
                            files.append(Path(entry.path))
                    except PermissionError:
                        pass
        except PermissionError:
            self._logger.colour_log("!error", "Permission denied:", "!path", str(self._directory))
        dirs.sort(key=lambda p: p.name.lower())
        files.sort(key=lambda p: p.name.lower())
        return dirs, files

    def render(self) -> None:
        """
        Print the FileListPane frame: a bordered header followed by
        a colour-coded listing of directories and files.
        """
        dirs, files = self._scan()

        self._logger.apply_border(
            text=f"  {self.TITLE}  —  {self._directory}",
            pattern=self.BORDER_PATTERN,
            total_length=self.FRAME_WIDTH,
            border_rainbow=True,
        )

        total = len(dirs) + len(files)
        visible = dirs + files
        if total > self.MAX_PREVIEW_ROWS:
            visible = visible[: self.MAX_PREVIEW_ROWS]
            truncated = total - self.MAX_PREVIEW_ROWS
        else:
            truncated = 0

        for entry in visible:
            if entry.is_dir():
                self._logger.colour_log("!thisfolder", f"  [DIR]  {entry.name}/")
            else:
                size = self._file_size_str(entry)
                self._logger.colour_log("!file", f"  {entry.name}", "!info", f"  ({size})")

        if truncated:
            self._logger.colour_log("!info", f"  … and {truncated} more entries")

        self._logger.colour_log(
            "!info",
            f"  {len(dirs)} director{'y' if len(dirs) == 1 else 'ies'},"
            f"  {len(files)} file{'s' if len(files) != 1 else ''}",
        )

    def select(self) -> Optional[Path]:
        """
        Launch an interactive selection prompt over the current directory.

        Returns:
            The Path chosen by the user, or None if cancelled.
        """
        dirs, files = self._scan()
        all_entries = dirs + files

        if not all_entries:
            self._logger.colour_log("!warn", "  Directory is empty.")
            return None

        labels = [
            f"[DIR]  {p.name}/" if p.is_dir() else p.name
            for p in all_entries
        ]
        icons = ["📁" if p.is_dir() else "📄" for p in all_entries]

        selected = self._menu.select_from_list(
            title=f"Select — {self._directory}",
            items=labels,
            multi_select=False,
            icons=icons,
        )
        if selected is None:
            return None
        idx = labels.index(selected[0])
        return all_entries[idx]

    @staticmethod
    def _file_size_str(path: Path) -> str:
        """Return a human-readable file size string."""
        try:
            size = path.stat().st_size
        except OSError:
            return "?"
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024:
                return f"{size:.0f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
