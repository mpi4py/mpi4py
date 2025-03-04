cdef class Errhandler:
    """
    Error handler.
    """

    def __cinit__(self, Errhandler errhandler: Errhandler | None = None):
        cinit(self, errhandler)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Errhandler): return NotImplemented
        return richcmp(self, other, op)

    def __bool__(self) -> bool:
        return nonnull(self)

    def __reduce__(self) -> str | tuple[Any, ...]:
        return reduce_default(self)

    property handle:
        """MPI handle."""
        def __get__(self) -> int:
            return tohandle(self)

    @classmethod
    def fromhandle(cls, handle: int) -> Errhandler:
        """
        Create object from MPI handle.
        """
        return fromhandle(<MPI_Errhandler> <Py_uintptr_t> handle)

    def free(self) -> None:
        """
        Call `Free` if not null.
        """
        safefree(self)

    # Freeing Errorhandlers
    # ---------------------

    def Free(self) -> None:
        """
        Free an error handler.
        """
        cdef MPI_Errhandler save = self.ob_mpi
        CHKERR( MPI_Errhandler_free(&self.ob_mpi) )
        if constobj(self): self.ob_mpi = save

    # Integer Handle
    # --------------

    def toint(self) -> int:
        """
        Translate object to integer handle.
        """
        return MPI_Errhandler_toint(self.ob_mpi)

    @classmethod
    def fromint(cls, arg: int, /) -> Errhandler:
        """
        Translate integer handle to object.
        """
        return fromhandle(MPI_Errhandler_fromint(arg))

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
        return fromhandle(MPI_Errhandler_f2c(arg))


cdef Errhandler __ERRHANDLER_NULL__  = def_Errhandler( MPI_ERRHANDLER_NULL  , "ERRHANDLER_NULL"  )  # noqa
cdef Errhandler __ERRORS_RETURN__    = def_Errhandler( MPI_ERRORS_RETURN    , "ERRORS_RETURN"    )  # noqa
cdef Errhandler __ERRORS_ABORT__     = def_Errhandler( MPI_ERRORS_ABORT     , "ERRORS_ABORT"     )  # noqa
cdef Errhandler __ERRORS_ARE_FATAL__ = def_Errhandler( MPI_ERRORS_ARE_FATAL , "ERRORS_ARE_FATAL" )  # noqa


# Predefined errhandler handles
# -----------------------------

ERRHANDLER_NULL  = __ERRHANDLER_NULL__   #: Null error handler
ERRORS_RETURN    = __ERRORS_RETURN__     #: Errors return error handler
ERRORS_ABORT     = __ERRORS_ABORT__      #: Errors abort error handler
ERRORS_ARE_FATAL = __ERRORS_ARE_FATAL__  #: Errors are fatal error handler
