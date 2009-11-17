from mpi4py import MPI
import numpy as np

x1 = -2.0
x2 =  1.0
y1 = -1.0
y2 =  1.0

w = 150
h = 100
maxit = 127

def mandelbrot(x, y, maxit):
    c = x + y*1j
    z = 0 + 0j
    it = 0
    while abs(z) < 2 and it < maxit:
        z = z**2 + c
        it += 1
    return it

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

rmsg = np.empty(4, dtype='f')
imsg = np.empty(3, dtype='i')

if rank == 0:
    rmsg[:] = [x1, x2, y1, y2]
    imsg[:] = [w, h, maxit]

comm.Bcast([rmsg, MPI.FLOAT], root=0)
comm.Bcast([imsg, MPI.INT], root=0)

x1, x2, y1, y2 = [float(r) for r in rmsg]
w, h, maxit    = [int(i) for i in imsg]
dx = (x2 - x1) / w
dy = (y2 - y1) / h

# number of lines to compute here
N = h // size + (h % size > rank)
N = np.array(N, dtype='i')
# indices of lines to compute here
I = np.arange(rank, h, size, dtype='i')
# compute local lines
C = np.empty([N, w], dtype='i')
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
    counts = np.empty(size, dtype='i')
    indices = np.empty(h, dtype='i')
    cdata = np.empty([h, w], dtype='i')
comm.Gather(sendbuf=[N, MPI.INT],
            recvbuf=[counts, MPI.INT],
            root=0)
comm.Gatherv(sendbuf=[I, MPI.INT],
             recvbuf=[indices, (counts, None), MPI.INT],
             root=0)
comm.Gatherv(sendbuf=[C, MPI.INT],
             recvbuf=[cdata, (counts*w, None), MPI.INT],
             root=0)

# reconstruct full result at root
if rank == 0:
    M = np.zeros([h,w], dtype='i')
    M[indices, :] = cdata


# eye candy (requires matplotlib)
if rank == 0:
    try:
        from matplotlib import pyplot as plt
        plt.imshow(M, aspect='equal')
        plt.spectral()
        try:
            import sys, signal
            def action(*args):
                raise SystemExit
            signal.signal(signal.SIGALRM, action)
            signal.alarm(2)
        except:
            pass
        plt.show()
    except:
        pass
MPI.COMM_WORLD.Barrier()
