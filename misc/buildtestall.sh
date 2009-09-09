#!/bin/sh
for py in 2.3 2.4 2.5 2.6 2.7 3.0 3.1; do
    for mpi in mpich2 openmpi sunmpi mpich1 lammpi; do
	./misc/buildtest.sh -q --py="$py" --mpi="$mpi"
    done
done
