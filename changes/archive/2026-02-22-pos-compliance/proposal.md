# Proposal: POS Compliance
**Status: Ready for Review**

## Intent
Bring `builder.py` into line with the updated POS standard, which changed how the uv guard is structured.

## Scope
- **In scope**: `builder.py` uv guard placement, check, message, and exit code; `test.py` passing `BUILDER_SCRIPT` explicitly rather than relying on defaults; corresponding updates to `SPEC.md`
- **Out of scope**: any other changes to script behaviour

## Delta

### MODIFIED
- uv guard moves from module level into the `if __name__ == "__main__":` block
- uv guard checks only `VIRTUAL_ENV` (drops `UV_INTERNAL__PARENT_INTERPRETER`)
- uv guard error message updated to match POS wording
- uv guard exit code: 2 → 100
