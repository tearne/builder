# Builder

A single-file Python script that clones a git repo and runs its build script. It's a lightweight alternative to GitHub self-hosted runners for cases where builds don't need to be fully automated.

## How It Works

1. Clones `REPO` at `BRANCH` into `BUILD_DIR/checkouts/<repo-name>/`, or fast-forwards an existing checkout.
2. Runs `BUILD_DIR/checkouts/<repo-name>/BUILD_SCRIPT` with `BUILD_DIR` as its only argument.

The build script receives `BUILD_DIR` as its only argument and is responsible for placing any artifacts it wishes to save there.

## Setup

Requires [`uv`](https://docs.astral.sh/uv/).

Fill in the configuration section near the top of `builder.py`:

| Variable | Description |
|----------|-------------|
| `BUILDER_REPO` | Full git URL of the repo to build |
| `BUILDER_BRANCH` | Branch to check out |
| `BUILDER_BUILD_DIR` | Directory where artifacts are placed; checkouts go in `BUILD_DIR/checkouts/` |
| `BUILDER_SCRIPT` | Build script filename inside the repo |

Add any variables your build script needs to the `BUILD_SCRIPT_VARS` dictionary in the same section.

If `BUILDER_BUILD_DIR` is inside a git repository, it must be covered by that repository's `.gitignore` to prevent build artifacts and checkouts from being accidentally committed. The script will tell you exactly what line to add if this check fails.

Then run:

```sh
./builder.py
```

## Example

`run_example.sh` demonstrates a self-contained run: it instructs `builder` to clone this repo itself, and run `example/build.sh` as the build script. That script builds a minimal Docker image and exports it as a `.tar` file into the build directory.

```sh
./run_example.sh
```

After it runs, `target/checkouts/builder/` will contain the cloned repo and `target/hello-world.tar` will hold the exported image.
