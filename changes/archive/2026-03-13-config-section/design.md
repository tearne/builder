# Design: Configuration Section in builder.py
**Status: Draft**

## Approach

Add a clearly delimited configuration section immediately after the imports, before any logic. Each variable is a plain Python string assignment with an inline example comment:

```python
# ==============================================================
# Configuration — fill in the values below to set up your build
# ==============================================================

BUILDER_REPO      = ""  # e.g. "https://github.com/org/myapp.git"
BUILDER_BRANCH    = ""  # e.g. "main"
BUILDER_BUILD_DIR = ""  # e.g. "/opt/build"
BUILDER_SCRIPT    = ""  # e.g. "build.sh"

# Variables required by your build script (add as many as needed):
BUILD_SCRIPT_VARS = {
    # "MY_VAR": "value",
}

# ==============================================================
```

After the section, any non-empty `BUILDER_*` value and all entries in `BUILD_SCRIPT_VARS` are written into `os.environ`, making them available to the build script as environment variables and taking precedence over any pre-existing shell values. Empty `BUILDER_*` strings are ignored, allowing env vars already in the shell to serve as a fallback.

The existing `os.environ.get(...)` reads that populate `REPO`, `BRANCH`, `BUILD_DIR`, and `BUILD_SCRIPT` are unchanged — they simply read from the now-updated environment.

The SPEC and error message that lists missing variables will continue to refer to the `BUILDER_*` names, since those remain the canonical identifiers.

## Tasks

1. ✓ Impl: Add the configuration section to `builder.py` and write non-empty values into `os.environ` before the existing `os.environ.get` reads.
2. ✓ Tests: Add a test that sets `BUILDER_*` values via the config section (not the environment) and verifies a successful build.
3. ✓ Tests: Add a test that sets a `BUILD_SCRIPT_VARS` entry and verifies it is present in the build script's environment.
4. ✓ Tests: Add a test that leaves config section values empty and verifies `BUILDER_*` env vars from the shell are used as fallback.
5. ✓ Verify: Run full test suite.
6. Process: Confirm ready to archive.
