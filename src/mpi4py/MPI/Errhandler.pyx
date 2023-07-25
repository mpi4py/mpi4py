cdef class Errhandler:
    """
    Error handler.
    """

    def __cinit__(self, Errhandler errhandler: Errhandler | None = None):
        self.ob_mpi = MPI_ERRHANDLER_NULL
        cinit(self, errhandler)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Errhandler): return NotImplemented
        return richcmp(self, other, op)

    def __bool__(self) -> bool:
        return self.ob_mpi != MPI_ERRHANDLER_NULL

    def __reduce__(self) -> str | tuple[Any, ...]:
        return reduce_default(self)

    def Free(self) -> None:
        """
        Free an error handler.
        """
        CHKERR( MPI_Errhandler_free(&self.ob_mpi) )
        if self is __ERRORS_RETURN__:    self.ob_mpi = MPI_ERRORS_RETURN
        if self is __ERRORS_ABORT__:     self.ob_mpi = MPI_ERRORS_ABORT
        if self is __ERRORS_ARE_FATAL__: self.ob_mpi = MPI_ERRORS_ARE_FATAL

    # Fortran Handle
    # --------------

    def py2f(self) -> int:
        """
        """
        return MPI_Errhandler_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg: int) -> Errhandler:
        """
        """
        return PyMPIErrhandler_New(MPI_Errhandler_f2c(arg))


cdef Errhandler __ERRHANDLER_NULL__  = def_Errhandler( MPI_ERRHANDLER_NULL  , "ERRHANDLER_NULL"  )
cdef Errhandler __ERRORS_RETURN__    = def_Errhandler( MPI_ERRORS_RETURN    , "ERRORS_RETURN"    )
cdef Errhandler __ERRORS_ABORT__     = def_Errhandler( MPI_ERRORS_ABORT     , "ERRORS_ABORT"     )
cdef Errhandler __ERRORS_ARE_FATAL__ = def_Errhandler( MPI_ERRORS_ARE_FATAL , "ERRORS_ARE_FATAL" )


# Predefined errhandler handles
# -----------------------------

ERRHANDLER_NULL  = __ERRHANDLER_NULL__  #: Null error handler
ERRORS_RETURN    = __ERRORS_RETURN__    #: Errors return error handler
ERRORS_ABORT     = __ERRORS_ABORT__     #: Errors abort error handler
ERRORS_ARE_FATAL = __ERRORS_ARE_FATAL__ #: Errors are fatal error handler
