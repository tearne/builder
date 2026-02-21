#!/bin/sh
set -e
TARGET="$1"
IMAGE="hello-world-builder"

docker build -t "$IMAGE" .
docker save "$IMAGE" -o "$TARGET/hello-world.tar"
