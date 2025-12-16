#!/bin/bash
# shellcheck disable=SC2034
set -euo pipefail

mpich=("4.3" "4.1" "3.4")
openmpi=("5.0" "4.1")
impi=("2021.17.0" "2021.10.0")
msmpi=("10.1.1")

mpi="$1"
mpipackage="$mpi"
mpiversion="${mpi}[@]"
test "$mpi" = impi && mpipackage=impi_rt

conda=$(command -v micromamba || command -v mamba || command -v conda)
: "${CONDA_EXE=${MAMBA_EXE=${conda:-conda-not-found}}}"

scriptdir=$(dirname "${BASH_SOURCE[0]}")
"$CONDA_EXE" uninstall -qy "$mpipackage"
for version in "${!mpiversion}"; do
    echo "::group::$mpipackage=$version"
    "$CONDA_EXE" install -qy "$mpipackage=$version"
    "$CONDA_EXE" list
    "$CONDA_EXE" run bash "$scriptdir"/run-tests-mpi.sh
    echo "::endgroup::"
    "$CONDA_EXE" uninstall -qy "$mpipackage"
done
