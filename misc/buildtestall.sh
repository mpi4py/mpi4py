#!/bin/sh

PYVER="2.3 2.4 2.5 2.6 2.7 3.0 3.1 3.2"
MPIIMPL="mpich2 openmpi sunmpi mpich1 lammpi"
QUIET=-q

for arg in "$@" ; do
    case "$arg" in
    -v)
    QUIET=
    ;;
    --py=*)
    PYVER=`echo A$arg | sed -e 's/A--py=//g'`
    ;;
    --mpi=*)
    MPIIMPL=`echo A$arg | sed -e 's/A--mpi=//g'`
    ;;
    esac
done

for py in $PYVER; do
    for mpi in $MPIIMPL; do
        ./misc/buildtest.sh $QUIET --py="$py" --mpi="$mpi"
    done
done
