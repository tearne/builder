# Rename BUILD to BUILD_DIR

## Intent
The configuration variable `BUILD` is easily confused with the concept of "running a build". Renaming it to `BUILD_DIR` makes its purpose — a directory path — immediately clear, especially now that `BUILD_SCRIPT` sits alongside it.

## Scope
- **In scope**: Renaming the variable throughout `builder.py` and `test.py`
- **Out of scope**: Behavioural changes, renaming the `<build>` placeholder in `SPEC.md`

## Delta

### MODIFIED
- **Configuration variable**: `BUILD` → `BUILD_DIR` in `builder.py`
- **Env-var override**: `BUILDER_BUILD` remains unchanged (user-facing, renaming would be a breaking change)
- **Tests**: `BUILDER_BUILD` env var key unchanged; any internal references to `BUILD` updated
