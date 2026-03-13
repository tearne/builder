# Design: Version Number
**Status: Draft**

## Approach

Add a `VERSION = "1.0.0"` constant immediately after the configuration section. Use `argparse` (pre-approved in POS) to handle `--version` — `argparse` provides this natively via `parser.add_argument("--version", action="version", version=VERSION)`, which prints the version and exits 0 automatically.

## Tasks

1. ✓ Tests: Add a test that runs `./builder.py --version` and verifies it exits 0 and prints `1.0.0`.
2. ✓ Impl: Add `VERSION` constant and `--version` handling to `builder.py`.
3. ✓ Verify: Run full test suite.
4. Process: Confirm ready to archive.
