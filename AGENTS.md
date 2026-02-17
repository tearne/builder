# AGENTS.md

## Project Overview
A single-file POS-style build script. See `SPEC.md` for the specification and `DEFNS.md` for definitions.

## Change Management Process
All changes to `SPEC.md` must follow this process:

### 1. Propose
Create `changes/<change-name>/proposal.md` with the following structure:

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

### 3. Apply
Apply the delta to `SPEC.md`. Do not modify `SPEC.md` without an approved proposal.

### 4. Archive
Move the change folder to `changes/archive/YYYY-MM-DD-<change-name>/`.

## Coding Conventions
- Follow the POS standard defined in `DEFNS.md`
