#!/bin/bash

RUN() { echo + $@; $@; }
RUN export ANACONDA=${ANACONDA-/opt/anaconda}

install-anaconda() {
  MINICONDA=Miniconda3-latest-Linux-$(arch).sh
  RUN curl -s -o ~/$MINICONDA https://repo.anaconda.com/miniconda/$MINICONDA
  RUN bash ~/$MINICONDA -b -f -p $ANACONDA
  RUN source $ANACONDA/bin/activate root
  RUN conda config --set show_channel_urls yes
}

test-package() {
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
  RUNTESTS=${RUNTESTS-no}
  COVERAGE=${COVERAGE-no}
  RUN source $ANACONDA/bin/activate root
  RUN rm -rf $ANACONDA/envs/test
  RUN conda create --quiet --yes -n test -c conda-forge python=$PY $MPI $MPI-mpicc numpy cython coverage
  RUN conda activate test
  RUN python setup.py build_src --force
  RUN python setup.py install
  RUN python setup.py --quiet clean --all
  if [[ "$RUNTESTS" == "yes" ]]; then
      if [[ "$MPI" == "mpich"   ]]; then local P=2; else local P=5; fi
      local MPIEXEC=${MPIEXEC-mpiexec}
      RUN $MPIEXEC -n 1  python $PWD/test/runtests.py
      RUN $MPIEXEC -n $P python $PWD/test/runtests.py -f
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
