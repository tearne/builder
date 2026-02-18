# Rename build.py to builder.py

## Intent
`build.py` risks confusion with the user's own `build.sh` that the script invokes. `builder.py` reflects the project name and makes the distinction clear.

## Scope
- **In scope**: renaming the script file
- **Out of scope**: behavioural changes, changes to `build.sh` or any other file

## Delta

### MODIFIED
- Script filename: `build.py` → `builder.py`
