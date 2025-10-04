#!/bin/bash
set -euo pipefail

dist=${1:-dist}

PYTHON=(
    "${python38-python3.8}"
    "${python39-python3.9}"
    "${python310-python3.10}"
    "${python311-python3.11}"
    "${python312-python3.12}"
    "${python313-python3.13}"
    "${python314-python3.14}"
    "${python313t-python3.13t}"
    "${python314t-python3.14t}"
    "${pypy311-pypy3.11}"
)

if [[ "$(uname)" =~ NT ]]; then
    MPI=(impi msmpi)
    bin="Scripts"
    exe=".exe"
else
    MPI=(mpich openmpi)
    bin="bin"
    exe=""
fi

venvroot=$(mktemp -d)
trap 'rm -rf $venvroot' EXIT
export PIP_QUIET=${PIP_QUIET:=1}

function setup-python {
    local venvdir
    venvdir=$(mktemp -d -p "$venvroot" XXX)
    "$python" -m venv "$venvdir"
    python="$venvdir/$bin/python$exe"
    "$python" --version
    "$python" -m pip install pip --upgrade
}

function setup-mpi4py {
    local opts=(--no-cache-dir --only-binary mpi4py)
    if test -d "$dist"; then
        opts+=(--no-index --find-links="$dist")
    fi
    "$python" -m pip install mpi4py "${opts[@]}"
    test $? -ne 0 && return 1
    "$python" -m mpi4py --version
}

function setup-mpi {
    local mpi=$1
    if command -v brew > /dev/null; then
        brew unlink mpich openmpi > /dev/null
        brew link "$mpi" > /dev/null
    elif command -v module > /dev/null; then
        module unload "mpi" > /dev/null 2>&1
        module load "mpi/$mpi-$(uname -m)"
    elif test "$(uname)" == Linux; then
        local version
        test "$mpi" == mpich && version=12 || version=40
        export MPI4PY_LIBMPI="libmpi.so.$version"
    else
        export MPI4PY_MPIABI="$mpi"
    fi
}

function clean-mpi {
    local mpi=$1
    if command -v brew > /dev/null; then
        brew unlink "$mpi" > /dev/null
    elif command -v module > /dev/null; then
        module unload "mpi/$mpi-$(uname -m)"
    fi
    unset MPI4PY_LIBMPI
    unset MPI4PY_MPIABI
}

function mpi4py-test-basic {
    "$python" -m mpi4py --mpi-vendor
    "$python" -m mpi4py --mpi-library
    "$python" -m mpi4py --mpi-abi-version
    "$python" -m mpi4py --mpi-std-version
    "$python" -m mpi4py --mpi-lib-version | head -n 1
}

for python in "${PYTHON[@]}"; do
    test -z "$(command -v "$python")" && continue
    pyversion=$("$python" -c "import sys; print(sys.version.split()[0])")
    pyimpname=$("$python" -c "import sys; print(sys.implementation.name)")
    echo "::group::Python $pyversion [$pyimpname]"
    setup-python
    setup-mpi4py || continue
    for mpi in "${MPI[@]}"; do
        echo "* Use MPI=$mpi"
        setup-mpi "$mpi"
        if [ "$mpi" == "$mpi" ]; then
            echo "- Test MPIABI discovery"
            mpi4py-test-basic
        fi
        if [ "$mpi" == mpich ] || [ "$mpi" == openmpi ]; then
            export MPI4PY_MPIABI=$mpi
            echo "- Test MPIABI=$MPI4PY_MPIABI"
            mpi4py-test-basic
        fi
        clean-mpi "$mpi"
    done
    echo "::endgroup::"
done
