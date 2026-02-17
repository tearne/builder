# AGENTS.md

## Project Overview
A single-file POS-style build script. See `SPEC.md` for the specification and `DEFNS.md` for definitions.

## Spec Structure
- The **root** `SPEC.md` covers the project as a whole.
- **Subfolder** `SPEC.md` files are scoped to that component — they own their own requirements and tests.
- Subfolder specs inherit project-wide non-functional requirements (e.g. POS style from `DEFNS.md`) unless they explicitly override them.
- When assessing drift or planning changes, read **all** `SPEC.md` files, not just the root.

## Change Management Process
All changes to `SPEC.md` files must follow this process:

### 1. Propose
Create a proposal in the `changes/` directory co-located with the target `SPEC.md` (e.g. `changes/<change-name>/proposal.md` for the root spec, or `<subfolder>/changes/<change-name>/proposal.md` for a subfolder spec).

```markdown
# <Change Name>

## Status (optional)
Draft | Ready

### Unresolved (optional, use with Draft)
- Items not yet fully specified

## Intent
Why this change is needed.

## Scope
- **In scope**: what this change covers
- **Out of scope**: what is deferred

## Delta

### ADDED
- New requirements being introduced

### MODIFIED
- Existing requirements being changed (note previous values)

### REMOVED
- Requirements being eliminated
```

Omit any empty delta sections (e.g. if nothing is removed, omit REMOVED).

### 2. Review
The proposal must be reviewed and approved before applying.

### 3. Plan
Add a `plan.md` to the change folder describing the technical approach. Keep lightweight.

### 4. Implement
Build the change. The target `SPEC.md` remains unchanged during implementation — the proposal's delta serves as the specification for what's being built.

### 5. Verify
Confirm the implementation satisfies the proposal's delta and any relevant verification steps from the spec.

### 6. Apply
Apply the delta to the co-located `SPEC.md` — **after** implementation, so the spec always reflects what's actually built. Pause between steps and invite the operator to review. Do not modify any `SPEC.md` without an approved proposal.

### 7. Archive
Move the change folder to the co-located `changes/archive/YYYY-MM-DD-<change-name>/`.

## Tests
- `uv run --with pytest pytest <path> -v` to run tests with pytest as an ad-hoc dependency.

## Coding Conventions
- Follow the POS standard defined in `DEFNS.md`
