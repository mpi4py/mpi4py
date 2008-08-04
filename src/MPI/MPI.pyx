"""
Message Passing Interface
"""

include "mpi.pxi"

include "atimport.pxi"

_init1() # management of MPI initialization
_init2() # installation of MPI_ERRORS_RETURN error handler
_init3() # Interception of call to MPI_Finalize()

BOTTOM = <MPI_Aint>MPI_BOTTOM
#"""Special address for buffers"""

IN_PLACE = <MPI_Aint>MPI_IN_PLACE
#"""*In-place* option for collective communications"""

include "allocate.pxi"
include "asmpistr.pxi"
include "asbuffer.pxi"
include "asmemory.pxi"
include "asarray.pxi"
include "helpers.pxi"
include "message.pxi"

include "Datatype.pyx"      # DONE
include "Status.pyx"        # DONE
include "Request.pyx"       # DONE (except Prequest)
include "Op.pyx"            # DONE (except user-defined operations)
include "Info.pyx"          # DONE
include "Group.pyx"         # DONE
include "Comm.pyx"          # DONE
include "Win.pyx"           # DONE
include "File.pyx"          # DONE
include "Errhandler.pyx"    # DONE
include "Exception.pyx"     # DONE

# Assorted constants
# ------------------

UNDEFINED = MPI_UNDEFINED
#"""Undefined integer value"""

ANY_SOURCE = MPI_ANY_SOURCE
#"""Wildcard source value for receives"""

ANY_TAG = MPI_ANY_TAG
#"""Wildcard tag value for receives"""

PROC_NULL = MPI_PROC_NULL
#"""Special process rank for send/receive"""

ROOT = MPI_ROOT
#"""Root process for collective inter-communications"""


# Memory Allocation
# -----------------

def Alloc_mem(Aint size, info=None):
    """
    Allocate memory for message passing and RMA
    """
    cdef void *base = NULL
    cdef MPI_Info cinfo = _arg_Info(info)
    CHKERR( MPI_Alloc_mem(size, cinfo, &base) )
    return tomemory(base, size)

def Free_mem(memory):
    """
    Free memory allocated with `Alloc_mem()`
    """
    cdef void *base = NULL
    asmemory(memory, &base, NULL)
    CHKERR( MPI_Free_mem(base) )


# Initialization and Exit
# -----------------------

def Init():
    """
    Initialize the MPI execution environment
    """
    CHKERR( MPI_Init(NULL, NULL) )

def Finalize():
    """
    Terminate the MPI execution environment
    """
    CHKERR( MPI_Finalize() )

# Levels of MPI threading support
# -------------------------------

THREAD_SINGLE     = MPI_THREAD_SINGLE
# """Only one thread will execute"""

THREAD_FUNNELED   = MPI_THREAD_FUNNELED
# """MPI calls are *funneled* to the main thread"""

THREAD_SERIALIZED = MPI_THREAD_SERIALIZED
# """MPI calls are *serialized*"""

THREAD_MULTIPLE   = MPI_THREAD_MULTIPLE
# """Multiple threads may call MPI"""

def Init_thread(int required):
    """
    Initialize the MPI execution environment
    """
    cdef int provided = MPI_THREAD_SINGLE
    CHKERR( MPI_Init_thread(NULL, NULL, required, &provided) )
    return provided

def Query_thread():
    """
    Return the level of thread support
    provided by the MPI library
    """
    cdef int provided = MPI_THREAD_SINGLE
    CHKERR( MPI_Query_thread(&provided) )
    return provided

def Is_thread_main():
    """
    Indicate whether this thread called
    ``Init`` or ``Init_thread``
    """
    cdef bint flag = 1
    CHKERR( MPI_Is_thread_main(&flag) )
    return flag

def Is_initialized():
    """
    Indicates whether ``Init`` has been called
    """
    cdef bint flag = 0
    CHKERR( MPI_Initialized(&flag) )
    return flag

def Is_finalized():
    """
    Indicates whether ``Finalize`` has completed
    """
    cdef bint flag = 0
    CHKERR( MPI_Finalized(&flag) )
    return flag

# Implementation Information
# --------------------------

# MPI Version Number
# -----------------

def Get_version():
    """
    Obtain the version number of the MPI standard supported
    by the implementation as a tuple ``(version, subversion)``
    """
    cdef int version = 1
    cdef int subversion = 0
    CHKERR( MPI_Get_version(&version, &subversion) )
    return (version, subversion)

VERSION    = MPI_VERSION
SUBVERSION = MPI_SUBVERSION

# Environmental Inquires
# ----------------------

def Get_processor_name():
    """
    Obtain the name of the calling processor
    """
    cdef char name[MPI_MAX_PROCESSOR_NAME+1]
    cdef int nlen = 0
    CHKERR( MPI_Get_processor_name(name, &nlen) )
    return tompistr(name, nlen)

# Timers and Synchronization
# --------------------------

def Wtime():
    """
    Return an elapsed time on the calling processor
    """
    return MPI_Wtime()

def Wtick():
    """
    Return the resolution of ``Wtime``
    """
    return MPI_Wtick()



# Maximum string sizes

# MPI-1
MAX_PROCESSOR_NAME = MPI_MAX_PROCESSOR_NAME
MAX_ERROR_STRING   = MPI_MAX_ERROR_STRING
# MPI-2
MAX_PORT_NAME      = MPI_MAX_PORT_NAME
MAX_INFO_KEY       = MPI_MAX_INFO_KEY
MAX_INFO_VAL       = MPI_MAX_INFO_VAL
MAX_OBJECT_NAME    = MPI_MAX_OBJECT_NAME
MAX_DATAREP_STRING = MPI_MAX_DATAREP_STRING




def get_vendor():
    """
    Infomation about the underlying MPI implementation

    :Returns:
    -`name`: implementation name
    -`version`: integer 3-tuple ``(major, minor, micro)``
    """
    name, version = PyMPI_Get_vendor()
    return (name, version)
