# Overview
This project contains a single template script for building software from a git repo, as a simpler and more flexible alternative to GitHub self-hosted runners. It's well suited to cases where builds are not so frequent that they must be automated.

# Usage
## Prerequisites
Ensure `uv` is installed - it will manage the Python installation within a virtual environment.

## Configuration
Set the required configuration via environment variables:

- **BUILDER_REPO** — repository URL accepted by `git` (assumed to be either public, or for git user credentials to already be set up on the server). The checkout directory name (repo name derived from the URL) follows `git clone` conventions (e.g. `https://github.com/org/myapp.git` → `myapp`).
- **BUILDER_BRANCH** — branch to be built.
- **BUILDER_BUILD_DIR** — build directory; artifacts are placed here and checkouts go in the `checkouts/` subdirectory. The directory is created if needed.
- **BUILDER_SCRIPT** — filename of the script to execute within the checked-out repository.

## Execution
Run `./builder.py` from any location outside the build directory `checkouts/` subdirectory.

## Behaviour
The script prints status messages to stdout as it progresses through each step.

- Checks the status of the checkout directory under `checkouts/` for the repo:
  - If it doesn't exist, it creates it, checks out the correct branch and continues.
  - If it's empty, it checks out the correct branch and continues.
  - If it's not empty, but contains the correct repo and branch, it fast-forwards to match origin.
  - Else (wrong repo, wrong branch, or cannot fast-forward) the script exits, suggesting the user reviews and clears the build directory.
- Passes through any `git` requests for credentials to the user during `fetch`/`pull` operations.
- Executes the build script from within the checkout directory (i.e. the working directory is the checkout), passing the build directory as the only argument.
- On success, prints a completion message.


## Error Handling
For each of the following conditions the script exits non-zero and prints a descriptive message to stderr:

- Script is run from within the build directory `checkouts/` subdirectory
- Script is run directly instead of via `uv`
- Required configuration env vars are missing
- Build directory is not empty and has no `checkouts/` subdirectory
- Checkout has uncommitted changes
- Checkout repo or branch are not as expected, or cannot be fast-forwarded to match origin
- `git clone` or `git fetch` fails (e.g. network error, auth failure)
- Build script is not found or not executable in the checkout
- Build script exits with a non-zero code

## Invariants
- `builder.py` never modifies the checkout directory beyond git operations — it only clones, pulls, or fast-forwards; it never edits, deletes, or commits files in the checkout.
- `builder.py` never modifies or deletes anything in the build directory directly — artifact placement is left entirely to the build script.
- `builder.py` never stores or handles credentials — git credential prompts are passed through to the user directly.
- The script is idempotent — running it twice in succession on a clean checkout produces the same result (assuming the build script is itself idempotent).

## Constraints
- Use the POS standard
- Tests use `target/test` as the base directory and expect the following structure:
  - `repos/` — contains bare git repos to clone from
  - `build/` — used as the build directory


## Verification
Tests use temporary local git repositories created on the filesystem. Since `git` accepts local paths as URLs, these repos can be used in place of remote URLs, avoiding any network dependency.

Each test run creates a temporary directory via `tempfile.mkdtemp(dir="target/test")`, giving each run an isolated workspace within a predictable location. The `target/` directory is gitignored.

1. **Fresh clone** — Run against a non-existent `<build>/checkouts/<repo-name>`. Verify it clones, runs `<build-script>`, and exits 0.
2. **Re-run on clean checkout** — Run again immediately after a successful build. Verify it fast-forwards and rebuilds successfully.
3. **Empty directory** — Create an empty `<build>/checkouts/<repo-name>` directory manually, then run. Verify it clones into it and builds.
4. **Wrong repo/branch or dirty checkout** — Modify a file in `<build>/checkouts/<repo-name>` (or check out a different branch), then run. Verify non-zero exit and stderr output.
5. **Run from within checkouts directory** — Run the script from inside `<build>/checkouts/`. Verify non-zero exit and stderr output.
6. **Run directly with Python** — Run via `python3 builder.py` instead of `./builder.py`. Verify non-zero exit and stderr output.
7. **Git failure** — Run with a non-existent local repo path. Verify non-zero exit and stderr output.
8. **Missing `<build-script>`** — Remove or `chmod -x` `<build-script>` in the repo. Verify non-zero exit and stderr output.
9. **Failing `<build-script>`** — Use a `<build-script>` that exits non-zero. Verify non-zero exit and stderr output.
10. **Checkouts directory creation** — Run with no pre-existing `<build>/checkouts/`. Verify it gets created before `build.sh` executes.
11. **Status messages** — Verify stdout contains progress messages at each step.
12. **Credential passthrough** — Manual verification only (cannot be tested with local repos). Run against a private remote repo without cached credentials. Verify git prompts for credentials.
