# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    int PyIndex_Check(object)
    int PySequence_Check(object)
    object PyNumber_Index(object)
    Py_ssize_t PySequence_Size(object) except -1

cdef inline int is_integral(object ob) noexcept:
    if not PyIndex_Check(ob):    return 0
    if not PySequence_Check(ob): return 1
    try: PySequence_Size(ob)
    except: pass
    else: return 0
    try: PyNumber_Index(ob)
    except: return 0
    else: return 1

# -----------------------------------------------------------------------------

cdef extern from * nogil:
    const int INT_MAX

ctypedef fused count_t:
    int
    MPI_Count

ctypedef fused integral_t:
    int
    MPI_Aint
    MPI_Count

cdef inline int chklength(Py_ssize_t size) except -1:
    cdef int overflow = (size > (<Py_ssize_t>INT_MAX))
    if overflow: raise OverflowError("length {size} larger than {INT_MAX}")
    return 0

cdef inline object newarray(Py_ssize_t n, integral_t **p):
    return allocate(n, sizeof(integral_t), p)

cdef inline object getarray(object ob, count_t *n, integral_t **p):
    cdef Py_ssize_t size = len(ob)
    if count_t is int: chklength(size)
    cdef integral_t *base = NULL
    cdef object mem = newarray(size, &base)
    for i in range(size):
        base[i] = PyNumber_Index(ob[i])
    n[0] = <count_t> size
    p[0] = base
    return mem

cdef inline object chkarray(object ob, count_t n, integral_t **p):
    cdef count_t size = 0
    cdef object mem = getarray(ob, &size, p)
    if n != size:
        raise ValueError(f"expecting {n} items, got {size}")
    return mem

# -----------------------------------------------------------------------------

cdef inline object asarray_Datatype(object sequence,
                                    MPI_Count size, MPI_Datatype **p):
     cdef MPI_Datatype *array = NULL
     if size != len(sequence):
         raise ValueError(f"expecting {size} items, got {len(sequence)}")
     cdef object ob = allocate(size, sizeof(MPI_Datatype), &array)
     for i in range(size):
         array[i] = (<Datatype?>sequence[i]).ob_mpi
     p[0] = array
     return ob

cdef inline object asarray_Info(object sequence,
                                MPI_Count size, MPI_Info **p):
     cdef MPI_Info *array = NULL
     cdef MPI_Info info = MPI_INFO_NULL
     cdef object ob
     if sequence is None or isinstance(sequence, Info):
         if sequence is not None:
             info = (<Info?>sequence).ob_mpi
         ob = allocate(size, sizeof(MPI_Info), &array)
         for i in range(size):
             array[i] = info
     else:
         if size != len(sequence):
             raise ValueError(f"expecting {size} items, got {len(sequence)}")
         ob = allocate(size, sizeof(MPI_Datatype), &array)
         for i in range(size):
             array[i] = (<Info?>sequence[i]).ob_mpi
     p[0] = array
     return ob

# -----------------------------------------------------------------------------

cdef inline int is_string(object obj):
     return isinstance(obj, str) or isinstance(obj, bytes)

cdef inline object asstring(object ob, char *s[]):
     cdef Py_ssize_t n = 0
     cdef char *p = NULL, *q = NULL
     ob = asmpistr(ob, &p)
     PyBytes_AsStringAndSize(ob, &p, &n)
     cdef object mem = allocate(n+1, sizeof(char), &q)
     <void>memcpy(q, p, <size_t>n)
     q[n] = 0; s[0] = q;
     return mem

cdef inline object asarray_str(object sequence, char ***p):
     cdef char** array = NULL
     cdef Py_ssize_t size = len(sequence)
     cdef object ob = allocate(size+1, sizeof(char*), &array)
     for i in range(size):
         sequence[i] = asstring(sequence[i], &array[i])
     array[size] = NULL
     p[0] = array
     return (sequence, ob)

cdef inline object asarray_argv(object sequence, char ***p):
     if sequence is None:
         p[0] = MPI_ARGV_NULL
         return None
     if is_string(sequence):
         sequence = [sequence]
     else:
         sequence = list(sequence)
     return asarray_str(sequence, p)

cdef inline object asarray_cmds(object sequence, int *count, char ***p):
     if is_string(sequence):
         raise ValueError("expecting a sequence of strings")
     sequence = list(sequence)
     count[0] = <int>len(sequence)
     return asarray_str(sequence, p)

cdef inline object asarray_argvs(object sequence, int size, char ****p):
     if sequence is None:
         p[0] = MPI_ARGVS_NULL
         return None
     if is_string(sequence):
         sequence = [sequence] * size
     else:
         sequence = list(sequence)
         if size != len(sequence):
             raise ValueError(f"expecting {size} items, got {len(sequence)}")
     cdef char*** array = NULL
     cdef object ob = allocate(size+1, sizeof(char**), &array)
     cdef object argv
     for i in range(size):
         argv = sequence[i]
         if argv is None: argv = []
         sequence[i] = asarray_argv(argv, &array[i])
     array[size] = NULL
     p[0] = array
     return (sequence, ob)

cdef inline object asarray_nprocs(object sequence, int size, int **p):
     cdef object ob
     cdef int *array = NULL
     cdef int value = 1
     if sequence is None or is_integral(sequence):
         if sequence is not None:
             value = sequence
         ob = newarray(size, &array)
         for i in range(size):
             array[i] = value
     else:
         ob = chkarray(sequence, size, &array)
     p[0] = array
     return ob

# -----------------------------------------------------------------------------
