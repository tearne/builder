# Proposal: Configuration Section in builder.py
**Status: Approved**

## Intent
Currently, users must set `BUILDER_*` environment variables externally (e.g. in a shell profile or wrapper script). There is no obvious place in `builder.py` itself to configure the build, and no provision for build-script-specific variables. A dedicated configuration section near the top of the file would make it immediately clear where values should be set, and give users a natural home for any additional variables their build script requires.

## Specification Deltas

### ADDED
- `builder.py` contains a clearly marked configuration section near the top of the file where users can set values for the required `BUILDER_*` variables and any variables needed by their build script.
- Variable values in the configuration section are set using plain string assignments (e.g. `BUILDER_REPO = "https://..."`), requiring no Python knowledge to fill in.
- The configuration section includes a `BUILD_SCRIPT_VARS` dictionary where users can add build-script-specific variables as `"KEY": "value"` entries; all entries are loaded into the environment before the build script runs.
- The configuration section is the intended customisation point — the rest of the script is not expected to be edited by users.
- Values set in the configuration section take precedence over any same-named environment variables already present in the shell.

### MODIFIED
- Usage — Configuration: notes that values may be set directly in the configuration section of `builder.py` rather than as external environment variables.
