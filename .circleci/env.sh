#!/bin/bash

export CFLAGS="-O0 -Wp,-U_FORTIFY_SOURCE"
export CPPFLAGS=$CFLAGS
export MPI4PY_COVERAGE_PLUGIN=cycoverage
export PYTHONPATH=$PWD/conf

export HYDRA_LAUNCHER=fork
export OMPI_MCA_plm_rsh_agent=false
export OMPI_MCA_btl=tcp,self
echo   OMPI_MCA_mpi_yield_when_idle=true
export OMPI_MCA_rmaps_base_oversubscribe=true
export OMPI_MCA_btl_base_warn_component_unused=false
export OMPI_MCA_btl_vader_single_copy_mechanism=none
export PRTE_MCA_rmaps_default_mapping_policy=:oversubscribe
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

export ANACONDA=${ANACONDA-/opt/conda}
source conf/ci/anaconda.sh
