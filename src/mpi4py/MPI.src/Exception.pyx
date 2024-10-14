# Exception Class
# ---------------

class Exception(RuntimeError):
    """
    Exception class.
    """

    def __init__(self, int ierr: int = 0, /) -> None:
        """Initialize self."""
        if ierr < MPI_SUCCESS: ierr = MPI_ERR_UNKNOWN
        RuntimeError.__init__(self, ierr)

    def __int__(self) -> int:
        """Return int(self)."""
        return self.args[0]

    def __bool__(self) -> bool:
        """Return bool(self)."""
        return <int>self != MPI_SUCCESS

    def __hash__(self) -> int:
        """Return hash(self)."""
        return hash(int(self))

    def __eq__(self, object value) -> bool:
        """Return self==value."""
        return int(self) == value

    def __ne__(self, object value) -> bool:
        """Return self!=value."""
        return int(self) != value

    def __lt__(self, object value) -> bool:
        """Return self<value."""
        return int(self) < value

    def __le__(self, object value) -> bool:
        """Return self<=value."""
        return int(self) <= value

    def __gt__(self, object value) -> bool:
        """Return self>value."""
        return int(self) > value

    def __ge__(self, object value) -> bool:
        """Return self>=value."""
        return int(self) >= value

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"MPI.Exception({int(self)})"

    def __str__(self) -> str:
        """Return str(self)."""
        if MPI_VERSION < 4 and not mpi_active():
            return f"error code: {int(self)}"  # ~> legacy
        return self.Get_error_string()

    def Get_error_code(self) -> int:
        """
        Error code.
        """
        cdef int errorcode = self
        return errorcode

    def Get_error_class(self) -> int:
        """
        Error class.
        """
        cdef int errorcode = self
        cdef int errorclass = MPI_SUCCESS
        CHKERR( MPI_Error_class(errorcode, &errorclass) )
        return errorclass

    def Get_error_string(self) -> str:
        """
        Error string.
        """
        cdef int errorcode = self
        cdef char string[MPI_MAX_ERROR_STRING+1]
        cdef int resultlen = 0
        CHKERR( MPI_Error_string(errorcode, string, &resultlen) )
        return tompistr(string, resultlen)

    @property
    def error_code(self) -> int:
        """Error code."""
        return self.Get_error_code()

    @property
    def error_class(self) -> int:
        """Error class."""
        return self.Get_error_class()

    @property
    def error_string(self) -> str:
        """Error string."""
        return self.Get_error_string()


MPIException = Exception
