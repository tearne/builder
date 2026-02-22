# Design: Checkouts Subdir
**Status: Ready for Review**

## Approach

Three files change; `run_example.sh` and `example/build.sh` are unaffected.

### `builder.py`
- `checkout` path: `build_dir / repo_name(REPO)` → `build_dir / "checkouts" / repo_name(REPO)`
- `target` variable removed; `build_dir` is passed directly to the build script
- `target.mkdir(...)` removed; `BUILD_DIR` is a precondition (must already exist), and `checkouts/<repo-name>/` creation is handled by the existing checkout logic
- Guard changes from `cwd.is_relative_to(build_dir)` → `cwd.is_relative_to(build_dir / "checkouts")`, since running from `BUILD_DIR` itself is now legitimate

### `test.py`
Tests reference the old `build/myrepo` checkout path and `build/target/built` artefact path; both must be updated throughout. The "run from within build dir" test and "target directory creation" test need repurposing:
- Test 5 (run from within build dir): change `cwd` to `build / "checkouts"` (or a subdirectory); running from `build` itself should now succeed
- Test 10 (target dir creation): repurpose to verify `checkouts/` is created automatically when absent (rather than a `target/` dir)

### `README.md`
Update "How It Works" to reflect `BUILD_DIR/checkouts/<repo-name>/` for the checkout and `BUILD_DIR` as the artefact directory.

## Tasks
- [ ] Update tests in `test.py` to reflect new paths and guard behaviour
- [ ] Run tests — expect failures (TDD baseline)
- [ ] Update `builder.py`: checkout path, remove `target`, update guard, pass `build_dir` to build script
- [ ] Run tests — expect all pass
- [ ] Update `README.md`
- [ ] Confirm implementation complete and ready to archive
