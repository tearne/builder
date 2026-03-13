# Proposal: Version Number
**Status: Approved**

## Intent
`builder.py` has no version number, making it difficult to tell which copy is deployed on a server, whether it is up to date, or what changed between copies.

## Specification Deltas

### ADDED
- `builder.py` carries a version number, visible near the top of the file.
- The initial version is `1.0.0`.
- Running `./builder.py --version` prints the version number and exits 0.
