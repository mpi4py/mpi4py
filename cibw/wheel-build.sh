#!/bin/bash

wheelhouse=${1:-wheelhouse}
test -f setup.py

python3 -m venv .venv
echo '*' > .venv/.gitignore
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip pipx wheel

py="cp313"
pysabi="0"
matrix_mpiabi=("mpiabi" "mpich" "openmpi")
matrix_arch=("$(uname -m)")

for mpiabi in "${matrix_mpiabi[@]}"; do
for arch in "${matrix_arch[@]}"; do

export MPI4PY_BUILD_MPIABI="1"
export MPI4PY_BUILD_PYSABI="$pysabi"
export MPI4PY_LOCAL_VERSION="$mpiabi"
export CIBW_CONTAINER_ENGINE=$containerengine
export CIBW_PROJECT_REQUIRES_PYTHON=">=3.10"
export CIBW_ENABLE="cpython-freethreading pypy"
export CIBW_BUILD_FRONTEND="build[uv]"
export CIBW_ARCHS="$arch"
export CIBW_BUILD="$py-*"
export CIBW_SKIP="*musllinux*"
export CIBW_BEFORE_ALL="bash {project}/cibw/install-mpi.sh $mpiabi $arch"
export CIBW_BEFORE_BUILD="bash {project}/cibw/patch-tools.sh"
export CIBW_TEST_COMMAND="bash {project}/cibw/run-tests.sh"
export CIBW_ENVIRONMENT_PASS_LINUX="MPI4PY_BUILD_MPIABI MPI4PY_BUILD_PYSABI MPI4PY_LOCAL_VERSION"
export CIBW_ENVIRONMENT_LINUX="CFLAGS='-g0 -Os'"

manylinuximage="manylinux_2_28"
export CIBW_MANYLINUX_AARCH64_IMAGE=$manylinuximage
export CIBW_MANYLINUX_X86_64_IMAGE=$manylinuximage

if test "$(uname)" = Linux; then
    platform=linux
    containerengine=$(basename "$(command -v podman || command -v docker)")
    export CIBW_CONTAINER_ENGINE=$containerengine
fi
if test "$(uname)" = Darwin; then
    platform=macos
    export CIBW_BUILD='pp311-*'
fi

python -m \
pipx run \
cibuildwheel \
--platform "$platform" \
--output-dir "$wheelhouse" \
.

done # arch
done # mpiabi

python cibw/merge-wheels.py "$wheelhouse"
