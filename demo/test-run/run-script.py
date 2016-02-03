from mpi4py import MPI
import sys, os, optparse

assert __name__ == '__main__'
from os.path import split, splitext, dirname, realpath
dirname = dirname(__file__)
assert sys.path[0] == realpath(dirname)
if split(__file__)[1] == '__main__.py':
    if splitext(dirname)[0] == '.zip':
        assert sys.argv[0] == dirname
    else:
        assert realpath(sys.argv[0]) == realpath(dirname)
else:
    assert sys.argv[0] == __file__

parser = optparse.OptionParser()
parser.add_option("--rank", action='store',
                  type='int', dest="rank", default=0)
parser.add_option("--sys-exit", action='store',
                  type='int', dest="sys_exit", default=None)
parser.add_option("--sys-exit-msg", action="store",
                  type="string", dest="sys_exit", default=None)
parser.add_option("--exception", action="store",
                  type="string", dest="exception", default=None)
(options, args) = parser.parse_args()
assert not args

comm = MPI.COMM_WORLD
if comm.rank == options.rank:
    if options.sys_exit:
        sys.exit(options.sys_exit)
    if options.exception:
        raise RuntimeError(options.exception)

comm.Barrier()
if comm.rank > 0:
    comm.Recv([None, 'B'], comm.rank - 1)
print("Hello, World!")
if comm.rank < comm.size - 1:
    comm.Send([None, 'B'], comm.rank + 1)
comm.Barrier()

sys.exit()
