# -----------------------------------------------------------------------------

cdef inline int AddTypeMap(key, Datatype dtype) except -1:
    global DTypeMap
    if dtype.ob_mpi != MPI_DATATYPE_NULL:
        DTypeMap[key] = dtype
    return 0

AddTypeMap( "c"  , __CHAR__ ) # PEP-3118 & NumPy
AddTypeMap( "S"  , __CHAR__ ) # NumPy

AddTypeMap( "?"  , __C_BOOL__ )

AddTypeMap( "b" , __SIGNED_CHAR__ )
AddTypeMap( "h" , __SHORT__       )
AddTypeMap( "i" , __INT__         )
AddTypeMap( "l" , __LONG__        )
AddTypeMap( "q" , __LONG_LONG__   )
AddTypeMap( "p" , __LONG__        ) # LP64
AddTypeMap( "p" , __AINT__        )

AddTypeMap( "B" , __UNSIGNED_CHAR__     )
AddTypeMap( "H" , __UNSIGNED_SHORT__    )
AddTypeMap( "I" , __UNSIGNED__          )
AddTypeMap( "L" , __UNSIGNED_LONG__     )
AddTypeMap( "Q" , __UNSIGNED_LONG_LONG__)
AddTypeMap( "P" , __UNSIGNED_LONG__     ) # LP64

AddTypeMap( "f" , __FLOAT__       )
AddTypeMap( "d" , __DOUBLE__      )
AddTypeMap( "g" , __LONG_DOUBLE__ ) # PEP-3118 & NumPy

## AddTypeMap( "Zf" , __COMPLEX__        ) # PEP-3118
## AddTypeMap( "F"  , __COMPLEX__        ) # NumPy
## AddTypeMap( "Zd" , __DOUBLE_COMPLEX__ ) # PEP-3118
## AddTypeMap( "D"  , __DOUBLE_COMPLEX__ ) # NumPy

AddTypeMap( "Zf" , __C_FLOAT_COMPLEX__       ) # PEP-3118
AddTypeMap( "F"  , __C_FLOAT_COMPLEX__       ) # NumPy
AddTypeMap( "Zd" , __C_DOUBLE_COMPLEX__      ) # PEP-3118
AddTypeMap( "D"  , __C_DOUBLE_COMPLEX__      ) # NumPy
AddTypeMap( "Zg" , __C_LONG_DOUBLE_COMPLEX__ ) # PEP-3118
AddTypeMap( "G"  , __C_LONG_DOUBLE_COMPLEX__ ) # NumPy

## AddTypeMap( "i1" , __INT8_T__   )
## AddTypeMap( "i2" , __INT16_T__  )
## AddTypeMap( "i4" , __INT32_T__  )
## AddTypeMap( "i8" , __INT64_T__  )
## AddTypeMap( "u1" , __UINT8_T__  )
## AddTypeMap( "u2" , __UINT16_T__ )
## AddTypeMap( "u4" , __UINT32_T__ )
## AddTypeMap( "u8" , __UINT64_T__ )
## if 4 == sizeof(float):
##     AddTypeMap( "f4"  , __FLOAT__            )
##     AddTypeMap( "c8"  , __COMPLEX__          ) # XXX
##     AddTypeMap( "c8"  , __C_FLOAT_COMPLEX__  )
## if 8 == sizeof(double):
##     AddTypeMap( "f8"  , __DOUBLE__           )
##     AddTypeMap( "c16" , __DOUBLE_COMPLEX__   ) # XXX
##     AddTypeMap( "c16" , __C_DOUBLE_COMPLEX__ )
## if 12 == sizeof(long double):  # XXX Linux32
##     AddTypeMap( "f12" , __LONG_DOUBLE__           )
##     AddTypeMap( "c24" , __C_LONG_DOUBLE_COMPLEX__ )
## if 16 == sizeof(long double):  # XXX Linux64
##     AddTypeMap( "f16" , __LONG_DOUBLE__           )
##     AddTypeMap( "c32" , __C_LONG_DOUBLE_COMPLEX__ )

# -----------------------------------------------------------------------------

##cdef dict FDTypeMap = { }
##
##cdef inline int AddFTypeMap(key, Datatype dtype) except -1:
##    if dtype.ob_mpi != MPI_DATATYPE_NULL:
##        FDTypeMap[key] = dtype
##    return 0

## AddFTypeMap( "i"   , __INTEGER__          )
## AddFTypeMap( "f"   , __REAL__             )
## AddFTypeMap( "d"   , __DOUBLE_PRECISION__ )
## AddFTypeMap( "F"   , __COMPLEX__          )
## AddFTypeMap( "D"   , __DOUBLE_COMPLEX__   )
##
## AddFTypeMap( "i1"  , __INTEGER1__  )
## AddFTypeMap( "i2"  , __INTEGER2__  )
## AddFTypeMap( "i4"  , __INTEGER4__  )
## AddFTypeMap( "i8"  , __INTEGER8__  )
## AddFTypeMap( "i16" , __INTEGER16__ )
##
## AddFTypeMap( "f2"  , __REAL2__     )
## AddFTypeMap( "f4"  , __REAL4__     )
## AddFTypeMap( "f8"  , __REAL8__     )
## AddFTypeMap( "f16" , __REAL16__    )
##
## AddFTypeMap( "c4"  , __COMPLEX4__  )
## AddFTypeMap( "c8"  , __COMPLEX8__  )
## AddFTypeMap( "c16" , __COMPLEX16__ )
## AddFTypeMap( "c32" , __COMPLEX32__ )

# -----------------------------------------------------------------------------

## cdef inline const_char* DType2Str(MPI_Datatype datatype) nogil:
##
##     if datatype == MPI_DATATYPE_NULL: return NULL
##
##     elif datatype == MPI_LB : return ""
##     elif datatype == MPI_UB : return ""
##
##     elif datatype == MPI_CHAR      : return ""#"S"# XXX
##     elif datatype == MPI_WCHAR     : return ""#"U"# XXX
##     elif datatype == MPI_CHARACTER : return ""#"S"# XXX
##
##     elif datatype == MPI_PACKED : return "B"
##     elif datatype == MPI_BYTE   : return "B"
##     elif datatype == MPI_AINT   : return "p"
##     elif datatype == MPI_OFFSET : return "q" # XXX
##
##     elif datatype == MPI_SIGNED_CHAR : return "b"
##     elif datatype == MPI_SHORT       : return "h"
##     elif datatype == MPI_INT         : return "i"
##     elif datatype == MPI_LONG        : return "l"
##     elif datatype == MPI_LONG_LONG   : return "q"
##
##     elif datatype == MPI_UNSIGNED_CHAR      : return "B"
##     elif datatype == MPI_UNSIGNED_SHORT     : return "H"
##     elif datatype == MPI_UNSIGNED           : return "I"
##     elif datatype == MPI_UNSIGNED_LONG      : return "L"
##     elif datatype == MPI_UNSIGNED_LONG_LONG : return "Q"
##
##     elif datatype == MPI_C_BOOL   : return "?"
##     elif datatype == MPI_INT8_T   : return "i1"
##     elif datatype == MPI_INT16_T  : return "i2"
##     elif datatype == MPI_INT32_T  : return "i4"
##     elif datatype == MPI_INT64_T  : return "i8"
##     elif datatype == MPI_UINT8_T  : return "u1"
##     elif datatype == MPI_UINT16_T : return "u2"
##     elif datatype == MPI_UINT32_T : return "u4"
##     elif datatype == MPI_UINT64_T : return "u8"
##
##     elif datatype == MPI_FLOAT       : return "f"
##     elif datatype == MPI_DOUBLE      : return "d"
##     elif datatype == MPI_LONG_DOUBLE : return "g"
##
##     elif datatype == MPI_C_COMPLEX             : return "F"
##     elif datatype == MPI_C_FLOAT_COMPLEX       : return "F"
##     elif datatype == MPI_C_DOUBLE_COMPLEX      : return "D"
##     elif datatype == MPI_C_LONG_DOUBLE_COMPLEX : return "G"
##
##     elif datatype == MPI_LOGICAL  : return ""#"?" # XXX
##     elif datatype == MPI_LOGICAL1 : return ""#"?1"# XXX
##     elif datatype == MPI_LOGICAL2 : return ""#"?2"# XXX
##     elif datatype == MPI_LOGICAL4 : return ""#"?4"# XXX
##     elif datatype == MPI_LOGICAL8 : return ""#"?8"# XXX
##
##     elif datatype == MPI_INTEGER   : return "i"
##     elif datatype == MPI_INTEGER1  : return "i1"
##     elif datatype == MPI_INTEGER2  : return "i2"
##     elif datatype == MPI_INTEGER4  : return "i4"
##     elif datatype == MPI_INTEGER8  : return "i8"
##     elif datatype == MPI_INTEGER16 : return "i16"
##
##     elif datatype == MPI_REAL             : return "f"
##     elif datatype == MPI_DOUBLE_PRECISION : return "d"
##     elif datatype == MPI_REAL2  : return "f2"
##     elif datatype == MPI_REAL4  : return "f4"
##     elif datatype == MPI_REAL8  : return "f8"
##     elif datatype == MPI_REAL16 : return "f16"
##
##     elif datatype == MPI_COMPLEX        : return "F"
##     elif datatype == MPI_DOUBLE_COMPLEX : return "D"
##     elif datatype == MPI_COMPLEX4  : return "c4"
##     elif datatype == MPI_COMPLEX8  : return "c8"
##     elif datatype == MPI_COMPLEX16 : return "c16"
##     elif datatype == MPI_COMPLEX32 : return "c32"
##
##     else : return ""

# -----------------------------------------------------------------------------
