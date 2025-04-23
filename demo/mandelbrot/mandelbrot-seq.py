import time

import numpy as np

tic = time.time()

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


dx = (x2 - x1) / w
dy = (y2 - y1) / h

C = np.empty([h, w], dtype="i")
for k in np.arange(h):
    y = y1 + k * dy
    for j in np.arange(w):
        x = x1 + j * dx
        C[k, j] = mandelbrot(x, y, maxit)

M = C

toc = time.time()
print(f"wall clock time: {toc - tic:8.2f} seconds")

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
