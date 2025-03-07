cdef class Status:
    """
    Status object.
    """

    def __cinit__(self, Status status: Status | None = None):
        cdef MPI_Status *s = &self.ob_mpi
        CHKERR( MPI_Status_set_source (s, MPI_ANY_SOURCE ) )
        CHKERR( MPI_Status_set_tag    (s, MPI_ANY_TAG    ) )
        CHKERR( MPI_Status_set_error  (s, MPI_SUCCESS    ) )
        if status is None: return
        self.ob_mpi = status.ob_mpi

    def __richcmp__(self, other, int op):
        if not isinstance(other, Status): return NotImplemented
        cdef Status s = <Status>self, o = <Status>other
        cdef int ne = memcmp(&s.ob_mpi, &o.ob_mpi, sizeof(MPI_Status))
        if   op == Py_EQ: return (ne == 0)
        elif op == Py_NE: return (ne != 0)
        cdef str mod = type(self).__module__
        cdef str cls = type(self).__name__
        raise TypeError(f"unorderable type '{mod}.{cls}'")

    def __reduce__(self) -> tuple[Any, tuple[Any, ...], dict[str, Any]]:
        return (__newobj__, (type(self),), self.__getstate__())

    def __getstate__(self) -> dict[str, int]:
        cdef dict state = {
            'source': self.Get_source(),
            'tag': self.Get_tag(),
            'error': self.Get_error(),
        }
        try:
            state['count'] = self.Get_elements(__BYTE__)
        except NotImplementedError:  # ~> legacy
            pass                     # ~> legacy
        try:
            state['cancelled'] = self.Is_cancelled()
        except NotImplementedError:  # ~> legacy
            pass                     # ~> legacy
        return state

    def __setstate__(self, state: dict[str, int]) -> None:
        self.Set_source(state['source'])
        self.Set_tag(state['tag'])
        self.Set_error(state['error'])
        if 'count' in state:
            self.Set_elements(__BYTE__, state['count'])
        if 'cancelled' in state:
            self.Set_cancelled(state['cancelled'])

    def Get_source(self) -> int:
        """
        Get message source.
        """
        cdef int source = MPI_ANY_SOURCE
        CHKERR( MPI_Status_get_source(&self.ob_mpi, &source) )
        return source

    def Set_source(self, int source: int) -> None:
        """
        Set message source.
        """
        CHKERR( MPI_Status_set_source(&self.ob_mpi, source) )

    property source:
        """Message source."""
        def __get__(self) -> int:
            return self.Get_source()

        def __set__(self, value: int):
            self.Set_source(value)

    def Get_tag(self) -> int:
        """
        Get message tag.
        """
        cdef int tag = MPI_ANY_TAG
        CHKERR( MPI_Status_get_tag(&self.ob_mpi, &tag) )
        return tag

    def Set_tag(self, int tag: int) -> None:
        """
        Set message tag.
        """
        CHKERR( MPI_Status_set_tag(&self.ob_mpi, tag) )

    property tag:
        """Message tag."""
        def __get__(self) -> int:
            return self.Get_tag()

        def __set__(self, value: int):
            self.Set_tag(value)

    def Get_error(self) -> int:
        """
        Get message error.
        """
        cdef int error = MPI_SUCCESS
        CHKERR( MPI_Status_get_error(&self.ob_mpi, &error) )
        return error

    def Set_error(self, int error: int) -> None:
        """
        Set message error.
        """
        CHKERR( MPI_Status_set_error(&self.ob_mpi, error) )

    property error:
        """Message error."""
        def __get__(self) -> int:
            return self.Get_error()

        def __set__(self, value: int):
            self.Set_error(value)

    def Get_count(self, Datatype datatype: Datatype = BYTE) -> int:
        """
        Get the number of *top level* elements.
        """
        cdef MPI_Datatype dtype = datatype.ob_mpi
        cdef MPI_Count count = MPI_UNDEFINED
        CHKERR( MPI_Get_count_c(&self.ob_mpi, dtype, &count) )
        return count

    property count:
        """Byte count."""
        def __get__(self) -> int:
            return self.Get_count(__BYTE__)

        def __set__(self, value: int):
            self.Set_elements(__BYTE__, value)

    def Get_elements(self, Datatype datatype: Datatype) -> int:
        """
        Get the number of basic elements in a datatype.
        """
        cdef MPI_Datatype dtype = datatype.ob_mpi
        cdef MPI_Count elements = MPI_UNDEFINED
        CHKERR( MPI_Get_elements_c(&self.ob_mpi, dtype, &elements) )
        return elements

    def Set_elements(
        self,
        Datatype datatype: Datatype,
        Count count: int,
    ) -> None:
        """
        Set the number of elements in a status.

        .. note:: This method should be only used when implementing
           query callback functions for generalized requests.
        """
        cdef MPI_Datatype dtype = datatype.ob_mpi
        CHKERR( MPI_Status_set_elements_c(&self.ob_mpi, dtype, count) )

    def Is_cancelled(self) -> bool:
        """
        Test to see if a request was cancelled.
        """
        cdef int flag = 0
        CHKERR( MPI_Test_cancelled(&self.ob_mpi, &flag) )
        return <bint>flag

    def Set_cancelled(self, bint flag: bool) -> None:
        """
        Set the cancelled state associated with a status.

        .. note:: This method should be used only when implementing
           query callback functions for generalized requests.
        """
        CHKERR( MPI_Status_set_cancelled(&self.ob_mpi, flag) )

    property cancelled:
        """Cancelled state."""
        def __get__(self) -> bool:
            return self.Is_cancelled()

        def __set__(self, value: bool):
            self.Set_cancelled(value)

    # Memory
    # ------

    def tomemory(self) -> memoryview:
        """
        Return status memory view.
        """
        cdef buffer buf = newbuffer()
        cdef void *base = <void*> &self.ob_mpi
        cdef Py_ssize_t size = <Py_ssize_t> sizeof(MPI_Status)
        PyBuffer_FillInfo(&buf.view, self, base, size, 0, PyBUF_SIMPLE)
        return PyMemoryView_FromObject(buf).cast('i')

    # Fortran Handle
    # --------------

    def py2f(self) -> list[int]:
        """
        """
        cdef MPI_Fint f_status[16]
        cdef MPI_Status *c_status = &self.ob_mpi
        cdef Py_ssize_t size = MPI_F_STATUS_SIZE
        CHKERR( MPI_Status_c2f(c_status, f_status) )
        return [f_status[i] for i in range(size)]

    @classmethod
    def f2py(cls, arg: list[int]) -> Self:
        """
        """
        cdef MPI_Fint f_status[16]
        cdef MPI_Status c_status[1]
        cdef Py_ssize_t size = MPI_F_STATUS_SIZE
        for i in range(size): f_status[i] = arg[i]
        CHKERR( MPI_Status_f2c(f_status, c_status) )
        return PyMPIStatus_New(c_status)


F_SOURCE      = MPI_F_SOURCE
F_TAG         = MPI_F_TAG
F_ERROR       = MPI_F_ERROR
F_STATUS_SIZE = MPI_F_STATUS_SIZE
