#!/bin/bash

RUN() { echo + $@; $@; }
RUN export ANACONDA=${ANACONDA-/opt/conda}

install-mambaforge() {
  local PROJECT=https://github.com/conda-forge/miniforge
  local BASEURL=$PROJECT/releases/latest/download
  local INSTALLER=Mambaforge-Linux-x86_64.sh
  RUN curl -sSL -o ~/$INSTALLER $BASEURL/$INSTALLER
  RUN bash ~/$INSTALLER -b -f -p $ANACONDA
  RUN source $ANACONDA/bin/activate base
  RUN conda config --set channel_priority strict
  RUN conda config --set show_channel_urls yes
  RUN conda deactivate
}

parse-args() {
  unset PY
  unset MPI
  unset RUNTESTS
  unset COVERAGE
  for arg in $@; do
    case $arg in
      python=?*)
        PY="${arg#*=}";;
      py=?*)
        PY="${arg#*=}";;
      MPI=?*)
        MPI="${arg#*=}";;
      mpi=?*)
        MPI="${arg#*=}";;
      runtests=?*)
        RUNTESTS="${arg#*=}";;
      coverage=?*)
        COVERAGE="${arg#*=}";;
      *)
        break
    esac
  done
  PY=${PY-3}
  MPI=${MPI-mpich}
  ENV=py$PY-$MPI
  RUNTESTS=${RUNTESTS-no}
  COVERAGE=${COVERAGE-no}
}

create-env() {
  parse-args $@
  RUN rm -rf $ANACONDA/envs/$ENV
  RUN source $ANACONDA/bin/activate base
  local packages=(python=$PY $MPI $MPI-mpicc numpy cython coverage)
  RUN mamba create --yes -n $ENV ${packages[@]}
  RUN conda deactivate
}

package-install() {
  parse-args $@
  RUN source $ANACONDA/bin/activate $ENV
  RUN python setup.py build_src --force
  RUN python setup.py install
  RUN python setup.py --quiet clean --all
  RUN conda deactivate
}

package-testing() {
  parse-args $@
  RUN source $ANACONDA/bin/activate $ENV
  RUN python -m mpi4py --version
  if [[ "$RUNTESTS" == "yes" ]]; then
      if [[ "$MPI" == "mpich"   ]]; then local P=2; else local P=5; fi
      local MPIEXEC=${MPIEXEC-mpiexec}
      RUN $MPIEXEC -n 1  python $PWD/test/main.py
      RUN $MPIEXEC -n $P python $PWD/test/main.py -f
      RUN $MPIEXEC -n 1  python $PWD/demo/futures/test_futures.py
      RUN $MPIEXEC -n $P python $PWD/demo/futures/test_futures.py -f
      RUN $MPIEXEC -n 1  python -m mpi4py.futures $PWD/demo/futures/test_futures.py
      RUN $MPIEXEC -n $P python -m mpi4py.futures $PWD/demo/futures/test_futures.py -f
      RUN python $PWD/demo/test-run/test_run.py
  fi
  if [[ "$COVERAGE" == "yes" ]]; then
      RUN test/coverage.sh
      RUN coverage report
      RUN coverage xml
      RUN mv coverage.xml coverage-py$PY-$MPI-$(uname).xml
  fi
  RUN conda deactivate
}
