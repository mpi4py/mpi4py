import math

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
    sqrt_n = math.floor(math.sqrt(n))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True


def test_primes():
    with MPIPoolExecutor(4) as executor:
        for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
            print(f"{number:d} is prime: {prime}")


if __name__ == "__main__":
    test_primes()
