import pathlib

import numpy as np

from mpi4py import MPI

x1 = -2.0
x2 = +1.0
y1 = -1.0
y2 = +1.0

w = 600
h = 400
maxit = 255


dirname = pathlib.Path(__file__).resolve().parent
executable = dirname / "mandelbrot-worker.exe"

# spawn worker
worker = MPI.COMM_SELF.Spawn(executable, maxprocs=7)
size = worker.Get_remote_size()

# send parameters
rmsg = np.array([x1, x2, y1, y2], dtype="f")
imsg = np.array([w, h, maxit], dtype="i")
worker.Bcast([rmsg, MPI.REAL], root=MPI.ROOT)
worker.Bcast([imsg, MPI.INTEGER], root=MPI.ROOT)

# gather results
counts = np.empty(size, dtype="i")
indices = np.empty(h, dtype="i")
cdata = np.empty([h, w], dtype="i")
worker.Gather(sendbuf=None, recvbuf=[counts, MPI.INTEGER], root=MPI.ROOT)
worker.Gatherv(
    sendbuf=None, recvbuf=[indices, (counts, None), MPI.INTEGER], root=MPI.ROOT
)
worker.Gatherv(
    sendbuf=None,
    recvbuf=[cdata, (counts * w, None), MPI.INTEGER],
    root=MPI.ROOT,
)

# disconnect worker
worker.Disconnect()

# reconstruct full result
M = np.zeros([h, w], dtype="i")
M[indices, :] = cdata

# eye candy (requires matplotlib)
if 1:
    import contextlib

    with contextlib.suppress(Exception):
        from matplotlib import pyplot as plt

        plt.imshow(M, aspect="equal")
        try:
            plt.nipy_spectral()
        except AttributeError:
            plt.spectral()
        plt.pause(2)
