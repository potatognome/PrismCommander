# Copilot Instructions — PrismCommander (pc) + tUilKit + Chromaspace

## Purpose

PrismCommander (`pc`) is a modular, extensible, pane-based terminal file
manager built on the tUilKit and Chromaspace suites.  Its primary entry point
is `pc.py` at the project root.  Source lives under `src/PrismCommander/`.

Copilot must treat tUilKit and Chromaspace as first-class, authoritative
frameworks — not optional helpers.  All rendering, colour, layout, file
operations, configuration, and logging must flow through those suites.

---

## What PrismCommander Is

PrismCommander is a **windowed, pane-based environment** for the terminal:

- **Dual-pane by default**, expandable to an arbitrary number of windows.
- Windows can be **split, duplicated, closed, and combined** at runtime.
- The window framework is **resizable** and adapts from small ARM devices to
  full workstation environments.
- Window contents are **swappable** — any supported pane type can occupy any
  window slot.
- A **preview pane system** renders file content inline.
- A **built-in vi-style editor** is available as a first-class pane.
- An **operations queue (OpsPane)** tracks and executes file operations with
  dry-run support.
- **Chromaspace-driven colour configuration** governs all visual output via
  a 2 × 36 × 4 × 4 OKLCH grid (hue × steps × chroma × lightness).
- **Swappable colour themes and border packs** can be changed without
  restarting.
- **ASCII art modules** provide decorative and structural framing.
- A first-class **extension system** allows additional panes, previewers,
  file handlers, media players, and other modules to register and integrate
  without modifying core code.

---

## Framework Rules

### tUilKit

Copilot must assume that tUilKit provides — and must not re-implement:

- **Rendering primitives** (canvas drawing, cursor positioning, colour
  application)
- **File system operations** (copy, move, delete, list, stat)
- **Structured logging** with colour-coded output
- **Deterministic config loading** with layered JSON/YAML fragments
- **Factory functions** as the canonical entry points for all singletons

> **Note:** The tUilKit API is still evolving.  Copilot must not assume
> specific method names beyond what is already present in the codebase.
> When referencing tUilKit capabilities, describe the intent (e.g.
> "use the tUilKit file system helper to list a directory") rather than
> hard-coding a call signature.

Factory pattern — always use factories, never instantiate directly:

```python
import tUilKit
logger        = tUilKit.get_logger()
menu          = tUilKit.get_cli_menu_handler()
config_loader = tUilKit.get_config_loader()
file_system   = tUilKit.get_file_system()
colour_manager = tUilKit.get_colour_manager()
```

Interfaces for type annotations:

```python
from tUilKit.interfaces.logger_interface     import LoggerInterface
from tUilKit.interfaces.cli_menu_interface   import CLIMenuInterface
```

### Chromaspace

Copilot must assume that Chromaspace:

- Defines a **semantic colour role system** over a 2 × 36 × 4 × 4 OKLCH grid.
- Is the **sole authority** for all colour values used in PrismCommander.
- Exposes colour through role names, not raw hex or RGB values.
- Hosts themes under `Core/chromaspace/themes/`.

> **Note:** Chromaspace's internal API is still evolving.  Copilot must not
> hard-code Chromaspace call signatures beyond what is present in the
> codebase.  Reference the intent and the role name, not the exact call.

Colour access pattern:

```python
# Conceptual — exact API subject to evolution
colour = chromaspace.get(role="ui.border.active")
colour = chromaspace.get(role="file.directory")
colour = chromaspace.get(role="accent.primary")
```

Copilot must **never** generate raw colour constants, hex literals, or ANSI
escape codes.  All colour must flow through Chromaspace.

---

## Folder Layout

```
PrismCommander/            ← project root
├── pc.py                  ← main entry point
├── pyproject.toml
├── config/
│   ├── PrismCommander_CONFIG.json   ← primary config
│   └── GLOBAL_SHARED.d/             ← shared colour/border/test fragments
├── src/
│   └── PrismCommander/
│       ├── __init__.py
│       ├── main.py              ← application wiring
│       ├── _pane_config.py      ← shared pane config helpers
│       ├── panes/               ← core pane implementations
│       │   ├── dir_pane.py
│       │   ├── file_list_pane.py
│       │   ├── preview_pane.py
│       │   └── ops_pane.py
│       ├── widgets/             ← chrome widgets (status bar, command strip)
│       ├── windows/             ← window manager and layout engine
│       ├── editor/              ← built-in vi-style editor pane
│       ├── extensions/          ← extension registry and loader
│       └── themes/              ← Chromaspace role mappings for pc
├── examples/
│   └── exemplar.py
└── tests/
```

New modules must be placed within this structure.  Do not generate code
outside `src/PrismCommander/`.

---

## Core Module Responsibilities

### Window Manager (`windows/`)

- Owns the top-level layout: which panes occupy which slots.
- Manages split, duplicate, close, combine, and resize operations.
- Tracks focus and routes keyboard events to the focused pane.
- Dispatches render requests to all visible panes.
- Must not contain file or colour logic — delegate to panes and Chromaspace.

### Panes (`panes/`)

Each pane is a self-contained tUilKit widget with a consistent lifecycle:

| Pane | Responsibility |
|------|---------------|
| `DirPane` | Navigate and display the directory tree |
| `FileListPane` | List and select files in the current directory |
| `PreviewPane` | Render file content inline (text, hex, image, etc.) |
| `OpsPane` | Queue, preview, and execute file operations |
| `EditorPane` | vi-style in-pane editor for text files |

All panes accept a `logger` and any required tUilKit interfaces via
dependency injection.  Panes must not instantiate tUilKit utilities directly.

### Preview System (`panes/preview_pane.py` + `extensions/`)

- `PreviewPane` delegates rendering to a registered previewer for the given
  file type.
- Built-in previewers cover plain text and hex.
- Extension previewers register against MIME types or file extensions.
- Previewers must use tUilKit rendering primitives and Chromaspace roles.

### Built-in Editor (`editor/`)

- Implements vi-style modal editing as a pane.
- Integrates with tUilKit file system helpers for read/write.
- Renders through tUilKit rendering primitives.
- Cursor and selection state use Chromaspace roles for highlight colouring.

### Operations Queue (`panes/ops_pane.py`)

- Collects pending file operations (copy, move, delete, rename, etc.).
- Supports dry-run mode before committing changes.
- Delegates all filesystem calls to the tUilKit file system interface.
- Emits structured log entries for every operation.

### Chrome Widgets (`widgets/`)

- `StatusBar` — current path, selection count, mode indicator.
- `CommandStrip` — contextual key-binding hints.
- Both accept `logger` via dependency injection and render through tUilKit.

---

## Extension System

The extension system is first-class in PrismCommander.  Extensions are the
primary mechanism for adding:

- New pane types
- New previewers (additional file formats, media players)
- New file handlers (archive openers, remote file systems)
- New ASCII art modules
- New Chromaspace theme packs and border packs

### Registration Pattern

Extensions register themselves through a descriptor object placed under
`src/PrismCommander/extensions/`.  The registry loads all descriptors at
startup and makes them available to the relevant subsystem (window manager,
preview system, ops queue, etc.).

An extension descriptor must declare:

- A unique identifier
- The subsystem it targets (pane, previewer, handler, theme, border)
- Any Chromaspace role mappings it introduces
- Any config keys it reads from the layered config system

Extensions must:

- Use tUilKit factories for all utilities
- Reference Chromaspace roles — never raw colours
- Place any config fragments in `config/` or `config/*.d/`
- Place any theme or role additions in `src/PrismCommander/themes/`
- Place tests under `tests/`

---

## Chromaspace Role Expectations

PrismCommander defines the following semantic role categories.  All new UI
code must map to roles in these categories.  New roles must be documented in
`src/PrismCommander/themes/`.

| Category | Example roles |
|----------|--------------|
| Window chrome | `ui.border.active`, `ui.border.inactive`, `ui.border.focus` |
| File type decorations | `file.directory`, `file.regular`, `file.symlink`, `file.executable`, `file.archive`, `file.media` |
| Selection and focus | `ui.selection.primary`, `ui.selection.secondary`, `ui.focus.cursor` |
| Status and feedback | `status.ok`, `status.warn`, `status.error`, `status.pending` |
| Editor | `editor.cursor`, `editor.selection`, `editor.line.active`, `editor.syntax.*` |
| Accent and branding | `accent.primary`, `accent.secondary`, `accent.rainbow` |

Themes and border packs are swappable without restarting pc.  New themes must
live under `src/PrismCommander/themes/` and reference these roles — not
raw values.  New border packs live under `config/GLOBAL_SHARED.d/` or the
extension's config fragment.

---

## Rendering and Event Handling

- All terminal output must use tUilKit rendering primitives.
- Raw `print()` calls and raw ANSI escape codes are forbidden in production
  code.
- Colour application must go through Chromaspace via tUilKit's colour
  pipeline.
- The window manager drives the render loop: it calls each visible pane's
  render method in layout order.
- Keyboard events are dispatched by the window manager to the focused pane.
  Panes consume events they handle and return unhandled events to the manager.
- Panes must not read stdin directly; all input routing flows through the
  tUilKit event/menu interface.

---

## Config Layering

All configuration must be:

- JSON or YAML
- Deterministically ordered using the `*.d/` fragment convention
- Located under `config/` (project-level) or within a `config/` directory
  inside an extension

The primary config file is `config/PrismCommander_CONFIG.json`.  Shared
fragments (colours, border patterns, test options, timestamps) live in
`config/GLOBAL_SHARED.d/`.

Config is loaded via the tUilKit config loader factory.  Modules must not
parse config files directly.

---

## General Coding Rules

### Always use existing modules

- Use tUilKit factories for logger, config, file system, colour manager,
  and menu handler.
- Use Chromaspace roles for all colour lookups.
- Use tUilKit rendering primitives for all output.
- Prefer existing helpers over new implementations.

### Naming conventions

| Pattern | Applied to |
|---------|-----------|
| `snake_case` | files and functions |
| `PascalCase` | classes |
| `SomethingPane` | pane classes |
| `SomethingWidget` | chrome widget classes |
| `SomethingManager` | manager/coordinator classes |
| `SomethingConfig` | config helper classes |
| `SomethingRenderer` | renderer classes |

### Dependency injection over global state

All tUilKit utilities must be passed into constructors — not obtained from
module-level globals in production panes and widgets.

### Composition over inheritance

PrismCommander is modular.  Prefer small, composable units with clear
separation between model, view, and operations.

### Docstrings

Every class and public function must include a docstring covering:

- Purpose
- Inputs / parameters
- Outputs / return values
- Integration points with tUilKit and/or Chromaspace

### Testability

Tests must:

- Live under `tests/`
- Use tUilKit test utilities where available
- Avoid real filesystem side effects unless using sandbox helpers

---

## Forbidden

Copilot must **not**:

- Recreate rendering primitives, colour math, or file operations
- Hardcode colours, hex literals, or ANSI escape sequences
- Bypass tUilKit factories (never instantiate Logger, ConfigLoader, etc. directly)
- Bypass Chromaspace (never assign raw colour values)
- Introduce external dependencies not already in `pyproject.toml`
- Place new application modules outside `src/PrismCommander/`
- Assume specific tUilKit or Chromaspace method signatures beyond what is
  present in the existing codebase

---

## Allowed

Copilot should:

- Generate new panes, widgets, managers, and extension descriptors
- Generate new Chromaspace role mappings in `src/PrismCommander/themes/`
- Generate new border pack fragments in `config/GLOBAL_SHARED.d/`
- Generate new config fragments
- Generate new extension registrations under `src/PrismCommander/extensions/`
- Generate tests for all of the above

---

## Summary

Copilot must treat tUilKit and Chromaspace as the authoritative frameworks
for rendering, colour, layout, file operations, configuration, and logging.
PrismCommander is a windowed, pane-based, extensible file manager.  All new
code must integrate with these systems, respect the extension system, and
treat the evolving API surfaces as intentionally vague — describe intent,
not exact call signatures.

---

## Reference

- For detailed import patterns, see `.github/copilot-instructions.d/tuilkit_imports.md`.
- For logging policy, see `.github/copilot-instructions.d/logging_policy.md`.
- For CLI menu patterns, see `.github/copilot-instructions.d/cli_menu_patterns.md`.
- For colour key usage, see `.github/copilot-instructions.d/colour_key_usage.md`.
- For tUilKit-enabled app guidelines, see `.github/copilot-instructions.d/tuilkit_enabled_apps_guidelines.md`.
- For modular extensions to these rules, see `.github/copilot-instructions.d/`.

---

## Building Exemplar Policy

The `examples/` folder must include supplementary scripts that run outside
pytest and stress public APIs and menu/error paths.

Requirements:

- Exercise all public functions across normal and adversarial input scenarios.
- Deliberately stress UI/menu edge cases (empty input, out-of-range values,
  special characters, very long strings).
- Produce visual, interactive, colour-logged output alongside structured logs
  for human review.
- Keep scripts as living behaviour documentation.
- Maintain an `examples/exemplar.py` mock application entry point.

`examples/exemplar.py` should:

- Load tUilKit factory imports in verbose mode where available.
- Generate a standard CLI menu with project header and submenus.
- Read the primary config file (`config/PrismCommander_CONFIG.json`).
- Read and test-load all `ROOT_MODES`.
- Verify and display resolved paths for `LOG_FILES`, config files, and input
  data files.

Refer to:

- [Modular copilot-instructions](./copilot-instructions.d/*.md) for
  extensions to the general rules in this file.
