# -*- shell-script -*-
export MPI_DIR=/home/devel/mpi/mpich-1.2.7p1
export PATH=$MPI_DIR/bin:$PATH
export LD_LIBRARY_PATH=$MPI_DIR/lib:$MPI_DIR/lib/shared:$LD_LIBRARY_PATH
export MPICH_USE_SHLIB=yes
