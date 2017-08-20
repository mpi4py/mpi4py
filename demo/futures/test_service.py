import sys
from mpi4py.futures import MPIPoolExecutor


def main():
    def getarg(opt, default=None):
        try:
            return sys.argv[sys.argv.index('--'+opt)+1]
        except ValueError:
            return default

    options = {}
    if '--host' in sys.argv or '--port' in sys.argv:
        service = (getarg('host'), getarg('port'))
    else:
        service = getarg('service')
    if '--info' in sys.argv:
        info = getarg('info').split(',')
        info = dict(entry.split('=') for entry in info if entry)
    else:
        info = None

    with MPIPoolExecutor(service=service, mpi_info=info) as executor:
        fut1 = executor.submit(abs, +42)
        fut2 = executor.submit(abs, -42)
    assert fut1.result(0) == 42
    assert fut2.result(0) == 42


if __name__ == '__main__':
    main()
