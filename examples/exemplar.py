#!/usr/bin/env python3
"""
examples/exemplar.py - PrismCommander exemplar mock entry point.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve()
TESTS_CONFIG = HERE.parent / "TESTS_CONFIG.py"
TEST_PATHS = HERE.parent / "test_paths.json"

if not TEST_PATHS.exists():
    subprocess.run([sys.executable, str(TESTS_CONFIG)], check=True)

PATHS = json.loads(TEST_PATHS.read_text(encoding="utf-8"))
PROJECT_ROOT = Path(PATHS["project_root"]).resolve()
WORKSPACE_ROOT = Path(PATHS["workspace_root"]).resolve()
CONFIG_FILE = Path(PATHS["config_file"]).resolve()

SRC_ROOT = PROJECT_ROOT / "src"
TUILKIT_SRC = WORKSPACE_ROOT / "Core" / "tUilKit" / "src"
for _path in (SRC_ROOT, TUILKIT_SRC):
    _path_s = str(_path)
    if _path.exists() and _path_s not in sys.path:
        sys.path.insert(0, _path_s)

from tUilKit.utils.config import ConfigLoader
from tUilKit.utils.output import ColourManager, Logger

# Initialize ConfigLoader with explicit tUilKit config path
TUILKIT_CONFIG = Path(PATHS.get("tuilkit_config_file", str(WORKSPACE_ROOT / "Core" / "tUilKit" / "config" / "tUilKit_CONFIG.json")))
config_loader = ConfigLoader(config_path=str(TUILKIT_CONFIG))
colour_manager = ColourManager(config_loader.load_colour_config())
logger = Logger(colour_manager)

try:
    if config_loader is not None:
        CONFIG = config_loader.load_config(str(CONFIG_FILE))
    else:
        CONFIG = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
except Exception:
    CONFIG = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def _resolve(mode_key: str, path_key: str, fallback: str) -> Path:
    mode = str(CONFIG.get("ROOT_MODES", {}).get(mode_key, "project")).lower().strip()
    base = WORKSPACE_ROOT if mode == "workspace" else PROJECT_ROOT
    rel = str(CONFIG.get("PATHS", {}).get(path_key, fallback))
    return (base / rel).resolve()


def _log_targets() -> list[str]:
    log_root = _resolve("LOG_PATHS", "LOG_PATHS", ".logs/PrismCommander/")
    log_root.mkdir(parents=True, exist_ok=True)
    out: list[str] = []
    for key in CONFIG.get("LOG_CATEGORIES", {}).get("default", ["MASTER", "SESSION"]):
        file_name = CONFIG.get("LOG_FILES", {}).get(key)
        if isinstance(file_name, str) and file_name:
            out.append(str(log_root / file_name))
    if not out:
        out = [str(log_root / "PrismCommander_SESSION.log"), str(log_root / "PrismCommander_MASTER.log")]
    return out


LOG_TARGETS = _log_targets()


def log_line(msg: str, key: str = "!info") -> None:
    try:
        logger.colour_log(key, msg, log_files=LOG_TARGETS, time_stamp=True)
    except Exception:
        print(msg)


def draw_header() -> None:
    title = f"{CONFIG.get('INFO', {}).get('PROJECT_NAME', 'PrismCommander')} Exemplar"
    try:
        logger.apply_border(
            text=title,
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=72,
            border_rainbow=True,
            log_files=LOG_TARGETS,
            include_timestamp=True,
        )
    except Exception:
        print("=" * 72)
        print(title)
        print("=" * 72)


def show_config_and_paths() -> None:
    log_line("Config and Paths", key="!proc")
    log_line(f"Primary config: {CONFIG_FILE}", key="!data")
    for key_name, value in CONFIG.get("ROOT_MODES", {}).items():
        log_line(f"ROOT_MODE[{key_name}] = {value}", key="!data")

    log_root = _resolve("LOG_PATHS", "LOG_PATHS", ".logs/PrismCommander/")
    cfg_root = _resolve("CONFIG", "CONFIG", "config/")
    input_root = _resolve("INPUT_DATA", "INPUT_DATA", ".projects_data/input_data/")
    log_line(f"Resolved LOG_PATHS: {log_root}", key="!info")
    log_line(f"Resolved CONFIG path: {cfg_root}", key="!info")
    log_line(f"Resolved INPUT_DATA path: {input_root}", key="!info")


def run_module_demo() -> None:
    log_line("Module demo", key="!proc")

    from PrismCommander._pane_config import get_pane_border

    border = get_pane_border()
    log_line(f"pane border keys: {sorted(list(border.keys()))}", key="!done")
    log_line(f"pane border sample: {border}", key="!data")


def run_edge_cases() -> None:
    log_line("Edge-case checks", key="!proc")

    from PrismCommander._pane_config import _first_or

    log_line(f"_first_or([], '=') -> {_first_or([], '=')}", key="!data")
    log_line(f"_first_or(['#'], '=') -> {_first_or(['#'], '=')}", key="!data")
    log_line(f"_first_or(None, '=') -> {_first_or(None, '=')}", key="!data")

    bad_json = HERE.parent / "_bad_config.json"
    bad_json.write_text("{", encoding="utf-8")
    try:
        if config_loader is not None:
            config_loader.load_config(str(bad_json))
        else:
            json.loads(bad_json.read_text(encoding="utf-8"))
        log_line("Malformed JSON unexpectedly parsed.", key="!error")
    except Exception as exc:
        log_line(f"Malformed JSON rejected as expected: {exc}", key="!done")
    finally:
        bad_json.unlink(missing_ok=True)


def menu_loop() -> None:
    while True:
        print()
        log_line("1. Config and path report", key="!list")
        log_line("2. Module demos", key="!list")
        log_line("3. Edge-case checks", key="!list")
        log_line("4. Exit", key="!list")
        choice = input("Select option (1-4): ").strip()
        if choice == "1":
            show_config_and_paths()
        elif choice == "2":
            run_module_demo()
        elif choice == "3":
            run_edge_cases()
        elif choice == "4":
            log_line("Exiting exemplar.", key="!done")
            return
        else:
            log_line("Invalid choice.", key="!error")


def main() -> int:
    draw_header()
    log_line("Loaded tUilKit factories in exemplar mode.", key="!done")
    menu_loop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
