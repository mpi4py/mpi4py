# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""
Run Python code (scripts, modules, zip files) using the ``runpy``
module. In case of an unhandled exception, abort execution of the MPI
program by calling ``MPI.COMM_WORLD.Abort()``.
"""
from __future__ import print_function


def main():
    """
    Entry-point for ``python -m mpi4py.run ...``
    """
    # pylint: disable=missing-docstring
    import sys
    from runpy import run_module
    try:
        from runpy import run_path
    except ImportError:  # Python 2.6  # pragma: no cover
        def run_path(path_name, init_globals=None, run_name=None):
            from pkgutil import read_code
            from runpy import _run_module_code
            with open(path_name, 'rb') as fobj:  # compiled file
                code = read_code(fobj)
            if code is None:
                with open(path_name, 'rU') as fobj:  # normal source code
                    code = compile(fobj.read(), path_name, 'exec')
            return _run_module_code(code, init_globals, run_name, path_name)

    def run_string(string, init_globals=None, run_name=None, argv0='-c'):
        from runpy import _run_module_code
        karg = 'script_name' if sys.version_info >= (3, 4) else 'mod_fname'
        code = compile(string, '<string>', 'exec', 0, 1)
        return _run_module_code(code, init_globals, run_name, **{karg: argv0})

    def version():
        from . import __version__
        print(__package__, __version__, file=sys.stdout)
        sys.exit(0)

    def usage(errmess=None):
        from textwrap import dedent
        if __name__ == '__main__':
            prog_name = __package__ + '.run'
        else:
            prog_name = __package__
        subs = dict(prog=prog_name, python='python'+sys.version[0])

        cmdline = dedent("""
        usage: {python} -m {prog} [options] <pyfile> [arg] ...
           or: {python} -m {prog} [options] -m <module> [arg] ...
           or: {python} -m {prog} [options] -c <string> [arg] ...
        """).strip().format(**subs)

        helptip = dedent("""
        Try `{python} -m {prog} -h` for more information.
        """).strip().format(**subs)

        options = dedent("""
        options:
          --version            show version number and exit
          -h|--help            show this help message and exit
          -rc <key=value,...>  set 'mpi4py.rc.key=value'
          -p|--profile <pmpi>  use <pmpi> for profiling
          --mpe                profile with MPE
          --vt                 profile with VampirTrace
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
        class Options(object):  # pylint: disable=too-few-public-methods
            rc_args = {}
            profile = None

        def poparg(args):
            if len(args) < 2 or args[1].startswith('-'):
                usage('Argument expected for option: ' + args[0])
            return args.pop(1)

        options = Options()
        args = sys.argv[1:] if args is None else args[:]
        while args and args[0].startswith('-'):
            if args[0] in ('-m', '-c'):
                break  # Stop processing options
            if args[0] in ('-h', '-help', '--help'):
                usage()  # Print help and exit
            if args[0] in ('-version', '--version'):
                version()  # Print version and exit
            try:
                arg0 = args[0]
                if arg0.startswith('--'):
                    if '=' in arg0:
                        i = arg0.index('=')
                        opt, arg = arg0[1:i], arg0[i+1:]
                        if opt in ('-rc', '-profile'):
                            arg0, args[1:1] = opt, [arg]
                    else:
                        arg0 = arg0[1:]
                if arg0 == '-rc':
                    for entry in poparg(args).split(','):
                        i = entry.index('=')
                        key = entry[:i].strip()
                        val = entry[i+1:].strip()
                        if not key or not val:
                            raise ValueError(entry)
                        try:
                            # pylint: disable=eval-used
                            options.rc_args[key] = eval(val, {})
                        except NameError:
                            options.rc_args[key] = val
                elif arg0 in ('-p', '-profile'):
                    options.profile = poparg(args) or None
                elif arg0 in ('-mpe', '-vt'):
                    options.profile = arg0[1:]
                else:
                    usage('Unknown option: ' + args[0])
                del args[0]
            except Exception:  # pylint: disable=broad-except
                # Bad option, print usage and exit with error
                usage('Cannot parse option: ' + args[0])
        # Final check and return to caller
        if len(args) < 1:
            usage("No path specified for execution")
        elif args[0] in ('-m', '-c') and len(args) < 2:
            usage('Argument expected for option: ' + args[0])
        return options, args

    def bootstrap(options):
        if options.rc_args:  # Set mpi4py.rc parameters
            from . import rc
            rc(**options.rc_args)
        if options.profile:  # Load profiling library
            from . import profile
            profile(options.profile)

    def set_abort_status(status):
        if status is None:
            status = 0
        if not isinstance(status, int):
            status = 1
        mpi = sys.modules.get(__package__ + '.MPI')
        if mpi is not None:
            # pylint: disable=protected-access
            mpi._set_abort_status(status)

    # Parse and process command line options
    options, sys.argv[:] = parse_command_line()
    bootstrap(options)

    # Run user code (scripts, modules, zip files) using the 'runpy'
    # module. In case of an unhandled exception, abort execution of
    # the MPI program by calling 'MPI_Abort()'.
    try:

        if sys.argv[0] == '-c':
            run_string(sys.argv[1], run_name='__main__')
        elif sys.argv[0] == '-m':
            del sys.argv[0]  # Remove "-m" from argument list
            run_module(sys.argv[0], run_name='__main__', alter_sys=True)
        else:
            from os.path import realpath, dirname
            sys.path[0] = realpath(dirname(sys.argv[0]))  # Fix sys.path
            run_path(sys.argv[0], run_name='__main__')

    except SystemExit as exc:
        set_abort_status(exc.code)
        raise
    except:
        set_abort_status(1)
        raise


if __name__ == '__main__':
    main()
