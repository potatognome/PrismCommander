"""
PrismCommander panes package.

Exports the four core pane widgets that make up the PrismCommander UI:
  - DirPane        — directory tree navigation
  - FileListPane   — file listing for an active directory
  - PreviewPane    — content preview for a selected file
  - OpsPane        — file-operation menu (copy, move, delete, rename, mkdir)
"""

from PrismCommander.panes.dir_pane import DirPane
from PrismCommander.panes.file_list_pane import FileListPane
from PrismCommander.panes.preview_pane import PreviewPane
from PrismCommander.panes.ops_pane import OpsPane

__all__ = ["DirPane", "FileListPane", "PreviewPane", "OpsPane"]
