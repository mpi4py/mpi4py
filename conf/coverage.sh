#!/bin/sh
coverage erase
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py --help > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py helloworld > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py ringtest > /dev/null
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py ringtest -q -l 2 -s 1
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py qwerty &> /dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py --mpe qwerty &> /dev/null || true
mpiexec -n 1 coverage run -p --branch --source=mpi4py -m mpi4py --vt  qwerty &> /dev/null || true
mpiexec -n 2 coverage run -p --branch --source=mpi4py -m mpi4py > /dev/null
mpiexec -n 2 coverage run -p --branch --source=mpi4py -m mpi4py helloworld -q
mpiexec -n 2 coverage run -p --branch --source=mpi4py -m mpi4py ringtest -q -l 2 -s 1
mpiexec -n 2 coverage run -p --branch --source=mpi4py -m mpi4py qwerty &> /dev/null || true
coverage combine
