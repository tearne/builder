#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# ///

import os
import subprocess
import sys
from functools import partial
from pathlib import Path

print = partial(print, flush=True)

# --- Configuration — Set BUILDER_* env vars or <hard code>---
REPO         = os.environ.get("BUILDER_REPO",      "<repo>")
BRANCH       = os.environ.get("BUILDER_BRANCH",    "<branch>")
BUILD_DIR    = os.environ.get("BUILDER_BUILD_DIR", "<build>")
BUILD_SCRIPT = os.environ.get("BUILDER_SCRIPT",    "<build-script>")

def main():
    cwd       = Path.cwd()
    build_dir = Path(os.path.abspath(BUILD_DIR))
    checkout  = build_dir / "checkouts" / repo_name(REPO)

    if cwd.is_relative_to(build_dir / "checkouts"):
        print("Error: do not run this script from within the build directory.", file=sys.stderr)
        sys.exit(1)

    if not checkout.exists():
        checkout.mkdir(parents=True)
        print(f"Cloning {REPO} into {checkout} ...")
        _clone(checkout)
    elif not any(checkout.iterdir()):
        print(f"Cloning {REPO} into {checkout} ...")
        _clone(checkout)
    else:
        print(f"Updating {checkout} ...")
        _verify_and_ff(checkout)

    build_sh = checkout / BUILD_SCRIPT
    if not build_sh.exists() or not os.access(build_sh, os.X_OK):
        print(f"Error: {BUILD_SCRIPT} not found or not executable in {checkout}.", file=sys.stderr)
        sys.exit(5)

    print(f"Running {BUILD_SCRIPT} ...")
    result = subprocess.run([f"./{BUILD_SCRIPT}", str(build_dir)], cwd=checkout)
    if result.returncode != 0:
        print(f"Error: {BUILD_SCRIPT} failed with exit code {result.returncode}.", file=sys.stderr)
        sys.exit(6)

    print("Build complete.")


def _clone(checkout: Path) -> None:
    result = subprocess.run(["git", "clone", "--branch", BRANCH, REPO, "."], cwd=checkout)
    if result.returncode != 0:
        print("Error: git operation failed.", file=sys.stderr)
        sys.exit(4)


def _verify_and_ff(checkout: Path) -> None:
    r_url    = subprocess.run(["git", "remote", "get-url", "origin"], cwd=checkout, capture_output=True, text=True)
    r_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],  cwd=checkout, capture_output=True, text=True)

    if r_url.stdout.strip() != REPO or r_branch.stdout.strip() != BRANCH:
        print(f"Error: {checkout} does not match expected repo/branch or cannot be fast-forwarded. Review and clear it manually.", file=sys.stderr)
        sys.exit(3)

    r_fetch = subprocess.run(["git", "fetch", "origin"], cwd=checkout)
    if r_fetch.returncode != 0:
        print("Error: git operation failed.", file=sys.stderr)
        sys.exit(4)

    r_merge = subprocess.run(["git", "merge", "--ff-only", f"origin/{BRANCH}"], cwd=checkout)
    if r_merge.returncode != 0:
        print(f"Error: {checkout} does not match expected repo/branch or cannot be fast-forwarded. Review and clear it manually.", file=sys.stderr)
        sys.exit(3)


def repo_name(url: str) -> str:
    return url.rstrip("/").split("/")[-1].removesuffix(".git")


if __name__ == "__main__":
    if not os.environ.get("VIRTUAL_ENV"):
        print("Error: no virtual environment detected. Run this script via './<script-name>' (requires uv), or activate a virtual environment first.", file=sys.stderr)
        sys.exit(100)
    main()
