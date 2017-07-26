#!/bin/bash

PYTHON=${1-${PYTHON-python}}
MPIEXEC=${MPIEXEC-mpiexec}
testdir=$(dirname "$0")

set -e

if [ $(command -v mpichversion) ]; then
    $MPIEXEC -n 1 $PYTHON -m mpi4py.futures.server --xyz > /dev/null 2>&1 || true
    $MPIEXEC -n 2 $PYTHON -m mpi4py.futures.server --bind localhost &
    mpi4pyserver=$!; sleep 0.25;
    $MPIEXEC -n 1 $PYTHON $testdir/test_service.py --host localhost
    wait $mpi4pyserver
    $MPIEXEC -n 2 $PYTHON -m mpi4py.futures.server --port 31414 --info "a=x,b=y" &
    mpi4pyserver=$!; sleep 0.25;
    $MPIEXEC -n 1 $PYTHON $testdir/test_service.py --port 31414 --info "a=x,b=y"
    wait $mpi4pyserver
fi

if [ $(command -v mpichversion) ] && [ $(command -v hydra_nameserver) ]; then
    hydra_nameserver &
    nameserver=$!; sleep 0.25;
    $MPIEXEC -nameserver localhost -n 2 $PYTHON -m mpi4py.futures.server &
    mpi4pyserver=$!; sleep 0.25;
    $MPIEXEC -nameserver localhost -n 1 $PYTHON $testdir/test_service.py
    wait $mpi4pyserver
    $MPIEXEC -nameserver localhost -n 2 $PYTHON -m mpi4py.futures.server --service test-service &
    mpi4pyserver=$!; sleep 0.25;
    $MPIEXEC -nameserver localhost -n 1 $PYTHON $testdir/test_service.py --service test-service
    wait $mpi4pyserver
    kill -s SIGTERM $nameserver
    wait $nameserver 2>/dev/null
fi
