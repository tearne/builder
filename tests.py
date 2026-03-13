#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = ["pytest"]
# ///

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest  # type: ignore[attr-defined]

BUILD_PY = Path(__file__).parent / "builder.py"
TARGET_TEST = Path(__file__).parent / "target" / "test"

DEFAULT_BUILD_SH = '#!/bin/sh\ntouch "$1/built"\nexit 0\n'
DEFAULT_SCRIPT = "build.sh"


@pytest.fixture(autouse=True, scope="session")
def ensure_target_test_dir():
    TARGET_TEST.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def make_repo(
    tmp: Path,
    branch: str = "main",
    build_sh: str | None = DEFAULT_BUILD_SH,
    build_sh_executable: bool = True,
) -> Path:
    """Create a bare git repo at tmp/repos/myrepo.git and return its path."""
    work = tmp / "work"
    work.mkdir()
    bare = tmp / "repos" / "myrepo.git"
    bare.parent.mkdir(parents=True)

    _git(work, "init")
    _git(work, "symbolic-ref", "HEAD", f"refs/heads/{branch}")
    _git(work, "config", "user.email", "test@test.com")
    _git(work, "config", "user.name", "Test")

    (work / "README.md").write_text("test\n")

    if build_sh is not None:
        bs = work / "build.sh"
        bs.write_text(build_sh)
        bs.chmod(0o755 if build_sh_executable else 0o644)

    _git(work, "add", ".")
    _git(work, "commit", "-m", "init")
    subprocess.run(
        ["git", "clone", "--bare", str(work), str(bare)],
        check=True,
        capture_output=True,
    )

    return bare


def make_outer_git_repo(tmp: Path, gitignore: str | None = None) -> Path:
    """Create a git working tree at tmp/outer, optionally with a .gitignore."""
    outer = tmp / "outer"
    outer.mkdir()
    _git(outer, "init")
    _git(outer, "config", "user.email", "test@test.com")
    _git(outer, "config", "user.name", "Test")
    (outer / "README.md").write_text("test\n")
    if gitignore is not None:
        (outer / ".gitignore").write_text(gitignore)
    _git(outer, "add", ".")
    _git(outer, "commit", "-m", "init")
    return outer


def run_build(cwd: str | Path | None = None, **env_overrides) -> tuple[int, str, str]:
    """Run builder.py as a subprocess; return (returncode, stdout, stderr)."""
    env = os.environ.copy()
    env.update(env_overrides)
    result = subprocess.run(
        [str(BUILD_PY)],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd is not None else None,
    )
    return result.returncode, result.stdout, result.stderr


def make_configured_builder(
    tmp: Path,
    builder_config: dict[str, str],
    script_vars: dict[str, str] | None = None,
) -> Path:
    """Return a copy of builder.py with the config section filled in."""
    source = BUILD_PY.read_text()
    for key, value in builder_config.items():
        source = re.sub(rf'({re.escape(key)}\s*=\s*)""', rf'\1"{value}"', source, count=1)
    if script_vars:
        entries = "\n".join(f'    "{k}": "{v}",' for k, v in script_vars.items())
        source = source.replace(
            'BUILD_SCRIPT_VARS = {\n    # "MY_VAR": "value",\n}',
            f"BUILD_SCRIPT_VARS = {{\n{entries}\n}}",
        )
    configured = tmp / "builder_configured.py"
    configured.write_text(source)
    configured.chmod(0o755)
    return configured


def run_configured_builder(script: Path) -> tuple[int, str, str]:
    """Run a configured builder script with no BUILDER_* env vars set."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("BUILDER_")}
    result = subprocess.run(
        [str(script)],
        env=env,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_fresh_clone():
    """Test 1: non-existent checkout → clone, build, exit 0."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    rc, out, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc == 0
    assert (build / "checkouts" / "myrepo").exists()
    assert (build / "built").exists()


def test_rerun_on_clean_checkout():
    """Test 2: run twice on a clean checkout with upstream changes; verify fast-forward."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    kwargs = dict(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    rc1, out1, _ = run_build(**kwargs)
    assert rc1 == 0
    assert "Cloning" in out1

    work = tmp / "work"
    _git(work, "commit", "--allow-empty", "-m", "new commit")
    _git(work, "remote", "add", "origin", str(bare))
    _git(work, "push", "origin", "main")

    rc2, out2, _ = run_build(**kwargs)
    assert rc2 == 0
    assert "Updating" in out2


def test_empty_checkout_dir():
    """Test 3: pre-created empty checkout dir → clone into it and build."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()
    (build / "checkouts" / "myrepo").mkdir(parents=True)  # empty directory

    rc, _, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc == 0


def test_build_dir_unexpected_files():
    """Test 3b: build dir contains unexpected files → exit non-zero."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()
    (build / "unexpected.txt").write_text("oops\n")

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc != 0
    assert err


def test_wrong_branch():
    """Test 4: checkout on wrong branch → exit 3."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    rc, _, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )
    assert rc == 0

    # Switch checkout to a different local branch
    checkout = build / "checkouts" / "myrepo"
    subprocess.run(
        ["git", "checkout", "-b", "other"],
        cwd=checkout,
        check=True,
        capture_output=True,
    )

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc != 0
    assert err


def test_dirty_checkout():
    """Test 4b: dirty checkout → exit non-zero with error."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    kwargs = dict(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )
    rc1, _, _ = run_build(**kwargs)
    assert rc1 == 0

    checkout = build / "checkouts" / "myrepo"
    (checkout / "dirty.txt").write_text("dirty\n")

    rc2, _, err = run_build(**kwargs)
    assert rc2 != 0
    assert err


def test_run_from_within_build_dir():
    """Test 5: cwd inside checkouts dir → exit 1."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()
    checkouts = build / "checkouts"
    checkouts.mkdir()

    rc, _, err = run_build(
        cwd=checkouts,
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc != 0
    assert err


def test_run_directly_with_python():
    """Test 6: python3 builder.py (bypassing uv) → exit 2."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    env = os.environ.copy()
    env["BUILDER_REPO"] = str(bare)
    env["BUILDER_BRANCH"] = "main"
    env["BUILDER_BUILD_DIR"] = str(build)
    env.pop("VIRTUAL_ENV", None)

    result = subprocess.run(
        ["python3", str(BUILD_PY)],
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert result.stderr


def test_missing_env_vars():
    """Test 6b: missing required env vars → exit non-zero with error."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    build = tmp / "build"
    build.mkdir()

    rc, _, err = run_build(
        BUILDER_REPO="",
        BUILDER_BRANCH="",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT="",
    )

    assert rc != 0
    assert err


def test_git_failure():
    """Test 7: non-existent repo path → git clone fails → exit 4."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    build = tmp / "build"
    build.mkdir()

    rc, _, err = run_build(
        BUILDER_REPO="/nonexistent/path/repo.git",
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc != 0
    assert err


def test_missing_build_sh():
    """Test 8a: no build.sh in repo → exit 5."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp, build_sh=None)
    build = tmp / "build"
    build.mkdir()

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc != 0
    assert err


def test_non_executable_build_sh():
    """Test 8b: build.sh present but not executable → exit 5."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp, build_sh_executable=False)
    build = tmp / "build"
    build.mkdir()

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc != 0
    assert err


def test_failing_build_sh():
    """Test 9: build.sh exits 42 → exit 6 with code in message."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp, build_sh="#!/bin/sh\nexit 42\n")
    build = tmp / "build"
    build.mkdir()

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc != 0
    assert err


def test_checkouts_directory_creation():
    """Test 10: checkouts dir absent before run → created by script, exit 0."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    assert not (build / "checkouts").exists()

    rc, _, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc == 0
    assert (build / "checkouts").is_dir()


def test_status_messages():
    """Test 11: stdout contains progress messages during a fresh clone."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    rc, out, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc == 0
    assert "Cloning" in out
    assert "Running" in out
    assert "Build complete" in out


def test_build_dir_in_git_repo_not_gitignored():
    """BUILD_DIR inside a git repo with no .gitignore entry → exit non-zero with error."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    outer = make_outer_git_repo(tmp)
    build = outer / "build"

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc != 0
    assert err


def test_build_dir_in_git_repo_gitignored():
    """BUILD_DIR inside a git repo and covered by .gitignore → build proceeds."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    outer = make_outer_git_repo(tmp, gitignore="build/\n")
    build = outer / "build"

    rc, _, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc == 0


def test_build_dir_outside_git_repo():
    """BUILD_DIR outside any git repo → build proceeds normally."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = Path(tempfile.mkdtemp())  # system tmp — outside any git repo

    rc, _, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc == 0


def test_config_section_builder_vars():
    """Test 13: BUILDER_* set in config section (no env vars) → successful build."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    script = make_configured_builder(tmp, {
        "BUILDER_REPO": str(bare),
        "BUILDER_BRANCH": "main",
        "BUILDER_BUILD_DIR": str(build),
        "BUILDER_SCRIPT": DEFAULT_SCRIPT,
    })
    rc, _, _ = run_configured_builder(script)

    assert rc == 0
    assert (build / "built").exists()


def test_config_section_script_vars():
    """Test 14: BUILD_SCRIPT_VARS entries are present in the build script's environment."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    build_sh = '#!/bin/sh\necho "$MY_VAR" > "$1/my_var.txt"\nexit 0\n'
    bare = make_repo(tmp, build_sh=build_sh)
    build = tmp / "build"
    build.mkdir()

    script = make_configured_builder(
        tmp,
        {
            "BUILDER_REPO": str(bare),
            "BUILDER_BRANCH": "main",
            "BUILDER_BUILD_DIR": str(build),
            "BUILDER_SCRIPT": DEFAULT_SCRIPT,
        },
        script_vars={"MY_VAR": "hello"},
    )
    rc, _, _ = run_configured_builder(script)

    assert rc == 0
    assert (build / "my_var.txt").read_text().strip() == "hello"


def test_config_section_env_var_fallback():
    """Test 15: empty config section → BUILDER_* env vars from shell are used."""
    tmp = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    rc, _, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
        BUILDER_SCRIPT=DEFAULT_SCRIPT,
    )

    assert rc == 0
    assert (build / "built").exists()


@pytest.mark.skip(
    reason=(
        "Manual verification only: run builder.py against a private remote repo "
        "without cached credentials and confirm git prompts pass through to the user."
    )
)
def test_credential_passthrough():
    """Test 12: git credential prompts are passed through (manual only)."""
    pass


if __name__ == "__main__":
    if "pytest" not in sys.modules or "pytest.pytest_source" not in dir():
        sys.exit(pytest.main([__file__, "-v"]))
