"""
Compare the speed of primes sequentially vs. using futures.
"""

import sys
import time
import math
try:
    range = xrange
except NameError:
    range = range

try:
    from concurrent.futures import ThreadPoolExecutor
except ImportError:
    ThreadPoolExecutor = None
try:
    from concurrent.futures import ProcessPoolExecutor
except ImportError:
    ProcessPoolExecutor = None

from mpi4py.futures import MPIPoolExecutor

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    117450548693743,
    993960000099397,
]

def is_prime(n):
    if n % 2 == 0:
        return False
    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True

def sequential():
    return list(map(is_prime, PRIMES))

def with_thread_pool_executor():
    if not ThreadPoolExecutor: return None
    with ThreadPoolExecutor(4) as executor:
        return list(executor.map(is_prime, PRIMES))

def with_process_pool_executor():
    if not ProcessPoolExecutor: return None
    with ProcessPoolExecutor(4) as executor:
        return list(executor.map(is_prime, PRIMES))

def with_mpi_pool_executor():
    with MPIPoolExecutor(4) as executor:
        return list(executor.map(is_prime, PRIMES))

def main():
    for name, fn in [('sequential', sequential),
                     ('threads', with_thread_pool_executor),
                     ('processes', with_process_pool_executor),
                     ('mpi4py', with_mpi_pool_executor)]:
        sys.stdout.write('%s: ' % name.ljust(11))
        sys.stdout.flush()
        start = time.time()
        result = fn()
        if result is None:
            sys.stdout.write(' not available\n')
        elif result != [True] * len(PRIMES):
            sys.stdout.write(' failed\n')
        else:
            sys.stdout.write('%5.2f seconds\n' % (time.time() - start))
        sys.stdout.flush()

if __name__ == '__main__':
    main()
