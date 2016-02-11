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
pip install pep8 pylint coverage --upgrade

echo "Loading MPI module: $MPI"
module purge
module load mpi/$MPI-$(uname -m)
hash -r

echo "Installing package"
pip -vvv install .

echo "Running pep8"
pep8 src | tee pep8-$PY-$MPI.out

echo "Running pylint"
pylint mpi4py --extension-pkg-whitelist=mpi4py | tee pylint-$PY-$MPI.out

echo "Running coverage"
/usr/bin/env bash ./conf/coverage.sh
coverage xml
mv coverage.xml coverage-$PY-$MPI.xml

echo "Running testsuite"
python demo/test-run/test_run.py -v
set -e
case "$MPI" in
    mpich)
        mpiexec -n 1 python test/runtests.py -v -e spawn -e dynproc
        mpiexec -n 2 python test/runtests.py -v -e spawn -e dynproc
        mpiexec -n 3 python test/runtests.py -v -e spawn -e dynproc
       #mpiexec -n 8 python test/runtests.py -v -e spawn -e dynproc
        ;;
    openmpi)
        mpiexec -n 1 python test/runtests.py -v -e spawn -e dynproc --no-threads
        mpiexec -n 2 python test/runtests.py -v -e spawn -e dynproc --no-threads
        mpiexec -n 3 python test/runtests.py -v -e spawn -e dynproc --no-threads
       #mpiexec -n 8 python test/runtests.py -v -e spawn -e dynproc --no-threads
        ;;
esac
set +e

module purge
deactivate
