import numpy as np

from mpi4py import MPI

tic = MPI.Wtime()

x1 = -2.0
x2 = +1.0
y1 = -1.0
y2 = +1.0

w = 150
h = 100
maxit = 127


def mandelbrot(x, y, maxit):
    c = x + y * 1j
    z = 0 + 0j
    it = 0
    while abs(z) < 2 and it < maxit:
        z = z**2 + c
        it += 1
    return it


comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

rmsg = np.empty(4, dtype="f")
imsg = np.empty(3, dtype="i")

if rank == 0:
    rmsg[:] = [x1, x2, y1, y2]
    imsg[:] = [w, h, maxit]

comm.Bcast([rmsg, MPI.FLOAT], root=0)
comm.Bcast([imsg, MPI.INT], root=0)

x1, x2, y1, y2 = (float(r) for r in rmsg)
w, h, maxit = (int(i) for i in imsg)
dx = (x2 - x1) / w
dy = (y2 - y1) / h

# number of lines to compute here
N = h // size + (h % size > rank)
N = np.array(N, dtype="i")
# indices of lines to compute here
I = np.arange(rank, h, size, dtype="i")  # noqa: E741
# compute local lines
C = np.empty([N, w], dtype="i")
for k in np.arange(N):
    y = y1 + I[k] * dy
    for j in np.arange(w):
        x = x1 + j * dx
        C[k, j] = mandelbrot(x, y, maxit)
# gather results at root
counts = 0
indices = None
cdata = None
if rank == 0:
    counts = np.empty(size, dtype="i")
    indices = np.empty(h, dtype="i")
    cdata = np.empty([h, w], dtype="i")
comm.Gather(sendbuf=[N, MPI.INT], recvbuf=[counts, MPI.INT], root=0)
comm.Gatherv(
    sendbuf=[I, MPI.INT], recvbuf=[indices, (counts, None), MPI.INT], root=0
)
comm.Gatherv(
    sendbuf=[C, MPI.INT], recvbuf=[cdata, (counts * w, None), MPI.INT], root=0
)
# reconstruct full result at root
if rank == 0:
    M = np.zeros([h, w], dtype="i")
    M[indices, :] = cdata

toc = MPI.Wtime()
wct = comm.gather(toc - tic, root=0)
if rank == 0:
    for task, time in enumerate(wct):
        print(f"wall clock time: {time:8.2f} seconds (task {task:d})")

    def mean(seq):
        return sum(seq) / len(seq)

    print(f"all tasks, mean: {mean(wct):8.2f} seconds")
    print(f"all tasks, min:  {min(wct):8.2f} seconds")
    print(f"all tasks, max:  {max(wct):8.2f} seconds")
    print(f"all tasks, sum:  {sum(wct):8.2f} seconds")

# eye candy (requires matplotlib)
if rank == 0:
    import contextlib

    with contextlib.suppress(Exception):
        from matplotlib import pyplot as plt

        plt.imshow(M, aspect="equal")
        try:
            plt.nipy_spectral()
        except AttributeError:
            plt.spectral()
        plt.pause(2)

MPI.COMM_WORLD.Barrier()
