import contextlib
import importlib
import os
import sys


def github():
    return os.environ.get('GITHUB_ACTIONS') == 'true'


def azure():
    return (os.environ.get('TF_BUILD') == 'True')


def import_MPI():
    return importlib.import_module("mpi4py.MPI")


def has_datatype(datatype):
    # https://github.com/pmodels/mpich/issues/7341
    MPI = import_MPI()
    if datatype == MPI.DATATYPE_NULL:
        return False
    try:
        size = datatype.Get_size()
    except MPI.Exception as exc:
        if exc.Get_error_class() != MPI.ERR_TYPE:
            raise
        return False
    if size in (0, MPI.UNDEFINED):
        return False
    return True


def appnum():
    MPI = import_MPI()
    if MPI.APPNUM != MPI.KEYVAL_INVALID:
        return MPI.COMM_WORLD.Get_attr(MPI.APPNUM)
    return None


def has_mpi_appnum():
    return appnum() is not None


def has_mpi_port():
    MPI = import_MPI()
    try:
        port = MPI.Open_port()
    except MPI.Exception:
        return False
    try:
        MPI.Close_port(port)
    except MPI.Exception:
        return False
    return True


def disable_mpi_spawn():
    MPI = import_MPI()
    skip_spawn = (
        os.environ.get('MPI4PY_TEST_SPAWN')
        in ('0', 'n', 'no', 'off', 'false')
    )
    if skip_spawn:
        return True
    macos = (sys.platform == 'darwin')
    windows = (sys.platform == 'win32')
    name, version = MPI.get_vendor()
    if name == 'Open MPI':
        if version < (3, 0, 0):
            return True
        if version == (4, 0, 0):
            return True
        if version == (4, 0, 1) and macos:
            return True
        if version == (4, 0, 2) and macos:
            return True
        if (4, 1, 0) <= version < (4, 2, 0):
            if azure() or github():
                return True
    if name == 'MPICH':
        if (3, 4, 0) <= version < (4, 0, 0):
            if  macos:
                return True
        if version < (4, 1):
            if not has_mpi_appnum():
                return True
        if version < (4, 3):
            try:
                port = MPI.Open_port()
                MPI.Close_port(port)
            except MPI.Exception:
                return True
    if name == 'Intel MPI':
        import mpi4py
        if mpi4py.rc.recv_mprobe:
            return True
        if MPI.COMM_WORLD.Get_size() > 1 and windows:
            return True
    if name == 'Microsoft MPI':
        if version < (8, 1, 0):
            return True
        if not has_mpi_appnum() is None:
            return True
        if os.environ.get("PMI_APPNUM") is None:
            return True
    if name == 'MVAPICH':
        if version < (3, 0, 0):
            return True
        if not has_mpi_appnum():
            return True
    if name == 'MPICH2':
        if not has_mpi_appnum():
            return True
    if MPI.Get_version() < (2, 0):
        return True
    if any(map(sys.modules.get, ('cupy', 'numba'))):
        return True
    #
    return False


@contextlib.contextmanager
def capture_stderr():
    import io
    import sys
    stderr = sys.stderr
    stream = io.StringIO()
    sys.stderr = stream
    try:
        yield stream
    finally:
        sys.stderr = stderr
