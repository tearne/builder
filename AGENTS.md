# AGENTS Guidelines

- Read definitions and terminology in `DEFINITIONS.md`, including the Change Management Process.
- Specifications live in `SPEC.md` files:
  - The **root** `SPEC.md` covers the project as a whole (structure, shared requirements, integration testing).
  - **Subfolder** `SPEC.md` files (e.g. `resources/tok/SPEC.md`) are scoped to that component — they own their own usage, implementation, and test definitions.
  - Subfolder specs inherit project-wide non-functional requirements (e.g. definitions in `DEFINITIONS.md`) unless they explicitly override them.
  - When assessing drift or planning changes, read **all** `SPEC.md` files, not just the root.

## Git
- Do not create commits. At suitable points (e.g. after a change is fully implemented or archived) suggest the user may wish to commit.

## Tests
- `test.sh` is the integration test for `bootstrap_inst.sh`/`install.py`. It launches a fresh incus container, runs setup, and verifies all tools, symlinks, and configs. Incus must be initialised on the host.
- The root `test.py` is the pytest suite for `builder.py`. Run it with `uv run --with pytest pytest test.py -v`.
- Subfolders with their own `SPEC.md` may have local pytest tests (e.g. `resources/tok/test.py`). pytest must be the entry point (it discovers and runs `test_*` functions), so use `uv run --with pytest pytest <path> -v` to supply pytest as an ad-hoc dependency.
