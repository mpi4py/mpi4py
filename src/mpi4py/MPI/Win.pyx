# Create flavors
# --------------
WIN_FLAVOR_CREATE   = MPI_WIN_FLAVOR_CREATE
WIN_FLAVOR_ALLOCATE = MPI_WIN_FLAVOR_ALLOCATE
WIN_FLAVOR_DYNAMIC  = MPI_WIN_FLAVOR_DYNAMIC
WIN_FLAVOR_SHARED   = MPI_WIN_FLAVOR_SHARED

# Memory model
# ------------
WIN_SEPARATE = MPI_WIN_SEPARATE
WIN_UNIFIED  = MPI_WIN_UNIFIED

# Assertion modes
# ---------------
MODE_NOCHECK   = MPI_MODE_NOCHECK
MODE_NOSTORE   = MPI_MODE_NOSTORE
MODE_NOPUT     = MPI_MODE_NOPUT
MODE_NOPRECEDE = MPI_MODE_NOPRECEDE
MODE_NOSUCCEED = MPI_MODE_NOSUCCEED

# Lock types
# ----------
LOCK_EXCLUSIVE = MPI_LOCK_EXCLUSIVE
LOCK_SHARED    = MPI_LOCK_SHARED


cdef class Win:
    """
    Remote memory access context.
    """

    def __cinit__(self, Win win: Win | None = None):
        cinit(self, win)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Win): return NotImplemented
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
    def fromhandle(cls, handle: int) -> Win:
        """
        Create object from MPI handle.
        """
        return fromhandle(<MPI_Win> <Py_uintptr_t> handle)

    # Window Creation
    # ---------------

    @classmethod
    def Create(
        cls,
        memory: Buffer | Bottom,
        Aint disp_unit: int = 1,
        Info info: Info = INFO_NULL,
        Intracomm comm: Intracomm = COMM_SELF,
    ) -> Self:
        """
        Create an window object for one-sided communication.
        """
        cdef void *base = MPI_BOTTOM
        cdef MPI_Aint size = 0
        if is_BOTTOM(memory):
            memory = None
        if memory is not None:
            memory = asbuffer_w(memory, &base, &size)
        cdef Win win = <Win>New(cls)
        with nogil: CHKERR( MPI_Win_create_c(
            base, size, disp_unit,
            info.ob_mpi, comm.ob_mpi, &win.ob_mpi) )
        win_set_eh(win.ob_mpi)
        win.ob_mem = memory
        return win

    @classmethod
    def Allocate(
        cls,
        Aint size: int,
        Aint disp_unit: int = 1,
        Info info: Info = INFO_NULL,
        Intracomm comm: Intracomm = COMM_SELF,
    ) -> Self:
        """
        Create an window object for one-sided communication.
        """
        cdef void *base = NULL
        cdef Win win = <Win>New(cls)
        with nogil: CHKERR( MPI_Win_allocate_c(
            size, disp_unit, info.ob_mpi,
            comm.ob_mpi, &base, &win.ob_mpi) )
        win_set_eh(win.ob_mpi)
        return win

    @classmethod
    def Allocate_shared(
        cls,
        Aint size: int,
        Aint disp_unit: int = 1,
        Info info: Info = INFO_NULL,
        Intracomm comm: Intracomm = COMM_SELF,
    ) -> Self:
        """
        Create an window object for one-sided communication.
        """
        cdef void *base = NULL
        cdef Win win = <Win>New(cls)
        with nogil: CHKERR( MPI_Win_allocate_shared_c(
            size, disp_unit, info.ob_mpi,
            comm.ob_mpi, &base, &win.ob_mpi) )
        win_set_eh(win.ob_mpi)
        return win

    def Shared_query(self, int rank: int) -> tuple[buffer, int]:
        """
        Query the process-local address for remote memory segments.
        """
        cdef void *base = NULL
        cdef MPI_Aint size = 0
        cdef MPI_Aint disp_unit = 1
        with nogil: CHKERR( MPI_Win_shared_query_c(
            self.ob_mpi, rank,
            &size, &disp_unit, &base) )
        return (tobuffer(self, base, size, 0), disp_unit)

    @classmethod
    def Create_dynamic(
        cls,
        Info info: Info = INFO_NULL,
        Intracomm comm: Intracomm = COMM_SELF,
    ) -> Self:
        """
        Create an window object for one-sided communication.
        """
        cdef Win win = <Win>New(cls)
        with nogil: CHKERR( MPI_Win_create_dynamic(
            info.ob_mpi, comm.ob_mpi, &win.ob_mpi) )
        win_set_eh(win.ob_mpi)
        win.ob_mem = {}
        return win

    def Attach(self, memory: Buffer) -> None:
        """
        Attach a local memory region.
        """
        cdef void *base = NULL
        cdef MPI_Aint size = 0
        memory = asbuffer_w(memory, &base, &size)
        with nogil: CHKERR( MPI_Win_attach(self.ob_mpi, base, size) )
        try:
            if self.ob_mem is None: self.ob_mem = {}
            (<dict>self.ob_mem)[<MPI_Aint>base] = memory
        except:   # ~> uncovered  # noqa
            pass  # ~> uncovered

    def Detach(self, memory: Buffer) -> None:
        """
        Detach a local memory region.
        """
        cdef void *base = NULL
        memory = asbuffer_w(memory, &base, NULL)
        with nogil: CHKERR( MPI_Win_detach(self.ob_mpi, base) )
        try:
            if self.ob_mem is None: return
            del (<dict>self.ob_mem)[<MPI_Aint>base]
        except:   # ~> uncovered  # noqa
            pass  # ~> uncovered

    def Free(self) -> None:
        """
        Free a window.
        """
        with nogil: CHKERR( MPI_Win_free(&self.ob_mpi) )
        self.ob_mem = None

    # Window Info
    # -----------

    def Set_info(self, Info info: Info) -> None:
        """
        Set new values for the hints associated with a window.
        """
        with nogil: CHKERR( MPI_Win_set_info(self.ob_mpi, info.ob_mpi) )

    def Get_info(self) -> Info:
        """
        Return the current hints for a window.
        """
        cdef Info info = <Info>New(Info)
        with nogil: CHKERR( MPI_Win_get_info( self.ob_mpi, &info.ob_mpi) )
        return info

    property info:
        """Info hints."""
        def __get__(self) -> Info:
            return self.Get_info()

        def __set__(self, value: Info):
            self.Set_info(value)

    # Window Group
    # -------------

    def Get_group(self) -> Group:
        """
        Access the group of processes that created the window.
        """
        cdef Group group = Group()
        with nogil: CHKERR( MPI_Win_get_group(self.ob_mpi, &group.ob_mpi) )
        return group

    property group:
        """Group."""
        def __get__(self) -> Group:
            return self.Get_group()

    # Window Attributes
    # -----------------

    def Get_attr(self, int keyval: int) -> int | Any | None:
        """
        Retrieve attribute value by key.
        """
        cdef void *attrval = NULL
        cdef int flag = 0
        CHKERR( MPI_Win_get_attr(self.ob_mpi, keyval, &attrval, &flag) )
        if flag == 0: return None
        if attrval == NULL: return 0
        # MPI-2 predefined attribute keyvals
        if keyval == MPI_WIN_BASE:
            return <MPI_Aint>attrval
        elif keyval == MPI_WIN_SIZE:
            return (<MPI_Aint*>attrval)[0]
        elif keyval == MPI_WIN_DISP_UNIT:
            return (<int*>attrval)[0]
        # MPI-3 predefined attribute keyvals
        elif keyval == MPI_WIN_CREATE_FLAVOR:
            return (<int*>attrval)[0]
        elif keyval == MPI_WIN_MODEL:
            return (<int*>attrval)[0]
        # user-defined attribute keyval
        return PyMPI_attr_get(self.ob_mpi, keyval, attrval)

    def Set_attr(self, int keyval: int, attrval: Any) -> None:
        """
        Store attribute value associated with a key.
        """
        PyMPI_attr_set(self.ob_mpi, keyval, attrval)

    def Delete_attr(self, int keyval: int) -> None:
        """
        Delete attribute value associated with a key.
        """
        PyMPI_attr_del(self.ob_mpi, keyval)

    @classmethod
    def Create_keyval(
        cls,
        copy_fn: Callable[[Win, int, Any], Any] | None = None,
        delete_fn: Callable[[Win, int, Any], None] | None = None,
        nopython: bool = False,
    ) -> int:
        """
        Create a new attribute key for windows.
        """
        cdef int keyval = MPI_KEYVAL_INVALID
        cdef MPI_Win_copy_attr_function *_copy = PyMPI_attr_copy_fn
        cdef MPI_Win_delete_attr_function *_del = PyMPI_attr_delete_fn
        cdef _p_keyval state = _p_keyval(copy_fn, delete_fn, nopython)
        CHKERR( MPI_Win_create_keyval(_copy, _del, &keyval, <void *>state) )
        PyMPI_attr_state_set(MPI_WIN_NULL, keyval, state)
        return keyval

    @classmethod
    def Free_keyval(cls, int keyval: int) -> int:
        """
        Free an attribute key for windows.
        """
        cdef int keyval_save = keyval
        CHKERR( MPI_Win_free_keyval(&keyval) )
        PyMPI_attr_state_del(MPI_WIN_NULL, keyval_save)
        return keyval

    property attrs:
        "Attributes."
        def __get__(self) -> tuple[int, int, int]:
            cdef void *base = NULL
            cdef MPI_Aint size = 0
            cdef int disp_unit = 1
            win_get_base(self.ob_mpi, &base)
            win_get_size(self.ob_mpi, &size)
            win_get_unit(self.ob_mpi, &disp_unit)
            return (<MPI_Aint>base, size, disp_unit)

    property flavor:
        """Create flavor."""
        def __get__(self) -> int:
            cdef int keyval = MPI_WIN_CREATE_FLAVOR
            cdef int *attrval = NULL, flag = 0
            cdef int flavor = MPI_WIN_FLAVOR_CREATE
            if keyval != MPI_KEYVAL_INVALID:
                CHKERR( MPI_Win_get_attr(self.ob_mpi, keyval,
                                         <void*>&attrval, &flag) )
                if flag and attrval != NULL:
                    flavor = attrval[0]
            return flavor

    property model:
        """Memory model."""
        def __get__(self) -> int:
            cdef int keyval = MPI_WIN_MODEL
            cdef int *attrval = NULL, flag = 0
            cdef int model = MPI_WIN_SEPARATE
            if keyval != MPI_KEYVAL_INVALID:
                CHKERR( MPI_Win_get_attr(self.ob_mpi, keyval,
                                         <void*>&attrval, &flag) )
                if flag and attrval != NULL:
                    model = attrval[0]
            return model

    def tomemory(self) -> buffer:
        """
        Return window memory buffer.
        """
        return getbuffer(self, 0, 1)

    # buffer interface (PEP 3118)

    def __getbuffer__(self, Py_buffer *view, int flags):
        cdef void *base = NULL
        cdef MPI_Aint size = 0
        win_get_base(self.ob_mpi, &base)
        win_get_size(self.ob_mpi, &size)
        PyBuffer_FillInfo(view, self, base, size, 0, flags)

    # Communication Operations
    # ------------------------

    def Put(
        self,
        origin: BufSpec,
        int target_rank: int,
        target: TargetSpec | None = None,
    ) -> None:
        """
        Put data into a memory window on a remote process.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_put(origin, target_rank, target)
        with nogil: CHKERR( MPI_Put_c(
            msg.oaddr, msg.ocount, msg.otype,
            target_rank,
            msg.tdisp, msg.tcount, msg.ttype,
            self.ob_mpi) )

    def Get(
        self,
        origin: BufSpec,
        int target_rank: int,
        target: TargetSpec | None = None,
    ) -> None:
        """
        Get data from a memory window on a remote process.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_get(origin, target_rank, target)
        with nogil: CHKERR( MPI_Get_c(
            msg.oaddr, msg.ocount, msg.otype,
            target_rank,
            msg.tdisp, msg.tcount, msg.ttype,
            self.ob_mpi) )

    def Accumulate(
        self,
        origin: BufSpec,
        int target_rank: int,
        target: TargetSpec | None = None,
        Op op: Op = SUM,
    ) -> None:
        """
        Accumulate data into the target process.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_acc(origin, target_rank, target)
        with nogil: CHKERR( MPI_Accumulate_c(
            msg.oaddr, msg.ocount, msg.otype,
            target_rank,
            msg.tdisp, msg.tcount, msg.ttype,
            op.ob_mpi, self.ob_mpi) )

    def Get_accumulate(
        self,
        origin: BufSpec,
        result: BufSpec,
        int target_rank: int,
        target: TargetSpec | None = None,
        Op op: Op = SUM,
    ) -> None:
        """
        Fetch-and-accumulate data into the target process.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_get_acc(origin, result, target_rank, target)
        with nogil: CHKERR( MPI_Get_accumulate_c(
            msg.oaddr, msg.ocount, msg.otype,
            msg.raddr, msg.rcount, msg.rtype,
            target_rank,
            msg.tdisp, msg.tcount, msg.ttype,
            op.ob_mpi, self.ob_mpi) )

    def Fetch_and_op(
        self,
        origin: BufSpec,
        result: BufSpec,
        int target_rank: int,
        Aint target_disp: int = 0,
        Op op: Op = SUM,
    ) -> None:
        """
        Perform one-sided read-modify-write.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_fetch_op(origin, result, target_rank, target_disp)
        with nogil: CHKERR( MPI_Fetch_and_op(
                msg.oaddr, msg.raddr, msg.ttype,
                target_rank, target_disp,
                op.ob_mpi, self.ob_mpi) )

    def Compare_and_swap(
        self,
        origin: BufSpec,
        compare: BufSpec,
        result: BufSpec,
        int target_rank: int,
        Aint target_disp: int = 0,
    ) -> None:
        """
        Perform one-sided atomic compare-and-swap.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_cmp_swap(origin, compare, result, target_rank, target_disp)
        with nogil: CHKERR( MPI_Compare_and_swap(
                msg.oaddr, msg.caddr, msg.raddr, msg.ttype,
                target_rank, target_disp, self.ob_mpi) )

    # Request-based RMA Communication Operations
    # ------------------------------------------

    def Rput(
        self,
        origin: BufSpec,
        int target_rank: int,
        target: TargetSpec | None = None,
    ) -> Request:
        """
        Put data into a memory window on a remote process.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_put(origin, target_rank, target)
        cdef Request request = <Request>New(Request)
        with nogil: CHKERR( MPI_Rput_c(
            msg.oaddr, msg.ocount, msg.otype,
            target_rank,
            msg.tdisp, msg.tcount, msg.ttype,
            self.ob_mpi, &request.ob_mpi) )
        request.ob_buf = msg
        return request

    def Rget(
        self,
        origin: BufSpec,
        int target_rank: int,
        target: TargetSpec | None = None,
    ) -> Request:
        """
        Get data from a memory window on a remote process.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_get(origin, target_rank, target)
        cdef Request request = <Request>New(Request)
        with nogil: CHKERR( MPI_Rget_c(
            msg.oaddr, msg.ocount, msg.otype,
            target_rank,
            msg.tdisp, msg.tcount, msg.ttype,
            self.ob_mpi, &request.ob_mpi) )
        request.ob_buf = msg
        return request

    def Raccumulate(
        self,
        origin: BufSpec,
        int target_rank: int,
        target: TargetSpec | None = None,
        Op op: Op = SUM,
    ) -> Request:
        """
        Fetch-and-accumulate data into the target process.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_acc(origin, target_rank, target)
        cdef Request request = <Request>New(Request)
        with nogil: CHKERR( MPI_Raccumulate_c(
            msg.oaddr, msg.ocount, msg.otype,
            target_rank,
            msg.tdisp, msg.tcount, msg.ttype,
            op.ob_mpi, self.ob_mpi, &request.ob_mpi) )
        request.ob_buf = msg
        return request

    def Rget_accumulate(
        self,
        origin: BufSpec,
        result: BufSpec,
        int target_rank: int,
        target: TargetSpec | None = None,
        Op op: Op = SUM,
    ) -> Request:
        """
        Accumulate data into the target process using remote memory access.
        """
        cdef _p_msg_rma msg = message_rma()
        msg.for_get_acc(origin, result, target_rank, target)
        cdef Request request = <Request>New(Request)
        with nogil: CHKERR( MPI_Rget_accumulate_c(
            msg.oaddr, msg.ocount, msg.otype,
            msg.raddr, msg.rcount, msg.rtype,
            target_rank,
            msg.tdisp, msg.tcount, msg.ttype,
            op.ob_mpi, self.ob_mpi, &request.ob_mpi) )
        request.ob_buf = msg
        return request

    # Synchronization Calls
    # ---------------------

    # Fence
    # -----

    def Fence(self, int assertion: int = 0) -> None:
        """
        Perform an MPI fence synchronization on a window.
        """
        with nogil: CHKERR( MPI_Win_fence(assertion, self.ob_mpi) )

    # General Active Target Synchronization
    # -------------------------------------

    def Start(self, Group group: Group, int assertion: int = 0) -> None:
        """
        Start an RMA access epoch for MPI.
        """
        with nogil: CHKERR( MPI_Win_start(
            group.ob_mpi, assertion, self.ob_mpi) )

    def Complete(self) -> None:
        """
        Complete an RMA operation begun after an `Start`.
        """
        with nogil: CHKERR( MPI_Win_complete(self.ob_mpi) )

    def Post(self, Group group: Group, int assertion: int = 0) -> None:
        """
        Start an RMA exposure epoch.
        """
        with nogil: CHKERR( MPI_Win_post(
            group.ob_mpi, assertion, self.ob_mpi) )

    def Wait(self) -> Literal[True]:
        """
        Complete an RMA exposure epoch begun with `Post`.
        """
        with nogil: CHKERR( MPI_Win_wait(self.ob_mpi) )
        return True

    def Test(self) -> bool:
        """
        Test whether an RMA exposure epoch has completed.
        """
        cdef int flag = 0
        with nogil: CHKERR( MPI_Win_test(self.ob_mpi, &flag) )
        return <bint>flag

    # Lock
    # ----

    def Lock(
        self,
        int rank: int,
        int lock_type: int = LOCK_EXCLUSIVE,
        int assertion: int = 0,
    ) -> None:
        """
        Begin an RMA access epoch at the target process.
        """
        with nogil: CHKERR( MPI_Win_lock(
            lock_type, rank, assertion, self.ob_mpi) )

    def Unlock(self, int rank: int) -> None:
        """
        Complete an RMA access epoch at the target process.
        """
        with nogil: CHKERR( MPI_Win_unlock(rank, self.ob_mpi) )

    def Lock_all(self, int assertion: int = 0) -> None:
        """
        Begin an RMA access epoch at all processes.
        """
        with nogil: CHKERR( MPI_Win_lock_all(assertion, self.ob_mpi) )

    def Unlock_all(self) -> None:
        """
        Complete an RMA access epoch at all processes.
        """
        with nogil: CHKERR( MPI_Win_unlock_all(self.ob_mpi) )

    # Flush and Sync
    # --------------

    def Flush(self, int rank: int) -> None:
        """
        Complete all outstanding RMA operations at a target.
        """
        with nogil: CHKERR( MPI_Win_flush(rank, self.ob_mpi) )

    def Flush_all(self) -> None:
        """
        Complete all outstanding RMA operations at all targets.
        """
        with nogil: CHKERR( MPI_Win_flush_all(self.ob_mpi) )

    def Flush_local(self, int rank: int) -> None:
        """
        Complete locally all outstanding RMA operations at a target.
        """
        with nogil: CHKERR( MPI_Win_flush_local(rank, self.ob_mpi) )

    def Flush_local_all(self) -> None:
        """
        Complete locally all outstanding RMA operations at all targets.
        """
        with nogil: CHKERR( MPI_Win_flush_local_all(self.ob_mpi) )

    def Sync(self) -> None:
        """
        Synchronize public and private copies of the window.
        """
        with nogil: CHKERR( MPI_Win_sync(self.ob_mpi) )

    # Error Handling
    # --------------

    @classmethod
    def Create_errhandler(
        cls,
        errhandler_fn: Callable[[Win, int], None],
    ) -> Errhandler:
        """
        Create a new error handler for windows.
        """
        cdef Errhandler errhandler = <Errhandler>New(Errhandler)
        cdef MPI_Win_errhandler_function *fn = NULL
        cdef int index = errhdl_new(errhandler_fn, &fn)
        try:
            CHKERR( MPI_Win_create_errhandler(fn, &errhandler.ob_mpi) )
        except:                     # ~> uncovered  # noqa
            errhdl_del(&index, fn)  # ~> uncovered
            raise                   # ~> uncovered
        return errhandler

    def Get_errhandler(self) -> Errhandler:
        """
        Get the error handler for a window.
        """
        cdef Errhandler errhandler = <Errhandler>New(Errhandler)
        CHKERR( MPI_Win_get_errhandler(self.ob_mpi, &errhandler.ob_mpi) )
        return errhandler

    def Set_errhandler(self, Errhandler errhandler: Errhandler) -> None:
        """
        Set the error handler for a window.
        """
        CHKERR( MPI_Win_set_errhandler(self.ob_mpi, errhandler.ob_mpi) )

    def Call_errhandler(self, int errorcode: int) -> None:
        """
        Call the error handler installed on a window.
        """
        CHKERR( MPI_Win_call_errhandler(self.ob_mpi, errorcode) )

    # Naming Objects
    # --------------

    def Get_name(self) -> str:
        """
        Get the print name for this window.
        """
        cdef char name[MPI_MAX_OBJECT_NAME+1]
        cdef int nlen = 0
        CHKERR( MPI_Win_get_name(self.ob_mpi, name, &nlen) )
        return tompistr(name, nlen)

    def Set_name(self, name: str) -> None:
        """
        Set the print name for this window.
        """
        cdef char *cname = NULL
        name = asmpistr(name, &cname)
        CHKERR( MPI_Win_set_name(self.ob_mpi, cname) )

    property name:
        """Print name."""
        def __get__(self) -> str:
            return self.Get_name()

        def __set__(self, value: str):
            self.Set_name(value)

    # Fortran Handle
    # --------------

    def py2f(self) -> int:
        """
        """
        return MPI_Win_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg: int) -> Win:
        """
        """
        return fromhandle(MPI_Win_f2c(arg))


cdef Win __WIN_NULL__ = def_Win( MPI_WIN_NULL , "WIN_NULL" )


# Predefined window handles
# -------------------------

WIN_NULL = __WIN_NULL__  #: Null window handle
