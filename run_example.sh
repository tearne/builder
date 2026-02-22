#!/bin/sh
THIS_DIR="$(cd "$(dirname "$0")" && pwd)"

# For this example, we just clone another copy of this repo into the target directory.  Normally, you'd specify a remote git repo.
export BUILDER_REPO="$THIS_DIR"
export BUILDER_BRANCH="main"
# The build script inside the repo to run
export BUILDER_SCRIPT="example/build.sh"
# The directory to pass to the build script, to tell it where to put artefacts
export BUILDER_BUILD_DIR="$THIS_DIR/target"

# echo "BUILDER_REPO=$BUILDER_REPO"
# echo "BUILDER_BRANCH=$BUILDER_BRANCH"
# echo "BUILDER_BUILD_DIR=$BUILDER_BUILD_DIR"
# echo "BUILDER_SCRIPT=$BUILDER_SCRIPT"

# Now the environment variables are set, just run builder.py
exec "$THIS_DIR/builder.py"
