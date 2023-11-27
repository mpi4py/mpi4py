# -----------------------------------------------------------------------------

@cython.final
cdef class BufferAutomaticType(int):
    """
    Type of `BUFFER_AUTOMATIC`.
    """

    def __cinit__(self):
        cdef MPI_Aint a = self, b = <MPI_Aint>MPI_BUFFER_AUTOMATIC
        if a != b:
            raise ValueError("cannot create instance")

    def __getbuffer__(self, Py_buffer *view, int flags):
        cdef void *bufauto = MPI_BUFFER_AUTOMATIC
        PyBuffer_FillInfo(view, <object>NULL, bufauto, 0, 0, flags)

    def __repr__(self) -> str:
        <void> self # unused
        return 'BUFFER_AUTOMATIC'

    def __reduce__(self) -> str:
        <void> self # unused
        return 'BUFFER_AUTOMATIC'


cdef object __BUFFER_AUTOMATIC__ = \
    BufferAutomaticType(<MPI_Aint>MPI_BUFFER_AUTOMATIC)

cdef inline bint is_BUFFER_AUTOMATIC(object obj):
    return is_constant(obj, __BUFFER_AUTOMATIC__)

# -----------------------------------------------------------------------------

ctypedef fused PyMPI_attach_buffer_type:
    Py_uintptr_t
    Comm
    Session

cdef dict _mpi_buffer_comm = {}
cdef dict _mpi_buffer_session = {}


cdef inline object attach_buffer(
    object buf,
    void **p,
    MPI_Count *n,
):
    cdef void *bptr = MPI_BUFFER_AUTOMATIC
    cdef MPI_Aint blen = 0
    if buf is None or is_BUFFER_AUTOMATIC(buf):
        buf = __BUFFER_AUTOMATIC__
    else:
        buf = asbuffer_w(buf, &bptr, &blen)
    p[0] = bptr
    n[0] = blen
    return buf

cdef inline int detach_buffer_set(
    PyMPI_attach_buffer_type obj,
    object buf,
) except -1:
    cdef Py_uintptr_t handle
    if PyMPI_attach_buffer_type is Py_uintptr_t:
        handle = <Py_uintptr_t>obj; <void>handle;  # unused
        _mpi_buffer_comm[None] = buf
    if PyMPI_attach_buffer_type is Comm:
        handle = <Py_uintptr_t>obj.ob_mpi  #~> MPI-4.1
        _mpi_buffer_comm[handle] = buf     #~> MPI-4.1
    if PyMPI_attach_buffer_type is Session:
        handle = <Py_uintptr_t>obj.ob_mpi  #~> MPI-4.1
        _mpi_buffer_session[handle] = buf  #~> MPI-4.1
    return 0

cdef inline object detach_buffer_get(
    PyMPI_attach_buffer_type obj,
    void *p,
    MPI_Count n,
):
    cdef Py_uintptr_t handle
    cdef buffer buf = <buffer>None
    if PyMPI_attach_buffer_type is Py_uintptr_t:
        handle = <Py_uintptr_t>obj; <void>handle;  # unused
        buf = <buffer>_mpi_buffer_comm.pop(None, None)
    if PyMPI_attach_buffer_type is Comm:
        handle = <Py_uintptr_t>obj.ob_mpi                 #~> MPI-4.1
        buf = <buffer>_mpi_buffer_comm.pop(handle, None)  #~> MPI-4.1
    if PyMPI_attach_buffer_type is Session:
        handle = <Py_uintptr_t>obj.ob_mpi                    #~> MPI-4.1
        buf = <buffer>_mpi_buffer_session.pop(handle, None)  #~> MPI-4.1
    if p == MPI_BUFFER_AUTOMATIC:
        return __BUFFER_AUTOMATIC__  #~> MPI-4.1
    if buf is not None and buf.view.buf == p and buf.view.obj != NULL:
        return <object> buf.view.obj
    return mpibuf(p, n)

# -----------------------------------------------------------------------------
