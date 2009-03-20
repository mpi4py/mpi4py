try:
    import threading
except ImportError:
    raise SystemExit(
        "threading module not available")
try:
    import numpy
except ImportError:
    raise SystemExit(
        "NumPy package not available")

from mpi4py import MPI
if MPI.Query_thread() < MPI.THREAD_MULTIPLE:
    raise SystemExit(
        "MPI does not provide enough thread support")

send_msg = numpy.arange(1000000, dtype='i')
recv_msg = numpy.zeros_like(send_msg)

start_event = threading.Event()

def self_send():
    start_event.wait()
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    comm.Send([send_msg, MPI.INT], dest=rank, tag=0)

def self_recv():
    start_event.wait()
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    comm.Recv([recv_msg, MPI.INT], source=rank, tag=0)

send_thread = threading.Thread(target=self_send)
recv_thread = threading.Thread(target=self_recv)

for t in (recv_thread, send_thread):
    t.start()
assert not numpy.allclose(send_msg, recv_msg)

start_event.set()

for t in (recv_thread, send_thread):
    t.join()
assert numpy.allclose(send_msg, recv_msg)
