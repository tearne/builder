#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# ///

import argparse
import os
import subprocess
import sys
from functools import partial
from pathlib import Path

print = partial(print, flush=True)

VERSION = "1.0.0"

# ==============================================================
# Configuration — fill in the values below to set up your build
# ==============================================================

BUILDER_REPO      = ""  # e.g. "https://github.com/org/myapp.git"
BUILDER_BRANCH    = ""  # e.g. "main"
BUILDER_BUILD_DIR = ""  # e.g. "/opt/build"
BUILDER_SCRIPT    = ""  # e.g. "build.sh"

# Variables required by your build script (add as many as needed):
BUILD_SCRIPT_VARS = {
    # "MY_VAR": "value",
}

# ==============================================================

for _k, _v in {
    "BUILDER_REPO": BUILDER_REPO,
    "BUILDER_BRANCH": BUILDER_BRANCH,
    "BUILDER_BUILD_DIR": BUILDER_BUILD_DIR,
    "BUILDER_SCRIPT": BUILDER_SCRIPT,
}.items():
    if _v:
        os.environ[_k] = _v
for _k, _v in BUILD_SCRIPT_VARS.items():
    os.environ[_k] = _v

REPO = os.environ.get("BUILDER_REPO", "")
BRANCH = os.environ.get("BUILDER_BRANCH", "")
BUILD_DIR = os.environ.get("BUILDER_BUILD_DIR", "")
BUILD_SCRIPT = os.environ.get("BUILDER_SCRIPT", "")


def main():
    parser = argparse.ArgumentParser(
        description="Clones (or updates) a git repo and runs its build script. "
                    "Configure the required variables in the configuration section near the top of this file."
    )
    parser.add_argument("--version", action="version", version=VERSION)
    parser.parse_args()

    cwd = Path.cwd()
    missing = [
        name
        for name, value in (
            ("BUILDER_REPO", REPO),
            ("BUILDER_BRANCH", BRANCH),
            ("BUILDER_BUILD_DIR", BUILD_DIR),
            ("BUILDER_SCRIPT", BUILD_SCRIPT),
        )
        if not value
    ]
    if missing:
        print(
            f"Error: missing required env var(s): {', '.join(missing)}", file=sys.stderr
        )
        sys.exit(2)

    build_dir = Path(os.path.abspath(BUILD_DIR))
    checkout = build_dir / "checkouts" / repo_name(REPO)
    checkouts_dir = build_dir / "checkouts"

    _check_gitignore(build_dir)

    if build_dir.exists():
        is_empty = not any(build_dir.iterdir())
        if not is_empty and not checkouts_dir.exists():
            print(
                f"Error: {build_dir} is not empty and has no checkouts directory. Review and clear it manually.",
                file=sys.stderr,
            )
            sys.exit(7)

    if cwd.is_relative_to(build_dir / "checkouts"):
        print(
            "Error: do not run this script from within the build directory.",
            file=sys.stderr,
        )
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
        print(
            f"Error: {BUILD_SCRIPT} not found or not executable in {checkout}.",
            file=sys.stderr,
        )
        sys.exit(5)

    print(f"Running {BUILD_SCRIPT} ...")
    result = subprocess.run([f"./{BUILD_SCRIPT}", str(build_dir)], cwd=checkout)
    if result.returncode != 0:
        print(
            f"Error: {BUILD_SCRIPT} failed with exit code {result.returncode}.",
            file=sys.stderr,
        )
        sys.exit(6)

    print("Build complete.")


def _check_gitignore(build_dir: Path) -> None:
    anchor = build_dir
    while not anchor.exists() and anchor != anchor.parent:
        anchor = anchor.parent

    in_repo = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=anchor,
        capture_output=True,
    )
    if in_repo.returncode != 0:
        return

    repo_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=anchor,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    ignored = subprocess.run(
        ["git", "check-ignore", "-q", str(build_dir.relative_to(repo_root)) + "/"],
        cwd=repo_root,
        capture_output=True,
    )
    if ignored.returncode != 0:
        gitignore_entry = str(build_dir.relative_to(repo_root)) + "/"
        print(
            f"Error: {build_dir} is inside a git repository but is not covered by .gitignore.\n"
            "Build artifacts and checkouts must not be accidentally committed.\n"
            f"Add the following line to {repo_root / '.gitignore'} before proceeding:\n"
            f"  {gitignore_entry}",
            file=sys.stderr,
        )
        sys.exit(8)


def _clone(checkout: Path) -> None:
    result = subprocess.run(
        ["git", "clone", "--branch", BRANCH, REPO, "."], cwd=checkout
    )
    if result.returncode != 0:
        print("Error: git operation failed.", file=sys.stderr)
        sys.exit(4)


def _verify_and_ff(checkout: Path) -> None:
    r_url = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=checkout,
        capture_output=True,
        text=True,
    )
    r_branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=checkout,
        capture_output=True,
        text=True,
    )
    r_status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=checkout,
        capture_output=True,
        text=True,
    )

    if r_url.stdout.strip() != REPO or r_branch.stdout.strip() != BRANCH:
        print(
            f"Error: {checkout} does not match expected repo/branch or cannot be fast-forwarded. Review and clear it manually.",
            file=sys.stderr,
        )
        sys.exit(3)

    if r_status.stdout.strip():
        print(
            f"Error: {checkout} has uncommitted changes. Review and clear it manually.",
            file=sys.stderr,
        )
        sys.exit(3)

    r_fetch = subprocess.run(["git", "fetch", "origin"], cwd=checkout)
    if r_fetch.returncode != 0:
        print("Error: git operation failed.", file=sys.stderr)
        sys.exit(4)

    r_merge = subprocess.run(
        ["git", "merge", "--ff-only", f"origin/{BRANCH}"], cwd=checkout
    )
    if r_merge.returncode != 0:
        print(
            f"Error: {checkout} does not match expected repo/branch or cannot be fast-forwarded. Review and clear it manually.",
            file=sys.stderr,
        )
        sys.exit(3)


def repo_name(url: str) -> str:
    return url.rstrip("/").split("/")[-1].removesuffix(".git")


if __name__ == "__main__":
    if not os.environ.get("VIRTUAL_ENV"):
        print(
            "Error: no virtual environment detected. Run this script via './<script-name>' (requires uv), or activate a virtual environment first.",
            file=sys.stderr,
        )
        sys.exit(100)
    main()
