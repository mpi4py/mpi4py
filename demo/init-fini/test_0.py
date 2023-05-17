import os
import sys
from mpi4py import rc

vmap = {'true': True, 'false': False}
for arg in sys.argv[1:]:
    attr, value = arg.split('=')
    setattr(rc, attr, vmap.get(value, value))

if rc.errors == 'abort':
    rc.initialize = False

from mpi4py import MPI

if rc.errors == 'abort':
    vendor, version = MPI.get_vendor()
    if vendor == 'MPICH':
        if version[0] > 3 and version[:2] < (4, 1):
            sys.exit(0)

def check_errhandler(obj):
    if rc.errors == 'default':
        if isinstance(obj, MPI.File):
            check_eh = MPI.ERRORS_RETURN
        else:
            check_eh = MPI.ERRORS_ARE_FATAL
    elif rc.errors == 'exception':
        check_eh = MPI.ERRORS_RETURN
    elif rc.errors == 'abort':
        if MPI.ERRORS_ABORT != MPI.ERRHANDLER_NULL:
            check_eh = MPI.ERRORS_ABORT
        else:
            check_eh = MPI.ERRORS_ARE_FATAL
    elif rc.errors == 'fatal':
        check_eh = MPI.ERRORS_ARE_FATAL
    else:
        assert 0
    eh = obj.Get_errhandler()
    try:
        assert eh == check_eh
    finally:
        if eh != MPI.ERRHANDLER_NULL:
            eh.Free()


if not MPI.Is_initialized():
    MPI.Init()


try:
    session = MPI.Session.Init()
    try:
        check_errhandler(session)
    finally:
        session.Finalize()
except NotImplementedError:
    pass
except MPI.Exception:
    pass


try:
    for commbase in (MPI.COMM_SELF, MPI.COMM_WORLD):
        check_errhandler(commbase)
        comm = commbase.Dup()
        try:
            check_errhandler(comm)
        finally:
            comm.Free()
except NotImplementedError:
    pass
except MPI.Exception:
    pass


weh = MPI.COMM_SELF.Get_errhandler()
MPI.COMM_SELF.Set_errhandler(MPI.ERRORS_RETURN)
try:
    win = MPI.Win.Create(
        MPI.BOTTOM, 1,
        MPI.INFO_NULL,
        MPI.COMM_SELF,
    )
    try:
        check_errhandler(win)
    finally:
        win.Free()
except NotImplementedError:
    pass
except MPI.Exception:
    pass
finally:
    MPI.COMM_SELF.Set_errhandler(weh)
    weh.Free()


try:
    # check_errhandler(MPI.FILE_NULL)  # TODO
    file = MPI.File.Open(
        MPI.COMM_SELF,
        os.devnull,
        MPI.MODE_WRONLY,
        MPI.INFO_NULL,
    )
    try:
        check_errhandler(file)
    finally:
        file.Close()
except NotImplementedError:
    pass
except MPI.Exception:
    pass


if not MPI.Is_finalized():
    MPI.Finalize()
