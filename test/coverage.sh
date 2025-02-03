#!/bin/bash
set -eux

MPIEXEC=${MPIEXEC:-mpiexec}
PYTHON=${PYTHON:-python${py:-}}

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONWARNINGS=error

$PYTHON -m coverage erase

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
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench pingpong    -l 2 -s 1 -n 64 --array none > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench pingpong    -l 2 -s 1 -n 64 --no-header  > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench pingpong    -l 2 -s 1 -n 64 --no-stats   > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench pingpong -q -l 1 -s 1 -n 2097152
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench pingpong -q -l 1 -s 1 -n 128
$MPIEXEC -n 3 $PYTHON -m coverage run -m mpi4py.bench pingpong -q -l 1 -s 1 -n 128
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench pingpong -q -l 1 -s 1 -n 128 -p
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench pingpong -q -l 1 -s 1 -n 128 -o
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench pingpong -q -l 1 -s 1 -n 128 -p --protocol 4
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench pingpong -q -l 1 -s 1 -n 128 -o --threshold 32
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench futures -w 1 -t 1 -l 1             > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench futures -w 1 -t 1 -n 8 --no-header > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench futures -w 1 -t 1 -n 8 --no-stats  > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench futures -w 1 -t 1 -n 8 -a numpy -e mpi     -q
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench futures -w 1 -t 1 -n 8 -a bytes -e process -q
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench futures -w 1 -t 1 -n 8 -a array -e thread  -q
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench              > /dev/null 2>&1 || true
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench              > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench qwerty       > /dev/null 2>&1 || true
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench qwerty       > /dev/null 2>&1 || true

$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.run --help        > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --prefix          > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --version         > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --mpi-library     > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --mpi-std-version > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --mpi-lib-version > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --help            > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -                 < /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -rc threads=0            -c "import mpi4py.MPI"
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc=thread_level=single -c "import mpi4py.MPI"
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py                   > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -m                > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c                > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -p                > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -bad              > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --bad=a           > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -rc               > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -rc=              > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc              > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc=a            > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc=a=           > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc==a           > /dev/null 2>&1 || true

$MPIEXEC -n 1 $PYTHON -m coverage run test/test_package.py
$MPIEXEC -n 1 $PYTHON -m coverage run test/test_toplevel.py
$MPIEXEC -n 1 $PYTHON -m coverage run test/test_util_dtlib.py
$MPIEXEC -n 1 $PYTHON -m coverage run test/test_util_pkl5.py
$MPIEXEC -n 2 $PYTHON -m coverage run test/test_util_pkl5.py
$MPIEXEC -n 3 $PYTHON -m coverage run test/test_util_pkl5.py
$MPIEXEC -n 1 $PYTHON -m coverage run test/test_util_pool.py
$MPIEXEC -n 1 $PYTHON -m coverage run test/test_util_sync.py
$MPIEXEC -n 2 $PYTHON -m coverage run test/test_util_sync.py
$MPIEXEC -n 3 $PYTHON -m coverage run test/test_util_sync.py
$PYTHON -m coverage run demo/test-run/test_run.py

$MPIEXEC -n 1 $PYTHON -m coverage run demo/futures/test_futures.py
$MPIEXEC -n 2 $PYTHON -m coverage run demo/futures/test_futures.py
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.run -rc threads=False demo/futures/test_futures.py -qf 2> /dev/null || true
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.run -rc threads=False demo/futures/test_futures.py -qf 2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures demo/futures/test_futures.py
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures demo/futures/test_futures.py SharedPoolInitTest
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures demo/futures/test_futures.py ProcessPoolPickleTest
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
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures                              > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures xy                           > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c                           > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -m                           > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -x                           > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "1/0"                     > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit(11)"    > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit('')"    > /dev/null 2>&1 || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "raise KeyboardInterrupt" > /dev/null 2>&1 || true
if [ $(command -v mpichversion) ]; then
    testdir=demo/futures
    $MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures.server --xyz > /dev/null 2>&1 || true
    $MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures.server --bind localhost &
    mpi4pyserver=$!; sleep 1;
    $MPIEXEC -n 1 $PYTHON -m coverage run $testdir/test_service.py --host localhost
    wait $mpi4pyserver
    $MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.futures.server --port 31414 --info "a=x,b=y" &
    mpi4pyserver=$!; sleep 1;
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
    kill -TERM $nameserver
    wait $nameserver 2>/dev/null || true
fi

if test -f src/mpi4py/MPI.c && grep -q CYTHON_TRACE src/mpi4py/MPI.c; then
    export PYTHONWARNINGS=default
    $MPIEXEC -n 2 $PYTHON -m coverage run test/main.py -f -e test_util_
    $MPIEXEC -n 3 $PYTHON -m coverage run test/main.py -f test_cco_buf_inter.TestCCOBufInter
    $MPIEXEC -n 3 $PYTHON -m coverage run test/main.py -f test_cco_obj_inter.TestCCOObjInter
    $MPIEXEC -n 4 $PYTHON -m coverage run test/main.py -f test_cco_obj.TestCCOObjWorld
    env MPI4PY_RC_RECV_MPROBE=false $MPIEXEC -n 2 $PYTHON -m coverage run test/main.py -f test_p2p_obj.TestP2PObjWorld
    env MPI4PY_RC_FAST_REDUCE=false $MPIEXEC -n 2 $PYTHON -m coverage run test/main.py -f test_cco_obj.TestCCOObjWorld
    env MPIEXEC="$MPIEXEC" PYTHON="$PYTHON -m coverage run -m mpi4py" demo/init-fini/run.sh
    env MPIEXEC="$MPIEXEC" PYTHON="$PYTHON -m coverage run -m mpi4py" demo/check-mpiexec/run.sh
fi

$PYTHON -m coverage combine
