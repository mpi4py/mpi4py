# -----------------------------------------------------------------------------

ctypedef fused mpi_scwf_t:
    MPI_Session
    MPI_Comm
    MPI_Win
    MPI_File

ctypedef fused mpi_ehfn_t:
    MPI_Session_errhandler_function
    MPI_Comm_errhandler_function
    MPI_Win_errhandler_function
    MPI_File_errhandler_function

cdef object errhdl_lock = Lock()
cdef list   errhdl_registry = [
    [None]*(1+32),  # Session
    [None]*(1+32),  # Comm
    [None]*(1+32),  # Win
    [None]*(1+32),  # File
]

cdef inline void errhdl_call_mpi(
    int index,
    mpi_scwf_t handle, int errcode,
) noexcept with gil:
    cdef object pyhandle = None
    cdef object registry = None
    # errors in user-defined error handler functions are unrecoverable
    try:
        if mpi_scwf_t is MPI_Session:
            pyhandle = fromhandle(handle)
            registry = errhdl_registry[0]
        if mpi_scwf_t is MPI_Comm:
            pyhandle = fromhandle(handle)
            registry = errhdl_registry[1]
        if mpi_scwf_t is MPI_Win:
            pyhandle = fromhandle(handle)
            registry = errhdl_registry[2]
        if mpi_scwf_t is MPI_File:
            pyhandle = fromhandle(handle)
            registry = errhdl_registry[3]
        try:
            registry[index](pyhandle, errcode)
        finally:
            if False: pass
            elif mpi_scwf_t is MPI_Session:
                (<Session>pyhandle).ob_mpi = MPI_SESSION_NULL
            elif mpi_scwf_t is MPI_Comm:
                (<Comm>pyhandle).ob_mpi = MPI_COMM_NULL
            elif mpi_scwf_t is MPI_Win:
                (<Win>pyhandle).ob_mpi = MPI_WIN_NULL
            elif mpi_scwf_t is MPI_File:
                (<File>pyhandle).ob_mpi = MPI_FILE_NULL
    except BaseException as exc:                                  # ~> uncovered
        PyErr_DisplayException(exc)                               # ~> uncovered
        PySys_WriteStderr(                                        # ~> uncovered
            b"Fatal Python error: %s\n",                          # ~> uncovered
            b"exception in user-defined error handler function",  # ~> uncovered
        )                                                         # ~> uncovered
        <void>MPI_Abort(MPI_COMM_WORLD, 1)                        # ~> uncovered


cdef inline void errhdl_call(
    int index,
    mpi_scwf_t handle, int errcode,
) noexcept nogil:
    # make it abort if Python has finalized
    if not Py_IsInitialized(): <void>MPI_Abort(MPI_COMM_WORLD, 1)
    # make it abort if module cleanup has been done
    if not py_module_alive():  <void>MPI_Abort(MPI_COMM_WORLD, 1)
    # make the actual GIL-safe Python call
    errhdl_call_mpi(index, handle, errcode)


@cython.callspec("MPIAPI")
cdef void errhdl_01(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call(  1, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_02(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call(  2, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_03(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call(  3, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_04(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call(  4, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_05(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call(  5, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_06(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call(  6, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_07(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call(  7, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_08(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call(  8, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_09(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call(  9, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_10(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 10, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_11(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 11, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_12(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 12, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_13(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 13, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_14(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 14, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_15(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 15, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_16(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 16, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_17(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 17, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_18(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 18, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_19(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 19, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_20(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 20, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_21(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 21, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_22(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 22, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_23(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 23, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_24(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 24, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_25(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 25, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_26(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 26, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_27(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 27, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_28(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 28, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_29(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 29, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_30(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 30, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_31(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 31, handle[0], errcode[0])


@cython.callspec("MPIAPI")
cdef void errhdl_32(mpi_scwf_t *handle, int *errcode, ...) noexcept nogil:
    errhdl_call( 32, handle[0], errcode[0])


cdef inline void errhdl_map(int index, mpi_ehfn_t **fn) noexcept nogil:
    if   index ==  1: fn[0] = errhdl_01
    elif index ==  2: fn[0] = errhdl_02
    elif index ==  3: fn[0] = errhdl_03
    elif index ==  4: fn[0] = errhdl_04
    elif index ==  5: fn[0] = errhdl_05
    elif index ==  6: fn[0] = errhdl_06
    elif index ==  7: fn[0] = errhdl_07
    elif index ==  8: fn[0] = errhdl_08
    elif index ==  9: fn[0] = errhdl_09
    elif index == 10: fn[0] = errhdl_10
    elif index == 11: fn[0] = errhdl_11
    elif index == 12: fn[0] = errhdl_12
    elif index == 13: fn[0] = errhdl_13
    elif index == 14: fn[0] = errhdl_14
    elif index == 15: fn[0] = errhdl_15
    elif index == 16: fn[0] = errhdl_16
    elif index == 17: fn[0] = errhdl_17
    elif index == 18: fn[0] = errhdl_18
    elif index == 19: fn[0] = errhdl_19
    elif index == 20: fn[0] = errhdl_20
    elif index == 21: fn[0] = errhdl_21
    elif index == 22: fn[0] = errhdl_22
    elif index == 23: fn[0] = errhdl_23
    elif index == 24: fn[0] = errhdl_24
    elif index == 25: fn[0] = errhdl_25
    elif index == 26: fn[0] = errhdl_26
    elif index == 27: fn[0] = errhdl_27
    elif index == 28: fn[0] = errhdl_28
    elif index == 29: fn[0] = errhdl_29
    elif index == 30: fn[0] = errhdl_30
    elif index == 31: fn[0] = errhdl_31
    elif index == 32: fn[0] = errhdl_32


cdef inline int errhdl_new(
    object function,
    mpi_ehfn_t **fn,
) except -1:
    # check whether the function is callable
    function.__call__
    # find a free slot in the registry
    # and register the Python function
    cdef list registry = None
    if mpi_ehfn_t is MPI_Session_errhandler_function:
        registry = errhdl_registry[0]
    if mpi_ehfn_t is MPI_Comm_errhandler_function:
        registry = errhdl_registry[1]
    if mpi_ehfn_t is MPI_Win_errhandler_function:
        registry = errhdl_registry[2]
    if mpi_ehfn_t is MPI_File_errhandler_function:
        registry = errhdl_registry[3]
    cdef int index = 0
    try:
        with errhdl_lock:
            index = registry.index(None, 1)
            registry[index] = function
    except ValueError:
        raise RuntimeError(
            "cannot create too many user-defined error handlers",
        )
    # map slot index to the associated C callback,
    # and return the slot index in the registry
    errhdl_map(index, fn)
    return index


@cython.linetrace(False)  # ~> TODO
cdef inline int errhdl_del(
    int *indexp,
    mpi_ehfn_t *fn,
) except -1:
    <void> fn  # unused
    # clear index value
    cdef int index = indexp[0]
    indexp[0] = 0
    # free slot in the registry
    cdef object registry = None
    if mpi_ehfn_t is MPI_Session_errhandler_function:
        registry = errhdl_registry[0]
    if mpi_ehfn_t is MPI_Comm_errhandler_function:
        registry = errhdl_registry[1]
    if mpi_ehfn_t is MPI_Win_errhandler_function:
        registry = errhdl_registry[2]
    if mpi_ehfn_t is MPI_File_errhandler_function:
        registry = errhdl_registry[3]
    with errhdl_lock:
        registry[index] = None
    return 0

# -----------------------------------------------------------------------------

cdef inline MPI_Errhandler options_get_errhandler() noexcept nogil:
    if options.errors == 0: return MPI_ERRHANDLER_NULL
    if options.errors == 1: return MPI_ERRORS_RETURN
    if options.errors == 2: return MPI_ERRORS_ABORT
    if options.errors == 3: return MPI_ERRORS_ARE_FATAL
    return MPI_ERRHANDLER_NULL  # ~> unreachable


cdef inline int options_set_errhandler(mpi_scwf_t handle) except -1 nogil:
    if handle == mpinull(handle): return 0
    cdef MPI_Errhandler errhandler = options_get_errhandler()
    if errhandler == MPI_ERRHANDLER_NULL: return 0
    if mpi_scwf_t is MPI_Session:
        CHKERR( MPI_Session_set_errhandler(handle, errhandler) )
    if mpi_scwf_t is MPI_Comm:
        CHKERR( MPI_Comm_set_errhandler(handle, errhandler) )
    if mpi_scwf_t is MPI_Win:
        CHKERR( MPI_Win_set_errhandler(handle, errhandler) )
    if mpi_scwf_t is MPI_File:
        CHKERR( MPI_File_set_errhandler(handle, errhandler) )
    return 0

# -----------------------------------------------------------------------------
