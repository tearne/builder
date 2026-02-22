#!/bin/sh
set -e

ARTEFACT_DIR="${1:?Usage: build.sh <artefact-dir>}"
printf "I will build into %s\n" $ARTEFACT_DIR

IMAGE="my_docker_image"

# Build the container
docker build -t "$IMAGE" "$(dirname "$0")"

# Do a test run
printf "Test run of container: %s\n" "$(docker run --rm $IMAGE)"

# Export the container and put it somewhere
docker save "$IMAGE" -o "$ARTEFACT_DIR/hello-world.tar"
