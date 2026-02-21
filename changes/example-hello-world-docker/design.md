# Design: Example Hello World Docker Build

## Status
Approved

## Approach

All files live under `examples/hello-world-docker/`.

**`run.sh`** — a POS-style shell script that sets the four `BUILDER_*` env vars and execs `../../builder.py`. Uses a path relative to the script's own location (`$(dirname "$0")`) so it works regardless of where the user invokes it from. `BUILDER_REPO` points to the builder repo root (`$EXAMPLE_DIR/../..`); `BUILDER_SCRIPT` is set to `examples/hello-world-docker/build.sh` so `builder.py` runs the correct script from within the cloned checkout.

**`build.sh`** — receives the target directory as `$1`. Builds a Docker image tagged `hello-world-builder`, then saves it as a `.tar` into the target directory. Kept minimal: just `docker build` and `docker save`.

**`Dockerfile`** — a single-stage image based on `alpine` that prints "Hello, World!" as its default command.

**`.gitignore`** — `examples/hello-world-docker/target/` is already covered by the existing root `target/` pattern, so no change is needed.

**`BUILDER_BUILD` → `BUILDER_BUILD_DIR`** — a simple string replacement across `builder.py`, `test.py`, and `SPEC.md`.

## Tasks

1. ~~Create `examples/hello-world-docker/Dockerfile`.~~ ✓
2. ~~Create `examples/hello-world-docker/build.sh`.~~ ✓
3. ~~Create `examples/hello-world-docker/run.sh`.~~ ✓ (needs update for `BUILDER_BUILD_DIR`)
4. ~~Verify `.gitignore` coverage.~~ ✓
5. Rename `BUILDER_BUILD` → `BUILDER_BUILD_DIR` in `builder.py`, `test.py`, and `SPEC.md`.
6. Update `run.sh` to use `BUILDER_BUILD_DIR`.
7. Run tests to verify.
