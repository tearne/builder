#!/bin/sh
EXAMPLE_DIR="$(cd "$(dirname "$0")" && pwd)"

export BUILDER_REPO="$(cd "$EXAMPLE_DIR/../.." && pwd)"
export BUILDER_BRANCH="main"
export BUILDER_BUILD_DIR="$EXAMPLE_DIR/target"
export BUILDER_SCRIPT="examples/hello-world-docker/build.sh"

echo "BUILDER_REPO=$BUILDER_REPO"
echo "BUILDER_BRANCH=$BUILDER_BRANCH"
echo "BUILDER_BUILD_DIR=$BUILDER_BUILD_DIR"
echo "BUILDER_SCRIPT=$BUILDER_SCRIPT"

exec "$EXAMPLE_DIR/../../builder.py"
