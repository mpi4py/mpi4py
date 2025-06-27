#!/bin/bash
set -euo pipefail

dist=${1:-dist}

images=(
    fedora:42
    debian:12
    ubuntu:24.04
)

arch=$(uname -m)

sdir=$(cd "$(dirname -- "$0")" && pwd -P)
for image in "${images[@]}"; do
    echo "Running on $image $arch"
    docker run --rm \
           --volume "$(pwd):$(pwd):z" \
           --workdir "$(pwd)" \
           --arch "$arch" "$image" \
           bash "$sdir"/wheel-test-Linux.sh "$dist"
done
