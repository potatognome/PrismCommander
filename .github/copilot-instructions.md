# Copilot Instructions — PrismCommander (pc) + tUilKit + Chromaspace

## Purpose

This repository contains the PrismCommander project under `Applications/PrismCommander/`.
The main entry point is `pc.py` at the project root.

Copilot should treat tUilKit and Chromaspace as first‑class frameworks, not
optional helpers.

---

## Project Structure Expectations

### tUilKit

Copilot should assume:

- All UI components must be implemented as widgets under `Core/tuilkit/widgets/`
- All file operations must use the existing fs layer under `Core/tuilkit/fs/`
- All logging must use tUilKit structured logging under `Core/tuilkit/logging/`
- All configuration must use the deterministic config layering system under
  `Core/tuilkit/config/`
- All rendering must use the Cursor / Canvas / Chroma pipeline under
  `Core/tuilkit/render/`

Copilot must **not** re‑implement:

- File operations
- Logging
- Config parsing
- Rendering primitives

Instead, it must call the existing modules.

---

### Chromaspace

Copilot should assume:

- Chromaspace defines a semantic colour system
- Colours are stored in a 2 × 36 × 4 × 4 OKLCH grid
  (hue × steps × chroma × lightness)
- All colour access must go through Chromaspace APIs under `Core/chromaspace/`
- Themes must reference roles, not raw RGB/hex values
- Any new theme, palette, or role mapping must be placed under
  `Core/chromaspace/themes/`

Copilot must **not** generate raw colour constants unless explicitly asked.
It should instead reference:

```python
chromaspace.get(role="ui.border.active")
chromaspace.get(role="file.directory")
chromaspace.get(role="accent.primary")
```

---

## General Rules for Copilot

### 1. Always use existing modules

When generating code, Copilot must:

- Import from `Core/tuilkit/...` and `Core/chromaspace/...`
- Prefer existing helpers over new implementations
- Use the established naming conventions:
  - `WidgetNameWidget`
  - `SomethingPane`
  - `SomethingRenderer`
  - `SomethingConfig`

### 2. Follow the tUilKit architecture

Copilot should generate code that fits into:

- Widgets
- Layouts
- Commands
- Config fragments
- Renderers
- Operations

### 3. Respect the config layering system

All new configuration must be:

- JSON or YAML
- Deterministically ordered using numbered fragments
- Located under:
  - `config/`
  - `config/*.d/`

### 4. Use Chromaspace roles, not colours

When styling:

- Use semantic roles
- Never hardcode colours
- Never bypass Chromaspace

### 5. Prefer composition over inheritance

tUilKit is modular. Copilot should generate:

- Small, composable widgets
- Clear separation between model, view, and operations

### 6. Generate code that is testable

Tests must:

- Live under `tests/`
- Use existing test utilities in `Core/tuilkit/testing/`
- Avoid filesystem side effects unless using the sandbox helpers

---

## When Generating UI Code

Copilot should:

- Use existing tUilKit interface modules
- Use `Canvas` for drawing, `Cursor` for positioning
- Use `Chroma` for colour application
- Use Chromaspace roles for all colour lookups
- Use Widget lifecycle methods (`render`, `handle_event`, etc.)

---

## When Generating File Operations

Copilot must use:

```python
from tuilkit.fs import copy, move, delete, list_dir, stat
```

Never re‑implement filesystem logic.

---

## When Generating Themes or Borders

Copilot should:

- Place themes under `Core/chromaspace/themes/`
- Place border sets under `Core/tuilkit/borders/`
- Use semantic roles like:
  - `ui.border.active`
  - `ui.border.inactive`
  - `file.directory`
  - `file.regular`
  - `file.symlink`

---

## When Generating Commands

Commands must:

- Register through the tUilKit command dispatcher
- Support dry‑run mode
- Emit structured logs

---

## When Generating Code for pc (PrismCommander)

Copilot should assume:

- `pc` is a tUilKit application
- `pc` uses:
  - Pane widgets
  - Chromaspace themes
  - tUilKit file operations
  - Config layering
  - ASCII border packs
- `pc` lives under `Applications/PrismCommander/`
- The main entry point is `pc.py` in the project root

Copilot should generate:

- `DirPane`
- `FileListPane`
- `PreviewPane`
- `OpsPane`
- `StatusBar`
- `CommandStrip`

All using tUilKit primitives.

---

## Style and Conventions

- Use `snake_case` for files and functions
- Use `PascalCase` for classes
- Keep modules small and focused
- Prefer dependency injection over global state
- Always include docstrings describing:
  - Purpose
  - Inputs
  - Outputs
  - Integration points with tUilKit/Chromaspace

---

## Forbidden

Copilot must **not**:

- Recreate rendering primitives
- Recreate colour math
- Recreate file operations
- Hardcode colours
- Introduce external dependencies
- Generate code outside the `Core/` structure
- Use raw ANSI escape codes (must use Chroma)

---

## Allowed

Copilot should:

- Generate new widgets
- Generate new panes
- Generate new commands
- Generate new Chromaspace role mappings
- Generate new border sets
- Generate new config fragments
- Generate tests for all of the above

---

## Summary

Copilot should treat tUilKit and Chromaspace as the authoritative frameworks
for:

- Rendering
- Colour
- Layout
- File operations
- Configuration
- Logging

All new code must integrate with these systems, not bypass them.

---

## Reference

- For shared workspace policies (testing, CLI menus, colour logging, docs,
  imports, versioning), see workspace-level `.github/copilot-instructions.d/`.
- For tUilKit core rules, see `Core/.github/copilot-instructions.md`.
- For Chromaspace rules, see `Core/Chromaspace/.github/copilot-instructions.md`.

## Building Exemplar Policy

The `examples/` folder must include supplementary scripts that run outside pytest and stress public APIs and menu/error paths.

Requirements:
- Exercise all public functions across normal and adversarial input scenarios.
- Deliberately stress UI/menu edge cases (empty input, out-of-range values, special characters, very long strings).
- Produce visual, interactive, colour-logged output alongside structured logs for human review.
- Keep scripts as living behavior documentation.
- Maintain an `examples/exemplar.py` mock application entry point.

`examples/exemplar.py` should:
- Load tUilKit factory imports in verbose mode where available (for example, ConfigLoader).
- Generate a standard CLI menu with project header and submenus.
- Read the project primary config file.
- Read and test-load all `ROOT_MODES`.
- Verify and display resolved paths for `LOG_FILES`, config files, and input data files.
