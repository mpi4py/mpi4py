mpi4py.MPI
==========

.. currentmodule:: mpi4py.MPI


Classes
-------

.. rubric:: Ancillary

.. autosummary::
   Datatype
   Status
   Request
   Prequest
   Grequest
   Op
   Group
   Info
   Session

.. rubric:: Communication

.. autosummary::
   Comm
   Intracomm
   Topocomm
   Cartcomm
   Graphcomm
   Distgraphcomm
   Intercomm
   Message

.. rubric:: One-sided operations

.. autosummary::
   Win

.. rubric:: Input/Output

.. autosummary::
   File

.. rubric:: Error handling

.. autosummary::
   Errhandler
   Exception

.. rubric:: Auxiliary

.. autosummary::
   Pickle
   buffer


Functions
---------

.. rubric:: Version inquiry

.. autosummary::
   Get_version
   Get_library_version

.. rubric:: Initialization and finalization

.. autosummary::
   Init
   Init_thread
   Finalize
   Is_initialized
   Is_finalized
   Query_thread
   Is_thread_main

.. rubric:: Memory allocation

.. autosummary::
   Alloc_mem
   Free_mem

.. rubric:: Address manipulation

.. autosummary::
   Get_address
   Aint_add
   Aint_diff

.. rubric:: Timer

.. autosummary::
   Wtick
   Wtime

.. rubric:: Error handling

.. autosummary::
   Get_error_class
   Get_error_string
   Add_error_class
   Add_error_code
   Add_error_string
   Remove_error_class
   Remove_error_code
   Remove_error_string

.. rubric:: Dynamic process management

.. autosummary::
   Open_port
   Close_port
   Publish_name
   Unpublish_name
   Lookup_name

.. rubric:: Miscellanea

.. autosummary::
   Attach_buffer
   Detach_buffer
   Flush_buffer
   Iflush_buffer
   Compute_dims
   Get_processor_name
   Register_datarep
   Pcontrol

.. rubric:: Utilities

.. autosummary::
   get_vendor
..
   _typecode
   _sizeof
   _addressof
   _handleof
..
   _comm_lock
   _comm_lock_table
   _commctx_inter
   _commctx_intra
   _set_abort_status


Attributes
----------

.. autosummary::

   UNDEFINED

   ANY_SOURCE
   ANY_TAG
   PROC_NULL
   ROOT

   BOTTOM
   IN_PLACE
   BUFFER_AUTOMATIC

   KEYVAL_INVALID

   TAG_UB
   IO
   WTIME_IS_GLOBAL
   UNIVERSE_SIZE
   APPNUM
   LASTUSEDCODE

   WIN_BASE
   WIN_SIZE
   WIN_DISP_UNIT
   WIN_CREATE_FLAVOR
   WIN_FLAVOR
   WIN_MODEL

   SUCCESS
   ERR_LASTCODE
   ERR_COMM
   ERR_GROUP
   ERR_TYPE
   ERR_REQUEST
   ERR_OP
   ERR_ERRHANDLER
   ERR_BUFFER
   ERR_COUNT
   ERR_TAG
   ERR_RANK
   ERR_ROOT
   ERR_TRUNCATE
   ERR_IN_STATUS
   ERR_PENDING
   ERR_TOPOLOGY
   ERR_DIMS
   ERR_ARG
   ERR_OTHER
   ERR_UNKNOWN
   ERR_INTERN
   ERR_INFO
   ERR_FILE
   ERR_WIN
   ERR_KEYVAL
   ERR_INFO_KEY
   ERR_INFO_VALUE
   ERR_INFO_NOKEY
   ERR_ACCESS
   ERR_AMODE
   ERR_BAD_FILE
   ERR_FILE_EXISTS
   ERR_FILE_IN_USE
   ERR_NO_SPACE
   ERR_NO_SUCH_FILE
   ERR_IO
   ERR_READ_ONLY
   ERR_CONVERSION
   ERR_DUP_DATAREP
   ERR_UNSUPPORTED_DATAREP
   ERR_UNSUPPORTED_OPERATION
   ERR_NAME
   ERR_NO_MEM
   ERR_NOT_SAME
   ERR_PORT
   ERR_QUOTA
   ERR_SERVICE
   ERR_SPAWN
   ERR_BASE
   ERR_SIZE
   ERR_DISP
   ERR_ASSERT
   ERR_LOCKTYPE
   ERR_RMA_CONFLICT
   ERR_RMA_SYNC
   ERR_RMA_RANGE
   ERR_RMA_ATTACH
   ERR_RMA_SHARED
   ERR_RMA_FLAVOR

   ORDER_C
   ORDER_F
   ORDER_FORTRAN

   TYPECLASS_INTEGER
   TYPECLASS_REAL
   TYPECLASS_COMPLEX

   DISTRIBUTE_NONE
   DISTRIBUTE_BLOCK
   DISTRIBUTE_CYCLIC
   DISTRIBUTE_DFLT_DARG

   COMBINER_NAMED
   COMBINER_DUP
   COMBINER_CONTIGUOUS
   COMBINER_VECTOR
   COMBINER_HVECTOR
   COMBINER_INDEXED
   COMBINER_HINDEXED
   COMBINER_INDEXED_BLOCK
   COMBINER_HINDEXED_BLOCK
   COMBINER_STRUCT
   COMBINER_SUBARRAY
   COMBINER_DARRAY
   COMBINER_RESIZED
   COMBINER_VALUE_INDEX
   COMBINER_F90_REAL
   COMBINER_F90_COMPLEX
   COMBINER_F90_INTEGER

   IDENT
   CONGRUENT
   SIMILAR
   UNEQUAL

   CART
   GRAPH
   DIST_GRAPH

   UNWEIGHTED
   WEIGHTS_EMPTY

   COMM_TYPE_SHARED

   BSEND_OVERHEAD

   WIN_FLAVOR_CREATE
   WIN_FLAVOR_ALLOCATE
   WIN_FLAVOR_DYNAMIC
   WIN_FLAVOR_SHARED

   WIN_SEPARATE
   WIN_UNIFIED

   MODE_NOCHECK
   MODE_NOSTORE
   MODE_NOPUT
   MODE_NOPRECEDE
   MODE_NOSUCCEED

   LOCK_EXCLUSIVE
   LOCK_SHARED

   MODE_RDONLY
   MODE_WRONLY
   MODE_RDWR
   MODE_CREATE
   MODE_EXCL
   MODE_DELETE_ON_CLOSE
   MODE_UNIQUE_OPEN
   MODE_SEQUENTIAL
   MODE_APPEND

   SEEK_SET
   SEEK_CUR
   SEEK_END

   DISPLACEMENT_CURRENT
   DISP_CUR

   THREAD_SINGLE
   THREAD_FUNNELED
   THREAD_SERIALIZED
   THREAD_MULTIPLE

   VERSION
   SUBVERSION

   MAX_PROCESSOR_NAME
   MAX_ERROR_STRING
   MAX_PORT_NAME
   MAX_INFO_KEY
   MAX_INFO_VAL
   MAX_OBJECT_NAME
   MAX_DATAREP_STRING
   MAX_LIBRARY_VERSION_STRING

   DATATYPE_NULL
   PACKED
   BYTE
   AINT
   OFFSET
   COUNT
   CHAR
   WCHAR
   SIGNED_CHAR
   SHORT
   INT
   LONG
   LONG_LONG
   UNSIGNED_CHAR
   UNSIGNED_SHORT
   UNSIGNED
   UNSIGNED_LONG
   UNSIGNED_LONG_LONG
   FLOAT
   DOUBLE
   LONG_DOUBLE
   C_BOOL
   INT8_T
   INT16_T
   INT32_T
   INT64_T
   UINT8_T
   UINT16_T
   UINT32_T
   UINT64_T
   C_COMPLEX
   C_FLOAT_COMPLEX
   C_DOUBLE_COMPLEX
   C_LONG_DOUBLE_COMPLEX
   CXX_BOOL
   CXX_FLOAT_COMPLEX
   CXX_DOUBLE_COMPLEX
   CXX_LONG_DOUBLE_COMPLEX
   SHORT_INT
   INT_INT
   TWOINT
   LONG_INT
   FLOAT_INT
   DOUBLE_INT
   LONG_DOUBLE_INT
   CHARACTER
   LOGICAL
   INTEGER
   REAL
   DOUBLE_PRECISION
   COMPLEX
   DOUBLE_COMPLEX
   LOGICAL1
   LOGICAL2
   LOGICAL4
   LOGICAL8
   INTEGER1
   INTEGER2
   INTEGER4
   INTEGER8
   INTEGER16
   REAL2
   REAL4
   REAL8
   REAL16
   COMPLEX4
   COMPLEX8
   COMPLEX16
   COMPLEX32
   UNSIGNED_INT
   SIGNED_SHORT
   SIGNED_INT
   SIGNED_LONG
   SIGNED_LONG_LONG
   BOOL
   SINT8_T
   SINT16_T
   SINT32_T
   SINT64_T
   F_BOOL
   F_INT
   F_FLOAT
   F_DOUBLE
   F_COMPLEX
   F_FLOAT_COMPLEX
   F_DOUBLE_COMPLEX

   REQUEST_NULL

   MESSAGE_NULL
   MESSAGE_NO_PROC

   OP_NULL
   MAX
   MIN
   SUM
   PROD
   LAND
   BAND
   LOR
   BOR
   LXOR
   BXOR
   MAXLOC
   MINLOC
   REPLACE
   NO_OP

   GROUP_NULL
   GROUP_EMPTY

   INFO_NULL
   INFO_ENV

   ERRHANDLER_NULL
   ERRORS_RETURN
   ERRORS_ARE_FATAL

   COMM_NULL
   COMM_SELF
   COMM_WORLD

   WIN_NULL

   FILE_NULL

   pickle


.. Local variables:
.. fill-column: 79
.. End:
