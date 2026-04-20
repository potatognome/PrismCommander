"""
PrismCommander PreviewPane.

Displays the content of a selected file inside a bordered frame.
Text files are shown line-by-line (up to MAX_LINES).  Binary files
show a hex dump of the first BINARY_PREVIEW_BYTES bytes.

Inputs:
    logger    — tUilKit LoggerInterface instance
    file_path — optional Path of the file to preview (can be set later)

Outputs:
    render()  — prints the preview frame to stdout
    load(path)— sets a new file to preview and renders it

Integration points:
    tUilKit: Logger.apply_border, Logger.colour_log, Logger.apply_border_multiline
"""

from pathlib import Path
from typing import Optional

from tUilKit.interfaces.logger_interface import LoggerInterface


class PreviewPane:
    """
    Renders a read-only file preview inside a bordered frame.

    Inputs:
        logger    — tUilKit LoggerInterface for colour output
        file_path — Path of the file to preview (may be None)
    """

    TITLE = "Preview"
    BORDER_PATTERN = {"TOP": "=", "BOTTOM": "=", "LEFT": "|", "RIGHT": "|"}
    FRAME_WIDTH = 72
    MAX_LINES = 20
    BINARY_PREVIEW_BYTES = 256
    ENCODINGS = ("utf-8", "latin-1")

    def __init__(
        self,
        logger: LoggerInterface,
        file_path: Optional[Path] = None,
    ) -> None:
        self._logger = logger
        self._path: Optional[Path] = Path(file_path) if file_path else None

    @property
    def file_path(self) -> Optional[Path]:
        """The file currently loaded into the preview pane."""
        return self._path

    def load(self, path: Path) -> None:
        """
        Set a new file to preview and immediately render it.

        Inputs:
            path — Path of the file to load
        """
        self._path = Path(path)
        self.render()

    def render(self) -> None:
        """
        Print the PreviewPane frame showing file content.

        If no file is loaded, a placeholder message is displayed.
        If the file is binary, a hex dump of the first bytes is shown.
        Otherwise, the first MAX_LINES of text are displayed.
        """
        if self._path is None:
            self._logger.apply_border(
                text=f"  {self.TITLE}  —  (no file selected)",
                pattern=self.BORDER_PATTERN,
                total_length=self.FRAME_WIDTH,
                border_rainbow=True,
            )
            self._logger.colour_log("!info", "  Select a file from the file list to preview it.")
            return

        title = f"  {self.TITLE}  —  {self._path.name}"
        self._logger.apply_border(
            text=title,
            pattern=self.BORDER_PATTERN,
            total_length=self.FRAME_WIDTH,
            border_rainbow=True,
        )

        if not self._path.exists():
            self._logger.colour_log("!error", "  File not found:", "!path", str(self._path))
            return

        if self._path.is_dir():
            self._logger.colour_log("!warn", "  Cannot preview a directory.")
            return

        content = self._read_content()
        for line in content:
            self._logger.colour_log("!data", f"  {line}")

    def _read_content(self) -> list[str]:
        """
        Read and return displayable lines from the current file.

        Returns a list of strings ready for rendering.
        Binary files are represented as a hex dump.
        """
        try:
            raw = self._path.read_bytes()
        except OSError as exc:
            return [f"[Error reading file: {exc}]"]

        for encoding in self.ENCODINGS:
            try:
                text = raw.decode(encoding)
                lines = text.splitlines()
                if len(lines) > self.MAX_LINES:
                    lines = lines[: self.MAX_LINES]
                    lines.append(f"[… truncated — showing {self.MAX_LINES} of {len(text.splitlines())} lines]")
                return lines
            except (UnicodeDecodeError, ValueError):
                continue

        # Binary fallback — hex dump
        chunk = raw[: self.BINARY_PREVIEW_BYTES]
        hex_lines = [
            " ".join(f"{b:02x}" for b in chunk[i : i + 16])
            for i in range(0, len(chunk), 16)
        ]
        hex_lines.insert(0, f"[Binary file — showing first {len(chunk)} bytes as hex]")
        return hex_lines
