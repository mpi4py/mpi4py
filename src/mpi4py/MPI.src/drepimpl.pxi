# -----------------------------------------------------------------------------

cdef object datarep_lock     = Lock()
cdef dict   datarep_registry = {}


@cython.linetrace(False)  # ~> TODO
@cython.final
@cython.internal
cdef class _p_datarep:

    cdef object read_fn
    cdef object write_fn
    cdef object extent_fn

    def __cinit__(self, read_fn, write_fn, extent_fn):
        self.read_fn   = read_fn
        self.write_fn  = write_fn
        self.extent_fn = extent_fn

    cdef int read(
        self,
        void *userbuf,
        MPI_Datatype datatype,
        MPI_Count count,
        void *filebuf,
        MPI_Offset position,
    ) except -1:
        cdef MPI_Count lb=0, extent=0
        CHKERR( MPI_Type_get_extent_c(datatype, &lb, &extent) )
        cdef MPI_Count ulen = (position + count) * extent
        cdef MPI_Count flen = <MPI_Count> PY_SSIZE_T_MAX
        cdef object ubuf = mpibuf(userbuf, ulen)
        cdef object fbuf = mpibuf(filebuf, flen)
        cdef Datatype dtype = <Datatype>New(Datatype)
        dtype.ob_mpi = datatype
        try:
            self.read_fn(ubuf, dtype, count, fbuf, position)
        finally:
            dtype.ob_mpi = MPI_DATATYPE_NULL
        return 0

    cdef int write(
        self,
        void *userbuf,
        MPI_Datatype datatype,
        MPI_Count count,
        void *filebuf,
        MPI_Offset position,
    ) except -1:
        cdef MPI_Count lb=0, extent=0
        CHKERR( MPI_Type_get_extent_c(datatype, &lb, &extent) )
        cdef MPI_Count ulen = (position + count) * extent
        cdef MPI_Count flen = <MPI_Count> PY_SSIZE_T_MAX
        cdef object ubuf = mpibuf(userbuf, ulen)
        cdef object fbuf = mpibuf(filebuf, flen)
        cdef Datatype dtype = <Datatype>New(Datatype)
        dtype.ob_mpi = datatype
        try:
            self.write_fn(ubuf, dtype, count, fbuf, position)
        finally:
            dtype.ob_mpi = MPI_DATATYPE_NULL
        return 0

    cdef int extent(
        self,
        MPI_Datatype datatype,
        MPI_Aint *file_extent,
    ) except -1:
        cdef Datatype dtype = <Datatype>New(Datatype)
        dtype.ob_mpi = datatype
        try:
            file_extent[0] = self.extent_fn(dtype)
        finally:
            dtype.ob_mpi = MPI_DATATYPE_NULL
        return 0


# ---


@cython.linetrace(False)  # ~> TODO
cdef int datarep_read(
    void *userbuf,
    MPI_Datatype datatype,
    MPI_Count count,
    void *filebuf,
    MPI_Offset position,
    void *extra_state,
) noexcept with gil:
    cdef _p_datarep state = <_p_datarep>extra_state
    cdef int ierr = MPI_SUCCESS
    cdef object exc
    try:
        state.read(userbuf, datatype, count, filebuf, position)
    except BaseException as exc:
        ierr = PyMPI_HandleException(exc)
    return ierr


@cython.linetrace(False)  # ~> TODO
cdef int datarep_write(
    void *userbuf,
    MPI_Datatype datatype,
    MPI_Count count,
    void *filebuf,
    MPI_Offset position,
    void *extra_state,
) noexcept with gil:
    cdef _p_datarep state = <_p_datarep>extra_state
    cdef int ierr = MPI_SUCCESS
    cdef object exc
    try:
        state.write(userbuf, datatype, count, filebuf, position)
    except BaseException as exc:
        ierr = PyMPI_HandleException(exc)
    return ierr


@cython.linetrace(False)  # ~> TODO
cdef int datarep_extent(
    MPI_Datatype datatype,
    MPI_Aint *file_extent,
    void *extra_state,
) noexcept with gil:
    cdef _p_datarep state = <_p_datarep>extra_state
    cdef int ierr = MPI_SUCCESS
    cdef object exc
    try:
        state.extent(datatype, file_extent)
    except BaseException as exc:
        ierr = PyMPI_HandleException(exc)
    return ierr


# ---


@cython.linetrace(False)  # ~> TODO
@cython.callspec("MPIAPI")
cdef int datarep_read_fn(
    void *userbuf,
    MPI_Datatype datatype,
    MPI_Count count,
    void *filebuf,
    MPI_Offset position,
    void *extra_state,
) noexcept nogil:
    if extra_state == NULL:    return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_ERR_INTERN
    if not py_module_alive():  return MPI_ERR_INTERN
    return datarep_read(
        userbuf, datatype, count,
        filebuf, position, extra_state,
    )


@cython.linetrace(False)  # ~> TODO
@cython.callspec("MPIAPI")
cdef int datarep_write_fn(
    void *userbuf,
    MPI_Datatype datatype,
    MPI_Count count,
    void *filebuf,
    MPI_Offset position,
    void *extra_state,
) noexcept nogil:
    if extra_state == NULL:    return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_ERR_INTERN
    if not py_module_alive():  return MPI_ERR_INTERN
    return datarep_write(
        userbuf, datatype, count,
        filebuf, position, extra_state,
    )


@cython.linetrace(False)  # ~> TODO
@cython.callspec("MPIAPI")
cdef int datarep_extent_fn(
    MPI_Datatype datatype,
    MPI_Aint *file_extent,
    void *extra_state,
) noexcept nogil:
    if extra_state == NULL:    return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_ERR_INTERN
    if not py_module_alive():  return MPI_ERR_INTERN
    return datarep_extent(
        datatype, file_extent, extra_state,
    )

# -----------------------------------------------------------------------------
