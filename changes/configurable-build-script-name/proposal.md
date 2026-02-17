# Configurable Build Script Name

## Status
Ready

## Intent
The build script name is currently hardcoded as `build.sh`. Different repositories may use different names for their build scripts (e.g. `make.sh`, `deploy.sh`). Making this configurable allows the tool to work with a wider range of projects without requiring repos to rename their scripts.

## Scope
- **In scope**: Adding a configuration variable for the build script name; updating behaviour, error handling, and verification references accordingly
- **Out of scope**: Changing how the script is invoked (still executed from `<build>/<repo-name>` with `<build>/target` as argument)

## Delta

### ADDED
- **Configuration**: New variable **Build script** (`<build-script>`) specifying the filename of the build script to execute within the checked-out repository. Defaults to `build.sh`.

### MODIFIED
- **Behaviour** (line 29): `build.sh` → `<build-script>` in the execution step
- **Error Handling** (exit code 5): Condition and message reference `<build-script>` instead of `build.sh`
- **Error Handling** (exit code 6): Message references `<build-script>` instead of `build.sh`
- **Verification** (tests 1, 2, 3, 8, 9): References to `build.sh` updated to `<build-script>`
