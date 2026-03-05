# Design: Spec Fixes
**Status: Draft**

## Approach
Fix spec inconsistencies and add safety checks.

## Tasks
1. ✓ Tests: Update test_rerun_on_clean_checkout to verify fast-forward occurs
2. ✓ Tests: Add test for build directory safety (fail on unexpected files)
3. ✓ Tests: Add test for missing env vars (meaningful error)
4. ✓ Tests: Add test for dirty checkout (fail before fast-forward)
5. ✓ Impl: Add env var validation with meaningful errors
6. ✓ Impl: Remove BUILD_SCRIPT default (require env var)
7. ✓ Impl: Remove <placeholder> notation from builder.py defaults
8. ✓ Impl: Add build directory safety check
9. ✓ Spec: Update SPEC.md with all changes
10. ✓ Verify: Run tests to confirm fix works
11. Process: Confirm ready to archive
