#!/bin/sh
EXAMPLE_DIR="$(cd "$(dirname "$0")" && pwd)"

export BUILDER_REPO="$(cd "$EXAMPLE_DIR/../.." && pwd)"
export BUILDER_BRANCH="main"
export BUILDER_BUILD_DIR="$EXAMPLE_DIR/target"
export BUILDER_SCRIPT="examples/hello-world-docker/build.sh"

exec "$EXAMPLE_DIR/../../builder.py"
