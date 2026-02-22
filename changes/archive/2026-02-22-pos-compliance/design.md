# Design: POS Compliance
**Status: Ready for Review**

## Approach

Four files change.

### `builder.py`
- Remove the module-level uv guard (current lines 20–24)
- Update `if __name__ == "__main__":` to run the guard before calling `main()`, checking only `VIRTUAL_ENV`, with the POS-specified message and exit code 100

### `test.py`
- `test_run_directly_with_python`: drop the `UV_INTERNAL__PARENT_INTERPRETER` pop; update expected exit code 2 → 100; update the stderr message substring to match new wording
- All other tests: pass `BUILDER_SCRIPT="build.sh"` explicitly via `run_build()` rather than relying on the default; add a `DEFAULT_SCRIPT` constant at the top of the test file for this
- Update the `run_build` helper or individual calls as appropriate

### `SPEC.md`
- Update exit code table: code 2 → 100, message updated to match

## Tasks
- [x] Update `test.py` for uv guard (exit code 100, message, drop env var pop)
- [ ] Update `test.py` to pass `BUILDER_SCRIPT` explicitly in all tests that invoke `run_build`
- [ ] Run tests — expect `test_run_directly_with_python` to pass, others that rely on default script name to pass
- [ ] Update `builder.py`
- [ ] Run tests — expect all pass
- [ ] Update `SPEC.md`
- [ ] Confirm implementation complete and ready to archive
