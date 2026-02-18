# Overview
This project contains a single template script for building software from a git repo, as a simpler and more flexible alternative to GitHub self-hosted runners. It's well suited to cases where builds are not so frequent that they must be automated.

# Usage
## Prerequisites
Ensure `uv` is installed - it will manage the Python installation within a virtual environment.

## Configuration
Add the following details to the relevant variables at top of the builder.py script.

- **Repository** URL (`<repo>`), a full URL accepted by `git` (assumed to be either public, or for git user credentials to already be set up on the server). The checkout directory name (`<repo-name>`) is derived from the URL as `git clone` would (e.g. `https://github.com/org/myapp.git` → `myapp`).
- **Branch** (`<branch>`) to be built.
- **Build directory** (`<build>`) where the code will be checked out and artifacts prepared. Must already exist.

## Execution
Run `./builder.py` from any location outside the `<build>`.

## Behaviour
The script prints status messages to stdout as it progresses through each step.

- Checks the status of the directory `<build>/<repo-name>`:
  - If it doesn't exist, it creates it, checks out the correct branch and continues.
  - If it's empty, it checks out the correct branch and continues.
  - If it's not empty, but contains the correct `<repo>` and `<branch>`, it fast-forwards to match origin.
  - Else (wrong repo, wrong branch, or cannot fast-forward) the script exits, suggesting the user reviews and clears the build directory.
- Passes through any `git` requests for credentials to the user during `fetch`/`pull` operations.
- Ensures `<build>/target` exists, creating it if necessary.
- Executes `<build>/<repo-name>/build.sh` from within `<build>/<repo-name>` (i.e. the working directory is the checkout), passing in a single argument the build target directory of `<build>/target`.
- On success, prints a completion message.


## Error Handling
The script exits with a non-zero code and prints a message to stderr for the following error situations:

| Exit Code | Condition | Message |
|-----------|-----------|---------|
| 1 | Script is run from within `<build>` | `Error: do not run this script from within the build directory.` |
| 2 | Script is run directly instead of via `uv` | `Error: run this script via './<script>', not directly.` |
| 3 | `<build>/<repo-name>` repo or branch are not as expected, or cannot be fast-forwarded to match origin | `Error: <build>/<repo-name> does not match expected repo/branch or cannot be fast-forwarded. Review and clear it manually.` |
| 4 | `git clone` or `git pull` fails (e.g. network error, auth failure) | `Error: git operation failed.` |
| 5 | `<build>/<repo-name>/build.sh` is not found or not executable | `Error: build.sh not found or not executable in <build>/<repo-name>.` |
| 6 | `build.sh` exits with a non-zero code | `Error: build.sh failed with exit code <N>.` |

## Invariants
- `builder.py` never modifies `<build>/<repo-name>` beyond git operations — it only clones, pulls, or fast-forwards; it never edits, deletes, or commits files in the checkout.
- `builder.py` never deletes `<build>/target` — it ensures the directory exists but leaves cleanup/management to `build.sh`.
- `builder.py` never stores or handles credentials — git credential prompts are passed through to the user directly.
- The script is idempotent — running it twice in succession on a clean checkout produces the same result (assuming `build.sh` is itself idempotent).

## Constraints
- Use the POS standard (see `DEFNS.md`)


## Verification
Tests use temporary local git repositories created on the filesystem. Since `git` accepts local paths as URLs, these repos can be used in place of remote URLs, avoiding any network dependency.

Each test run creates a temporary directory via `tempfile.mkdtemp(dir="target/test")`, giving each run an isolated workspace within a predictable location. The `target/` directory is gitignored. Within each temp directory:
- `repos/` — contains bare git repos to clone from
- `build/` — used as the `<build>` directory

1. **Fresh clone** — Run against a non-existent `<build>/<repo-name>`. Verify it clones, runs `build.sh`, and exits 0.
2. **Re-run on clean checkout** — Run again immediately after a successful build. Verify it fast-forwards and rebuilds successfully.
3. **Empty directory** — Create an empty `<build>/<repo-name>` directory manually, then run. Verify it clones into it and builds.
4. **Wrong repo/branch or dirty checkout** — Modify a file in `<build>/<repo-name>` (or check out a different branch), then run. Verify exit code 3 with expected message.
5. **Run from within build directory** — Run the script from inside `<build>`. Verify exit code 1.
6. **Run directly with Python** — Run via `python3 builder.py` instead of `./builder.py`. Verify exit code 2.
7. **Git failure** — Run with a non-existent local repo path. Verify exit code 4.
8. **Missing `build.sh`** — Remove or `chmod -x` the `build.sh` in the repo. Verify exit code 5.
9. **Failing `build.sh`** — Use a `build.sh` that exits non-zero. Verify exit code 6 with the correct code reported.
10. **Target directory creation** — Delete `<build>/target` before running. Verify it gets created before `build.sh` executes.
11. **Status messages** — Verify stdout contains progress messages at each step.
12. **Credential passthrough** — Manual verification only (cannot be tested with local repos). Run against a private remote repo without cached credentials. Verify git prompts for credentials.
