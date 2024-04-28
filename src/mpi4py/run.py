# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Run Python code using ``mpi4py``.

Run Python code (scripts, modules, zip files) using the ``runpy``
module. In case of an unhandled exception, abort execution of the MPI
program by calling ``MPI.COMM_WORLD.Abort()``.
"""


def run_command_line(args=None):
    """Run command line ``[pyfile | -m mod | -c cmd | -] [arg] ...``.

    * ``pyfile`` : program read from script file
    * ``-m mod`` : run library module as a script
    * ``-c cmd`` : program passed in as a command string
    * ``-``      : program read from standard input (``sys.stdin``)
    * ``arg ...``: arguments passed to program in ``sys.argv[1:]``
    """
    # pylint: disable=import-outside-toplevel
    import sys
    from runpy import run_module, run_path

    def run_string(string, init_globals=None, run_name=None,
                   filename='<string>', argv0='-c'):
        from runpy import _run_module_code
        code = compile(string, filename, 'exec', 0, True)
        kwargs = {'script_name': argv0}
        return _run_module_code(code, init_globals, run_name, **kwargs)

    sys.argv[:] = args if args is not None else sys.argv[1:]

    if sys.argv[0] == '-':
        cmd = sys.stdin.read()
        run_string(cmd, run_name='__main__', filename='<stdin>', argv0='-')
    elif sys.argv[0] == '-c':
        cmd = sys.argv.pop(1)  # Remove "cmd" from argument list
        run_string(cmd, run_name='__main__', filename='<string>', argv0='-c')
    elif sys.argv[0] == '-m':
        del sys.argv[0]  # Remove "-m" from argument list
        run_module(sys.argv[0], run_name='__main__', alter_sys=True)
    else:
        from os.path import realpath, dirname
        if not getattr(sys.flags, 'isolated', 0):  # pragma: no branch
            sys.path[0] = realpath(dirname(sys.argv[0]))  # Fix sys.path
        run_path(sys.argv[0], run_name='__main__')


def set_abort_status(status):
    """Terminate MPI execution environment at Python exit.

    Terminate MPI execution environment at Python exit by calling
    ``MPI.COMM_WORLD.Abort(status)``. This function should be called
    within an ``except`` block. Afterwards, exceptions should be
    re-raised.
    """
    # pylint: disable=import-outside-toplevel
    import sys
    if isinstance(status, SystemExit):
        status = status.code
    elif isinstance(status, KeyboardInterrupt):
        from _signal import SIGINT
        status = SIGINT + 128
    if not isinstance(status, int):
        status = 0 if status is None else 1
    pkg = __spec__.parent
    mpi = sys.modules.get(f'{pkg}.MPI')
    if mpi is not None and status:
        # pylint: disable=protected-access
        mpi._set_abort_status(status)


def main():
    """Entry-point for ``python -m mpi4py.run ...``."""
    # pylint: disable=too-many-statements
    # pylint: disable=import-outside-toplevel
    import os
    import sys

    def prefix():
        prefix = os.path.dirname(__spec__.origin)
        print(prefix, file=sys.stdout)
        sys.exit(0)

    def version():
        from . import __version__
        package = __spec__.parent
        print(f"{package} {__version__}", file=sys.stdout)
        sys.exit(0)

    def mpi_std_version():
        from . import rc
        rc.initialize = rc.finalize = False
        from . import MPI
        version = ".".join(map(str, (MPI.VERSION, MPI.SUBVERSION)))
        rtversion = ".".join(map(str, MPI.Get_version()))
        note = f" (runtime: MPI {rtversion})" if rtversion != version else ""
        print(f"MPI {version}{note}", file=sys.stdout)
        sys.exit(0)

    def mpi_lib_version():
        from . import rc
        rc.initialize = rc.finalize = False
        from . import MPI
        library_version = MPI.Get_library_version()
        print(library_version, file=sys.stdout)
        sys.exit(0)

    def usage(errmess=None):
        from textwrap import dedent
        python = os.path.basename(sys.executable)
        program = __spec__.name

        cmdline = dedent(f"""
        usage: {python} -m {program} [options] <pyfile> [arg] ...
           or: {python} -m {program} [options] -m <mod> [arg] ...
           or: {python} -m {program} [options] -c <cmd> [arg] ...
           or: {python} -m {program} [options] - [arg] ...
        """).strip()

        helptip = dedent(f"""
        Try `{python} -m {program} -h` for more information.
        """).strip()

        options = dedent("""
        options:
          --prefix             show install path and exit
          --version            show version number and exit
          --mpi-std-version    show MPI standard version and exit
          --mpi-lib-version    show MPI library version and exit
          -h|--help            show this help message and exit
          -rc <key=value,...>  set 'mpi4py.rc.key=value'
        """).strip()

        if errmess:
            print(errmess, file=sys.stderr)
            print(cmdline, file=sys.stderr)
            print(helptip, file=sys.stderr)
            sys.exit(1)
        else:
            print(cmdline, file=sys.stdout)
            print(options, file=sys.stdout)
            sys.exit(0)

    def parse_command_line(args=None):
        # pylint: disable=too-many-branches

        class Options:
            # pylint: disable=too-few-public-methods
            # pylint: disable=missing-class-docstring
            rc_args = {}

        def poparg(args):
            if len(args) < 2 or args[1].startswith('-'):
                usage('Argument expected for option: ' + args[0])
            return args.pop(1)

        options = Options()
        args = sys.argv[1:] if args is None else args[:]
        while args and args[0].startswith('-'):
            arg0 = args[0]
            if arg0 in ('-m', '-c', '-'):
                break  # Stop processing options
            if arg0 in ('-h', '-help', '--help'):
                usage()  # Print help and exit
            if arg0 in ('-prefix', '--prefix'):
                prefix()  # Print install path and exit
            if arg0 in ('-version', '--version'):
                version()  # Print version number and exit
            if arg0 in ('-mpi-std-version', '--mpi-std-version'):
                mpi_std_version()  # Print MPI standard version and exit
            if arg0 in ('-mpi-lib-version', '--mpi-lib-version'):
                mpi_lib_version()  # Print MPI library version and exit
            if arg0.startswith('--'):
                if '=' in arg0:
                    opt, _, arg = arg0[1:].partition('=')
                    if opt in ('-rc',):
                        arg0, args[1:1] = opt, [arg]
                else:
                    arg0 = arg0[1:]
            if arg0 == '-rc':
                from ast import literal_eval
                for entry in poparg(args).split(','):
                    key, _, val = entry.partition('=')
                    if not key or not val:
                        usage('Cannot parse rc option: ' + entry)
                    try:
                        val = literal_eval(val)
                    except ValueError:
                        pass
                    options.rc_args[key] = val
            else:
                usage('Unknown option: ' + args[0])
            del args[0]
        # Check remaining args and return to caller
        if not args:
            usage("No path specified for execution")
        if args[0] in ('-m', '-c') and len(args) < 2:
            usage("Argument expected for option: " + args[0])
        return options, args

    def bootstrap(options):
        if options.rc_args:  # Set mpi4py.rc parameters
            from . import rc
            rc(**options.rc_args)

    # Parse and process command line options
    options, args = parse_command_line()
    bootstrap(options)

    # Run user code. In case of an unhandled exception, abort
    # execution of the MPI program by calling 'MPI_Abort()'.
    try:
        run_command_line(args)
    except SystemExit as exc:
        set_abort_status(exc)
        raise
    except KeyboardInterrupt as exc:
        set_abort_status(exc)
        raise
    except BaseException:
        set_abort_status(1)
        raise


if __name__ == '__main__':
    main()
