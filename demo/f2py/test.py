from mpi4py import MPI
import helloworld as hw

comm = MPI.COMM_WORLD
fcomm = comm.py2f()
hw.sayhello(fcomm)
