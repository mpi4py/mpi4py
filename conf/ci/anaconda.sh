#!/bin/bash

RUN() { echo + $@; $@; }
RUN export ANACONDA=${ANACONDA-/opt/anaconda}
RUN export CFLAGS=-O0

install-anaconda() {
  MINICONDA=Miniconda2-latest-Linux-$(arch).sh
  RUN curl -s -o ~/$MINICONDA https://repo.continuum.io/miniconda/$MINICONDA
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
  RUN conda create --quiet --yes -n test -c conda-forge python=$PY $MPI numpy cython
  RUN source activate test
  RUN python setup.py build_src --force
  RUN python setup.py install
  RUN python setup.py --quiet clean --all
  if [[ "$MPI" == "mpich"   ]]; then P=2; else P=5; fi
  if [[ "$MPI" == "openmpi" ]]; then MPIEXEC="mpiexec --allow-run-as-root"; fi
  export MPIEXEC=${MPIEXEC-mpiexec}
  RUN $MPIEXEC -n 1  python $PWD/test/runtests.py
  RUN $MPIEXEC -n $P python $PWD/test/runtests.py -f
  RUN $MPIEXEC -n 1  python $PWD/demo/futures/test_futures.py
  RUN $MPIEXEC -n $P python $PWD/demo/futures/test_futures.py -f
  RUN $MPIEXEC -n 1  python -m mpi4py.futures $PWD/demo/futures/test_futures.py
  RUN $MPIEXEC -n $P python -m mpi4py.futures $PWD/demo/futures/test_futures.py -f
  if [[ "$coverage" == "yes" ]]; then
      RUN conda install --quiet --yes -c conda-forge coverage
      RUN ./conf/coverage.sh
      RUN coverage report
      RUN coverage xml
      RUN mv coverage.xml coverage-py$PY-$MPI.xml
  fi
  RUN source deactivate
}
