#!/usr/bin/env bash
# Test script running on Fedora Jenkins
# http://jenkins.fedorainfracloud.org/job/mpi4py/
# Copyright (c) 2015, Thomas Spura.

source /etc/profile.d/modules.sh

MPI=mpich
PYTHON=$(command -v python)
for arg in "$@"; do
    case "$arg" in
        mpich|openmpi)
            MPI="$arg"
            ;;
        python|python2|python3|pypy|pypy3)
            PYTHON=$(command -v "$arg")
            ;;
        *)
            echo "Unknown argument: $arg"
            exit 1
            ;;
    esac
done

PY=$(basename "$PYTHON")
echo "Creating virtualenv: venv-$PY-$MPI"
rm -rf  build venv-$PY-$MPI
virtualenv -p "$PYTHON" venv-$PY-$MPI
source venv-$PY-$MPI/bin/activate
pip install pip --upgrade

echo "Installing dependencies"
pip install Cython
pip install pylint coverage --upgrade

echo "Loading MPI module: $MPI"
module purge
module load mpi/$MPI-$(uname -m)
hash -r

echo "Installing package"
pip -vvv install .

echo "Running pylint"
pylint mpi4py | tee pylint-$PY-$MPI.out

echo "Running coverage"
/usr/bin/env bash ./conf/coverage.sh
coverage xml
mv coverage.xml coverage-$PY-$MPI.xml

echo "Running testsuite"
case "$MPI" in
    mpich)
        python demo/test-run/test_run.py -v
        ;;
    openmpi)
       #python demo/test-run/test_run.py -v
        ;;
esac
set -e
case "$MPI" in
    mpich)
        mpiexec -n 1 python test/main.py -v
        mpiexec -n 2 python test/main.py -v -f -e spawn
        mpiexec -n 3 python test/main.py -v -f -e spawn
       #mpiexec -n 8 python test/main.py -v -f -e spawn
        mpiexec -n 1 python demo/futures/test_futures.py -v
        mpiexec -n 2 python -m mpi4py.futures demo/futures/test_futures.py -v -f
        mpiexec -n 3 python -m mpi4py.futures demo/futures/test_futures.py -v -f
        ;;
    openmpi)
        mpiexec -n 1 python test/main.py --no-threads -v -f
        mpiexec -n 2 python test/main.py --no-threads -v -f -e spawn
        mpiexec -n 3 python test/main.py --no-threads -v -f -e spawn
       #mpiexec -n 8 python test/main.py --no-threads -v -f -e spawn
        mpiexec -n 1 python demo/futures/test_futures.py -v
        mpiexec -n 2 python -m mpi4py.futures demo/futures/test_futures.py -v -f
        mpiexec -n 3 python -m mpi4py.futures demo/futures/test_futures.py -v -f
        ;;
esac
set +e

module purge
deactivate
