import contextlib
import os
import sys

from mpi4py import rc

vmap = {
    "true": True,
    "false": False,
    "0": 0,
    "1": 1,
    "1024": 1024,
}
for arg in sys.argv[1:]:
    attr, value = arg.split("=")
    setattr(rc, attr, vmap.get(value, value))

if rc.errors == "abort":
    rc.initialize = False

from mpi4py import MPI  # noqa: E402

if rc.errors == "abort":
    vendor, version = MPI.get_vendor()
    if vendor == "Intel MPI":
        if version[:2] < (2021, 11):
            sys.exit(0)
    if vendor == "MPICH":
        if version[:2] < (4, 1):
            sys.exit(0)
    if vendor == "Open MPI":
        if version[:2] < (5, 0):
            sys.exit(0)


def check_errhandler(obj):
    if rc.errors == "default":
        if isinstance(obj, MPI.File):
            check_eh = MPI.ERRORS_RETURN
        else:
            check_eh = MPI.ERRORS_ARE_FATAL
    elif rc.errors == "exception":
        check_eh = MPI.ERRORS_RETURN
    elif rc.errors == "abort":
        check_eh = MPI.ERRORS_ABORT
        if MPI.ERRORS_ABORT == MPI.ERRHANDLER_NULL:
            check_eh = MPI.ERRORS_ARE_FATAL
    elif rc.errors == "fatal":
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


with contextlib.suppress(NotImplementedError, MPI.Exception):
    session = MPI.Session.Init()
    try:
        check_errhandler(session)
    finally:
        session.Finalize()


with contextlib.suppress(NotImplementedError, MPI.Exception):
    for commbase in (MPI.COMM_SELF, MPI.COMM_WORLD):
        check_errhandler(commbase)
        comm = commbase.Dup()
        try:
            check_errhandler(comm)
        finally:
            comm.Free()


weh = MPI.COMM_SELF.Get_errhandler()
MPI.COMM_SELF.Set_errhandler(MPI.ERRORS_RETURN)
with contextlib.suppress(NotImplementedError, MPI.Exception):
    win = MPI.Win.Create(
        MPI.BOTTOM,
        1,
        MPI.INFO_NULL,
        MPI.COMM_SELF,
    )
    try:
        check_errhandler(win)
    finally:
        win.Free()
MPI.COMM_SELF.Set_errhandler(weh)
weh.Free()


with contextlib.suppress(NotImplementedError, MPI.Exception):
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


if not MPI.Is_finalized():
    MPI.Finalize()
