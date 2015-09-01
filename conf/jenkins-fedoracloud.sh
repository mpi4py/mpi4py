#!/usr/bin/env bash
# Test script running on Fedora Jenkins
# http://jenkins.cloud.fedoraproject.org/job/mpi4py
# Copyright (c) 2015, Thomas Spura.

if [ "$#" -ne 1 ]; then
    echo "Usage: jenkins-fedoracloud.sh \$MPI_IMPLEMENTATION"
    exit 1
fi
MPI=$1
case "$MPI" in
    mpich|openmpi)
        echo "Running tests with MPI: $MPI"
        ;;
    *)
        echo "Unknown MPI implementation: $MPI"
        exit 1
        ;;
esac

## define mpi_{un,}load
source /etc/profile.d/modules.sh
_mpi_load="module load mpi/$MPI-$(uname -m)"
_mpi_unload="module purge"

echo "Creating virtualenv: mpi4py-venv-$MPI"
rm -rf mpi4py-venv-$MPI build
virtualenv mpi4py-venv-$MPI
source mpi4py-venv-$MPI/bin/activate

echo "Installing dependencies"
pip install Cython
pip install nose pylint --upgrade
pip install nosexcover  --upgrade

echo "Loading MPI module: $MPI"
$_mpi_unload
$_mpi_load
hash -r

echo "Installing package"
pip -vvv install .

echo "Running lint"
pep8 demo src | tee pep8.out
pylint mpi4py --extension-pkg-whitelist=mpi4py | tee pylint.out

echo "Running coverage"
/usr/bin/env bash ./conf/coverage.sh
coverage xml

echo "Running testsuite"
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

$_mpi_unload

deactivate
