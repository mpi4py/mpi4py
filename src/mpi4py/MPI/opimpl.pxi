# -----------------------------------------------------------------------------

cdef object op_MAX(object x, object y):
    """maximum"""
    if y > x:
        return y
    else:
        return x

cdef object op_MIN(object x, object y):
    """minimum"""
    if y < x:
        return y
    else:
        return x

cdef object op_SUM(object x, object y):
    """sum"""
    return x + y

cdef object op_PROD(object x, object y):
    """product"""
    return x * y

cdef object op_BAND(object x, object y):
    """bit-wise and"""
    return x & y

cdef object op_BOR(object x, object y):
    """bit-wise or"""
    return x | y

cdef object op_BXOR(object x, object y):
    """bit-wise xor"""
    return x ^ y

cdef object op_LAND(object x, object y):
    """logical and"""
    return bool(x) & bool(y)

cdef object op_LOR(object x, object y):
    """logical or"""
    return bool(x) | bool(y)

cdef object op_LXOR(object x, object y):
    """logical xor"""
    return bool(x) ^ bool(y)

cdef object op_MAXLOC(object x, object y):
    """maximum and location"""
    cdef object i, j, u, v
    u, i = x
    v, j = y
    if u > v:
        return u, i
    elif v > u:
        return v, j
    elif j < i:
        return v, j
    else:
        return u, i

cdef object op_MINLOC(object x, object y):
    """minimum and location"""
    cdef object i, j, u, v
    u, i = x
    v, j = y
    if u < v:
        return u, i
    elif v < u:
        return v, j
    elif j < i:
        return v, j
    else:
        return u, i

cdef object op_REPLACE(object x, object y):
    """replace,  (x, y) -> y"""
    <void> x # unused
    return y

cdef object op_NO_OP(object x, object y):
    """no-op,  (x, y) -> x"""
    <void> y # unused
    return x

# -----------------------------------------------------------------------------

cdef object op_user_lock     = Lock()
cdef list   op_user_registry = [None]*(1+32)

cdef inline object op_user_py(int index, object x, object y, object dt):
    return op_user_registry[index](x, y, dt)

cdef inline void op_user_mpi(
    int index,
    void *a, void *b, MPI_Count n, MPI_Datatype t,
) with gil:
    cdef Datatype datatype
    # errors in user-defined reduction operations are unrecoverable
    try:
        datatype = Datatype.__new__(Datatype)
        datatype.ob_mpi = t
        try:
            op_user_py(index, mpibuf(a, n), mpibuf(b, n), datatype)
        finally:
            datatype.ob_mpi = MPI_DATATYPE_NULL
    except:
        # print the full exception traceback and abort
        PySys_WriteStderr(
            b"Fatal Python error: %s\n",
            b"exception in user-defined reduction operation",
        )
        try:
            print_traceback()
        finally:
            <void>MPI_Abort(MPI_COMM_WORLD, 1)

cdef inline void op_user_call(
    int index,
    void *a, void *b, MPI_Count count, MPI_Datatype t,
) noexcept nogil:
    # make it abort if Python has finalized
    if not Py_IsInitialized():
        <void>MPI_Abort(MPI_COMM_WORLD, 1)
    # make it abort if module cleanup has been done
    if not py_module_alive():
        <void>MPI_Abort(MPI_COMM_WORLD, 1)
    # compute the byte-size of memory buffers
    cdef MPI_Count lb=0, extent=0
    <void>MPI_Type_get_extent_c(t, &lb, &extent)
    cdef MPI_Count n = count * extent
    # make the actual GIL-safe Python call
    op_user_mpi(index, a, b, n, t)

ctypedef fused op_count_t:
    int
    MPI_Count

ctypedef fused op_usrfn_t:
    MPI_User_function
    MPI_User_function_c

@cython.callspec("MPIAPI")
cdef void op_user_01(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call( 1, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_02(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call( 2, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_03(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call( 3, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_04(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call( 4, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_05(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call( 5, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_06(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call( 6, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_07(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call( 7, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_08(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call( 8, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_09(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call( 9, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_10(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(10, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_11(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(11, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_12(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(12, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_13(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(13, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_14(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(14, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_15(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(15, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_16(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(16, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_17(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(17, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_18(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(18, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_19(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(19, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_20(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(20, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_21(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(21, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_22(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(22, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_23(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(23, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_24(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(24, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_25(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(25, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_26(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(26, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_27(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(27, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_28(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(28, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_29(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(29, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_30(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(30, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_31(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(31, a, b, n[0], t[0])
@cython.callspec("MPIAPI")
cdef void op_user_32(void *a, void *b, op_count_t *n, MPI_Datatype *t) noexcept nogil:
    op_user_call(32, a, b, n[0], t[0])

cdef void op_user_map(int index, op_usrfn_t **fn) noexcept nogil:
    if   index ==  1: fn[0] = op_user_01
    elif index ==  2: fn[0] = op_user_02
    elif index ==  3: fn[0] = op_user_03
    elif index ==  4: fn[0] = op_user_04
    elif index ==  5: fn[0] = op_user_05
    elif index ==  6: fn[0] = op_user_06
    elif index ==  7: fn[0] = op_user_07
    elif index ==  8: fn[0] = op_user_08
    elif index ==  9: fn[0] = op_user_09
    elif index == 10: fn[0] = op_user_10
    elif index == 11: fn[0] = op_user_11
    elif index == 12: fn[0] = op_user_12
    elif index == 13: fn[0] = op_user_13
    elif index == 14: fn[0] = op_user_14
    elif index == 15: fn[0] = op_user_15
    elif index == 16: fn[0] = op_user_16
    elif index == 17: fn[0] = op_user_17
    elif index == 18: fn[0] = op_user_18
    elif index == 19: fn[0] = op_user_19
    elif index == 20: fn[0] = op_user_20
    elif index == 21: fn[0] = op_user_21
    elif index == 22: fn[0] = op_user_22
    elif index == 23: fn[0] = op_user_23
    elif index == 24: fn[0] = op_user_24
    elif index == 25: fn[0] = op_user_25
    elif index == 26: fn[0] = op_user_26
    elif index == 27: fn[0] = op_user_27
    elif index == 28: fn[0] = op_user_28
    elif index == 29: fn[0] = op_user_29
    elif index == 30: fn[0] = op_user_30
    elif index == 31: fn[0] = op_user_31
    elif index == 32: fn[0] = op_user_32
    else:             fn[0] = NULL

cdef int op_user_new(
    object function,
    MPI_User_function   **fn_i,
    MPI_User_function_c **fn_c,
) except -1:
    # check whether the function is callable
    function.__call__
    # find a free slot in the registry
    # and register the Python function
    cdef int index = 0
    try:
        with op_user_lock:
            index = op_user_registry.index(None, 1)
            op_user_registry[index] = function
    except ValueError:
        raise RuntimeError(
            "cannot create too many user-defined reduction operations",
        )
    # map slot index to the associated C callback,
    # and return the slot index in the registry
    op_user_map(index, fn_i)
    op_user_map(index, fn_c)
    return index

cdef int op_user_del(
    int *indexp,
) except -1:
    # clear index value
    cdef int index = indexp[0]
    indexp[0] = 0
    # free slot in the registry
    with op_user_lock:
        op_user_registry[index] = None
    return 0

# -----------------------------------------------------------------------------

cdef object op_call(MPI_Op op, int index, object x, object y):
    if op == MPI_MAX     : return op_MAX(x, y)
    if op == MPI_MIN     : return op_MIN(x, y)
    if op == MPI_SUM     : return op_SUM(x, y)
    if op == MPI_PROD    : return op_PROD(x, y)
    if op == MPI_LAND    : return op_LAND(x, y)
    if op == MPI_BAND    : return op_BAND(x, y)
    if op == MPI_LOR     : return op_LOR(x, y)
    if op == MPI_BOR     : return op_BOR(x, y)
    if op == MPI_LXOR    : return op_LXOR(x, y)
    if op == MPI_BXOR    : return op_BXOR(x, y)
    if op == MPI_MAXLOC  : return op_MAXLOC(x, y)
    if op == MPI_MINLOC  : return op_MINLOC(x, y)
    if op == MPI_REPLACE : return op_REPLACE(x, y)
    if op == MPI_NO_OP   : return op_NO_OP(x, y)
    if index > 0         : return op_user_py(index, x, y, None)
    raise ValueError("cannot call user-defined operation")

# -----------------------------------------------------------------------------
