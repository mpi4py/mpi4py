cdef class Request:

    """
    Request handle
    """

    def __cinit__(self, Request request: Request | None = None):
        self.ob_mpi = MPI_REQUEST_NULL
        cinit(self, request)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Request): return NotImplemented
        return richcmp(self, other, op)

    def __bool__(self) -> bool:
        return self.ob_mpi != MPI_REQUEST_NULL

    def __reduce__(self) -> Union[str, tuple[Any, ...]]:
        return reduce_default(self)

    # Completion Operations
    # ---------------------

    def Wait(self, Status status: Status | None = None) -> Literal[True]:
        """
        Wait for a send or receive to complete
        """
        cdef MPI_Status *statusp = arg_Status(status)
        with nogil: CHKERR( MPI_Wait(
            &self.ob_mpi, statusp) )
        if self.ob_mpi == MPI_REQUEST_NULL:
            self.ob_buf = None
        return True

    def Test(self, Status status: Status | None = None) -> bool:
        """
        Test for the completion of a send or receive
        """
        cdef int flag = 0
        cdef MPI_Status *statusp = arg_Status(status)
        with nogil: CHKERR( MPI_Test(
            &self.ob_mpi, &flag, statusp) )
        if self.ob_mpi == MPI_REQUEST_NULL:
            self.ob_buf = None
        return <bint>flag

    def Free(self) -> None:
        """
        Free a communication request
        """
        with nogil: CHKERR( MPI_Request_free(&self.ob_mpi) )

    def Get_status(self, Status status: Status | None = None) -> bool:
        """
        Non-destructive test for the completion of a request
        """
        cdef int flag = 0
        cdef MPI_Status *statusp = arg_Status(status)
        with nogil: CHKERR( MPI_Request_get_status(
            self.ob_mpi, &flag, statusp) )
        return <bint>flag

    # Multiple Completions
    # --------------------

    @classmethod
    def Waitany(
        cls,
        requests: Sequence[Request],
        Status status: Status | None = None,
    ) -> int:
        """
        Wait for any previously initiated request to complete
        """
        cdef int count = 0
        cdef MPI_Request *irequests = NULL
        cdef int index = MPI_UNDEFINED
        cdef MPI_Status *statusp = arg_Status(status)
        #
        cdef tmp = acquire_rs(requests, None, &count, &irequests, NULL)
        try:
            with nogil: CHKERR( MPI_Waitany(
                count, irequests, &index, statusp) )
        finally:
            release_rs(requests, None, count, irequests, 0, NULL)
        return index

    @classmethod
    def Testany(
        cls,
        requests: Sequence[Request],
        Status status: Status | None = None,
    ) -> tuple[int, bool]:
        """
        Test for completion of any previously initiated request
        """
        cdef int count = 0
        cdef MPI_Request *irequests = NULL
        cdef int index = MPI_UNDEFINED
        cdef int flag = 0
        cdef MPI_Status *statusp = arg_Status(status)
        #
        cdef tmp = acquire_rs(requests, None, &count, &irequests, NULL)
        try:
            with nogil: CHKERR( MPI_Testany(
                count, irequests, &index, &flag, statusp) )
        finally:
            release_rs(requests, None, count, irequests, 0, NULL)
        #
        return (index, <bint>flag)

    @classmethod
    def Waitall(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> Literal[True]:
        """
        Wait for all previously initiated requests to complete
        """
        cdef int count = 0
        cdef MPI_Request *irequests = NULL
        cdef MPI_Status *istatuses = MPI_STATUSES_IGNORE
        #
        cdef tmp = acquire_rs(requests, statuses,
                              &count, &irequests, &istatuses)
        try:
            with nogil: CHKERR( MPI_Waitall(
                count, irequests, istatuses) )
        finally:
            release_rs(requests, statuses, count, irequests, count, istatuses)
        return True

    @classmethod
    def Testall(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> bool:
        """
        Test for completion of all previously initiated requests
        """
        cdef int count = 0
        cdef MPI_Request *irequests = NULL
        cdef int flag = 0
        cdef MPI_Status *istatuses = MPI_STATUSES_IGNORE
        #
        cdef tmp = acquire_rs(requests, statuses,
                              &count, &irequests, &istatuses)
        try:
            with nogil: CHKERR( MPI_Testall(
                count, irequests, &flag, istatuses) )
        finally:
            release_rs(requests, statuses,count, irequests, count, istatuses)
        return <bint>flag

    @classmethod
    def Waitsome(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> list[int] | None:
        """
        Wait for some previously initiated requests to complete
        """
        cdef int incount = 0
        cdef MPI_Request *irequests = NULL
        cdef int outcount = MPI_UNDEFINED, *iindices = NULL
        cdef MPI_Status *istatuses = MPI_STATUSES_IGNORE
        #
        cdef tmp1 = acquire_rs(requests, statuses,
                               &incount, &irequests, &istatuses)
        cdef tmp2 = newarray(incount, &iindices)
        try:
            with nogil: CHKERR( MPI_Waitsome(
                incount, irequests, &outcount, iindices, istatuses) )
        finally:
            release_rs(requests, statuses,
                       incount, irequests,
                       outcount, istatuses)
        #
        cdef object indices = None
        if outcount != MPI_UNDEFINED:
            indices = [iindices[i] for i in range(outcount)]
        return indices

    @classmethod
    def Testsome(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> list[int] | None:
        """
        Test for completion of some previously initiated requests
        """
        cdef int incount = 0
        cdef MPI_Request *irequests = NULL
        cdef int outcount = MPI_UNDEFINED, *iindices = NULL
        cdef MPI_Status *istatuses = MPI_STATUSES_IGNORE
        #
        cdef tmp1 = acquire_rs(requests, statuses,
                               &incount, &irequests, &istatuses)
        cdef tmp2 = newarray(incount, &iindices)
        try:
            with nogil: CHKERR( MPI_Testsome(
                incount, irequests, &outcount, iindices, istatuses) )
        finally:
            release_rs(requests, statuses,
                       incount, irequests,
                       outcount, istatuses)
        #
        cdef object indices = None
        if outcount != MPI_UNDEFINED:
            indices = [iindices[i] for i in range(outcount)]
        return indices

    # Cancel
    # ------

    def Cancel(self) -> None:
        """
        Cancel a communication request
        """
        with nogil: CHKERR( MPI_Cancel(&self.ob_mpi) )

    # Fortran Handle
    # --------------

    def py2f(self) -> int:
        """
        """
        return MPI_Request_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg: int) -> Request:
        """
        """
        if issubclass(cls, Prequest):
            return PyMPIPrequest_New(MPI_Request_f2c(arg))
        if issubclass(cls, Grequest):
            return PyMPIGrequest_New(MPI_Request_f2c(arg))
        return PyMPIRequest_New(MPI_Request_f2c(arg))

    # Python Communication
    # --------------------
    #
    def wait(
        self,
        Status status: Status | None = None,
    ) -> Any:
        """
        Wait for a send or receive to complete
        """
        cdef msg = PyMPI_wait(self, status)
        return msg
    #
    def test(
        self,
            Status status: Status | None = None,
    ) -> tuple[bool, Any | None]:
        """
        Test for the completion of a send or receive
        """
        cdef int flag = 0
        cdef msg = PyMPI_test(self, &flag, status)
        return (<bint>flag, msg)
    #
    def get_status(
        self,
        Status status: Status | None = None,
    ) -> bool:
        """
        Non-destructive test for the completion of a request
        """
        cdef int flag = 0
        cdef MPI_Status *statusp = arg_Status(status)
        with nogil: CHKERR( MPI_Request_get_status(
            self.ob_mpi, &flag, statusp) )
        return <bint>flag
    #
    @classmethod
    def waitany(
        cls,
        requests: Sequence[Request],
        Status status: Status | None = None
    ) -> tuple[int, Any]:
        """
        Wait for any previously initiated request to complete
        """
        cdef int index = MPI_UNDEFINED
        cdef msg = PyMPI_waitany(requests, &index, status)
        return (index, msg)
    #
    @classmethod
    def testany(
        cls,
        requests: Sequence[Request],
        Status status: Status | None = None,
    ) -> tuple[int, bool, Any | None]:
        """
        Test for completion of any previously initiated request
        """
        cdef int index = MPI_UNDEFINED
        cdef int flag  = 0
        cdef msg = PyMPI_testany(requests, &index, &flag, status)
        return (index, <bint>flag, msg)
    #
    @classmethod
    def waitall(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> list[Any]:
        """
        Wait for all previously initiated requests to complete
        """
        cdef msg = PyMPI_waitall(requests, statuses)
        return msg
    #
    @classmethod
    def testall(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None
    ) -> tuple[bool, list[Any] | None]:
        """
        Test for completion of all previously initiated requests
        """
        cdef int flag = 0
        cdef msg = PyMPI_testall(requests, &flag, statuses)
        return (<bint>flag, msg)
    #
    @classmethod
    def waitsome(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> tuple[list[int] | None, list[Any] | None]:
        """
        Wait for some previously initiated requests to complete
        """
        return PyMPI_waitsome(requests, statuses)
    #
    @classmethod
    def testsome(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> tuple[list[int] | None, list[Any] | None]:
        """
        Test for completion of some previously initiated requests
        """
        return PyMPI_testsome(requests, statuses)
    #
    def cancel(self) -> None:
        """
        Cancel a communication request
        """
        with nogil: CHKERR( MPI_Cancel(&self.ob_mpi) )


cdef class Prequest(Request):

    """
    Persistent request handle
    """

    def __cinit__(self, Request request: Request | None = None):
        if self.ob_mpi == MPI_REQUEST_NULL: return
        <void>(<Prequest?>request)

    def Start(self) -> None:
        """
        Initiate a communication with a persistent request
        """
        with nogil: CHKERR( MPI_Start(&self.ob_mpi) )

    @classmethod
    def Startall(cls, requests: list[Prequest]) -> None:
        """
        Start a collection of persistent requests
        """
        cdef int count = 0
        cdef MPI_Request *irequests = NULL
        cdef tmp = acquire_rs(requests, None, &count, &irequests, NULL)
        #
        try:
            with nogil: CHKERR( MPI_Startall(count, irequests) )
        finally:
            release_rs(requests, None, count, irequests, 0, NULL)

    # Partitioned completion
    # ----------------------

    def Pready(
        self,
        int partition: int,
    ) -> None:
        """
        Mark a given partition as ready
        """
        CHKERR( MPI_Pready(partition, self.ob_mpi) )

    def Pready_range(
        self,
        int partition_low: int,
        int partition_high: int,
    ) -> None:
        """
        Mark a range of partitions as ready
        """
        CHKERR( MPI_Pready_range(partition_low, partition_high, self.ob_mpi) )

    def Pready_list(
        self,
        partitions: Sequence[int],
    ) -> None:
        """
        Mark a sequence of partitions as ready
        """
        cdef int length = 0, *array_of_partitions = NULL
        partitions = getarray(partitions, &length, &array_of_partitions)
        CHKERR( MPI_Pready_list(length, array_of_partitions, self.ob_mpi) )

    def Parrived(
        self,
        int partition: int,
    ) -> bool:
        """
        Test partial completion of a partitioned receive operation
        """
        cdef int flag = 0
        CHKERR( MPI_Parrived(self.ob_mpi, partition, &flag) )
        return <bint>flag


cdef class Grequest(Request):

    """
    Generalized request handle
    """

    def __cinit__(self, Request request: Request | None = None):
        self.ob_grequest = self.ob_mpi
        if self.ob_mpi == MPI_REQUEST_NULL: return
        <void>(<Grequest?>request)

    @classmethod
    def Start(
        cls,
        query_fn: Callable[..., None],
        free_fn: Callable[..., None],
        cancel_fn: Callable[..., None],
        args: tuple[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Grequest:
        """
        Create and return a user-defined request
        """
        cdef Grequest request = <Grequest>New(Grequest)
        cdef _p_greq state = _p_greq(
            query_fn, free_fn, cancel_fn,args, kwargs)
        with nogil: CHKERR( MPI_Grequest_start(
            greq_query_fn, greq_free_fn, greq_cancel_fn,
            <void*>state, &request.ob_mpi) )
        Py_INCREF(state)
        request.ob_grequest = request.ob_mpi
        return request

    def Complete(self) -> None:
        """
        Notify that a user-defined request is complete
        """
        if self.ob_mpi != MPI_REQUEST_NULL:
            if self.ob_mpi != self.ob_grequest:
                raise MPIException(MPI_ERR_REQUEST)
        cdef MPI_Request grequest = self.ob_grequest
        self.ob_grequest = self.ob_mpi ## or MPI_REQUEST_NULL ??
        with nogil: CHKERR( MPI_Grequest_complete(grequest) )
        self.ob_grequest = self.ob_mpi ## or MPI_REQUEST_NULL ??



cdef Request __REQUEST_NULL__ = def_Request( MPI_REQUEST_NULL , "REQUEST_NULL" )


# Predefined request handles
# --------------------------

REQUEST_NULL = __REQUEST_NULL__  #: Null request handle
