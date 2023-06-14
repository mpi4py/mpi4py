import math
import sys
from mpi4py.futures import MPIPoolExecutor, wait
from mpi4py.futures import get_comm_workers


def compute_pi(n):
    comm = get_comm_workers()
    comm.barrier()

    n = comm.bcast(n, root=0)
    h = 1.0 / n
    s = 0.0
    for i in range(comm.rank + 1, n + 1, comm.size):
        x = h * (i - 0.5)
        s += 4.0 / (1.0 + x**2)
    pi = comm.allreduce(s * h)
    return pi


def main():
    try:
        n = int(sys.argv[1])
    except IndexError:
        n = 256
    try:
        P = int(sys.argv[2])
    except IndexError:
        P = 5
    with MPIPoolExecutor(P) as executor:
        P = executor.num_workers
        fs = [executor.submit(compute_pi, n) for _ in range(P)]
        wait(fs)
        pi = fs[0].result()
        print(
            f"pi: {pi:.15f}, error: {abs(pi - math.pi):.3e}",
            f"({n:d} intervals, {P:d} workers)",
        )


if __name__ == '__main__':
    main()
