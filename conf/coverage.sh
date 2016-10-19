#!/bin/sh

PYTHON=${1-${PYTHON-python}}
export PYTHONDONTWRITEBYTECODE=1

$PYTHON -m coverage erase

mpiexec -n 1 $PYTHON -m coverage run "$(dirname "$0")/coverage-helper.py" &> /dev/null || true

mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.bench > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.bench --help > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.bench helloworld > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.bench ringtest > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.bench ringtest -q -l 2 -s 1
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.bench qwerty &> /dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.bench --mpe qwerty &> /dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.bench --vt  qwerty &> /dev/null || true
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.bench > /dev/null
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.bench helloworld -q
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.bench ringtest -q -l 2 -s 1
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.bench qwerty &> /dev/null || true

mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.run --help > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py --version > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py --help > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py - < /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -c "123" > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -m this > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py "$(dirname "$0")/coverage-helper.py" > /dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -p mpe -profile mpe --profile mpe --profile=mpe  -c "" > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -vt --vt -mpe --mpe -c "123" > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -rc threads=0 --rc=threads=0,thread_level=multiple  -c "" > /dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -m &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -c &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -p &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -bad &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py --bad=a &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -rc= &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py --rc=a &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py --rc=a= &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py --rc==a &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit()" &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit(0)" &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit(1)" &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -c "import sys; sys.exit('error')" &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py -c "from mpi4py import MPI; 1/0;" &>/dev/null || true

MPIEXEC_TIMEOUT=60 \
mpiexec -n 1 $PYTHON -m coverage run demo/futures/test_futures.py -q
mpiexec -n 2 $PYTHON -m coverage run demo/futures/test_futures.py -q
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures demo/futures/test_futures.py -q MPICommExecutorTest
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.futures demo/futures/test_futures.py -q MPICommExecutorTest
mpiexec -n 3 $PYTHON -m coverage run -m mpi4py.futures demo/futures/test_futures.py -q
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures -h &>/dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures    &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures xy &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures -c &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures -m &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures -x &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures - </dev/null
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.futures - </dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures -m this &>/dev/null
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.futures -m this &>/dev/null
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "42"
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.futures -c "42"
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit"
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit()"
mpiexec -n 2 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit(0)"
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "1/0" &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit(11)" &>/dev/null || true
mpiexec -n 1 $PYTHON -m coverage run -m mpi4py.futures -c "raise SystemExit('')" &>/dev/null || true

$PYTHON -m coverage combine
