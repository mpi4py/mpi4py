#!/bin/sh
coverage erase

mpiexec -n 1 coverage run -p --branch --source=mpi4py "$(dirname "$0")/coverage-helper.py" &> /dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py.bench > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py.bench --help > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py.bench helloworld > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py.bench ringtest > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py.bench ringtest -q -l 2 -s 1
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py.bench qwerty &> /dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py.bench --mpe qwerty &> /dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py.bench --vt  qwerty &> /dev/null || true
mpiexec -n 2 coverage run -p --branch --source=mpi4py -m mpi4py.bench > /dev/null
mpiexec -n 2 coverage run -p --branch --source=mpi4py -m mpi4py.bench helloworld -q
mpiexec -n 2 coverage run -p --branch --source=mpi4py -m mpi4py.bench ringtest -q -l 2 -s 1
mpiexec -n 2 coverage run -p --branch --source=mpi4py -m mpi4py.bench qwerty &> /dev/null || true

mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py.run --help > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py --version > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py --help > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -c "123" > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -m this > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py "$(dirname "$0")/coverage-helper.py" > /dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -p mpe -profile mpe --profile mpe --profile=mpe  -c "" > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -vt --vt -mpe --mpe -c "123" > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -rc threads=0 --rc=threads=0,thread_level=multiple  -c "" > /dev/null

mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -m &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -c &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -p &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -bad &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py --bad=a &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -rc= &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py --rc=a &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py --rc=a= &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py --rc==a &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -c "import sys; sys.exit()" &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -c "import sys; sys.exit(0)" &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -c "import sys; sys.exit(1)" &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -c "import sys; sys.exit('error')" &>/dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py -c "from mpi4py import MPI; 1/0;" &>/dev/null || true

coverage combine
