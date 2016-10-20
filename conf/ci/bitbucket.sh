#!/bin/bash
# Test script running on Bitbucket Pipelines
# https://bitbucket.org/mpi4py/mpi4py/addon/pipelines/home

RUN() { echo + $@; $@; }
RUN export ANACONDA=${ANACONDA-/opt/anaconda}
RUN export CFLAGS=-O0

install-anaconda() {
  MINICONDA=Miniconda2-latest-Linux-$(arch).sh
  RUN wget --quiet -P ~ http://repo.continuum.io/miniconda/$MINICONDA
  RUN bash ~/$MINICONDA -b -f -p $ANACONDA
  RUN source $ANACONDA/bin/activate root
  RUN conda config --set show_channel_urls yes
  RUN conda install --quiet --yes -n root conda-build
}

test-package() {
  for arg in $@; do
    case $arg in
      python=?*)
        PY="${arg#*=}";;
      MPI=?*)
        MPI="${arg#*=}";;
      *)
        break
    esac
  done
  PY=${PY-2.7} MPI=${MPI-mpich}
  RUN source $ANACONDA/bin/activate root
  RUN rm -rf $ANACONDA/envs/test
  RUN conda create --quiet --yes -n test --channel mpi4py python=$PY $MPI numpy nomkl cython coverage
  RUN source activate test
  RUN python setup.py build_src --force
  RUN python setup.py install
  RUN python setup.py --quiet clean --all
  if [[ "$MPI" == "mpich"   ]]; then P=2; else P=5; fi
  if [[ "$MPI" == "openmpi" ]]; then MPIEXEC="mpiexec --allow-run-as-root"; fi
  export MPIEXEC=${MPIEXEC-mpiexec}
  RUN $MPIEXEC -n 1  python $PWD/test/runtests.py
  RUN $MPIEXEC -n $P python $PWD/test/runtests.py -f --exclude=spawn
  RUN $MPIEXEC -n 1  python $PWD/demo/futures/test_futures.py
  RUN $MPIEXEC -n $P python $PWD/demo/futures/test_futures.py -f
  RUN $MPIEXEC -n 1  python -m mpi4py.futures $PWD/demo/futures/test_futures.py
  RUN $MPIEXEC -n $P python -m mpi4py.futures $PWD/demo/futures/test_futures.py -f
  RUN ./conf/coverage.sh
  RUN coverage report
  RUN source deactivate
}
