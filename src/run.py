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

    def usage(prog_name):
        return "\n".join([
            "usage: {python} -m {prog} <pyfile> [arg] ...",
            "   or: {python} -m {prog} -m <module> [arg] ...",
        ]).format(python='python'+sys.version[0], prog=prog_name)

    def set_abort_status(status):
        if status is None:
            status = 0
        if not isinstance(status, int):
            status = 1
        mpi = sys.modules.get((__package__ or 'mpi4py') + '.MPI')
        if mpi is not None:
            # pylint: disable=protected-access
            mpi._set_abort_status(status)

    # Quick check of command line arguments
    if len(sys.argv) < 2 or sys.argv[1] == '-m' and len(sys.argv) < 3:
        prog_name = (__package__ or 'mpi4py') + '.run'
        sys.exit(usage(prog_name))

    try:

        del sys.argv[0]  # Remove "mpi4py/run.py" from argument list
        if sys.argv[0] == '-m':
            del sys.argv[0]  # Remove "-m" from argument list
            run_module(sys.argv[0], run_name='__main__', alter_sys=1)
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
