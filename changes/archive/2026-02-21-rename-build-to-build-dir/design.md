# Design: Rename BUILD to BUILD_DIR

## Status
Approved

## Approach

Four references in `builder.py` need updating:

1. The configuration block declaration (line 14): `BUILD` → `BUILD_DIR`.
2. The env-var override assignment (line 26): `BUILD` → `BUILD_DIR`.
3. The use in `main()` to construct the local path (line 32): `BUILD` → `BUILD_DIR`.
4. The local variable `build` throughout `main()` → `build_dir`, to consistently reflect its role as a directory path.

`test.py` uses only the `BUILDER_BUILD` env var key (unchanged) and has no references to the Python-level `BUILD` name, so it requires no edits.

## Tasks

1. In `builder.py`, rename `BUILD` → `BUILD_DIR` in the configuration block, the env-var override, and the `main()` usage.
2. Run tests to verify.
