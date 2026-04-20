"""
PrismCommander main module.

Entry point for the PrismCommander terminal file-manager application.
Wires together the pane widgets (DirPane, FileListPane, PreviewPane, OpsPane)
and the chrome widgets (StatusBar, CommandStrip) using tUilKit factories for
logging, colour management, and interactive menus.

Run via:
    python pc.py                    (from project root)
    pc                              (if installed as a package script)
"""

from pathlib import Path

import tUilKit
from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.interfaces.cli_menu_interface import CLIMenuInterface

from PrismCommander.panes import DirPane, FileListPane, PreviewPane, OpsPane
from PrismCommander.widgets import StatusBar, CommandStrip


# ── Top-level menu options ────────────────────────────────────────────────────

_MAIN_MENU_OPTIONS = [
    {"key": "browse",  "label": "Browse / Navigate directory",  "icon": "📂"},
    {"key": "list",    "label": "List files in current directory", "icon": "📋"},
    {"key": "preview", "label": "Preview a file",               "icon": "🔍"},
    {"key": "ops",     "label": "File operations",              "icon": "⚙️ "},
]


def _render_splash(logger: LoggerInterface) -> None:
    """Print the PrismCommander splash / title block."""
    logger.apply_border(
        text="  PrismCommander  —  Terminal File Manager",
        pattern={"TOP": "=", "BOTTOM": "=", "LEFT": "|", "RIGHT": "|"},
        total_length=72,
        border_rainbow=True,
    )


def main() -> None:
    """
    Launch the PrismCommander application.

    Initialises tUilKit components via the factory layer, constructs all
    pane and widget instances, then drives the main interactive loop.
    """
    logger: LoggerInterface = tUilKit.get_logger()
    menu: CLIMenuInterface = tUilKit.get_cli_menu_handler()

    cwd = Path.cwd()

    # ── Instantiate widgets ───────────────────────────────────────────────
    status_bar = StatusBar(logger=logger, path=cwd)
    command_strip = CommandStrip(logger=logger)
    dir_pane = DirPane(logger=logger, menu_handler=menu, start_path=cwd)
    file_list_pane = FileListPane(logger=logger, menu_handler=menu, directory=cwd)
    preview_pane = PreviewPane(logger=logger)
    ops_pane = OpsPane(logger=logger, menu_handler=menu)

    # ── Main loop ─────────────────────────────────────────────────────────
    while True:
        _render_splash(logger)
        status_bar.update(path=dir_pane.current_path)
        command_strip.render()

        choice = menu.show_numbered_menu(
            title="Main Menu",
            options=_MAIN_MENU_OPTIONS,
            allow_back=False,
            allow_quit=True,
        )

        if choice in (None, "quit"):
            logger.colour_log("!info", "  Goodbye.")
            break

        if choice == "browse":
            selected = dir_pane.navigate()
            if selected is not None:
                file_list_pane.directory = dir_pane.current_path
                status_bar.update(path=dir_pane.current_path)

        elif choice == "list":
            file_list_pane.directory = dir_pane.current_path
            file_list_pane.render()
            chosen = file_list_pane.select()
            if chosen is not None:
                if chosen.is_dir():
                    dir_pane.current_path = chosen
                    file_list_pane.directory = chosen
                else:
                    ops_pane.target = chosen
                    preview_pane.load(chosen)

        elif choice == "preview":
            file_list_pane.directory = dir_pane.current_path
            chosen = file_list_pane.select()
            if chosen is not None and chosen.is_file():
                preview_pane.load(chosen)
                ops_pane.target = chosen

        elif choice == "ops":
            ops_pane.run()
