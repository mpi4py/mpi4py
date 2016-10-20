#!/bin/sh

MPIEXEC=${MPIEXEC-mpiexec}
PYTHON=${1-${PYTHON-python}}
export PYTHONDONTWRITEBYTECODE=1

$PYTHON -m coverage erase

$MPIEXEC -n 1 $PYTHON -m coverage run "$(dirname "$0")/coverage-helper.py" > /dev/null || true

$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench --help > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench helloworld > /dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench helloworld -q
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench ringtest > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench ringtest -q -l 2 -s 1
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench ringtest -q -l 2 -s 1
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench              2> /dev/null || true
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench              2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench qwerty       2> /dev/null || true
$MPIEXEC -n 2 $PYTHON -m coverage run -m mpi4py.bench qwerty       2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench --mpe qwerty 2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.bench --vt  qwerty 2> /dev/null || true

$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.run --help > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --version > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --help > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py - < /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "123" > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -m this  > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py "$(dirname "$0")/coverage-helper.py" > /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -p mpe -profile mpe --profile mpe --profile=mpe  -c "" > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -vt --vt -mpe --mpe -c "123" > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -rc threads=0 --rc=threads=0,thread_level=multiple  -c "" > /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py                                    2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -m                                 2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c                                 2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -p                                 2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -bad                               2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --bad=a                            2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -rc=                               2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc=a                             2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc=a=                            2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py --rc==a                            2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit()"        2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit(0)"       2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit(1)"       2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit('error')" 2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py -c "from mpi4py import MPI; 1/0;"  2> /dev/null || true

MPIEXEC_TIMEOUT=60 \
$MPIEXEC -n 1 $PYTHON -m coverage run demo/futures/test_futures.py -q 2> /dev/null
$MPIEXEC -n 2 $PYTHON -m coverage run demo/futures/test_futures.py -q 2> /dev/null
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures demo/futures/test_futures.py -q MPICommExecutorTest   2> /dev/null
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
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures                           2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures xy                        2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c                        2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -m                        2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -x                        2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "1/0"                  2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit(11)" 2> /dev/null || true
$MPIEXEC -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit('')" 2> /dev/null || true

$PYTHON -m coverage combine
