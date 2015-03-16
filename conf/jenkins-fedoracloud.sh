#!/usr/bin/env bash
# Test script running on Fedora jenkins http://jenkins.cloud.fedoraproject.org/job/mpi4py
# Copyright (c) 2014, Thomas Spura.

#rpm -qa | sort

if [ "$#" -ne 1 ]; then
    echo "Usage: jenkins-fedoracloud.sh \$MPI_IMPLEMENTATION"
    exit 1
fi
MPI=$1
echo "Running tests with MPI: $MPI"
# TODO check if this MPI implementation is available
case "$1" in

    mpich|openmpi)
        ;;
    *) echo "MPI $MPI not supported yet"
        exit 1
        ;;
esac

## define mpi_{un,}load
source /etc/profile.d/modules.sh
_mpi_load="module load mpi/$MPI-$(uname -m)"
_mpi_unload="module purge"

rm -rf mpi4pyenv_$MPI build
virtualenv mpi4pyenv_$MPI
source mpi4pyenv_$MPI/bin/activate

pip install Cython
pip install nose pylint --upgrade  ## Needed within the venv
hash -r  ## Reload where the nosetests app is (within the venv) - see `which nosetests` with and without
pip install nosexcover

$_mpi_unload
$_mpi_load

make build

coverage run --source=mpi4py,test test/runtests.py --no-threads
coverage xml

case "$1" in
    mpich)
        mpiexec -np 1 python test/runtests.py -v
        mpiexec -np 2 python test/runtests.py -v
        mpiexec -np 3 python test/runtests.py -v
        #mpiexec -np 8 python test/runtests.py -v
        ;;
    openmpi)
        mpiexec -np 1 python test/runtests.py -v --no-threads
        #mpiexec -np 2 python test/runtests.py -v --no-threads
        #mpiexec -np 3 python test/runtests.py -v --no-threads
        #mpiexec -np 8 python test/runtests.py -v --no-threads
        ;;
esac

$_mpi_unload

pep8 demo build/*/mpi4py | tee pep8.out
pylint build/*/mpi4py | tee pylint.out

deactivate
