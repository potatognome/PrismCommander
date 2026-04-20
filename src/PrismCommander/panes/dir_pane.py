"""
PrismCommander DirPane.

Displays a navigable directory tree rooted at a given path.
Uses tUilKit Logger for colour-coded output and the CLIMenuHandler
browse_directory helper for interactive navigation.

Inputs:
    logger          — tUilKit LoggerInterface instance
    menu_handler    — tUilKit CLIMenuInterface instance
    start_path      — initial root directory (default: cwd)

Outputs:
    render()        — prints the directory tree frame to stdout
    navigate()      — runs an interactive browse loop; returns chosen Path

Integration points:
    tUilKit: Logger.apply_border, Logger.colour_log, CLIMenuHandler.browse_directory
"""

from pathlib import Path
from typing import Optional

from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.interfaces.cli_menu_interface import CLIMenuInterface

from PrismCommander._pane_config import get_pane_border


class DirPane:
    """
    Renders a directory navigation frame and drives interactive traversal.

    Inputs:
        logger       — tUilKit LoggerInterface for colour output
        menu_handler — tUilKit CLIMenuInterface for browse interaction
        start_path   — root directory to display (default: Path.cwd())
    """

    TITLE = "Directory"
    FRAME_WIDTH = 72

    def __init__(
        self,
        logger: LoggerInterface,
        menu_handler: CLIMenuInterface,
        start_path: Optional[Path] = None,
    ) -> None:
        self._logger = logger
        self._menu = menu_handler
        self._path = Path(start_path) if start_path else Path.cwd()

    @property
    def current_path(self) -> Path:
        """The directory currently focused in this pane."""
        return self._path

    @current_path.setter
    def current_path(self, path: Path) -> None:
        """Set the directory currently focused in this pane."""
        self._path = Path(path)

    def render(self) -> None:
        """
        Print the DirPane header frame showing the current directory path.

        Outputs a bordered title line followed by the resolved path.
        """
        self._logger.apply_border(
            text=f"  {self.TITLE}",
            pattern=get_pane_border(),
            total_length=self.FRAME_WIDTH,
            border_rainbow=True,
        )
        self._logger.colour_log("!info", "  Path:", "!path", str(self._path))

    def navigate(self) -> Optional[Path]:
        """
        Launch the interactive directory browser.

        Returns:
            The Path selected by the user, or None if cancelled.
        """
        selected = self._menu.browse_directory(
            start_path=self._path,
            title=self.TITLE,
            allow_creation=True,
        )
        if selected is not None:
            self._path = selected
        return selected
