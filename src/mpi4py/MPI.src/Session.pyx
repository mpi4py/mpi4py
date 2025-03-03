cdef class Session:
    """
    Session context.
    """

    def __cinit__(self, Session session: Session | None = None):
        cinit(self, session)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Session): return NotImplemented
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
    def fromhandle(cls, handle: int) -> Session:
        """
        Create object from MPI handle.
        """
        return fromhandle(<MPI_Session> <Py_uintptr_t> handle)

    def free(self) -> None:
        """
        Call `Finalize` if not null.
        """
        safefree(self)

    #

    @classmethod
    def Init(
        cls,
        Info info: Info = INFO_NULL,
        Errhandler errhandler: Errhandler | None = None,
    ) -> Self:
        """
        Create a new session.
        """
        cdef MPI_Errhandler cerrhdl = arg_Errhandler(errhandler)
        cdef Session session = <Session>New(cls)
        CHKERR( MPI_Session_init(
            info.ob_mpi, cerrhdl, &session.ob_mpi) )
        session_set_eh(session.ob_mpi)
        return session

    def Finalize(self) -> None:
        """
        Finalize a session.
        """
        cdef MPI_Session save = self.ob_mpi
        CHKERR( MPI_Session_finalize(&self.ob_mpi) )
        if constobj(self): self.ob_mpi = save

    def Get_num_psets(self, Info info: Info = INFO_NULL) -> int:
        """
        Number of available process sets.
        """
        cdef int num_psets = -1
        CHKERR( MPI_Session_get_num_psets(
            self.ob_mpi, info.ob_mpi, &num_psets) )
        return num_psets

    def Get_nth_pset(self, int n: int, Info info: Info = INFO_NULL) -> str:
        """
        Name of the *n*-th process set.
        """
        cdef int nlen = MPI_MAX_PSET_NAME_LEN
        cdef char *pset_name = NULL
        cdef unused = allocate(nlen+1, sizeof(char), &pset_name)
        CHKERR( MPI_Session_get_nth_pset(
            self.ob_mpi, info.ob_mpi, n, &nlen, pset_name) )
        return mpistr(pset_name)

    def Get_info(self) -> Info:
        """
        Return the current hints for a session.
        """
        cdef Info info = <Info>New(Info)
        CHKERR( MPI_Session_get_info(
            self.ob_mpi, &info.ob_mpi) )
        return info

    def Get_pset_info(self, pset_name: str) -> Info:
        """
        Return the current hints for a session and process set.
        """
        cdef char *cname = NULL
        pset_name = asmpistr(pset_name, &cname)
        cdef Info info = <Info>New(Info)
        CHKERR( MPI_Session_get_pset_info(
            self.ob_mpi, cname, &info.ob_mpi) )
        return info

    def Create_group(self, pset_name: str) -> Group:
        """
        Create a new group from session and process set.
        """
        cdef char *cname = NULL
        pset_name = asmpistr(pset_name, &cname)
        cdef Group group = <Group>New(Group)
        CHKERR( MPI_Group_from_session_pset(
            self.ob_mpi, cname, &group.ob_mpi) )
        return group

    # Buffer Allocation and Usage
    # ---------------------------

    def Attach_buffer(self, buf: Buffer | None) -> None:
        """
        Attach a user-provided buffer for sending in buffered mode.
        """
        cdef void *base = NULL
        cdef MPI_Count size = 0
        buf = attach_buffer(buf, &base, &size)
        with nogil: CHKERR( MPI_Session_attach_buffer_c(
            self.ob_mpi, base, size) )
        detach_buffer_set(self, buf)  # ~> MPI-4.1

    def Detach_buffer(self) -> Buffer | None:
        """
        Remove an existing attached buffer.
        """
        cdef void *base = NULL
        cdef MPI_Count size = 0
        with nogil: CHKERR( MPI_Session_detach_buffer_c(
            self.ob_mpi, &base, &size) )
        return detach_buffer_get(self, base, size)  # ~> MPI-4.1

    def Flush_buffer(self) -> None:
        """
        Block until all buffered messages have been transmitted.
        """
        with nogil: CHKERR( MPI_Session_flush_buffer(self.ob_mpi) )

    def Iflush_buffer(self) -> Request:
        """
        Nonblocking flush for buffered messages.
        """
        cdef Request request = <Request>New(Request)
        with nogil: CHKERR( MPI_Session_iflush_buffer(
            self.ob_mpi, &request.ob_mpi) )
        return request  # ~> MPI-4.1

    # Error handling
    # --------------

    @classmethod
    def Create_errhandler(
        cls,
        errhandler_fn: Callable[[Session, int], None],
    ) -> Errhandler:
        """
        Create a new error handler for sessions.
        """
        cdef Errhandler errhandler = <Errhandler>New(Errhandler)
        cdef MPI_Session_errhandler_function *fn = NULL
        cdef int index = errhdl_new(errhandler_fn, &fn)
        try:
            CHKERR( MPI_Session_create_errhandler(fn, &errhandler.ob_mpi) )
        except:                     # ~> uncovered  # noqa
            errhdl_del(&index, fn)  # ~> uncovered
            raise                   # ~> uncovered
        return errhandler

    def Get_errhandler(self) -> Errhandler:
        """
        Get the error handler for a session.
        """
        cdef Errhandler errhandler = <Errhandler>New(Errhandler)
        CHKERR( MPI_Session_get_errhandler(self.ob_mpi, &errhandler.ob_mpi) )
        return errhandler

    def Set_errhandler(self, Errhandler errhandler: Errhandler) -> None:
        """
        Set the error handler for a session.
        """
        CHKERR( MPI_Session_set_errhandler(self.ob_mpi, errhandler.ob_mpi) )

    def Call_errhandler(self, int errorcode: int) -> None:
        """
        Call the error handler installed on a session.
        """
        CHKERR( MPI_Session_call_errhandler(self.ob_mpi, errorcode) )

    # Integer Handle
    # --------------

    def toint(self) -> int:
        """
        Translate object to integer handle.
        """
        return MPI_Session_toint(self.ob_mpi)

    @classmethod
    def fromint(cls, arg: int, /) -> Session:
        """
        Translate integer handle to object.
        """
        return fromhandle(MPI_Session_fromint(arg))

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
        return fromhandle(MPI_Session_f2c(arg))


cdef Session __SESSION_NULL__ = def_Session( MPI_SESSION_NULL , "SESSION_NULL" )


# Predefined session handle
# -------------------------

SESSION_NULL  = __SESSION_NULL__  #: Null session handler
