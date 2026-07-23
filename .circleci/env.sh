#!/bin/bash
# shellcheck source-path=SCRIPTDIR
# shellcheck source-path=SCRIPTDIR/..

export CFLAGS="-O0 -Wp,-U_FORTIFY_SOURCE"
export CPPFLAGS=$CFLAGS
export MPI4PY_COVERAGE_PLUGIN=cycoverage
export PYTHONPATH=$PWD/conf

set -ax
source .ci/env.mpich
source .ci/env.openmpi
set +ax

export ANACONDA=${ANACONDA-/opt/conda}
source "$(dirname "$0")"/anaconda.sh
