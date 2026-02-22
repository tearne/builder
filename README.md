# Builder

A single-file Python script that clones (or updates) a git repo and runs its build script. It's a lightweight alternative to GitHub self-hosted runners for cases where builds don't need to be fully automated.

## How It Works

1. Clones `REPO` at `BRANCH` into `BUILD_DIR/checkouts/<repo-name>/`, or fast-forwards an existing checkout.
2. Runs `BUILD_DIR/checkouts/<repo-name>/BUILD_SCRIPT` with `BUILD_DIR` as its only argument.

The build script receives `BUILD_DIR` as its only argument and is responsible for placing artifacts there.

## Setup

Requires [`uv`](https://docs.astral.sh/uv/). Set the four configuration variables at the top of `builder.py`, or pass them as environment variables:

| Variable | Env override | Description |
|----------|-------------|-------------|
| `REPO` | `BUILDER_REPO` | Full git URL of the repo to build |
| `BRANCH` | `BUILDER_BRANCH` | Branch to check out |
| `BUILD_DIR` | `BUILDER_BUILD_DIR` | Directory where artifacts are placed; checkouts go in `BUILD_DIR/checkouts/` (must exist) |
| `BUILD_SCRIPT` | `BUILDER_SCRIPT` | Build script filename inside the repo (default: `build.sh`) |

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
