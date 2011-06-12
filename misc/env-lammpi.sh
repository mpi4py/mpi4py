# -*- shell-script -*-
export MPI_DIR=/home/devel/mpi/lam-7.1.4
export PATH=$MPI_DIR/bin:$PATH
export LD_LIBRARY_PATH=$MPI_DIR/lib:$LD_LIBRARY_PATH
MPISTARTUP=lamboot
MPISHUTDOWN=lamclean
