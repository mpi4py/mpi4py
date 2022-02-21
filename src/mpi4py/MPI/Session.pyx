cdef class Session:

    """
    Session
    """

    def __cinit__(self, Session session: Optional[Session] = None):
        self.ob_mpi = MPI_SESSION_NULL
        if session is None: return
        self.ob_mpi = session.ob_mpi

    def __dealloc__(self):
        if not (self.flags & PyMPI_OWNED): return
        CHKERR( del_Session(&self.ob_mpi) )

    def __richcmp__(self, other, int op):
        if not isinstance(other, Session): return NotImplemented
        cdef Session s = <Session>self, o = <Session>other
        if   op == Py_EQ: return (s.ob_mpi == o.ob_mpi)
        elif op == Py_NE: return (s.ob_mpi != o.ob_mpi)
        cdef mod = type(self).__module__
        cdef cls = type(self).__name__
        raise TypeError("unorderable type: '%s.%s'" % (mod, cls))

    def __bool__(self) -> bool:
        return self.ob_mpi != MPI_SESSION_NULL

    @classmethod
    def Init(
        cls,
        Info info: Info = INFO_NULL,
        Errhandler errhandler: Optional[Errhandler] = None,
    ) -> Session:
        """
        Create a new session
        """
        cdef MPI_Errhandler cerrhdl = arg_Errhandler(errhandler)
        cdef Session session = Session.__new__(Session)
        CHKERR( MPI_Session_init(
            info.ob_mpi, cerrhdl, &session.ob_mpi) )
        session_set_eh(session.ob_mpi)
        return session

    def Finalize(self) -> None:
        """
        Finalize a session
        """
        CHKERR( MPI_Session_finalize(&self.ob_mpi) )

    def Get_num_psets(self, Info info: Info = INFO_NULL) -> int:
        """
        Number of available process sets
        """
        cdef int num_psets = -1
        CHKERR( MPI_Session_get_num_psets(
            self.ob_mpi, info.ob_mpi, &num_psets) )
        return num_psets

    def Get_nth_pset(self, int n: int, Info info: Info = INFO_NULL) -> str:
        """
        Name of the nth process set
        """
        cdef int nlen = MPI_MAX_PSET_NAME_LEN
        cdef char *pset_name = NULL
        cdef tmp = allocate(nlen+1, sizeof(char), &pset_name)
        CHKERR( MPI_Session_get_nth_pset(
            self.ob_mpi, info.ob_mpi, n, &nlen, pset_name) )
        return mpistr(pset_name)
    
    def Get_info(self) -> Info:
        """
        Return the hints for a session
        """
        cdef Info info = Info.__new__(Info)
        CHKERR( MPI_Session_get_info(
            self.ob_mpi, &info.ob_mpi) )
        return info
    
    def Get_pset_info(self, pset_name: str) -> Info:
        """
        Return the hints for a session and process set
        """
        cdef char *cname = NULL
        pset_name = asmpistr(pset_name, &cname)
        cdef Info info = Info.__new__(Info)
        CHKERR( MPI_Session_get_pset_info(
            self.ob_mpi, cname, &info.ob_mpi) )
        return info

    def Create_group(self, pset_name: str) -> Group:
        """
        Create a new group from session and process set
        """
        cdef char *cname = NULL
        pset_name = asmpistr(pset_name, &cname)
        cdef Group group = Group.__new__(Group)
        CHKERR( MPI_Group_from_session_pset(
            self.ob_mpi, cname, &group.ob_mpi) )
        return group

    # Error handling
    # --------------

    def Get_errhandler(self) -> Errhandler:
        """
        Get the error handler for a session
        """
        cdef Errhandler errhandler = Errhandler.__new__(Errhandler)
        CHKERR( MPI_Session_get_errhandler(self.ob_mpi, &errhandler.ob_mpi) )
        return errhandler

    def Set_errhandler(self, Errhandler errhandler: Errhandler) -> None:
        """
        Set the error handler for a session
        """
        CHKERR( MPI_Session_set_errhandler(self.ob_mpi, errhandler.ob_mpi) )

    def Call_errhandler(self, int errorcode: int) -> None:
        """
        Call the error handler installed on a session
        """
        CHKERR( MPI_Session_call_errhandler(self.ob_mpi, errorcode) )

    # Fortran Handle
    # --------------

    def py2f(self) -> int:
        """
        """
        return MPI_Session_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg: int) -> Session:
        """
        """
        cdef Session session = Session.__new__(Session)
        session.ob_mpi = MPI_Session_f2c(arg)
        return session



cdef Session __SESSION_NULL__ = new_Session(MPI_SESSION_NULL)


# Predefined session handle
# -------------------------

SESSION_NULL  = __SESSION_NULL__  #: Null session handler
