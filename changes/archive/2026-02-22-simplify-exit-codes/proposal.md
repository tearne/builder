# Proposal: Simplify Error Handling Spec
**Status: Ready for Review**

## Intent
Specific exit codes and exact error messages are implementation details that don't need to be pinned in the spec. The spec should only require that errors produce a non-zero exit and a sensible stderr message describing the condition.

## Scope
- **In scope**: `SPEC.md` error handling section; `test.py` assertions on exit codes and message content
- **Out of scope**: the actual exit codes and messages in `builder.py` (left as-is)

## Delta

### MODIFIED
- Error handling section: replace the detailed table with a simple list of error conditions, noting only that each exits non-zero with a descriptive message
- `test.py`: replace specific exit code assertions with `assert rc != 0`; replace exact message substring assertions with a check that stderr is non-empty
