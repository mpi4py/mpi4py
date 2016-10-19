from __future__ import print_function
from __future__ import division
import sys
import time

from mpi4py.futures import MPICommExecutor

try:
    range = xrange
except NameError:
    pass

x0 = -2.0
x1 = +2.0
y0 = -1.5
y1 = +1.5

w = 1600
h = 1200

dx = (x1 - x0) / w
dy = (y1 - y0) / h

def julia(x, y):
    c = complex(0, 0.65)
    z = complex(x, y)
    n = 255
    while abs(z) < 3 and n > 1:
        z = z**2 + c
        n -= 1
    return n

def julia_line(k):
    line = bytearray(w)
    y = y1 - k * dy
    for j in range(w):
        x = x0 + j * dx
        line[j] = julia(x, y)
    return line

def plot(image):
    import warnings
    warnings.simplefilter('ignore', UserWarning)
    try:
        from matplotlib import pyplot as plt
    except ImportError:
        return
    plt.figure()
    plt.imshow(image, aspect='equal', cmap='cubehelix')
    plt.axis('off')
    try:
        plt.draw()
        plt.pause(2)
    except:
        pass

def test_julia():
    with MPICommExecutor() as executor:
        if executor is None: return # worker process
        tic = time.time()
        image = list(executor.map(julia_line, range(h), chunksize=10))
        toc = time.time()

    print("%s Set %dx%d in %.2f seconds." % ('Julia', w, h, toc-tic))
    if len(sys.argv) > 1 and sys.argv[1] == '-plot':
        plot(image)

if __name__ == '__main__':
    test_julia()
