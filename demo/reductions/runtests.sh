#!/bin/sh

MPIEXEC=mpiexec
NP_FLAG=-n
NP=5

PYTHON=python

set -x
$MPIEXEC $NP_FLAG $NP $PYTHON test_reductions.py -q
