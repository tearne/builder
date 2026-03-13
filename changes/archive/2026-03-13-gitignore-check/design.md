# Design: Gitignore Check for BUILD_DIR
**Status: Draft**

## Approach

After resolving `BUILD_DIR` to an absolute path, check whether it sits inside a git repository using `git rev-parse --is-inside-work-tree` (run with `capture_output=True` so it is silent). If the command exits non-zero, `BUILD_DIR` is not inside a git repo and no further check is needed.

If it is inside a git repo, obtain the repo root via `git rev-parse --show-toplevel`, then check whether `BUILD_DIR` is covered by `.gitignore` rules by running `git check-ignore -q <absolute-path-to-BUILD_DIR>` from the repo root. This ensures `.gitignore` rules at any level of the repo are resolved correctly, regardless of where `BUILD_DIR` sits within it. `git check-ignore` exits 0 if the path is ignored and 1 if not. If not ignored, exit non-zero with a message such as:

```
Error: the build directory is inside a git repository but is not covered by .gitignore.
Build artifacts and checkouts must not be accidentally committed.
Add the build directory to .gitignore before proceeding.
```

The check runs before any other validation so the user sees the gitignore error even on a first run.

`git check-ignore` handles the case where `BUILD_DIR` does not yet exist — it evaluates the rules without requiring the path to be present on disk.

## Tasks

1. ✓ Tests: Add a test for `BUILD_DIR` inside a git repo and not gitignored → exit non-zero with error.
2. ✓ Tests: Add a test for `BUILD_DIR` inside a git repo and gitignored → build proceeds normally.
3. ✓ Tests: Add a test for `BUILD_DIR` outside any git repo → build proceeds normally.
4. ✓ Impl: Add the gitignore check to `builder.py`.
5. ✓ Verify: Run full test suite.
6. Process: Confirm ready to archive.
