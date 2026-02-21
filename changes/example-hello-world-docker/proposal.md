# Example: Hello World Docker Build

## Status
Approved

## Intent
Provide an illustrative example of a project build script that users can reference when setting up their own builds. A minimal "hello world" Docker container keeps the example simple while demonstrating a realistic use case.

## Scope
- **In scope**: An `examples/hello-world-docker/` directory containing a `run.sh`, a `build.sh`, and a minimal `Dockerfile`; `examples/hello-world-docker/target/` as the build directory (gitignored); renaming the `BUILDER_BUILD` env var to `BUILDER_BUILD_DIR` for consistency with the `BUILD_DIR` config variable
- **Out of scope**: Production Docker patterns, multi-stage builds, CI/CD integration

## Delta

### ADDED
- `examples/hello-world-docker/run.sh` — sets `BUILDER_*` env vars (repo: the builder repo itself via a relative path, branch: `main`, build dir: `examples/hello-world-docker/target`, script: `examples/hello-world-docker/build.sh`) and invokes `../../builder.py`
- `examples/hello-world-docker/build.sh` — builds a minimal hello world Docker container, writing output to the target directory
- `examples/hello-world-docker/Dockerfile` — minimal Dockerfile for the hello world image
- `examples/hello-world-docker/target/` added to `.gitignore`

### MODIFIED
- **Env var**: `BUILDER_BUILD` → `BUILDER_BUILD_DIR` in `builder.py`, `test.py`, and `SPEC.md`
