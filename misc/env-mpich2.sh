# -*- shell-script -*-
export MPI_DIR=/home/devel/mpi/mpich2-1.3.2p1
export PATH=$MPI_DIR/bin:$PATH
export LD_LIBRARY_PATH=$MPI_DIR/lib:$LD_LIBRARY_PATH
MPISTARTUP=mpdboot
MPISHUTDOWN=mpdallexit
