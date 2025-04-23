from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor, get_comm_workers, wait


def helloworld():
    comm = get_comm_workers()
    comm.Barrier()

    size = comm.Get_size()
    rank = comm.Get_rank()
    name = MPI.Get_processor_name()

    greet = f"Hello, World! I am worker {rank} of {size} on {name}."

    sbuf = bytearray(128)
    rbuf = bytearray(128)
    dest = (rank + 1) % size
    source = (rank - 1) % size
    rbuf[: len(greet)] = greet.encode()
    for _ in range(size):
        sbuf, rbuf = rbuf, sbuf
        comm.Sendrecv(sbuf, dest, 42, rbuf, source, 42)
    return bytes(rbuf).decode()


if __name__ == "__main__":
    executor = MPIPoolExecutor(5)
    futures = []
    for _ in range(executor.num_workers):
        f = executor.submit(helloworld)
        futures.append(f)
    wait(futures)
    for f in futures:
        print(f.result())
    executor.shutdown()
