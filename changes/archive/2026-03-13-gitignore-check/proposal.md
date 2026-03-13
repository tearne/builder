# Proposal: Gitignore Check for BUILD_DIR
**Status: Approved**

## Intent
When `BUILDER_BUILD_DIR` is located inside a git repository, artifacts and checkouts placed there risk being accidentally committed. The builder should detect this situation and warn the user if `BUILD_DIR` is not covered by a `.gitignore` entry in the containing repository.

## Specification Deltas

### ADDED
- If `BUILD_DIR` is located within a git repository, the builder checks that it is covered by that repository's `.gitignore` rules. If it is not, the script exits non-zero with an error message that explains why the build directory must be gitignored (to prevent build artifacts and checkouts from being accidentally committed) and instructs the user to add it before proceeding.
- New error condition: Build directory is inside a git repository but not covered by `.gitignore`.
