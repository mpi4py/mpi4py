cdef class Errhandler:

    """
    Error Handler
    """

    def __cinit__(self):
        self.ob_mpi = MPI_ERRHANDLER_NULL

    def __dealloc__(self):
        cdef int ierr = 0
        if not (self.flags & PyMPI_SKIP_FREE):
            ierr = _del_Errhandler(&self.ob_mpi); CHKERR(ierr)

    def __richcmp__(self, other, int op):
        if not isinstance(self,  Errhandler): return NotImplemented
        if not isinstance(other, Errhandler): return NotImplemented
        cdef Errhandler s = self, o = other
        if   op == 2: return (s.ob_mpi == o.ob_mpi)
        elif op == 3: return (s.ob_mpi != o.ob_mpi)
        else: raise TypeError("only '==' and '!='")

    def __nonzero__(self):
        return self.ob_mpi != MPI_ERRHANDLER_NULL

    def __bool__(self):
        return self.ob_mpi != MPI_ERRHANDLER_NULL


    def Free(self):
        """
        Free an error handler
        """
        CHKERR( MPI_Errhandler_free(&self.ob_mpi) )



# Null errhandler handle
# ----------------------

ERRHANDLER_NULL  = _new_Errhandler(MPI_ERRHANDLER_NULL)



# Predefined errhandler handles
# -----------------------------

ERRORS_RETURN    = _new_Errhandler(MPI_ERRORS_RETURN)

ERRORS_ARE_FATAL = _new_Errhandler(MPI_ERRORS_ARE_FATAL)
