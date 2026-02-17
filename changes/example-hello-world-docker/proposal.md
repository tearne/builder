# Example: Hello World Docker Build

## Status
Draft

### Unresolved
- How the example is run — should the user copy `build.py` and edit the configuration variables, or should `build.py` accept a configuration file / command-line argument pointing to a config?
- If a config file is introduced, what format (TOML, INI, plain shell variables)?
- Whether this change implies a modification to `build.py` itself (config file support) or is purely an example that works with the existing design

## Intent
Provide an illustrative example of a project build script that users can reference when setting up their own builds. A minimal "hello world" Docker container keeps the example simple while demonstrating a realistic use case.

## Scope
- **In scope**: An `examples/hello-world-docker/` directory containing a `build.sh` (or `<build-script>`) and a minimal Dockerfile; documentation on how to run the example
- **Out of scope**: Production Docker patterns, multi-stage builds, CI/CD integration

## Delta

### ADDED
- `examples/hello-world-docker/build.sh` — builds a minimal hello world Docker container into the target directory
- `examples/hello-world-docker/Dockerfile` — minimal Dockerfile
- Documentation or instructions for running the example (details pending resolution of unresolved items above)
