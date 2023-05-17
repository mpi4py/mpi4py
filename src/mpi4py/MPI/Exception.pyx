# Exception Class
# ---------------

cdef extern from "Python.h":
    ctypedef class __builtin__.RuntimeError [object PyBaseExceptionObject]:
        pass

cdef class Exception(RuntimeError):

    """
    Exception class
    """

    cdef int ob_mpi

    def __cinit__(self, int ierr: int = 0):
        if ierr < MPI_SUCCESS: ierr = MPI_ERR_UNKNOWN
        self.ob_mpi = ierr
        RuntimeError.__init__(self, ierr)

    def __richcmp__(Exception self, object error, int op):
        cdef int ierr  = self.ob_mpi
        if op == Py_LT: return ierr <  error
        if op == Py_LE: return ierr <= error
        if op == Py_EQ: return ierr == error
        if op == Py_NE: return ierr != error
        if op == Py_GT: return ierr >  error
        if op == Py_GE: return ierr >= error

    def __hash__(self) -> int:
        return hash(self.ob_mpi)

    def __bool__(self) -> bool:
        return self.ob_mpi != MPI_SUCCESS

    def __int__(self) -> int:
        return self.ob_mpi

    def __repr__(self) -> str:
        return f"MPI.Exception({self.ob_mpi})"

    def __str__(self) -> str:
        if MPI_VERSION < 4 and not mpi_active():
            return f"error code: {self.ob_mpi}"  #> legacy
        return self.Get_error_string()

    def Get_error_code(self) -> int:
        """
        Error code
        """
        cdef int errorcode = MPI_SUCCESS
        errorcode = self.ob_mpi
        return errorcode

    property error_code:
        """error code"""
        def __get__(self) -> int:
            return self.Get_error_code()

    def Get_error_class(self) -> int:
        """
        Error class
        """
        cdef int errorclass = MPI_SUCCESS
        CHKERR( MPI_Error_class(self.ob_mpi, &errorclass) )
        return errorclass

    property error_class:
        """error class"""
        def __get__(self) -> int:
            return self.Get_error_class()

    def Get_error_string(self) -> str:
        """
        Error string
        """
        cdef char string[MPI_MAX_ERROR_STRING+1]
        cdef int resultlen = 0
        CHKERR( MPI_Error_string(self.ob_mpi, string, &resultlen) )
        return tompistr(string, resultlen)

    property error_string:
        """error string"""
        def __get__(self) -> str:
            return self.Get_error_string()


MPIException = Exception
