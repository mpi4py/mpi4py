# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""
Run some benchmarks and tests
"""

def helloworld(comm, args=None, verbose=True):
    """
    Hello, World! using MPI
    """
    from mpi4py import MPI
    from optparse import OptionParser
    parser = OptionParser(prog="mpi4py helloworld")
    parser.add_option("-q","--quiet", action="store_false",
                      dest="verbose", default=verbose)
    (options, args) = parser.parse_args(args)
    size = comm.Get_size()
    rank = comm.Get_rank()
    name = MPI.Get_processor_name()
    message = ("Hello, World! I am process %*d of %d on %s."
               % (len(str(size-1)), rank, size, name) )
    _seq_begin(comm)
    if options.verbose:
        _println(message, stream=_stdout)
    _seq_end(comm)
    return message

def ringtest(comm, args=None, verbose=True):
    """
    Time a message going around the ring of processes
    """
    from array import array
    from mpi4py import MPI
    from optparse import OptionParser
    parser = OptionParser(prog="mpi4py ringtest")
    parser.add_option("-q","--quiet", action="store_false",
                      dest="verbose", default=verbose)
    parser.add_option("-n", "--size",  type="int", default=1, dest="size")
    parser.add_option("-l", "--loop",  type="int", default=1, dest="loop")
    parser.add_option("-s", "--skip",  type="int", default=0, dest="skip")
    (options, args) = parser.parse_args(args)
    def ring(comm, n=1, loops=1, skip=0):
        iterations = list(range((loops+skip)))
        size = comm.Get_size()
        rank = comm.Get_rank()
        source  = (rank - 1) % size
        dest = (rank + 1) % size
        Sendrecv = comm.Sendrecv
        Send = comm.Send
        Recv = comm.Recv
        Wtime = MPI.Wtime
        sendmsg = array('B', [42])*n
        recvmsg = array('B', [ 0])*n
        if size == 1:
            for i in iterations:
                if i == skip:
                    tic = Wtime()
                Sendrecv(sendmsg, dest,   0,
                         recvmsg, source, 0)
        else:
            if rank == 0:
                for i in iterations:
                    if i == skip:
                        tic = Wtime()
                    Send(sendmsg, dest,   0)
                    Recv(recvmsg, source, 0)
            else:
                sendmsg = recvmsg
                for i in iterations:
                    if i == skip:
                        tic = Wtime()
                    Recv(recvmsg, source, 0)
                    Send(sendmsg, dest,   0)
        toc = Wtime()
        if comm.rank == 0 and sendmsg != recvmsg:
            import warnings, traceback
            try:
                warnings.warn("received message does not match!")
            except UserWarning:
                traceback.print_exc()
                comm.Abort(2)
        return toc - tic
    size  = getattr(options, 'size',  1)
    loops = getattr(options, 'loops', 1)
    skip  = getattr(options, 'skip',  0)
    comm.Barrier()
    elapsed = ring(comm, size, loops, skip)
    if options.verbose and comm.rank == 0:
        _println("time for %d loops = %g seconds (%d processes, %d bytes)"
                 % (loops, elapsed, comm.size, size),
                 stream=_stdout)
    return elapsed

from sys import stdout as _stdout
from sys import stderr as _stderr

def _println(message, stream):
    stream.write(message+'\n')
    stream.flush()

def _seq_begin(comm):
    comm.Barrier()
    size = comm.Get_size()
    rank = comm.Get_rank()
    if rank > 0:
        comm.Recv([None, 'B'], rank - 1)

def _seq_end(comm):
    size = comm.Get_size()
    rank = comm.Get_rank()
    if rank < size - 1:
        comm.Send([None, 'B'], rank + 1)
    comm.Barrier()

_commands = {
    'helloworld' : helloworld,
    'ringtest'   : ringtest,
    }

def _main(args=None):
    from optparse import OptionParser
    from mpi4py import __name__    as prog
    from mpi4py import __version__ as version
    parser = OptionParser(prog=prog, version='%prog ' + version,
                          usage="%prog [options] <command> [args]")
    parser.add_option("--no-threads",
                      action="store_false", dest="threaded", default=True,
                      help="initialize MPI without thread support")
    parser.add_option("--thread-level", type="choice", metavar="LEVEL",
                      choices=["single", "funneled", "serialized", "multiple"],
                      action="store", dest="thread_level", default="multiple",
                      help="initialize MPI with required thread support")
    parser.add_option("--mpe",
                      action="store_true", dest="mpe", default=False,
                      help="use MPE for MPI profiling")
    parser.add_option("--vt",
                      action="store_true", dest="vt", default=False,
                      help="use VampirTrace for MPI profiling")
    parser.disable_interspersed_args()
    (options, args) = parser.parse_args(args)
    #
    import mpi4py
    mpi4py.rc.threaded = options.threaded
    mpi4py.rc.thread_level = options.thread_level
    if options.mpe:
        mpi4py.profile('mpe', logfile='mpi4py')
    if options.vt:
        mpi4py.profile('vt', logfile='mpi4py')
    #
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    if not args:
        if comm.rank == 0:
            parser.print_usage()
        parser.exit()
    command = args.pop(0)
    if command not in _commands:
        if comm.rank == 0:
            parser.error("unknown command '%s'" % command)
        parser.exit(2)
    command = _commands[command]
    command(comm, args=args)
    parser.exit()

if __name__ == '__main__':
    _main()
