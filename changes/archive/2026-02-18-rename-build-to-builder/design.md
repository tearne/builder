# Rename build.py to builder.py — Design

## Approach
A straight file rename. The error message for exit 2 already uses `Path(sys.argv[0]).name` dynamically, so no internal string changes are needed. Two files reference the name explicitly and must be updated: `test.py` (the `BUILD_PY` path constant and docstring comments) and `SPEC.md` (updated in the Archive step, not during implementation).

## Tasks
1. Rename `build.py` → `builder.py` and ensure it remains executable
2. Update `test.py`: `BUILD_PY` path constant and comment references to `build.py`
3. Run tests to verify
