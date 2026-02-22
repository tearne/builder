# Proposal: Checkouts Subdir
**Status: Ready for Review**

## Intent
The current layout places checkouts directly in `BUILD_DIR/<repo-name>/` and passes `BUILD_DIR/target/` to the build script as the artefact directory. This means setting `BUILDER_BUILD_DIR=/some/path` results in artefacts landing at `/some/path/target/`, which is surprising — users expect artefacts to appear in the directory they configured.

The fix is to invert the layout: checkouts move into `BUILD_DIR/checkouts/<repo-name>/` (an internal detail), and `BUILD_DIR` itself is passed to the build script as the artefact directory.

## Scope
- **In scope**: directory layout used by `builder.py`; corresponding updates to `example/build.sh`, `run_example.sh`, `SPEC.md`, and `README.md`
- **Out of scope**: changes to configuration variables or their names

## Delta

### MODIFIED
- Checkout directory: `BUILD_DIR/<repo-name>/` → `BUILD_DIR/checkouts/<repo-name>/`
- Artefact directory passed to build script: `BUILD_DIR/target/` → `BUILD_DIR`
- Guard against running from within build directory now checks `BUILD_DIR/checkouts/` (since `BUILD_DIR` itself may be a parent of the working directory in normal use)
