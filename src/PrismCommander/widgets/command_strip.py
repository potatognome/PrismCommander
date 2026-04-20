"""
PrismCommander CommandStrip.

Renders a horizontal strip of labelled function-key shortcuts at the
bottom of the screen, giving the user a persistent reference to available
commands.

Inputs:
    logger   — tUilKit LoggerInterface instance
    commands — optional list of (key_label, description) tuples to override
               the default set

Outputs:
    render() — prints the command strip to stdout

Integration points:
    tUilKit: Logger.colour_log
"""

from typing import List, Optional, Tuple

from tUilKit.interfaces.logger_interface import LoggerInterface


class CommandStrip:
    """
    Renders a row of function-key shortcuts as a persistent command reference.

    Inputs:
        logger   — tUilKit LoggerInterface for colour output
        commands — list of (key_label, description) pairs; falls back to
                   the default PrismCommander shortcut set if not supplied
    """

    DEFAULT_COMMANDS: List[Tuple[str, str]] = [
        ("F1",  "Help"),
        ("F2",  "Dir"),
        ("F3",  "View"),
        ("F4",  "Edit"),
        ("F5",  "Copy"),
        ("F6",  "Move"),
        ("F7",  "MkDir"),
        ("F8",  "Delete"),
        ("F9",  "Menu"),
        ("F10", "Quit"),
    ]

    def __init__(
        self,
        logger: LoggerInterface,
        commands: Optional[List[Tuple[str, str]]] = None,
    ) -> None:
        self._logger = logger
        self._commands = commands if commands is not None else self.DEFAULT_COMMANDS

    def render(self) -> None:
        """
        Print a single-row command strip to stdout.

        Each command is shown as:  [Fkey] Description
        separated by spaces.  The strip is rendered using tUilKit colour keys
        so that function-key labels are visually distinct from their descriptions.
        """
        self._logger.colour_log("!info", "  " + "  ".join(
            f"[{key}] {desc}" for key, desc in self._commands
        ))
