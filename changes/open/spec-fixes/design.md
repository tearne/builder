# Design: Spec Fixes
**Status: Draft**

## Approach
Fix spec inconsistencies and add safety checks.

## Tasks
1. ✓ Tests: Update test_rerun_on_clean_checkout to verify fast-forward occurs
2. ✓ Tests: Add test for build directory safety (fail on unexpected files)
3. ✓ Tests: Add test for missing env vars (meaningful error)
4. ✓ Impl: Add env var validation with meaningful errors
5. ✓ Impl: Remove BUILD_SCRIPT default (require env var)
6. ✓ Impl: Remove <placeholder> notation from builder.py defaults
7. ✓ Impl: Add build directory safety check
8. ✓ Spec: Update SPEC.md with all changes
9. ✓ Verify: Run tests to confirm fix works
10. Process: Confirm ready to archive
