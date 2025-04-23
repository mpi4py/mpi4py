import optparse
import pathlib
import sys

from mpi4py import MPI

assert __name__ == "__main__"
assert sys.path[0] == str(pathlib.Path(__file__).parent)
if pathlib.Path(__file__).name == "__main__.py":
    assert sys.argv[0] == sys.path[0]
else:
    assert sys.argv[0] == __file__

parser = optparse.OptionParser()
parser.add_option(
    "--rank",
    action="store",
    type="int",
    dest="rank",
    default=0,
)
parser.add_option(
    "--interrupt",
    action="store_true",
    dest="interrupt",
    default=False,
)
parser.add_option(
    "--sys-exit",
    action="store",
    type="int",
    dest="sys_exit",
    default=None,
)
parser.add_option(
    "--sys-exit-msg",
    action="store",
    type="string",
    dest="sys_exit",
    default=None,
)
parser.add_option(
    "--exception",
    action="store",
    type="string",
    dest="exception",
    default=None,
)
(options, args) = parser.parse_args()
assert not args

comm = MPI.COMM_WORLD

comm.Barrier()
comm.Barrier()
if comm.rank == options.rank:
    if options.interrupt:
        raise KeyboardInterrupt
    if options.sys_exit:
        sys.exit(options.sys_exit)
    if options.exception:
        raise RuntimeError(options.exception)

comm.Barrier()
comm.Barrier()
if comm.rank > 0:
    comm.Recv([None, "B"], comm.rank - 1)
print("Hello, World!", flush=True)
if comm.rank < comm.size - 1:
    comm.Send([None, "B"], comm.rank + 1)
comm.Barrier()

sys.exit()
