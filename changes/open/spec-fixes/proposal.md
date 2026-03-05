# Proposal: Spec Fixes
**Status: Approved**

## Intent
Fix inconsistencies between spec and implementation.

## Specification Deltas

### MODIFIED
- **Build script** (Usage line 14): Remove default, require BUILDER_SCRIPT env var to be set.
- **Configuration validation** (Error Handling): Add meaningful errors for missing required env vars.
- **Build directory** (Usage line 13): Change from "must already exist" to "is created if needed" to match implementation.
- **Build directory safety** (Error Handling): Add check that build dir only contains expected checkouts subdirectory; fail if other files present.
- **Configuration section** (Usage lines 11-14): Remove `<placeholder>` notation, simplify to just env var names with descriptions.
- **builder.py defaults** (lines 14-18): Remove `<placeholder>` notation from code. Update defaults to be sensible (empty string or actual defaults like "build.sh").
 - **Dirty checkout** (Error Handling): If checkout has uncommitted changes, exit with a clear error before fast-forward.

### ADDED
- **Test workspace** (Constraints section): Add note about `target/test` temp dir structure for tests.

## Scope
- Fix default value in builder.py to match spec (default to "build.sh")
- Add test for build directory safety
