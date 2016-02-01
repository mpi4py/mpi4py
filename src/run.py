# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""
Run Python code (scripts, modules, zip files) using the ``runpy``
module. In case of an unhandled exception, abort execution of the MPI
program by calling ``MPI.COMM_WORLD.Abort()``.
"""


def main():
    """
    Entry-point for ``python -m mpi4py.run ...``
    """
    # pylint: disable=missing-docstring
    # pylint: disable=too-many-locals
    import sys
    from runpy import run_module
    try:
        from runpy import run_path
    except ImportError:  # Python 2.6
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
        code = compile(string, '<string>', 'exec')
        return _run_module_code(code, init_globals, run_name, argv0)

    def usage():
        from textwrap import dedent
        prog_name = __package__ + '.run'
        return dedent("""\
        usage: {python} -m {prog} [options] <pyfile> [arg] ..."
           or: {python} -m {prog} [options] -m <module> [arg] ..."

        options:
          -rc <key=value,...>  set 'mpi4py.rc.key=value'
          -p|--profile <pmpi>  use <pmpi> for profiling
          --mpe                profile with MPE
          --vt                 profile with VampirTrace
        """).format(python='python'+sys.version[0], prog=prog_name)

    def parse_command_line(args=None):
        class Options(object):
            # pylint: disable=too-few-public-methods
            rc_args = {}
            profile = None
        if args is None:
            args = sys.argv[1:]
        else:
            args = args[:]
        options = Options()
        while args and args[0].startswith('-'):
            if args[0].startswith('--'):
                args[0] = opt = args[0][1:]
                if '=' in opt:
                    i = opt.index('=')
                    opt, arg = opt[:i], opt[i+1:]
                    assert opt and arg
                    args[0:1] = opt, arg
            if args[0] == '-rc':
                for entry in args[1].split(','):
                    i = entry.index('=')
                    key = entry[:i].strip()
                    val = entry[i+1:].strip()
                    assert key and val
                    try:
                        # pylint: disable=eval-used
                        options.rc_args[key] = eval(val, {})
                    except NameError:
                        options.rc_args[key] = val
                del args[0:2]
                continue
            if args[0] in ('-p', '-prof', '-profile'):
                options.profile = args[1]
                del args[0:2]
                continue
            if args[0] in ('-mpe', '-vt'):
                options.profile = args[0][1:]
                del args[0]
                continue
            break
        return options, args

    def set_abort_status(status):
        if status is None:
            status = 0
        if not isinstance(status, int):
            status = 1
        mpi = sys.modules.get(__package__ + '.MPI')
        if mpi is not None:
            # pylint: disable=protected-access
            mpi._set_abort_status(status)

    # Parse command line and check remaining args
    try:
        options, args = parse_command_line()
    except:  # pylint: disable=bare-except
        sys.exit(usage())
    if len(args) < 1 or args[0] in ('-m', '-c') and len(args) < 2:
        sys.exit(usage())

    # Process command line options
    if options.rc_args:  # Set mpi4py.rc parameters
        from . import rc
        rc(**options.rc_args)
    if options.profile:  # Load profiling library
        from . import profile
        profile(options.profile)

    # Set sys.argv to remaining args
    sys.argv[:] = args

    # Run user code (scripts, modules, zip files) using the 'runpy'
    # module. In case of an unhandled exception, abort execution of
    # the MPI program by calling 'MPI_Abort()'.
    try:

        if sys.argv[0] == '-c':
            dct = {'__builtins__': __builtins__}
            run_string(sys.argv[1], dct, run_name='__main__')
        elif sys.argv[0] == '-m':
            del sys.argv[0]  # Remove "-m" from argument list
            run_module(sys.argv[0], {}, run_name='__main__', alter_sys=1)
        else:
            from os.path import realpath, dirname
            sys.path[0] = realpath(dirname(sys.argv[0]))
            dct = {'__builtins__': __builtins__}
            run_path(sys.argv[0], dct, run_name='__main__')

    except SystemExit as exc:
        set_abort_status(exc.code)
        raise
    except:
        set_abort_status(1)
        raise


if __name__ == '__main__':
    main()
