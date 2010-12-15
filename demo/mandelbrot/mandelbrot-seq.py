import numpy as np
import time

tic = time.time()

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

dx = (x2 - x1) / w
dy = (y2 - y1) / h

C = np.empty([h, w], dtype='i')
for k in np.arange(h):
    y = y1 + k * dy
    for j in np.arange(w):
        x = x1 + j * dx
        C[k, j] = mandelbrot(x, y, maxit)

M = C

toc = time.time()
print('wall clock time: %8.2f seconds' % (toc-tic))

# eye candy (requires matplotlib)
if 1:
    try:
        from matplotlib import pyplot as plt
        plt.imshow(M, aspect='equal')
        plt.spectral()
        try:
            import signal
            def action(*args): raise SystemExit
            signal.signal(signal.SIGALRM, action)
            signal.alarm(2)
        except:
            pass
        plt.show()
    except:
        pass
