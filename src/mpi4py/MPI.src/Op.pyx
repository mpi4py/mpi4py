cdef class Op:
    """
    Reduction operation.
    """

    def __cinit__(self, Op op: Op | None = None):
        cinit(self, op)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Op): return NotImplemented
        return richcmp(self, other, op)

    def __bool__(self) -> bool:
        return nonnull(self)

    def __reduce__(self) -> str | tuple[Any, ...]:
        return reduce_Op(self)

    def __call__(self, x: Any, y: Any) -> Any:
        cdef int index = op_user_id_get(self)
        return op_call(self.ob_mpi, index, x, y)

    property handle:
        """MPI handle."""
        def __get__(self) -> int:
            return tohandle(self)

    @classmethod
    def fromhandle(cls, handle: int) -> Op:
        """
        Create object from MPI handle.
        """
        return fromhandle(<MPI_Op> <Py_uintptr_t> handle)

    def free(self) -> None:
        """
        Call `Free` if not null or predefined.
        """
        safefree(self)

    # User-Defined Reduction Operations
    # ---------------------------------

    @classmethod
    def Create(
        cls,
        function: Callable[[Buffer, Buffer, Datatype], None],
        bint commute: bool = False,
    ) -> Self:
        """
        Create a user-defined reduction operation.
        """
        cdef Op self = <Op>New(cls)
        cdef MPI_User_function   *fn_i = NULL
        cdef MPI_User_function_c *fn_c = NULL
        op_user_new(self, function, &fn_i, &fn_c)
        try:
            try:
                CHKERR( MPI_Op_create_c(fn_c, commute, &self.ob_mpi) )
            except NotImplementedError:                               # ~> legacy
                CHKERR( MPI_Op_create(fn_i, commute, &self.ob_mpi) )  # ~> legacy
        except:                # ~> uncovered  # noqa
            op_user_del(self)  # ~> uncovered
            raise              # ~> uncovered
        return self

    def Free(self) -> None:
        """
        Free a user-defined reduction operation.
        """
        cdef MPI_Op save = self.ob_mpi
        CHKERR( MPI_Op_free(&self.ob_mpi) )
        if constobj(self): self.ob_mpi = save
        op_user_del(self)

    # Process-local reduction
    # -----------------------

    def Is_commutative(self) -> bool:
        """
        Query reduction operations for their commutativity.
        """
        cdef int flag = 0
        CHKERR( MPI_Op_commutative(self.ob_mpi, &flag) )
        return <bint>flag

    property is_commutative:
        """Is a commutative operation."""
        def __get__(self) -> bool:
            return self.Is_commutative()

    def Reduce_local(self, inbuf: BufSpec, inoutbuf: BufSpec) -> None:
        """
        Apply a reduction operation to local data.
        """
        # get *in* and *inout* buffers
        cdef _p_msg_cco m = message_cco()
        m.for_cro_recv(inoutbuf, 0)
        m.for_cro_send(inbuf, 0)
        m.chk_cro_args()
        # do local reduction
        with nogil: CHKERR( MPI_Reduce_local_c(
            m.sbuf, m.rbuf, m.rcount, m.rtype, self.ob_mpi) )

    property is_predefined:
        """Is a predefined operation."""
        def __get__(self) -> bool:
            cdef MPI_Op op = self.ob_mpi
            return (
                op == MPI_OP_NULL or
                op == MPI_MAX or
                op == MPI_MIN or
                op == MPI_SUM or
                op == MPI_PROD or
                op == MPI_LAND or
                op == MPI_BAND or
                op == MPI_LOR or
                op == MPI_BOR or
                op == MPI_LXOR or
                op == MPI_BXOR or
                op == MPI_MAXLOC or
                op == MPI_MINLOC or
                op == MPI_REPLACE or
                op == MPI_NO_OP
            )

    # Fortran Handle
    # --------------

    def py2f(self) -> int:
        """
        """
        return MPI_Op_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg: int) -> Op:
        """
        """
        return fromhandle(MPI_Op_f2c(arg))


cdef Op __OP_NULL__ = def_Op( MPI_OP_NULL , "OP_NULL" )
cdef Op __MAX__     = def_Op( MPI_MAX     , "MAX"     )
cdef Op __MIN__     = def_Op( MPI_MIN     , "MIN"     )
cdef Op __SUM__     = def_Op( MPI_SUM     , "SUM"     )
cdef Op __PROD__    = def_Op( MPI_PROD    , "PROD"    )
cdef Op __LAND__    = def_Op( MPI_LAND    , "LAND"    )
cdef Op __BAND__    = def_Op( MPI_BAND    , "BAND"    )
cdef Op __LOR__     = def_Op( MPI_LOR     , "LOR"     )
cdef Op __BOR__     = def_Op( MPI_BOR     , "BOR"     )
cdef Op __LXOR__    = def_Op( MPI_LXOR    , "LXOR"    )
cdef Op __BXOR__    = def_Op( MPI_BXOR    , "BXOR"    )
cdef Op __MAXLOC__  = def_Op( MPI_MAXLOC  , "MAXLOC"  )
cdef Op __MINLOC__  = def_Op( MPI_MINLOC  , "MINLOC"  )
cdef Op __REPLACE__ = def_Op( MPI_REPLACE , "REPLACE" )
cdef Op __NO_OP__   = def_Op( MPI_NO_OP   , "NO_OP"   )


# Predefined operation handles
# ----------------------------

OP_NULL = __OP_NULL__  #: Null
MAX     = __MAX__      #: Maximum
MIN     = __MIN__      #: Minimum
SUM     = __SUM__      #: Sum
PROD    = __PROD__     #: Product
LAND    = __LAND__     #: Logical and
BAND    = __BAND__     #: Bit-wise and
LOR     = __LOR__      #: Logical or
BOR     = __BOR__      #: Bit-wise or
LXOR    = __LXOR__     #: Logical xor
BXOR    = __BXOR__     #: Bit-wise xor
MAXLOC  = __MAXLOC__   #: Maximum and location
MINLOC  = __MINLOC__   #: Minimum and location
REPLACE = __REPLACE__  #: Replace (for RMA)
NO_OP   = __NO_OP__    #: No-op   (for RMA)
