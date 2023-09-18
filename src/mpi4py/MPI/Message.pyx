cdef class Message:
    """
    Matched message.
    """

    def __cinit__(self, Message message: Message | None = None):
        cinit(self, message)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Message): return NotImplemented
        return richcmp(self, other, op)

    def __bool__(self) -> bool:
        return nonnull(self)

    def __reduce__(self) -> str | tuple[Any, ...]:
        return reduce_default(self)

    # Matching Probe
    # --------------

    @classmethod
    def Probe(
        cls,
        Comm comm: Comm,
        int source: int = ANY_SOURCE,
        int tag: int = ANY_TAG,
        Status status: Status | None = None,
    ) -> Self:
        """
        Blocking test for a matched message.
        """
        cdef MPI_Message cmessage = MPI_MESSAGE_NULL
        cdef MPI_Status *statusp = arg_Status(status)
        with nogil: CHKERR( MPI_Mprobe(
            source, tag, comm.ob_mpi, &cmessage, statusp) )
        cdef Message message = <Message>New(cls)
        message.ob_mpi = cmessage
        return message

    @classmethod
    def Iprobe(
        cls,
        Comm comm: Comm,
        int source: int = ANY_SOURCE,
        int tag: int = ANY_TAG,
        Status status: Status | None = None,
    ) -> Self | None:
        """
        Nonblocking test for a matched message.
        """
        cdef int flag = 0
        cdef MPI_Message cmessage = MPI_MESSAGE_NULL
        cdef MPI_Status *statusp = arg_Status(status)
        with nogil: CHKERR( MPI_Improbe(
             source, tag, comm.ob_mpi, &flag, &cmessage, statusp) )
        if flag == 0: return None
        cdef Message message = <Message>New(cls)
        message.ob_mpi = cmessage
        return message

    # Matched receives
    # ----------------

    def Recv(
        self,
        buf: BufSpec,
        Status status: Status | None = None,
    ) -> None:
        """
        Blocking receive of matched message.
        """
        cdef MPI_Message message = self.ob_mpi
        cdef int source = MPI_ANY_SOURCE
        if message == MPI_MESSAGE_NO_PROC:
            source = MPI_PROC_NULL
        cdef _p_msg_p2p rmsg = message_p2p_recv(buf, source)
        cdef MPI_Status *statusp = arg_Status(status)
        with nogil: CHKERR( MPI_Mrecv_c(
            rmsg.buf, rmsg.count, rmsg.dtype,
            &message, statusp) )
        if self is not __MESSAGE_NO_PROC__:
            self.ob_mpi = message

    def Irecv(self, buf: BufSpec) -> Request:
        """
        Nonblocking receive of matched message.
        """
        cdef MPI_Message message = self.ob_mpi
        cdef int source = MPI_ANY_SOURCE
        if message == MPI_MESSAGE_NO_PROC:
            source = MPI_PROC_NULL
        cdef _p_msg_p2p rmsg = message_p2p_recv(buf, source)
        cdef Request request = <Request>New(Request)
        with nogil: CHKERR( MPI_Imrecv_c(
            rmsg.buf, rmsg.count, rmsg.dtype,
            &message, &request.ob_mpi) )
        if self is not __MESSAGE_NO_PROC__:
            self.ob_mpi = message
        request.ob_buf = rmsg
        return request

    # Python Communication
    # --------------------
    #
    @classmethod
    def probe(
        cls,
        Comm comm: Comm,
        int source: int = ANY_SOURCE,
        int tag: int = ANY_TAG,
        Status status: Status | None = None,
    ) -> Self:
        """
        Blocking test for a matched message.
        """
        cdef Message message = <Message>New(cls)
        cdef MPI_Status *statusp = arg_Status(status)
        message.ob_buf = PyMPI_mprobe(source, tag, comm.ob_mpi,
                                      &message.ob_mpi, statusp)
        return message
    #
    @classmethod
    def iprobe(
        cls,
        Comm comm: Comm,
        int source: int = ANY_SOURCE,
        int tag: int = ANY_TAG,
        Status status: Status | None = None,
    ) -> Self | None:
        """
        Nonblocking test for a matched message.
        """
        cdef int flag = 0
        cdef Message message = <Message>New(cls)
        cdef MPI_Status *statusp = arg_Status(status)
        message.ob_buf = PyMPI_improbe(source, tag, comm.ob_mpi, &flag,
                                       &message.ob_mpi, statusp)
        if flag == 0: return None
        return message
    #
    def recv(self, Status status: Status | None = None) -> Any:
        """
        Blocking receive of matched message.
        """
        cdef object rmsg = self.ob_buf
        cdef MPI_Message message = self.ob_mpi
        cdef MPI_Status *statusp = arg_Status(status)
        rmsg = PyMPI_mrecv(rmsg, &message, statusp)
        if self is not __MESSAGE_NO_PROC__: self.ob_mpi = message
        if self.ob_mpi == MPI_MESSAGE_NULL: self.ob_buf = None
        return rmsg
    #
    def irecv(self) -> Request:
        """
        Nonblocking receive of matched message.
        """
        cdef object rmsg = self.ob_buf
        cdef MPI_Message message = self.ob_mpi
        cdef Request request = <Request>New(Request)
        request.ob_buf = PyMPI_imrecv(rmsg, &message, &request.ob_mpi)
        if self is not __MESSAGE_NO_PROC__: self.ob_mpi = message
        if self.ob_mpi == MPI_MESSAGE_NULL: self.ob_buf = None
        return request

    # Fortran Handle
    # --------------

    def py2f(self) -> int:
        """
        """
        return MPI_Message_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg: int) -> Message:
        """
        """
        return PyMPIMessage_New(MPI_Message_f2c(arg))


cdef Message __MESSAGE_NULL__    = def_Message ( MPI_MESSAGE_NULL    , "MESSAGE_NULL"    )
cdef Message __MESSAGE_NO_PROC__ = def_Message ( MPI_MESSAGE_NO_PROC , "MESSAGE_NO_PROC" )


# Predefined message handles
# --------------------------

MESSAGE_NULL    = __MESSAGE_NULL__    #: Null message handle
MESSAGE_NO_PROC = __MESSAGE_NO_PROC__ #: No-proc message handle
