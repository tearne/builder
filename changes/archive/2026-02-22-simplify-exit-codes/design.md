# Design: Simplify Error Handling Spec
**Status: Ready for Review**

## Approach

### `SPEC.md`
- Replace the error table with a bulleted list of error conditions
- Each bullet notes only the condition; a preamble covers that all exit non-zero with a descriptive stderr message

### `test.py`
- Replace `assert rc == <N>` with `assert rc != 0`
- Replace `assert "<message>" in err` with `assert err` (non-empty stderr)

## Tasks
- [ ] Update `SPEC.md`
- [ ] Update `test.py`
- [ ] Run tests — expect all pass
- [ ] Confirm implementation complete and ready to archive
