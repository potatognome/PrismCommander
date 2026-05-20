# Copilot Instructions — PrismCommander (pc) + tUilKit + Chromaspace

## Purpose

PrismCommander (`pc`) is a modular, extensible, pane-based file manager built on
tUilKit and Chromaspace. Its primary entry point is `pc.py` at the project root,
with source under `src/PrismCommander/`.

Copilot must treat tUilKit and Chromaspace as first-class, authoritative
frameworks. Rendering, composition, layout, file operations, configuration,
colour, and logging must flow through those systems.

---

## What PrismCommander Is

PrismCommander is a **windowed, pane-based environment** powered by the tUilKit
compositor.

In this document, a **folder-content window** means a window whose primary pane
shows directory/file content for navigation and file operations.

- **Dual-pane file manager by default**, with any number of windows supported.
- A **true windowed model** where windows are tUilKit widgets managed by a
  `WindowManager` widget.
- **Horizontal and vertical splits**, plus duplication, close, combine, and
  content-swapping across windows.
- **Resizable windows** using compositor layout capabilities.
- **Optional window frames** per window, with toggleable frame panes for
  navigation elements.
- **Address-bar pane required at the top** of every folder-content window.
- **Preview pane support** for inline content rendering.
- **Built-in vi-style editor** as a first-class pane.
- **Ops queue pane** for queued file operations with dry-run support.
- **Chromaspace-driven colour roles** with swappable themes and border packs.
- **ASCII art modules** for preview decoration and borders.
- **Deterministic config layering** for themes, borders, keymaps, and layouts.
- **Scales from small ARM devices to full workstations**.
- **Architected for both terminal windows and future true GUI window surfaces**
  outside the terminal.

---

## Framework Rules

### tUilKit

Copilot must assume tUilKit provides—and PrismCommander must use:

- Compositor-backed window management and composition
- Rendering primitives and drawing pipelines
- Layout and clipping capabilities
- Redraw region tracking and damage-aware repaint behavior
- Existing widget lifecycle and event routing system
- File system operations (copy/move/delete/list/stat)
- Structured logging
- Deterministic layered config loading
- Factory functions as canonical singleton entry points

> **API evolution requirement:** tUilKit APIs are evolving. Do not hard-code
> assumptions about exact method names or signatures beyond what exists in the
> codebase. Describe intent, such as:
> - "use the compositor to create and manage windows"
> - "render this pane through the compositor’s drawing pipeline"
> - "use the existing tUilKit event routing system"
> - "use the compositor’s layout or clipping capabilities"
> - "use the existing tUilKit widget lifecycle"

Factory pattern (conceptual):

```python
import tUilKit
logger         = tUilKit.get_logger()
menu           = tUilKit.get_cli_menu_handler()
config_loader  = tUilKit.get_config_loader()
file_system    = tUilKit.get_file_system()
colour_manager = tUilKit.get_colour_manager()
```

### Chromaspace

Copilot must assume Chromaspace:

- Defines semantic colour roles over a 2 × 36 × 4 × 4 OKLCH grid.
- Is the sole authority for colour values in PrismCommander.
- Exposes colours by role names, not raw RGB/hex values.
- Supports swappable theme packs used by PrismCommander.

> **API evolution requirement:** Chromaspace APIs are evolving. Reference intent
> and role names, not hard-coded call signatures.

Copilot must **never** generate raw colour constants, ANSI escapes, or custom
colour math for PrismCommander UI code.

---

## Base Layer Expectations

### Expected project layout

```text
PrismCommander/
├── pc.py
├── pyproject.toml
├── config/
│   ├── PrismCommander_CONFIG.json
│   └── GLOBAL_SHARED.d/
├── src/
│   └── PrismCommander/
│       ├── __init__.py
│       ├── main.py
│       ├── windows/
│       ├── panes/
│       ├── widgets/
│       ├── editor/
│       ├── extensions/
│       └── themes/
├── examples/
└── tests/
```

New application modules must live under `src/PrismCommander/`.

### Responsibilities

- **WindowManager**
  - Owns window graph/state, focus, z-order intent, and UI orchestration.
  - Creates/manages window widgets through compositor concepts.
  - Handles split/duplicate/close/combine/swap/resize operations.

- **Window frames**
  - Optional per-window frame layer, toggleable per window.
  - May include panes for folder tree, drive letters, shortcut folders,
    network drives, Samba shares, cloud/device/git lists, and similar
    navigation contexts.
  - When a window hosts folder content, its address-bar pane remains at the top.

- **Pane widgets**
  - Self-contained widgets with consistent lifecycle.
  - Render through compositor pipeline and participate in routed events.
  - Must not bypass tUilKit for rendering/input/filesystem.

- **Preview system**
  - Delegates file rendering to previewers (built-in + extension-provided).
  - Supports text, hex, media, and future format handlers via registry.

- **Editor system**
  - vi-style modal editing in a pane/widget.
  - Uses tUilKit file helpers and compositor-driven rendering.

- **Ops queue**
  - Tracks/executes copy/move/delete/rename and related operations.
  - Supports dry-run and structured logging for all operations.

- **Theme and border loaders**
  - Resolve Chromaspace role mappings and border packs from layered config.
  - Support runtime theme/border swapping without architectural rewrites.

- **Extension registry**
  - First-class subsystem for discovery, registration, and integration.
  - Supplies extensions to windowing, panes, previewers, handlers, commands,
    themes, ASCII modules, and additional navigation/window types.

### Conceptual pane/compositor contract

- Panes are widgets that expose lifecycle-compatible render/update/input hooks.
- The compositor composes panes/windows, applies clipping/layout/z-order, and
  drives redraw regions.
- PrismCommander coordinates pane arrangement, focus policy, and window-level
  behavior; it does not reimplement compositor internals.

### Chromaspace role expectations

All UI state must map to semantic roles (examples):

- Window chrome: `ui.border.active`, `ui.border.inactive`, `ui.border.focus`
- Navigation/frame: `ui.nav.*`, `ui.addressbar.*`, `ui.frame.*`
- File types: `file.directory`, `file.regular`, `file.symlink`, `file.media`
- Selection/focus: `ui.selection.primary`, `ui.selection.secondary`, `ui.focus.cursor`
- Status: `status.ok`, `status.warn`, `status.error`, `status.pending`
- Editor: `editor.cursor`, `editor.selection`, `editor.line.active`, `editor.syntax.*`
- Accent/branding: `accent.primary`, `accent.secondary`, `accent.rainbow`

New roles must be added through theme mappings under
`src/PrismCommander/themes/` and/or extension-provided theme fragments.

### Rendering and event handling patterns

- Use compositor drawing flow for all rendering.
- Use existing tUilKit event routing for keyboard/mouse/command input.
- Avoid direct stdin handling in panes.
- Prefer redraw-region aware updates over full repaint assumptions.
- Keep UI components surface-agnostic so they work on terminal and future GUI
  compositor surfaces.

### Surface compatibility requirement

All UI elements (windows, frames, panes, widgets, overlays, previews, editor,
status/chrome components) must be designed to work with:

1. Current terminal-backed compositor surfaces
2. Future non-terminal GUI compositor surfaces

Do not hard-code terminal-only assumptions into architecture decisions.

---

## Extension System (First-Class)

The `src/PrismCommander/extensions/` folder is a first-class architectural
surface. Copilot must preserve and expand this model rather than bypass it.

Extensions may add:

- New pane types
- New previewers
- New file handlers
- New commands
- New Chromaspace role mappings
- New ASCII art modules
- Media players (e.g., mp3)
- Additional window types
- Additional navigation panes (cloud drives, git repos, device lists, etc.)

Extension descriptors should declare:

- Unique extension ID
- Target subsystem(s)
- Config keys they consume
- Role mappings and theme/border additions
- Integration points for panes/windows/previewers/commands/handlers

Extensions must use tUilKit and Chromaspace conceptually, follow config
layering conventions, and include tests under `tests/`.

---

## Config Layering

All configuration should be JSON or YAML and loaded deterministically through
layered fragments (`*.d/` conventions) via tUilKit config systems.

Use layered config for:

- Themes and role mappings
- Border packs
- Keymaps
- Layout/window presets
- Extension descriptors/options

Primary config remains `config/PrismCommander_CONFIG.json`, with shared
fragments under `config/GLOBAL_SHARED.d/`.

---

## Coding Expectations

Copilot is explicitly allowed to update and generate code for PrismCommander.

Copilot should:

- Update existing modules
- Generate new modules
- Create new panes, widgets, managers, and config files
- Modify modules to integrate with the compositor architecture
- Add architectural components needed for windowed/compositor behavior
- Keep implementations composable and extension-friendly

Copilot must not:

- Reimplement compositor internals, rendering primitives, file operations, or
  colour math
- Hard-code colours, hex literals, or ANSI escape sequences
- Bypass tUilKit factories or Chromaspace role systems
- Assume fixed tUilKit/Chromaspace APIs that are not present in the codebase

---

## General Coding Rules

### Use existing systems

- Use tUilKit factories for logger/config/filesystem/menus/colour management.
- Use compositor-oriented widget patterns instead of custom rendering loops.
- Use Chromaspace roles for all colours and visual states.
- Prefer existing helpers and extension hooks over new ad-hoc abstractions.

### Naming conventions

| Pattern | Applied to |
|---------|-----------|
| `snake_case` | files and functions |
| `PascalCase` | classes |
| `SomethingPane` | pane classes |
| `SomethingWidget` | widget classes |
| `SomethingManager` | coordinator/manager classes |
| `SomethingConfig` | config helper classes |
| `SomethingRenderer` | renderer classes |

### Dependency injection over globals

Pass required interfaces/utilities into constructors. Avoid module-level global
singleton lookups in production widget/pane classes.

### Composition over inheritance

Prefer small composable units with clear separation of responsibilities.

### Docstrings

Public classes/functions should document:

- Purpose
- Inputs and outputs
- Integration intent with tUilKit/Chromaspace/compositor concepts

### Testability

- Place tests under `tests/`
- Prefer sandboxed/file-safe test patterns
- Cover extension registration and window/pane behavior where applicable

---

## Summary

PrismCommander is a modular, extensible, compositor-driven windowed
application. It defaults to dual-pane operation but supports arbitrary windows,
optional frame panes, and per-window address bars. It must scale across device
classes and remain compatible with both terminal and future GUI surfaces.

Copilot should generate and update composable PrismCommander architecture using
tUilKit + Chromaspace concepts, keep extension support first-class, use
Chromaspace roles, respect deterministic config layering, and avoid hard-coded
API assumptions.

---

## Reference

- `.github/copilot-instructions.d/tuilkit_imports.md`
- `.github/copilot-instructions.d/logging_policy.md`
- `.github/copilot-instructions.d/cli_menu_patterns.md`
- `.github/copilot-instructions.d/colour_key_usage.md`
- `.github/copilot-instructions.d/tuilkit_enabled_apps_guidelines.md`
- `.github/copilot-instructions.d/windowed_apps_compositor.md`
- `.github/copilot-instructions.d/`

---

## Building Exemplar Policy

The `examples/` folder should include supplementary scripts that run outside
pytest and stress public APIs, menu paths, and error paths.

`examples/exemplar.py` should:

- Load tUilKit factory imports in verbose mode where available
- Build representative CLI/menu structures
- Read `config/PrismCommander_CONFIG.json`
- Exercise configured root/workspace modes
- Verify/display resolved paths for logs, config files, and input data files

Refer to:
- [Modular copilot-instructions](./copilot-instructions.d/*.md) for extensions to the general rules in this file.
