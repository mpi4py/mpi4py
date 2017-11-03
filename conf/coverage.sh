#!/bin/bash

MPIEXEC=${MPIEXEC-mpiexec}
PYTHON=${1-${PYTHON-python}}
export PYTHONDONTWRITEBYTECODE=1

$PYTHON -m coverage erase

$MPIEXEC -n 1 $PYTHON -m coverage run "$(dirname "$0")/coverage-helper.py" > /dev/null || true

$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench --help > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench --threads             helloworld -q
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench --no-threads          helloworld -q
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench --thread-level=single helloworld -q
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench helloworld > /dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench helloworld > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench helloworld > /dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench helloworld -q
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench ringtest > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench ringtest -q -l 2 -s 1
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench ringtest -q -l 2 -s 1
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench              > /dev/null 2>&1 || true
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench              > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench qwerty       > /dev/null 2>&1 || true
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench qwerty       > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench --mpe qwerty > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench --vt  qwerty > /dev/null 2>&1 || true

$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.run --help > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --version > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --help > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py - < /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "42" > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -m this > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py "$(dirname "$0")/coverage-helper.py" > /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -rc threads=0 --rc=thread_level=single -c "" > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -p mpe -profile mpe -c ""          > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --profile mpe --profile=mpe -c ""  > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -vt --vt -mpe --mpe -c ""          > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py                                    > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -m                                 > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c                                 > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -p                                 > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -bad                               > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --bad=a                            > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -rc=                               > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc=a                             > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc=a=                            > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc==a                            > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit()"        > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit(0)"       > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit(1)"       > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit('error')" > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "from mpi4py import MPI; 1/0;"  > /dev/null 2>&1 || true

$MPIEXEC -n 1 $PYTHON -m coverage run demo/futures/test_futures.py -q 2> /dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run demo/futures/test_futures.py -q 2> /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures demo/futures/test_futures.py -q 2> /dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures demo/futures/test_futures.py -q ProcessPoolPickleTest 2> /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -h > /dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures -h > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -m this > /dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures -m this > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "42"
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures -c "42"
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures - </dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures - </dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit"
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit()"
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit(0)"
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures                           > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures xy                        > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c                        > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -m                        > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -x                        > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "1/0"                  > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit(11)" > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit('')" > /dev/null 2>&1 || true
if [ $(command -v mpichversion) ]; then
    testdir=demo/futures
    $MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures.server --xyz > /dev/null 2>&1 || true
    $MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures.server --bind localhost &
    mpi4pyserver=$!; sleep 0.25;
    $MPIEXEC -n 1 $PYTHON -m coverage run $testdir/test_service.py --host localhost
    wait $mpi4pyserver
    $MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures.server --port 31414 --info "a=x,b=y" &
    mpi4pyserver=$!; sleep 0.25;
    $MPIEXEC -n 1 $PYTHON -m coverage run $testdir/test_service.py --port 31414 --info "a=x,b=y"
    wait $mpi4pyserver
fi
if [ $(command -v mpichversion) ] && [ $(command -v hydra_nameserver) ]; then
    testdir=demo/futures
    hydra_nameserver &
    nameserver=$!; sleep 1;
    $MPIEXEC -nameserver localhost -n 2 $PYTHON -m coverage run -m mpi4py.futures.server &
    mpi4pyserver=$!; sleep 1;
    $MPIEXEC -nameserver localhost -n 1 $PYTHON -m coverage run $testdir/test_service.py
    wait $mpi4pyserver
    kill -s SIGTERM $nameserver
    wait $nameserver 2>/dev/null
fi

$PYTHON -m coverage combine
