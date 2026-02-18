# Configurable Build Script Name — Design

## Approach

A new `BUILD_SCRIPT` variable is added to the configuration block in `builder.py`, defaulting to `"build.sh"`. It follows the same pattern as `REPO`, `BRANCH`, and `BUILD`: a hardcoded default overridable via the `BUILDER_SCRIPT` environment variable.

Since `BUILDER_SCRIPT` (and the other `BUILDER_*` env vars) are now user-facing, the comment on the env-var override block is updated from "for test injection; does not change user-facing behaviour" to reflect that they are a supported configuration mechanism.

In `main()`, the three hardcoded `"build.sh"` strings (existence check, error message, and subprocess invocation) are replaced with `BUILD_SCRIPT`.

In `test.py`, the exit-5 message assertions currently check for the literal string `"build.sh not found or not executable"`. Since the message will now embed the configured script name, these assertions are loosened to check for `"not found or not executable"` only.

The SPEC's Configuration section is updated to document that all configuration variables can be set via `BUILDER_*` environment variables as an alternative to editing the script.

## Tasks
1. Add `BUILD_SCRIPT = "build.sh"` to the configuration block and `BUILDER_SCRIPT` env-var override in `builder.py`; update the env-var block comment
2. Replace hardcoded `build.sh` references in `main()` with `BUILD_SCRIPT`
3. Update exit-5 message assertions in `test_missing_build_sh` and `test_non_executable_build_sh` to not hardcode `build.sh`
4. Run tests to verify
