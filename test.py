import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

BUILD_PY    = Path(__file__).parent / "builder.py"
TARGET_TEST = Path(__file__).parent / "target" / "test"

DEFAULT_BUILD_SH = '#!/bin/sh\ntouch "$1/built"\nexit 0\n'


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
    subprocess.run(["git", "clone", "--bare", str(work), str(bare)], check=True, capture_output=True)

    return bare


def run_build(cwd: Path | None = None, **env_overrides) -> tuple[int, str, str]:
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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_fresh_clone():
    """Test 1: non-existent checkout → clone, build, exit 0."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    rc, out, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 0
    assert (build / "checkouts" / "myrepo").exists()
    assert (build / "built").exists()


def test_rerun_on_clean_checkout():
    """Test 2: run twice on a clean checkout; both exit 0."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    kwargs = dict(BUILDER_REPO=str(bare), BUILDER_BRANCH="main", BUILDER_BUILD_DIR=str(build))
    rc1, _, _ = run_build(**kwargs)
    rc2, _, _ = run_build(**kwargs)

    assert rc1 == 0
    assert rc2 == 0


def test_empty_checkout_dir():
    """Test 3: pre-created empty checkout dir → clone into it and build."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()
    (build / "checkouts" / "myrepo").mkdir(parents=True)  # empty directory

    rc, _, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 0


def test_wrong_branch():
    """Test 4: checkout on wrong branch → exit 3."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    rc, _, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )
    assert rc == 0

    # Switch checkout to a different local branch
    checkout = build / "checkouts" / "myrepo"
    subprocess.run(["git", "checkout", "-b", "other"], cwd=checkout, check=True, capture_output=True)

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 3
    assert "does not match" in err


def test_run_from_within_build_dir():
    """Test 5: cwd inside checkouts dir → exit 1."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()
    checkouts = build / "checkouts"
    checkouts.mkdir()

    rc, _, err = run_build(
        cwd=checkouts,
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 1
    assert "do not run this script from within the build directory" in err


def test_run_directly_with_python():
    """Test 6: python3 builder.py (bypassing uv) → exit 2."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    env = os.environ.copy()
    env["BUILDER_REPO"]   = str(bare)
    env["BUILDER_BRANCH"] = "main"
    env["BUILDER_BUILD_DIR"]  = str(build)
    env.pop("VIRTUAL_ENV", None)
    env.pop("UV_INTERNAL__PARENT_INTERPRETER", None)

    result = subprocess.run(
        ["python3", str(BUILD_PY)],
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "not directly" in result.stderr


def test_git_failure():
    """Test 7: non-existent repo path → git clone fails → exit 4."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    build = tmp / "build"
    build.mkdir()

    rc, _, err = run_build(
        BUILDER_REPO="/nonexistent/path/repo.git",
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 4
    assert "git operation failed" in err


def test_missing_build_sh():
    """Test 8a: no build.sh in repo → exit 5."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp, build_sh=None)
    build = tmp / "build"
    build.mkdir()

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 5
    assert "not found or not executable" in err


def test_non_executable_build_sh():
    """Test 8b: build.sh present but not executable → exit 5."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp, build_sh_executable=False)
    build = tmp / "build"
    build.mkdir()

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 5
    assert "not found or not executable" in err


def test_failing_build_sh():
    """Test 9: build.sh exits 42 → exit 6 with code in message."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp, build_sh="#!/bin/sh\nexit 42\n")
    build = tmp / "build"
    build.mkdir()

    rc, _, err = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 6
    assert "42" in err


def test_checkouts_directory_creation():
    """Test 10: checkouts dir absent before run → created by script, exit 0."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    assert not (build / "checkouts").exists()

    rc, _, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 0
    assert (build / "checkouts").is_dir()


def test_status_messages():
    """Test 11: stdout contains progress messages during a fresh clone."""
    tmp   = Path(tempfile.mkdtemp(dir=TARGET_TEST))
    bare  = make_repo(tmp)
    build = tmp / "build"
    build.mkdir()

    rc, out, _ = run_build(
        BUILDER_REPO=str(bare),
        BUILDER_BRANCH="main",
        BUILDER_BUILD_DIR=str(build),
    )

    assert rc == 0
    assert "Cloning" in out
    assert "Running" in out
    assert "Build complete" in out


@pytest.mark.skip(
    reason=(
        "Manual verification only: run builder.py against a private remote repo "
        "without cached credentials and confirm git prompts pass through to the user."
    )
)
def test_credential_passthrough():
    """Test 12: git credential prompts are passed through (manual only)."""
    pass
