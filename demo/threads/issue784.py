import faulthandler
import sys
import threading
import time

from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if size < 3:
    if rank == 0:
        print("Run with at least 3 processes", file=sys.stderr)
    sys.exit(0)
if MPI.Query_thread() < MPI.THREAD_MULTIPLE:
    if rank == 0:
        print("MPI does not provide enough thread support", file=sys.stderr)
    sys.exit(0)

color = 1 if rank in {0, 1} else 0
commA = comm.Split(color, rank)


def collective():
    time.sleep(commA.rank * 2.0)
    result = commA.allreduce(True, op=MPI.LAND)
    assert result is True


comm.Barrier()
faulthandler.dump_traceback_later(rank + 5.0, exit=True)

if color:
    threading.Thread(target=collective, name=f"T{rank}").start()

time.sleep(1.0)
commB = comm.Dup()

for t in threading.enumerate():
    if t is not threading.current_thread():
        t.join()

comm.Barrier()
faulthandler.cancel_dump_traceback_later()

commA.Free()
commB.Free()
