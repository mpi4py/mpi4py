# Error Classes
# -------------

# No Errors
SUCCESS          = MPI_SUCCESS
ERR_LASTCODE     = MPI_ERR_LASTCODE
# Object Handles
ERR_TYPE         = MPI_ERR_TYPE
ERR_REQUEST      = MPI_ERR_REQUEST
ERR_OP           = MPI_ERR_OP
ERR_GROUP        = MPI_ERR_GROUP
ERR_INFO         = MPI_ERR_INFO
ERR_ERRHANDLER   = MPI_ERR_ERRHANDLER
ERR_SESSION      = MPI_ERR_SESSION
ERR_COMM         = MPI_ERR_COMM
ERR_WIN          = MPI_ERR_WIN
ERR_FILE         = MPI_ERR_FILE
# Communication Arguments
ERR_BUFFER       = MPI_ERR_BUFFER
ERR_COUNT        = MPI_ERR_COUNT
ERR_TAG          = MPI_ERR_TAG
ERR_RANK         = MPI_ERR_RANK
ERR_ROOT         = MPI_ERR_ROOT
ERR_TRUNCATE     = MPI_ERR_TRUNCATE
# Multiple Completion
ERR_IN_STATUS    = MPI_ERR_IN_STATUS
ERR_PENDING      = MPI_ERR_PENDING
# Topology Arguments
ERR_TOPOLOGY     = MPI_ERR_TOPOLOGY
ERR_DIMS         = MPI_ERR_DIMS
# Other Arguments
ERR_ARG          = MPI_ERR_ARG
# Other Errors
ERR_OTHER        = MPI_ERR_OTHER
ERR_UNKNOWN      = MPI_ERR_UNKNOWN
ERR_INTERN       = MPI_ERR_INTERN
# Attributes
ERR_KEYVAL       = MPI_ERR_KEYVAL
# Memory Allocation
ERR_NO_MEM       = MPI_ERR_NO_MEM
# Info Object
ERR_INFO_KEY     = MPI_ERR_INFO_KEY
ERR_INFO_VALUE   = MPI_ERR_INFO_VALUE
ERR_INFO_NOKEY   = MPI_ERR_INFO_NOKEY
# Dynamic Process Management
ERR_SPAWN        = MPI_ERR_SPAWN
ERR_PORT         = MPI_ERR_PORT
ERR_SERVICE      = MPI_ERR_SERVICE
ERR_NAME         = MPI_ERR_NAME
ERR_PROC_ABORTED = MPI_ERR_PROC_ABORTED
# One-Sided Communications
ERR_BASE         = MPI_ERR_BASE
ERR_SIZE         = MPI_ERR_SIZE
ERR_DISP         = MPI_ERR_DISP
ERR_ASSERT       = MPI_ERR_ASSERT
ERR_LOCKTYPE     = MPI_ERR_LOCKTYPE
ERR_RMA_CONFLICT = MPI_ERR_RMA_CONFLICT
ERR_RMA_SYNC     = MPI_ERR_RMA_SYNC
ERR_RMA_RANGE    = MPI_ERR_RMA_RANGE
ERR_RMA_ATTACH   = MPI_ERR_RMA_ATTACH
ERR_RMA_SHARED   = MPI_ERR_RMA_SHARED
ERR_RMA_FLAVOR   = MPI_ERR_RMA_FLAVOR
# Input/Output
ERR_BAD_FILE     = MPI_ERR_BAD_FILE
ERR_NO_SUCH_FILE = MPI_ERR_NO_SUCH_FILE
ERR_FILE_EXISTS  = MPI_ERR_FILE_EXISTS
ERR_FILE_IN_USE  = MPI_ERR_FILE_IN_USE
ERR_AMODE        = MPI_ERR_AMODE
ERR_ACCESS       = MPI_ERR_ACCESS
ERR_READ_ONLY    = MPI_ERR_READ_ONLY
ERR_NO_SPACE     = MPI_ERR_NO_SPACE
ERR_QUOTA        = MPI_ERR_QUOTA
ERR_NOT_SAME     = MPI_ERR_NOT_SAME
ERR_IO           = MPI_ERR_IO
ERR_UNSUPPORTED_OPERATION  = MPI_ERR_UNSUPPORTED_OPERATION
ERR_UNSUPPORTED_DATAREP    = MPI_ERR_UNSUPPORTED_DATAREP
ERR_CONVERSION             = MPI_ERR_CONVERSION
ERR_DUP_DATAREP            = MPI_ERR_DUP_DATAREP
ERR_VALUE_TOO_LARGE        = MPI_ERR_VALUE_TOO_LARGE
# Process Fault Tolerance
ERR_REVOKED             = MPI_ERR_REVOKED
ERR_PROC_FAILED         = MPI_ERR_PROC_FAILED
ERR_PROC_FAILED_PENDING = MPI_ERR_PROC_FAILED_PENDING


def Get_error_class(int errorcode: int) -> int:
    """
    Convert an *error code* into an *error class*.
    """
    cdef int errorclass = MPI_SUCCESS
    CHKERR( MPI_Error_class(errorcode, &errorclass) )
    return errorclass

def Get_error_string(int errorcode: int) -> str:
    """
    Return the *error string* for a given *error class* or *error code*.
    """
    cdef char string[MPI_MAX_ERROR_STRING+1]
    cdef int resultlen = 0
    CHKERR( MPI_Error_string(errorcode, string, &resultlen) )
    return tompistr(string, resultlen)

def Add_error_class() -> int:
    """
    Add an *error class* to the known error classes.
    """
    cdef int errorclass = MPI_SUCCESS
    CHKERR( MPI_Add_error_class(&errorclass) )
    return errorclass

def Remove_error_class(int errorclass: int) -> None:
    """
    Remove an *error class* from the known error classes.
    """
    CHKERR( MPI_Remove_error_class(errorclass) )

def Add_error_code(int errorclass: int) -> int:
    """
    Add an *error code* to an *error class*.
    """
    cdef int errorcode = MPI_SUCCESS
    CHKERR( MPI_Add_error_code(errorclass, &errorcode) )
    return errorcode

def Remove_error_code(int errorcode: int) -> None:
    """
    Remove an *error code* from the known error codes.
    """
    CHKERR( MPI_Remove_error_code(errorcode) )

def Add_error_string(int errorcode: int, string: str) -> None:
    """
    Associate an *error string* with an *error class* or *error code*.
    """
    cdef char *cstring = NULL
    string = asmpistr(string, &cstring)
    CHKERR( MPI_Add_error_string(errorcode, cstring) )

def Remove_error_string(int errorcode: int) -> None:
    """
    Remove *error string* association from *error class* or *error code*.
    """
    CHKERR( MPI_Remove_error_string(errorcode) )
