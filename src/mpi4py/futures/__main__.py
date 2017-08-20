# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Run Python code using ``mpi4py.futures``.

Python code (scripts, modules, zip files) is run in the process with rank 0 in
``MPI.COMM_WORLD`` and creates `MPIPoolExecutor` instances to submit tasks. The
other processes team-up in a static-size shared pool of workers executing tasks
submitted from the master process.
"""
from __future__ import print_function


def main():
    """Entry point for ``python -m mpi4py.futures ...``."""
    # pylint: disable=missing-docstring
    import os
    import sys
    from ..run import run_command_line
    from ..run import set_abort_status
    from ._lib import SharedPoolCtx

    class UsageExit(SystemExit):
        pass

    def usage(error=None):
        from textwrap import dedent
        usage = dedent("""
        usage: python{0} -m {prog} <pyfile> [arg] ...
           or: python{0} -m {prog} -m <module> [arg] ...
           or: python{0} -m {prog} -c <string> [arg] ...
        """).strip().format(sys.version[0], prog=__package__)
        if error:
            print(error, file=sys.stderr)
            print(usage, file=sys.stderr)
            raise UsageExit(1)
        else:
            print(usage, file=sys.stdout)
            raise UsageExit(0)

    def chk_command_line():
        args = sys.argv[1:]
        if len(args) < 1:
            usage("No path specified for execution")
        elif args[0] == '-':
            pass
        elif args[0] in ('-h', '--help'):
            usage()
        elif args[0] in ('-m', '-c'):
            if len(args) < 2:
                usage("Argument expected for option: " + args[0])
        elif args[0].startswith('-'):
            usage("Unknown option: " + args[0])
        elif not os.path.exists(args[0]):
            usage("Path does not exist: " + args[0])

    try:
        with SharedPoolCtx() as context:
            if context is not None:
                chk_command_line()
                run_command_line()
    except UsageExit:
        raise
    except SystemExit as exc:
        set_abort_status(exc.code)
        raise
    except:
        set_abort_status(1)
        raise


if __name__ == '__main__':
    main()
