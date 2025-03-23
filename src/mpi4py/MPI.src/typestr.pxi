# -----------------------------------------------------------------------------

def _typecode(Datatype datatype: Datatype) -> str | None:
    """
    Map MPI datatype to character code or type string.
    """
    cdef const char *tc = DatatypeCode(datatype.ob_mpi)
    return pystr(tc) if tc != NULL else None


def _typealign(Datatype datatype: Datatype) -> int | None:
    """
    Return MPI datatype alignment.
    """
    cdef size_t align = DatatypeAlign(datatype.ob_mpi)
    return align if align > 0 else None


# -----------------------------------------------------------------------------

cdef inline const char* typechr(const char kind[], size_t size) noexcept nogil:
    cdef char k = kind[0]
    if k == c'b':  # boolean
        if size == 1: return "?"
        if size >= 2: return typechr('i', size)
        return NULL  # ~> unreachable
    if k == c'i':  # signed integral
        if size == sizeof(char)      : return "b"
        if size == sizeof(short)     : return "h"
        if size == sizeof(int)       : return "i"
        if size == sizeof(long)      : return "l"
        if size == sizeof(long long) : return "q"  # ~> uncovered
        return NULL  # ~> unreachable
    if k == c'u':  # unsigned integral
        if size == sizeof(char)      : return "B"
        if size == sizeof(short)     : return "H"
        if size == sizeof(int)       : return "I"
        if size == sizeof(long)      : return "L"
        if size == sizeof(long long) : return "Q"  # ~> uncovered
        return NULL  # ~> unreachable
    if k == c'f':  # real floating
        if size == sizeof(float)//2    : return "e"
        if size == sizeof(float)       : return "f"
        if size == sizeof(double)      : return "d"
        if size == sizeof(long double) : return "g"
        return NULL  # ~> unreachable
    if k == c'c':  # complex floating
        if size == 2*sizeof(float)//2    : return "E"
        if size == 2*sizeof(float)       : return "F"
        if size == 2*sizeof(double)      : return "D"
        if size == 2*sizeof(long double) : return "G"
        return NULL  # ~> unreachable
    return NULL  # ~> unreachable

cdef inline const char* typestr(const char kind[], size_t size) noexcept nogil:
    cdef char k = kind[0]
    if k == c'b':  # boolean
        if size ==  1: return "b1"
        if size >=  2: return typestr('i', size)  # ~> uncovered
        return NULL  # ~> unreachable
    if k == c'i':  # signed integral
        if size ==  1: return "i1"
        if size ==  2: return "i2"
        if size ==  4: return "i4"
        if size ==  8: return "i8"
        if size == 16: return "i16"  # ~> uncovered
        return NULL  # ~> unreachable
    if k == c'u':  # unsigned integral
        if size ==  1: return "u1"
        if size ==  2: return "u2"
        if size ==  4: return "u4"
        if size ==  8: return "u8"
        if size == 16: return "u16"  # ~> uncovered
        return NULL  # ~> unreachable
    if k == c'f':  # real floating
        if size ==  2: return "f2"
        if size ==  4: return "f4"
        if size ==  8: return "f8"
        if size == 12: return "f12"
        if size == 16: return "f16"
        return NULL  # ~> unreachable
    if k == c'c':  # complex floating
        if size ==  4: return "c4"
        if size ==  8: return "c8"
        if size == 16: return "c16"
        if size == 24: return "c24"
        if size == 32: return "c32"
        return NULL  # ~> unreachable
    return NULL  # ~> unreachable

cdef inline const char* typechr_to_typestr(const char tchr[]) noexcept nogil:
    if tchr == NULL: return NULL
    cdef char c = tchr[0]
    # boolean
    if c == c'?': return typestr('b', 1)
    # signed integral
    if c == c'b': return typestr('i', sizeof(char))
    if c == c'h': return typestr('i', sizeof(short))
    if c == c'i': return typestr('i', sizeof(int))
    if c == c'l': return typestr('i', sizeof(long))
    if c == c'q': return typestr('i', sizeof(long long))
    if c == c'p': return typestr('i', sizeof(MPI_Aint))
    # unsigned integral
    if c == c'B': return typestr('u', sizeof(char))
    if c == c'H': return typestr('u', sizeof(short))
    if c == c'I': return typestr('u', sizeof(int))
    if c == c'L': return typestr('u', sizeof(long))
    if c == c'Q': return typestr('u', sizeof(long long))
    if c == c'P': return typestr('u', sizeof(MPI_Aint))
    # floating real
    if c == c'e': return typestr('f', sizeof(float)//2)
    if c == c'f': return typestr('f', sizeof(float))
    if c == c'd': return typestr('f', sizeof(double))
    if c == c'g': return typestr('f', sizeof(long double))
    # floating complex
    if c == c'E': return typestr('c', 2*sizeof(float)//2)
    if c == c'F': return typestr('c', 2*sizeof(float))
    if c == c'D': return typestr('c', 2*sizeof(double))
    if c == c'G': return typestr('c', 2*sizeof(long double))
    # character
    if c == c'S': return "S1"  # NumPy
    if c == c'U': return "U1"  # NumPy
    if c == c'c': return "S1"  # PEP 3118
    if c == c'u': return "u2"  # PEP 3118  # ~> uncovered
    if c == c'w': return "U1"  # PEP 3118  # ~> uncovered
    return NULL  # ~> uncovered

cdef inline const char* mpiaddrchr(size_t size) noexcept nogil:
    if size == sizeof(MPI_Aint)  : return "p"
    if size == sizeof(long long) : return "q"  # ~> uncovered
    if size == sizeof(long)      : return "l"  # ~> uncovered
    if size == sizeof(int)       : return "i"  # ~> uncovered
    return NULL  # ~> uncovered

cdef inline int mpicombiner(MPI_Datatype datatype) noexcept nogil:
    if not mpi_active(): return MPI_COMBINER_NAMED
    cdef int combiner = MPI_COMBINER_NAMED
    cdef MPI_Count ni = 0, na = 0, nc = 0, nd = 0
    <void> MPI_Type_get_envelope_c(datatype, &ni, &na, &nc, &nd, &combiner)
    return combiner

cdef inline size_t mpisizeof(MPI_Datatype datatype) noexcept nogil:
    if not mpi_active(): return 0
    cdef MPI_Count size = MPI_UNDEFINED
    cdef int ierr = MPI_Type_size_c(datatype, &size)
    if ierr != MPI_SUCCESS or size < 0: size = 0
    return <size_t> size

cdef inline MPI_Count mpiextent(MPI_Datatype datatype) noexcept nogil:
    if not mpi_active(): return 0
    cdef MPI_Count lb = 0, extent = MPI_UNDEFINED
    cdef int ierr = MPI_Type_get_extent_c(datatype, &lb, &extent)
    if ierr != MPI_SUCCESS or extent < 0: extent = 0
    return extent

cdef inline const char* mpifortchr(
    const char kind[],
    MPI_Datatype datatype,
) noexcept nogil:
    return typechr(kind, <size_t> mpisizeof(datatype))

cdef inline const char* mpifortstr(
    const char kind[],
    MPI_Datatype datatype,
) noexcept nogil:
    return typestr(kind, <size_t> mpisizeof(datatype))

cdef inline const char* typeDUP(
    const char *(*convert)(MPI_Datatype) noexcept nogil,
    MPI_Datatype datatype,
) noexcept nogil:
    cdef MPI_Datatype basetype = MPI_DATATYPE_NULL
    <void> MPI_Type_get_contents_c(
        datatype, 0, 0, 0, 1, NULL, NULL, NULL, &basetype)
    cdef const char *result = convert(basetype)
    if not predefined(basetype): <void> MPI_Type_free(&basetype)
    return result

cdef extern from * nogil:
    """
    #include <stddef.h>
    #if defined(__cplusplus)
    template<typename T> struct pympi_alignof_struct {char c; T member;};
    #define pympi_alignof(type) offsetof(pympi_alignof_struct<type>, member)
    #else
    #define pympi_alignof(type) offsetof(struct _{char c; type member;}, member)
    #endif
    """
    const size_t alignof_bool       "pympi_alignof(char)"
    const size_t alignof_short      "pympi_alignof(short)"
    const size_t alignof_int        "pympi_alignof(int)"
    const size_t alignof_long       "pympi_alignof(long)"
    const size_t alignof_longlong   "pympi_alignof(long long)"
    const size_t alignof_float      "pympi_alignof(float)"
    const size_t alignof_double     "pympi_alignof(double)"
    const size_t alignof_longdouble "pympi_alignof(long double)"
    const size_t alignof_char       "pympi_alignof(char)"
    const size_t alignof_wchar      "pympi_alignof(wchar_t)"
    const size_t alignof_voidp      "pympi_alignof(void*)"
    const size_t alignof_int128     "16"  # TODO: review
    const size_t alignof_float128   "16"  # TODO: review

cdef inline size_t typealign(const char tchr[]) noexcept nogil:
    if tchr == NULL: return 0
    cdef char c = tchr[0]
    # bool
    if c == c'?': return alignof_bool
    # signed integral
    if c == c'b': return alignof_char
    if c == c'h': return alignof_short
    if c == c'i': return alignof_int
    if c == c'l': return alignof_long
    if c == c'q': return alignof_longlong
    # unsigned integral
    if c == c'B': return alignof_char
    if c == c'H': return alignof_short
    if c == c'I': return alignof_int
    if c == c'L': return alignof_long
    if c == c'Q': return alignof_longlong
    # floating real
    if c == c'e': return alignof_float//2
    if c == c'f': return alignof_float
    if c == c'd': return alignof_double
    if c == c'g': return alignof_longdouble
    # floating complex
    if c == c'E': return alignof_float//2
    if c == c'F': return alignof_float
    if c == c'D': return alignof_double
    if c == c'G': return alignof_longdouble
    # character
    if c == c'c': return alignof_char
    if c == c'S': return alignof_char
    if c == c'U': return alignof_wchar
    # pointer
    if c == c'p': return alignof_voidp
    if c == c'P': return alignof_voidp  # ~> uncovered
    return 0  # ~> unreachable

cdef inline size_t typealignpair(
    const char tc_a[],
    const char tc_b[],
) noexcept nogil:
    cdef size_t align_a = typealign(tc_a)
    cdef size_t align_b = typealign(tc_b)
    return align_a if align_a > align_b else align_b

# -----------------------------------------------------------------------------

cdef inline const char* DatatypeChar(MPI_Datatype datatype) noexcept nogil:
    if datatype == MPI_DATATYPE_NULL: return NULL
    # MPI
    if datatype == MPI_PACKED : return "B"
    if datatype == MPI_BYTE   : return "B"
    if datatype == MPI_AINT   : return mpiaddrchr(sizeof(MPI_Aint))
    if datatype == MPI_OFFSET : return mpiaddrchr(sizeof(MPI_Offset))
    if datatype == MPI_COUNT  : return mpiaddrchr(sizeof(MPI_Count))
    # C - character
    if datatype == MPI_CHAR : return "c"
    if datatype == MPI_WCHAR and sizeof(wchar_t) == 2: return typechr('u', 2)
    if datatype == MPI_WCHAR and sizeof(wchar_t) == 4: return "U"
    # C - (signed) integral
    if datatype == MPI_SIGNED_CHAR : return "b"
    if datatype == MPI_SHORT       : return "h"
    if datatype == MPI_INT         : return "i"
    if datatype == MPI_LONG        : return "l"
    if datatype == MPI_LONG_LONG   : return "q"
    # C - unsigned integral
    if datatype == MPI_UNSIGNED_CHAR      : return "B"
    if datatype == MPI_UNSIGNED_SHORT     : return "H"
    if datatype == MPI_UNSIGNED           : return "I"
    if datatype == MPI_UNSIGNED_LONG      : return "L"
    if datatype == MPI_UNSIGNED_LONG_LONG : return "Q"
    # C - (real) floating
    if datatype == MPI_FLOAT       : return "f"
    if datatype == MPI_DOUBLE      : return "d"
    if datatype == MPI_LONG_DOUBLE : return "g"
    # C99 - boolean
    if datatype == MPI_C_BOOL : return "?"
    # C99 - integral
    if datatype == MPI_INT8_T   : return typechr('i', 1)
    if datatype == MPI_INT16_T  : return typechr('i', 2)
    if datatype == MPI_INT32_T  : return typechr('i', 4)
    if datatype == MPI_INT64_T  : return typechr('i', 8)
    if datatype == MPI_UINT8_T  : return typechr('u', 1)
    if datatype == MPI_UINT16_T : return typechr('u', 2)
    if datatype == MPI_UINT32_T : return typechr('u', 4)
    if datatype == MPI_UINT64_T : return typechr('u', 8)
    # C99 - complex floating
    if datatype == MPI_C_COMPLEX             : return "F"
    if datatype == MPI_C_FLOAT_COMPLEX       : return "F"
    if datatype == MPI_C_DOUBLE_COMPLEX      : return "D"
    if datatype == MPI_C_LONG_DOUBLE_COMPLEX : return "G"
    # C++ - boolean
    if datatype == MPI_CXX_BOOL : return "?"
    # C++ - complex floating
    if datatype == MPI_CXX_FLOAT_COMPLEX       : return "F"
    if datatype == MPI_CXX_DOUBLE_COMPLEX      : return "D"
    if datatype == MPI_CXX_LONG_DOUBLE_COMPLEX : return "G"
    # Fortran 77
    if datatype == MPI_CHARACTER        : return "c"
    if datatype == MPI_LOGICAL          : return mpifortchr('b', datatype)
    if datatype == MPI_INTEGER          : return mpifortchr('i', datatype)
    if datatype == MPI_REAL             : return mpifortchr('f', datatype)
    if datatype == MPI_DOUBLE_PRECISION : return mpifortchr('f', datatype)
    if datatype == MPI_COMPLEX          : return mpifortchr('c', datatype)
    if datatype == MPI_DOUBLE_COMPLEX   : return mpifortchr('c', datatype)
    # Fortran 90
    if datatype == MPI_LOGICAL1  : return typechr('b',  1)
    if datatype == MPI_LOGICAL2  : return typechr('b',  2)
    if datatype == MPI_LOGICAL4  : return typechr('b',  4)
    if datatype == MPI_LOGICAL8  : return typechr('b',  8)
    if datatype == MPI_LOGICAL16 : return typechr('b', 16)
    if datatype == MPI_INTEGER1  : return typechr('i',  1)
    if datatype == MPI_INTEGER2  : return typechr('i',  2)
    if datatype == MPI_INTEGER4  : return typechr('i',  4)
    if datatype == MPI_INTEGER8  : return typechr('i',  8)
    if datatype == MPI_INTEGER16 : return typechr('i', 16)
    if datatype == MPI_REAL2     : return typechr('f',  2)
    if datatype == MPI_REAL4     : return typechr('f',  4)
    if datatype == MPI_REAL8     : return typechr('f',  8)
    if datatype == MPI_REAL16    : return typechr('f', 16)
    if datatype == MPI_COMPLEX4  : return typechr('c',  4)
    if datatype == MPI_COMPLEX8  : return typechr('c',  8)
    if datatype == MPI_COMPLEX16 : return typechr('c', 16)
    if datatype == MPI_COMPLEX32 : return typechr('c', 32)
    cdef int combiner = mpicombiner(datatype)
    if combiner == MPI_COMBINER_F90_INTEGER : return mpifortchr('i', datatype)
    if combiner == MPI_COMBINER_F90_REAL    : return mpifortchr('f', datatype)
    if combiner == MPI_COMBINER_F90_COMPLEX : return mpifortchr('c', datatype)
    # duplicate
    if combiner == MPI_COMBINER_DUP: return typeDUP(DatatypeChar, datatype)
    # fallback
    return NULL

# -----------------------------------------------------------------------------

cdef inline const char* DatatypeStr(MPI_Datatype datatype) noexcept nogil:
    if datatype == MPI_DATATYPE_NULL : return NULL
    # C99
    if datatype == MPI_C_BOOL   : return typestr('b', 1)
    if datatype == MPI_INT8_T   : return typestr('i', 1)
    if datatype == MPI_INT16_T  : return typestr('i', 2)
    if datatype == MPI_INT32_T  : return typestr('i', 4)
    if datatype == MPI_INT64_T  : return typestr('i', 8)
    if datatype == MPI_UINT8_T  : return typestr('u', 1)
    if datatype == MPI_UINT16_T : return typestr('u', 2)
    if datatype == MPI_UINT32_T : return typestr('u', 4)
    if datatype == MPI_UINT64_T : return typestr('u', 8)
    # Fortran 90
    if datatype == MPI_LOGICAL1  : return typestr('b',  1)
    if datatype == MPI_LOGICAL2  : return typestr('b',  2)
    if datatype == MPI_LOGICAL4  : return typestr('b',  4)
    if datatype == MPI_LOGICAL8  : return typestr('b',  8)
    if datatype == MPI_LOGICAL16 : return typestr('b', 16)
    if datatype == MPI_INTEGER1  : return typestr('i',  1)
    if datatype == MPI_INTEGER2  : return typestr('i',  2)
    if datatype == MPI_INTEGER4  : return typestr('i',  4)
    if datatype == MPI_INTEGER8  : return typestr('i',  8)
    if datatype == MPI_INTEGER16 : return typestr('i', 16)
    if datatype == MPI_REAL2     : return typestr('f',  2)
    if datatype == MPI_REAL4     : return typestr('f',  4)
    if datatype == MPI_REAL8     : return typestr('f',  8)
    if datatype == MPI_REAL16    : return typestr('f', 16)
    if datatype == MPI_COMPLEX4  : return typestr('c',  4)
    if datatype == MPI_COMPLEX8  : return typestr('c',  8)
    if datatype == MPI_COMPLEX16 : return typestr('c', 16)
    if datatype == MPI_COMPLEX32 : return typestr('c', 32)
    cdef int combiner = mpicombiner(datatype)
    if combiner == MPI_COMBINER_F90_INTEGER : return mpifortstr('i', datatype)
    if combiner == MPI_COMBINER_F90_REAL    : return mpifortstr('f', datatype)
    if combiner == MPI_COMBINER_F90_COMPLEX : return mpifortstr('c', datatype)
    # duplicate
    if combiner == MPI_COMBINER_DUP: return typeDUP(DatatypeStr, datatype)
    # fallback
    return typechr_to_typestr(DatatypeChar(datatype))

# -----------------------------------------------------------------------------

cdef inline const char* DatatypeCode(MPI_Datatype datatype) noexcept nogil:
    if datatype == MPI_DATATYPE_NULL : return NULL
    # C99
    if datatype == MPI_C_BOOL   : return typestr('b', 1)
    if datatype == MPI_INT8_T   : return typestr('i', 1)
    if datatype == MPI_INT16_T  : return typestr('i', 2)
    if datatype == MPI_INT32_T  : return typestr('i', 4)
    if datatype == MPI_INT64_T  : return typestr('i', 8)
    if datatype == MPI_UINT8_T  : return typestr('u', 1)
    if datatype == MPI_UINT16_T : return typestr('u', 2)
    if datatype == MPI_UINT32_T : return typestr('u', 4)
    if datatype == MPI_UINT64_T : return typestr('u', 8)
    # Fortran 90
    if datatype == MPI_LOGICAL1  : return typestr('b',  1)
    if datatype == MPI_LOGICAL2  : return typestr('b',  2)
    if datatype == MPI_LOGICAL4  : return typestr('b',  4)
    if datatype == MPI_LOGICAL8  : return typestr('b',  8)
    if datatype == MPI_LOGICAL16 : return typestr('b', 16)
    if datatype == MPI_INTEGER1  : return typestr('i',  1)
    if datatype == MPI_INTEGER2  : return typestr('i',  2)
    if datatype == MPI_INTEGER4  : return typestr('i',  4)
    if datatype == MPI_INTEGER8  : return typestr('i',  8)
    if datatype == MPI_INTEGER16 : return typestr('i', 16)
    if datatype == MPI_REAL2     : return typestr('f',  2)
    if datatype == MPI_REAL4     : return typestr('f',  4)
    if datatype == MPI_REAL8     : return typestr('f',  8)
    if datatype == MPI_REAL16    : return typestr('f', 16)
    if datatype == MPI_COMPLEX4  : return typestr('c',  4)
    if datatype == MPI_COMPLEX8  : return typestr('c',  8)
    if datatype == MPI_COMPLEX16 : return typestr('c', 16)
    if datatype == MPI_COMPLEX32 : return typestr('c', 32)
    cdef int combiner = mpicombiner(datatype)
    if combiner == MPI_COMBINER_F90_INTEGER : return mpifortstr('i', datatype)
    if combiner == MPI_COMBINER_F90_REAL    : return mpifortstr('f', datatype)
    if combiner == MPI_COMBINER_F90_COMPLEX : return mpifortstr('c', datatype)
    # duplicate
    if combiner == MPI_COMBINER_DUP: return typeDUP(DatatypeCode, datatype)
    # fallback
    return DatatypeChar(datatype)

# -----------------------------------------------------------------------------

cdef inline size_t DatatypeAlign(MPI_Datatype datatype) noexcept nogil:
    if datatype == MPI_DATATYPE_NULL   : return 0
    if datatype == MPI_LOGICAL16       : return alignof_int128
    if datatype == MPI_INTEGER16       : return alignof_int128
    if datatype == MPI_REAL16          : return alignof_float128
    if datatype == MPI_COMPLEX32       : return alignof_float128
    cdef size_t align = typealign(DatatypeChar(datatype))
    if align > 0: return align
    if datatype == MPI_SHORT_INT       : return typealignpair("h", "i")
    if datatype == MPI_2INT            : return typealignpair("i", "i")
    if datatype == MPI_LONG_INT        : return typealignpair("l", "i")
    if datatype == MPI_FLOAT_INT       : return typealignpair("f", "i")
    if datatype == MPI_DOUBLE_INT      : return typealignpair("d", "i")
    if datatype == MPI_LONG_DOUBLE_INT : return typealignpair("g", "i")
    return 0

# -----------------------------------------------------------------------------
