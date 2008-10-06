from mpi4py import MPI
import helloworld as hw

comm = MPI.COMM_WORLD
hw.sayhello(comm)
