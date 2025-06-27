#!/bin/bash
set -euo pipefail

packages_py=(
    python@3.9
    python@3.10
    python@3.11
    python@3.12
    python@3.13
    pypy3.10
    pypy3.11
)
packages_mpi=(
    mpich
    openmpi
)
brew install "${packages_py[@]}"
for mpi in "${packages_mpi[@]}"; do
    brew unlink "$mpi" || true
done
for mpi in "${packages_mpi[@]}"; do
    brew install "$mpi"
    brew unlink  "$mpi"
done

sdir=$(cd "$(dirname -- "$0")" && pwd -P)
"$sdir"/wheel-test-basic.sh
