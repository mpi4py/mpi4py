import sys

import mpi4py

mpi4py.rc.initialize = False

from mpi4py import MPI  # noqa: E402


def test_error():
    for errcls in [
        getattr(MPI, attr) for attr in dir(MPI) if attr.startswith("ERR_")
    ]:
        if errcls == MPI.ERR_LASTCODE:
            continue

        errcod = MPI.Get_error_class(errcls)
        assert errcod > MPI.SUCCESS
        assert errcod == errcls

        errstr = MPI.Get_error_string(errcls)
        assert errstr

        excobj = MPI.Exception(errcls)
        excstr = str(excobj)
        assert errstr == errstr


def test_info():
    info = MPI.Info.Create()

    info.Dup().Free()

    info.Set("hello", "world")

    info.Dup().Free()

    key = info.Get_nthkey(0)
    assert key == "hello"

    value = info.Get("hello")
    assert value == "world"

    info.Delete("hello")

    nkeys = info.Get_nkeys()
    assert nkeys == 0

    value = info.Get("hello")
    assert value is None

    finfo = MPI.Info.f2py(info.py2f())
    assert info == finfo

    info.Free()


def test_session():
    for _ in range(2):
        session = MPI.Session.Init()

        for n in range(session.Get_num_psets()):
            pset_name = session.Get_nth_pset(n)
            info = session.Get_pset_info(pset_name)
            mpi_size = int(info.Get("mpi_size"))
            info.Free()
            assert mpi_size > 0

            group = session.Create_group(pset_name)
            assert mpi_size == group.Get_size()
            comm = MPI.Intracomm.Create_from_group(group)
            assert group.Get_size() == comm.Get_size()
            assert group.Get_rank() == comm.Get_rank()
            comm.Barrier()
            group.Free()
            comm.Free()

        session.Finalize()


def test_all():
    test_error()
    test_info()
    test_session()


def skip():
    name, version = MPI.get_vendor()
    if name == "MPICH":
        if version >= (5, 0, 0):
            return False
    if name == "Open MPI":
        if version >= (5, 1, 0):
            return False
    return True


if skip():
    sys.exit(0)

assert not MPI.Is_initialized()
assert not MPI.Is_finalized()

test_all()

assert not MPI.Is_initialized()
assert not MPI.Is_finalized()

MPI.Init()

assert MPI.Is_initialized()
assert not MPI.Is_finalized()

test_all()

assert MPI.Is_initialized()
assert not MPI.Is_finalized()

MPI.Finalize()

assert MPI.Is_initialized()
assert MPI.Is_finalized()

test_all()

assert MPI.Is_initialized()
assert MPI.Is_finalized()
