#! /bin/sh
for py in 2.3 2.4 2.5 2.6 2.7 3.0 3.1; do
    for mpi in mpich2 openmpi mpich1 lam; do
	./misc/buildtest.sh --py="$py" --mpi="$mpi"
    done
done
