#!/bin/bash

wheelhouse=${1:-wheelhouse}
test -f setup.py

venv=.venv-cibw
python3 -m venv .venv-cibw
echo '*' > "$venv"/.gitignore
# shellcheck disable=SC1091
source "$venv"/bin/activate
python -m pip install --upgrade pip pipx wheel

pysabi="0"
matrix_py=("cp314")
matrix_mpiabi=("mpiabi" "mpich" "openmpi")
matrix_arch=("$(uname -m)")

for py in "${matrix_py[@]}"; do
for mpiabi in "${matrix_mpiabi[@]}"; do
for arch in "${matrix_arch[@]}"; do

export MPI4PY_BUILD_MPIABI="1"
export MPI4PY_BUILD_PYSABI="$pysabi"
export MPI4PY_LOCAL_VERSION="$mpiabi"
export CIBW_BUILD="$py-*"
export CIBW_ARCHS="$arch"

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
--config-file "cibw/config.toml" \
.

done # arch
done # mpiabi
done # py

python cibw/merge-wheels.py "$wheelhouse"
