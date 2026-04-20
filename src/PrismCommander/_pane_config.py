"""
PrismCommander shared pane configuration helpers.

Loads border patterns from the tUilKit config layer so that individual
panes do not hardcode border characters directly.

Integration points:
    tUilKit: ConfigLoader.load_border_patterns_config
"""

from tUilKit import get_config_loader

_DEFAULT_PANE_BORDER = {"TOP": "=", "BOTTOM": "=", "LEFT": "|", "RIGHT": "|"}


def get_pane_border() -> dict:
    """
    Return the border pattern dict for pane frames.

    Reads from the project's BORDER_PATTERNS config when available,
    falling back to a simple ASCII box if the config cannot be loaded.

    Returns:
        dict with keys TOP, BOTTOM, LEFT, RIGHT mapped to border strings.
    """
    try:
        cfg = get_config_loader().load_border_patterns_config()
        raw = cfg.get("BORDER_PATTERNS", {})
        return {
            "TOP":    _first_or(raw.get("TOP"),    "="),
            "BOTTOM": _first_or(raw.get("BOTTOM"), "="),
            "LEFT":   _first_or(raw.get("LEFT"),   "|"),
            "RIGHT":  _first_or(raw.get("RIGHT"),  "|"),
        }
    except Exception:
        return _DEFAULT_PANE_BORDER.copy()


def _first_or(value, default: str) -> str:
    """Return the first element if value is a list, or value itself, or default."""
    if isinstance(value, list):
        return value[0] if value else default
    if isinstance(value, str):
        return value
    return default
