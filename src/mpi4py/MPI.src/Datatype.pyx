# Storage order for arrays
# ------------------------
ORDER_C       = MPI_ORDER_C        #: C order (a.k.a. row major)
ORDER_FORTRAN = MPI_ORDER_FORTRAN  #: Fortran order (a.k.a. column major)
ORDER_F       = MPI_ORDER_FORTRAN  #: Convenience alias for ORDER_FORTRAN


# Type classes for Fortran datatype matching
# ------------------------------------------
TYPECLASS_INTEGER = MPI_TYPECLASS_INTEGER
TYPECLASS_REAL    = MPI_TYPECLASS_REAL
TYPECLASS_COMPLEX = MPI_TYPECLASS_COMPLEX


# Type of distributions (HPF-like arrays)
# ---------------------------------------
DISTRIBUTE_NONE      = MPI_DISTRIBUTE_NONE       #: Dimension not distributed
DISTRIBUTE_BLOCK     = MPI_DISTRIBUTE_BLOCK      #: Block distribution
DISTRIBUTE_CYCLIC    = MPI_DISTRIBUTE_CYCLIC     #: Cyclic distribution
DISTRIBUTE_DFLT_DARG = MPI_DISTRIBUTE_DFLT_DARG  #: Default distribution


# Combiner values for datatype decoding
# -------------------------------------
COMBINER_NAMED            = MPI_COMBINER_NAMED
COMBINER_DUP              = MPI_COMBINER_DUP
COMBINER_CONTIGUOUS       = MPI_COMBINER_CONTIGUOUS
COMBINER_VECTOR           = MPI_COMBINER_VECTOR
COMBINER_HVECTOR          = MPI_COMBINER_HVECTOR
COMBINER_INDEXED          = MPI_COMBINER_INDEXED
COMBINER_HINDEXED         = MPI_COMBINER_HINDEXED
COMBINER_INDEXED_BLOCK    = MPI_COMBINER_INDEXED_BLOCK
COMBINER_HINDEXED_BLOCK   = MPI_COMBINER_HINDEXED_BLOCK
COMBINER_STRUCT           = MPI_COMBINER_STRUCT
COMBINER_SUBARRAY         = MPI_COMBINER_SUBARRAY
COMBINER_DARRAY           = MPI_COMBINER_DARRAY
COMBINER_RESIZED          = MPI_COMBINER_RESIZED
COMBINER_VALUE_INDEX      = MPI_COMBINER_VALUE_INDEX
COMBINER_F90_INTEGER      = MPI_COMBINER_F90_INTEGER
COMBINER_F90_REAL         = MPI_COMBINER_F90_REAL
COMBINER_F90_COMPLEX      = MPI_COMBINER_F90_COMPLEX


cdef class Datatype:
    """
    Datatype object.
    """

    def __cinit__(self, Datatype datatype: Datatype | None = None):
        cinit(self, datatype)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Datatype): return NotImplemented
        return richcmp(self, other, op)

    def __bool__(self) -> bool:
        return nonnull(self)

    def __reduce__(self) -> str | tuple[Any, ...]:
        return reduce_Datatype(self)

    property handle:
        """MPI handle."""
        def __get__(self) -> int:
            return tohandle(self)

    @classmethod
    def fromhandle(cls, handle: int) -> Datatype:
        """
        Create object from MPI handle.
        """
        return fromhandle(<MPI_Datatype> <Py_uintptr_t> handle)

    def free(self) -> None:
        """
        Call `Free` if not null or predefined.
        """
        safefree(self)

    # Datatype Accessors
    # ------------------

    def Get_size(self) -> int:
        """
        Return the number of bytes occupied by entries in the datatype.
        """
        cdef MPI_Count size = 0
        CHKERR( MPI_Type_size_c(self.ob_mpi, &size) )
        return size

    property size:
        """Size (in bytes)."""
        def __get__(self) -> int:
            cdef MPI_Count size = 0
            CHKERR( MPI_Type_size_c(self.ob_mpi, &size) )
            return size

    def Get_extent(self) -> tuple[int, int]:
        """
        Return lower bound and extent of datatype.
        """
        cdef MPI_Count lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent_c(self.ob_mpi, &lb, &extent) )
        return (lb, extent)

    property extent:
        """Extent."""
        def __get__(self) -> int:
            cdef MPI_Count lb = 0, extent = 0
            CHKERR( MPI_Type_get_extent_c(self.ob_mpi, &lb, &extent) )
            return extent

    property lb:
        """Lower bound."""
        def __get__(self) -> int:
            cdef MPI_Count lb = 0, extent = 0
            CHKERR( MPI_Type_get_extent_c(self.ob_mpi, &lb, &extent) )
            return lb

    property ub:
        """Upper bound."""
        def __get__(self) -> int:
            cdef MPI_Count lb = 0, extent = 0
            CHKERR( MPI_Type_get_extent_c(self.ob_mpi, &lb, &extent) )
            return lb + extent

    # Datatype Constructors
    # ---------------------

    def Dup(self) -> Self:
        """
        Duplicate a datatype.
        """
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_dup(self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    Create_dup = Dup  #: convenience alias

    def Create_contiguous(self, Count count: int) -> Self:
        """
        Create a contiguous datatype.
        """
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_contiguous_c(
            count,
            self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    def Create_vector(
        self,
        Count count: int,
        Count blocklength: int,
        Count stride: int,
    ) -> Self:
        """
        Create a vector (strided) datatype.
        """
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_vector_c(
            count, blocklength, stride,
            self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    def Create_hvector(
        self,
        Count count: int,
        Count blocklength: int,
        Count stride: int,
    ) -> Self:
        """
        Create a vector (strided) datatype with stride in bytes.
        """
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_create_hvector_c(
            count, blocklength, stride,
            self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    def Create_indexed(
        self,
        blocklengths: Sequence[int],
        displacements: Sequence[int],
    ) -> Self:
        """
        Create an indexed datatype.
        """
        cdef MPI_Count count = 0, *iblen = NULL, *idisp = NULL
        blocklengths  = getarray(blocklengths,  &count, &iblen)
        displacements = chkarray(displacements,  count, &idisp)
        #
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_indexed_c(
            count, iblen, idisp,
            self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    def Create_hindexed(
        self,
        blocklengths: Sequence[int],
        displacements: Sequence[int],
    ) -> Self:
        """
        Create an indexed datatype.

        .. note:: Displacements are measured in bytes.
        """
        cdef MPI_Count count = 0, *iblen = NULL, *idisp = NULL
        blocklengths = getarray(blocklengths, &count, &iblen)
        displacements = chkarray(displacements, count, &idisp)
        #
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_create_hindexed_c(
            count, iblen, idisp,
            self.ob_mpi,
            &datatype.ob_mpi) )
        return datatype

    def Create_indexed_block(
        self,
        Count blocklength: int,
        displacements: Sequence[int],
    ) -> Self:
        """
        Create an indexed datatype with constant-sized blocks.
        """
        cdef Count count = 0, *idisp = NULL
        displacements = getarray(displacements, &count, &idisp)
        #
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_create_indexed_block_c(
            count, blocklength, idisp,
            self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    def Create_hindexed_block(
        self,
        Count blocklength: int,
        displacements: Sequence[int],
    ) -> Self:
        """
        Create an indexed datatype with constant-sized blocks.

        .. note:: Displacements are measured in bytes.
        """
        cdef MPI_Count count = 0, *idisp = NULL
        displacements = getarray(displacements, &count, &idisp)
        #
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_create_hindexed_block_c(
            count, blocklength, idisp,
            self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    @classmethod
    def Create_struct(
        cls,
        blocklengths: Sequence[int],
        displacements: Sequence[int],
        datatypes: Sequence[Datatype],
    ) -> Self:
        """
        Create a general composite (struct) datatype.

        .. note:: Displacements are measured in bytes.
        """
        cdef MPI_Count count = 0, *iblen = NULL, *idisp = NULL
        cdef MPI_Datatype *ptype = NULL
        blocklengths = getarray(blocklengths, &count, &iblen)
        displacements = chkarray(displacements, count, &idisp)
        datatypes = asarray_Datatype(datatypes, count, &ptype)
        #
        cdef Datatype datatype = <Datatype>New(cls)
        CHKERR( MPI_Type_create_struct_c(
            count, iblen, idisp, ptype,
            &datatype.ob_mpi) )
        return datatype

    # Subarray Datatype Constructor
    # -----------------------------

    def Create_subarray(
        self,
        sizes: Sequence[int],
        subsizes: Sequence[int],
        starts: Sequence[int],
        int order: int = ORDER_C,
    ) -> Self:
        """
        Create a datatype for a subarray of a multidimensional array.
        """
        cdef int ndims = 0
        cdef MPI_Count *isizes = NULL
        cdef MPI_Count *isubsizes = NULL
        cdef MPI_Count *istarts = NULL
        sizes    = getarray(sizes,   &ndims, &isizes   )
        subsizes = chkarray(subsizes, ndims, &isubsizes)
        starts   = chkarray(starts,   ndims, &istarts  )
        #
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_create_subarray_c(
            ndims, isizes, isubsizes, istarts, order,
            self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    # Distributed Array Datatype Constructor
    # --------------------------------------

    def Create_darray(
        self,
        int size: int,
        int rank: int,
        gsizes: Sequence[int],
        distribs: Sequence[int],
        dargs: Sequence[int],
        psizes: Sequence[int],
        int order: int = ORDER_C,
    ) -> Self:
        """
        Create a datatype for a distributed array on Cartesian process grids.
        """
        cdef int ndims = 0
        cdef MPI_Count *igsizes = NULL
        cdef int *idistribs = NULL, *idargs = NULL, *ipsizes = NULL
        gsizes   = getarray(gsizes,  &ndims, &igsizes   )
        distribs = chkarray(distribs, ndims, &idistribs )
        dargs    = chkarray(dargs,    ndims, &idargs    )
        psizes   = chkarray(psizes,   ndims, &ipsizes   )
        #
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_create_darray_c(
            size, rank, ndims, igsizes,
            idistribs, idargs, ipsizes, order,
            self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    # Pair Datatype
    # -------------

    @classmethod
    def Get_value_index(
        cls,
        Datatype value: Datatype,
        Datatype index: Datatype,
    ) -> Self:
        """
        Return a predefined pair datatype.
        """
        cdef Datatype datatype = <Datatype>New(cls)
        CHKERR( MPI_Type_get_value_index(
            value.ob_mpi, index.ob_mpi, &datatype.ob_mpi) )
        return datatype

    # Parametrized and size-specific Fortran Datatypes
    # ------------------------------------------------

    @classmethod
    def Create_f90_integer(cls, int r: int) -> Self:
        """
        Return a bounded integer datatype.
        """
        cdef Datatype datatype = <Datatype>New(cls)
        CHKERR( MPI_Type_create_f90_integer(r, &datatype.ob_mpi) )
        return datatype

    @classmethod
    def Create_f90_real(cls, int p: int, int r: int) -> Self:
        """
        Return a bounded real datatype.
        """
        cdef Datatype datatype = <Datatype>New(cls)
        CHKERR( MPI_Type_create_f90_real(p, r, &datatype.ob_mpi) )
        return datatype

    @classmethod
    def Create_f90_complex(cls, int p: int, int r: int) -> Self:
        """
        Return a bounded complex datatype.
        """
        cdef Datatype datatype = <Datatype>New(cls)
        CHKERR( MPI_Type_create_f90_complex(p, r, &datatype.ob_mpi) )
        return datatype

    @classmethod
    def Match_size(cls, int typeclass: int, int size: int) -> Self:
        """
        Find a datatype matching a specified size in bytes.
        """
        cdef Datatype datatype = <Datatype>New(cls)
        CHKERR( MPI_Type_match_size(typeclass, size, &datatype.ob_mpi) )
        return datatype

    # Use of Derived Datatypes
    # ------------------------

    def Commit(self) -> Self:
        """
        Commit the datatype.
        """
        CHKERR( MPI_Type_commit(&self.ob_mpi) )
        return self

    def Free(self) -> None:
        """
        Free the datatype.
        """
        cdef MPI_Datatype save = self.ob_mpi
        CHKERR( MPI_Type_free(&self.ob_mpi) )
        if constobj(self): self.ob_mpi = save

    # Datatype Resizing
    # -----------------

    def Create_resized(self, Count lb: int, Count extent: int) -> Self:
        """
        Create a datatype with a new lower bound and extent.
        """
        cdef Datatype datatype = <Datatype>New(type(self))
        CHKERR( MPI_Type_create_resized_c(
            self.ob_mpi, lb, extent, &datatype.ob_mpi) )
        return datatype

    Resized = Create_resized  #: compatibility alias

    def Get_true_extent(self) -> tuple[int, int]:
        """
        Return the true lower bound and extent of a datatype.
        """
        cdef MPI_Count lb = 0, extent = 0
        CHKERR( MPI_Type_get_true_extent_c(
            self.ob_mpi, &lb, &extent) )
        return (lb, extent)

    property true_extent:
        """True extent."""
        def __get__(self) -> int:
            cdef MPI_Count lb = 0, extent = 0
            CHKERR( MPI_Type_get_true_extent_c(
                self.ob_mpi, &lb, &extent) )
            return extent

    property true_lb:
        """True lower bound."""
        def __get__(self) -> int:
            cdef MPI_Count lb = 0, extent = 0
            CHKERR( MPI_Type_get_true_extent_c(
                self.ob_mpi, &lb, &extent) )
            return lb

    property true_ub:
        """True upper bound."""
        def __get__(self) -> int:
            cdef MPI_Count lb = 0, extent = 0
            CHKERR( MPI_Type_get_true_extent_c(
                self.ob_mpi, &lb, &extent) )
            return lb + extent

    # Decoding a Datatype
    # -------------------

    def Get_envelope(self) -> tuple[int, int, int, int, int]:
        """
        Return the number of input arguments used to create a datatype.
        """
        cdef int combiner = MPI_UNDEFINED
        cdef MPI_Count ni = 0, na = 0, nc = 0, nd = 0
        CHKERR( MPI_Type_get_envelope_c(
            self.ob_mpi, &ni, &na, &nc, &nd, &combiner) )
        return (ni, na, nc, nd, combiner)

    property envelope:
        """Envelope."""
        def __get__(self) -> tuple[int, int, int, int, int]:
            return self.Get_envelope()

    def Get_contents(self) -> \
            tuple[list[int], list[int], list[int], list[Datatype]]:
        """
        Return the input arguments used to create a datatype.
        """
        cdef int combiner = MPI_UNDEFINED
        cdef MPI_Count ni = 0, na = 0, nc = 0, nd = 0
        CHKERR( MPI_Type_get_envelope_c(
            self.ob_mpi, &ni, &na, &nc, &nd, &combiner) )
        cdef int *i = NULL
        cdef MPI_Aint *a = NULL
        cdef MPI_Count *c = NULL
        cdef MPI_Datatype *d = NULL
        cdef unused1 = allocate(ni, sizeof(int), &i)
        cdef unused2 = allocate(na, sizeof(MPI_Aint), &a)
        cdef unused3 = allocate(nc, sizeof(MPI_Count), &c)
        cdef unused4 = allocate(nd, sizeof(MPI_Datatype), &d)
        CHKERR( MPI_Type_get_contents_c(
            self.ob_mpi, ni, na, nc, nd, i, a, c, d) )
        cdef object integers  = [i[k] for k in range(ni)]
        cdef object addresses = [a[k] for k in range(na)]
        cdef object counts    = [c[k] for k in range(nc)]
        cdef object datatypes = [ref_Datatype(d[k]) for k in range(nd)]
        return (integers, addresses, counts, datatypes)

    property contents:
        """Contents."""
        def __get__(self) -> \
                tuple[list[int], list[int], list[int], list[Datatype]]:
            return self.Get_contents()

    def decode(self) -> tuple[Datatype, str, dict[str, Any]]:
        """
        Convenience method for decoding a datatype.
        """
        return datatype_decode(self, mark=False)

    property combiner:
        """Combiner."""
        def __get__(self) -> int:
            cdef int combiner = self.Get_envelope()[-1]
            return combiner

    property is_named:
        """Is a named datatype."""
        def __get__(self) -> bool:
            cdef int combiner = self.Get_envelope()[-1]
            return combiner == MPI_COMBINER_NAMED

    property is_predefined:
        """Is a predefined datatype."""
        def __get__(self) -> bool:
            if self.ob_mpi == MPI_DATATYPE_NULL: return True
            cdef int combiner = self.Get_envelope()[-1]
            return (combiner == MPI_COMBINER_NAMED or
                    combiner == MPI_COMBINER_VALUE_INDEX or
                    combiner == MPI_COMBINER_F90_INTEGER or
                    combiner == MPI_COMBINER_F90_REAL or
                    combiner == MPI_COMBINER_F90_COMPLEX)

    # Pack and Unpack
    # ---------------

    def Pack(
        self,
        inbuf: BufSpec,
        outbuf: BufSpec,
        Count position: int,
        Comm comm: Comm,
    ) -> int:
        """
        Pack into contiguous memory according to datatype.
        """
        cdef MPI_Count lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent_c(self.ob_mpi, &lb, &extent) )
        #
        cdef void *ibptr = NULL, *obptr = NULL
        cdef MPI_Aint iblen = 0, oblen = 0
        cdef unused1 = asbuffer_r(inbuf,  &ibptr, &iblen)
        cdef unused2 = asbuffer_w(outbuf, &obptr, &oblen)
        cdef MPI_Count icount = iblen // extent
        cdef MPI_Count ocount = oblen
        #
        CHKERR( MPI_Pack_c(
            ibptr, icount, self.ob_mpi,
            obptr, ocount, &position,
            comm.ob_mpi) )
        return position

    def Unpack(
        self,
        inbuf: BufSpec,
        Count position: int,
        outbuf: BufSpec,
        Comm comm: Comm,
    ) -> int:
        """
        Unpack from contiguous memory according to datatype.
        """
        cdef MPI_Count lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent_c(self.ob_mpi, &lb, &extent) )
        #
        cdef void *ibptr = NULL, *obptr = NULL
        cdef MPI_Aint iblen = 0, oblen = 0
        cdef unused1 = asbuffer_r(inbuf,  &ibptr, &iblen)
        cdef unused2 = asbuffer_w(outbuf, &obptr, &oblen)
        cdef MPI_Count icount = iblen
        cdef MPI_Count ocount = oblen // extent
        #
        CHKERR( MPI_Unpack_c(
            ibptr, icount, &position,
            obptr, ocount, self.ob_mpi,
            comm.ob_mpi) )
        return position

    def Pack_size(
        self,
        Count count: int,
        Comm comm: Comm,
    ) -> int:
        """
        Determine the amount of space needed to pack a message.

        .. note:: Returns an upper bound measured in bytes.
        """
        cdef MPI_Count size = 0
        CHKERR( MPI_Pack_size_c(
            count, self.ob_mpi,
            comm.ob_mpi, &size) )
        return size

    # Canonical Pack and Unpack
    # -------------------------

    def Pack_external(
        self,
        datarep: str,
        inbuf: BufSpec,
        outbuf: BufSpec,
        Count position: int,
    ) -> int:
        """
        Pack into contiguous memory according to datatype.

        Uses the portable data representation **external32**.
        """
        cdef char *cdatarep = NULL
        datarep = asmpistr(datarep, &cdatarep)
        cdef MPI_Count lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent_c(self.ob_mpi, &lb, &extent) )
        #
        cdef void *ibptr = NULL, *obptr = NULL
        cdef MPI_Aint iblen = 0, oblen = 0
        cdef unused1 = asbuffer_r(inbuf,  &ibptr, &iblen)
        cdef unused2 = asbuffer_w(outbuf, &obptr, &oblen)
        cdef MPI_Count icount = iblen // extent
        cdef MPI_Count ocount = oblen
        #
        CHKERR( MPI_Pack_external_c(
            cdatarep,
            ibptr, icount, self.ob_mpi,
            obptr, ocount, &position) )
        return position

    def Unpack_external(
        self,
        datarep: str,
        inbuf: BufSpec,
        Count position: int,
        outbuf: BufSpec,
    ) -> int:
        """
        Unpack from contiguous memory according to datatype.

        Uses the portable data representation **external32**.
        """
        cdef char *cdatarep = NULL
        datarep = asmpistr(datarep, &cdatarep)
        cdef MPI_Count lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent_c(self.ob_mpi, &lb, &extent) )
        #
        cdef void *ibptr = NULL, *obptr = NULL
        cdef MPI_Aint iblen = 0, oblen = 0
        cdef unused1 = asbuffer_r(inbuf,  &ibptr, &iblen)
        cdef unused2 = asbuffer_w(outbuf, &obptr, &oblen)
        cdef MPI_Count icount = iblen
        cdef MPI_Count ocount = oblen // extent
        #
        CHKERR( MPI_Unpack_external_c(
            cdatarep,
            ibptr, icount, &position,
            obptr, ocount, self.ob_mpi) )
        return position

    def Pack_external_size(
        self,
        datarep: str,
        Count count: int,
    ) -> int:
        """
        Determine the amount of space needed to pack a message.

        Uses the portable data representation **external32**.

        .. note:: Returns an upper bound measured in bytes.
        """
        cdef char *cdatarep = NULL
        cdef MPI_Count size = 0
        datarep = asmpistr(datarep, &cdatarep)
        CHKERR( MPI_Pack_external_size_c(
            cdatarep, count, self.ob_mpi, &size) )
        return size

    # Attributes
    # ----------

    def Get_attr(self, int keyval: int) -> int | Any | None:
        """
        Retrieve attribute value by key.
        """
        cdef void *attrval = NULL
        cdef int flag = 0
        CHKERR( MPI_Type_get_attr(self.ob_mpi, keyval, &attrval, &flag) )
        if not flag: return None
        if attrval == NULL: return 0
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
        copy_fn: Callable[[Datatype, int, Any], Any] | None = None,
        delete_fn: Callable[[Datatype, int, Any], None] | None = None,
        nopython: bool = False,
    ) -> int:
        """
        Create a new attribute key for datatypes.
        """
        cdef int keyval = MPI_KEYVAL_INVALID
        cdef MPI_Type_copy_attr_function *_copy = PyMPI_attr_copy_fn
        cdef MPI_Type_delete_attr_function *_del = PyMPI_attr_delete_fn
        cdef _p_keyval state = _p_keyval(copy_fn, delete_fn, nopython)
        CHKERR( MPI_Type_create_keyval(_copy, _del, &keyval, <void *>state) )
        PyMPI_attr_state_set(MPI_DATATYPE_NULL, keyval, state)
        return keyval

    @classmethod
    def Free_keyval(cls, int keyval: int) -> int:
        """
        Free an attribute key for datatypes.
        """
        cdef int keyval_save = keyval
        CHKERR( MPI_Type_free_keyval(&keyval) )
        PyMPI_attr_state_del(MPI_DATATYPE_NULL, keyval_save)
        return keyval

    # Naming Objects
    # --------------

    def Get_name(self) -> str:
        """
        Get the print name for this datatype.
        """
        cdef char name[MPI_MAX_OBJECT_NAME+1]
        cdef int nlen = 0
        CHKERR( MPI_Type_get_name(self.ob_mpi, name, &nlen) )
        return tompistr(name, nlen)

    def Set_name(self, name: str) -> None:
        """
        Set the print name for this datatype.
        """
        cdef char *cname = NULL
        name = asmpistr(name, &cname)
        CHKERR( MPI_Type_set_name(self.ob_mpi, cname) )

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
        return MPI_Type_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg: int) -> Datatype:
        """
        """
        return fromhandle(MPI_Type_f2c(arg))

    # Python/NumPy interoperability
    # -----------------------------

    def tocode(self) -> str:
        """
        Get character code or type string from predefined MPI datatype.
        """
        cdef const char *s = DatatypeCode(self.ob_mpi)
        if s != NULL: return pystr(s)
        raise ValueError("cannot map to character code or type string")

    @classmethod
    def fromcode(cls, code: str) -> Datatype:
        """
        Get predefined MPI datatype from character code or type string.
        """
        try:
            return <Datatype?> TypeDict[code]
        except KeyError:
            raise ValueError(f"cannot map code {code!r} to MPI datatype")

    property typestr:
        """Type string."""
        def __get__(self) -> str:
            if self.ob_mpi == MPI_DATATYPE_NULL: return ""
            cdef const char *s = DatatypeStr(self.ob_mpi)
            if s != NULL: return pystr(s)
            return f"V{mpiextent(self.ob_mpi)}"

    property typechar:
        """Character code."""
        def __get__(self) -> str:
            if self.ob_mpi == MPI_DATATYPE_NULL: return ""
            cdef const char *s = DatatypeChar(self.ob_mpi)
            if s != NULL: return pystr(s)
            return "V"


# Address Functions
# -----------------

def Get_address(location: Buffer | Bottom) -> int:
    """
    Get the address of a location in memory.
    """
    cdef void *baseptr = MPI_BOTTOM
    if not is_BOTTOM(location):
        asbuffer_r(location, &baseptr, NULL)
    cdef MPI_Aint address = 0
    CHKERR( MPI_Get_address(baseptr, &address) )
    return address


def Aint_add(Aint base: int, Aint disp: int) -> int:
    """
    Return the sum of base address and displacement.
    """
    return MPI_Aint_add(base, disp)


def Aint_diff(Aint addr1: int, Aint addr2: int) -> int:
    """
    Return the difference between absolute addresses.
    """
    return MPI_Aint_diff(addr1, addr2)


cdef Datatype __DATATYPE_NULL__ = def_Datatype( MPI_DATATYPE_NULL , "DATATYPE_NULL" )  # noqa

cdef Datatype __PACKED__ = def_Datatype( MPI_PACKED , "PACKED" )
cdef Datatype __BYTE__   = def_Datatype( MPI_BYTE   , "BYTE"   )
cdef Datatype __AINT__   = def_Datatype( MPI_AINT   , "AINT"   )
cdef Datatype __OFFSET__ = def_Datatype( MPI_OFFSET , "OFFSET" )
cdef Datatype __COUNT__  = def_Datatype( MPI_COUNT  , "COUNT"  )

cdef Datatype __CHAR__               = def_Datatype( MPI_CHAR               , "CHAR"               )  # noqa
cdef Datatype __WCHAR__              = def_Datatype( MPI_WCHAR              , "WCHAR"              )  # noqa
cdef Datatype __SIGNED_CHAR__        = def_Datatype( MPI_SIGNED_CHAR        , "SIGNED_CHAR"        )  # noqa
cdef Datatype __SHORT__              = def_Datatype( MPI_SHORT              , "SHORT"              )  # noqa
cdef Datatype __INT__                = def_Datatype( MPI_INT                , "INT"                )  # noqa
cdef Datatype __LONG__               = def_Datatype( MPI_LONG               , "LONG"               )  # noqa
cdef Datatype __LONG_LONG__          = def_Datatype( MPI_LONG_LONG          , "LONG_LONG"          )  # noqa
cdef Datatype __UNSIGNED_CHAR__      = def_Datatype( MPI_UNSIGNED_CHAR      , "UNSIGNED_CHAR"      )  # noqa
cdef Datatype __UNSIGNED_SHORT__     = def_Datatype( MPI_UNSIGNED_SHORT     , "UNSIGNED_SHORT"     )  # noqa
cdef Datatype __UNSIGNED__           = def_Datatype( MPI_UNSIGNED           , "UNSIGNED"           )  # noqa
cdef Datatype __UNSIGNED_LONG__      = def_Datatype( MPI_UNSIGNED_LONG      , "UNSIGNED_LONG"      )  # noqa
cdef Datatype __UNSIGNED_LONG_LONG__ = def_Datatype( MPI_UNSIGNED_LONG_LONG , "UNSIGNED_LONG_LONG" )  # noqa
cdef Datatype __FLOAT__              = def_Datatype( MPI_FLOAT              , "FLOAT"              )  # noqa
cdef Datatype __DOUBLE__             = def_Datatype( MPI_DOUBLE             , "DOUBLE"             )  # noqa
cdef Datatype __LONG_DOUBLE__        = def_Datatype( MPI_LONG_DOUBLE        , "LONG_DOUBLE"        )  # noqa

cdef Datatype __C_BOOL__                = def_Datatype( MPI_C_BOOL   , "C_BOOL"   )  # noqa
cdef Datatype __INT8_T__                = def_Datatype( MPI_INT8_T   , "INT8_T"   )  # noqa
cdef Datatype __INT16_T__               = def_Datatype( MPI_INT16_T  , "INT16_T"  )  # noqa
cdef Datatype __INT32_T__               = def_Datatype( MPI_INT32_T  , "INT32_T"  )  # noqa
cdef Datatype __INT64_T__               = def_Datatype( MPI_INT64_T  , "INT64_T"  )  # noqa
cdef Datatype __UINT8_T__               = def_Datatype( MPI_UINT8_T  , "UINT8_T"  )  # noqa
cdef Datatype __UINT16_T__              = def_Datatype( MPI_UINT16_T , "UINT16_T" )  # noqa
cdef Datatype __UINT32_T__              = def_Datatype( MPI_UINT32_T , "UINT32_T" )  # noqa
cdef Datatype __UINT64_T__              = def_Datatype( MPI_UINT64_T , "UINT64_T" )  # noqa

cdef Datatype __C_COMPLEX__             = def_Datatype( MPI_C_COMPLEX             , "C_COMPLEX"             )  # noqa
cdef Datatype __C_FLOAT_COMPLEX__       = __C_COMPLEX__
cdef Datatype __C_DOUBLE_COMPLEX__      = def_Datatype( MPI_C_DOUBLE_COMPLEX      , "C_DOUBLE_COMPLEX"      )  # noqa
cdef Datatype __C_LONG_DOUBLE_COMPLEX__ = def_Datatype( MPI_C_LONG_DOUBLE_COMPLEX , "C_LONG_DOUBLE_COMPLEX" )  # noqa

cdef Datatype __CXX_BOOL__                = def_Datatype( MPI_CXX_BOOL                , "CXX_BOOL"                )  # noqa
cdef Datatype __CXX_FLOAT_COMPLEX__       = def_Datatype( MPI_CXX_FLOAT_COMPLEX       , "CXX_FLOAT_COMPLEX"       )  # noqa
cdef Datatype __CXX_DOUBLE_COMPLEX__      = def_Datatype( MPI_CXX_DOUBLE_COMPLEX      , "CXX_DOUBLE_COMPLEX"      )  # noqa
cdef Datatype __CXX_LONG_DOUBLE_COMPLEX__ = def_Datatype( MPI_CXX_LONG_DOUBLE_COMPLEX , "CXX_LONG_DOUBLE_COMPLEX" )  # noqa

cdef Datatype __SHORT_INT__        = def_Datatype( MPI_SHORT_INT       , "SHORT_INT"       )  # noqa
cdef Datatype __INT_INT__          = def_Datatype( MPI_2INT            , "INT_INT"         )  # noqa
cdef Datatype __LONG_INT__         = def_Datatype( MPI_LONG_INT        , "LONG_INT"        )  # noqa
cdef Datatype __FLOAT_INT__        = def_Datatype( MPI_FLOAT_INT       , "FLOAT_INT"       )  # noqa
cdef Datatype __DOUBLE_INT__       = def_Datatype( MPI_DOUBLE_INT      , "DOUBLE_INT"      )  # noqa
cdef Datatype __LONG_DOUBLE_INT__  = def_Datatype( MPI_LONG_DOUBLE_INT , "LONG_DOUBLE_INT" )  # noqa

cdef Datatype __CHARACTER__        = def_Datatype( MPI_CHARACTER        , "CHARACTER"        )  # noqa
cdef Datatype __LOGICAL__          = def_Datatype( MPI_LOGICAL          , "LOGICAL"          )  # noqa
cdef Datatype __INTEGER__          = def_Datatype( MPI_INTEGER          , "INTEGER"          )  # noqa
cdef Datatype __REAL__             = def_Datatype( MPI_REAL             , "REAL"             )  # noqa
cdef Datatype __DOUBLE_PRECISION__ = def_Datatype( MPI_DOUBLE_PRECISION , "DOUBLE_PRECISION" )  # noqa
cdef Datatype __COMPLEX__          = def_Datatype( MPI_COMPLEX          , "COMPLEX"          )  # noqa
cdef Datatype __DOUBLE_COMPLEX__   = def_Datatype( MPI_DOUBLE_COMPLEX   , "DOUBLE_COMPLEX"   )  # noqa

cdef Datatype __LOGICAL1__  = def_Datatype( MPI_LOGICAL1  , "LOGICAL1"  )
cdef Datatype __LOGICAL2__  = def_Datatype( MPI_LOGICAL2  , "LOGICAL2"  )
cdef Datatype __LOGICAL4__  = def_Datatype( MPI_LOGICAL4  , "LOGICAL4"  )
cdef Datatype __LOGICAL8__  = def_Datatype( MPI_LOGICAL8  , "LOGICAL8"  )
cdef Datatype __INTEGER1__  = def_Datatype( MPI_INTEGER1  , "INTEGER1"  )
cdef Datatype __INTEGER2__  = def_Datatype( MPI_INTEGER2  , "INTEGER2"  )
cdef Datatype __INTEGER4__  = def_Datatype( MPI_INTEGER4  , "INTEGER4"  )
cdef Datatype __INTEGER8__  = def_Datatype( MPI_INTEGER8  , "INTEGER8"  )
cdef Datatype __INTEGER16__ = def_Datatype( MPI_INTEGER16 , "INTEGER16" )
cdef Datatype __REAL2__     = def_Datatype( MPI_REAL2     , "REAL2"     )
cdef Datatype __REAL4__     = def_Datatype( MPI_REAL4     , "REAL4"     )
cdef Datatype __REAL8__     = def_Datatype( MPI_REAL8     , "REAL8"     )
cdef Datatype __REAL16__    = def_Datatype( MPI_REAL16    , "REAL16"    )
cdef Datatype __COMPLEX4__  = def_Datatype( MPI_COMPLEX4  , "COMPLEX4"  )
cdef Datatype __COMPLEX8__  = def_Datatype( MPI_COMPLEX8  , "COMPLEX8"  )
cdef Datatype __COMPLEX16__ = def_Datatype( MPI_COMPLEX16 , "COMPLEX16" )
cdef Datatype __COMPLEX32__ = def_Datatype( MPI_COMPLEX32 , "COMPLEX32" )

# Predefined datatype handles
# ---------------------------

DATATYPE_NULL = __DATATYPE_NULL__  #: Null datatype handle
# MPI-specific datatypes
PACKED = __PACKED__
BYTE   = __BYTE__
AINT   = __AINT__
OFFSET = __OFFSET__
COUNT  = __COUNT__
# Elementary C datatypes
CHAR                = __CHAR__
WCHAR               = __WCHAR__
SIGNED_CHAR         = __SIGNED_CHAR__
SHORT               = __SHORT__
INT                 = __INT__
LONG                = __LONG__
LONG_LONG           = __LONG_LONG__
UNSIGNED_CHAR       = __UNSIGNED_CHAR__
UNSIGNED_SHORT      = __UNSIGNED_SHORT__
UNSIGNED            = __UNSIGNED__
UNSIGNED_LONG       = __UNSIGNED_LONG__
UNSIGNED_LONG_LONG  = __UNSIGNED_LONG_LONG__
FLOAT               = __FLOAT__
DOUBLE              = __DOUBLE__
LONG_DOUBLE         = __LONG_DOUBLE__
# C99 datatypes
C_BOOL                = __C_BOOL__
INT8_T                = __INT8_T__
INT16_T               = __INT16_T__
INT32_T               = __INT32_T__
INT64_T               = __INT64_T__
UINT8_T               = __UINT8_T__
UINT16_T              = __UINT16_T__
UINT32_T              = __UINT32_T__
UINT64_T              = __UINT64_T__
C_COMPLEX             = __C_COMPLEX__
C_FLOAT_COMPLEX       = __C_FLOAT_COMPLEX__
C_DOUBLE_COMPLEX      = __C_DOUBLE_COMPLEX__
C_LONG_DOUBLE_COMPLEX = __C_LONG_DOUBLE_COMPLEX__
# C++ datatypes
CXX_BOOL                = __CXX_BOOL__
CXX_FLOAT_COMPLEX       = __CXX_FLOAT_COMPLEX__
CXX_DOUBLE_COMPLEX      = __CXX_DOUBLE_COMPLEX__
CXX_LONG_DOUBLE_COMPLEX = __CXX_LONG_DOUBLE_COMPLEX__
# C Datatypes for reduction operations
SHORT_INT        = __SHORT_INT__
INT_INT = TWOINT = __INT_INT__
LONG_INT         = __LONG_INT__
FLOAT_INT        = __FLOAT_INT__
DOUBLE_INT       = __DOUBLE_INT__
LONG_DOUBLE_INT  = __LONG_DOUBLE_INT__
# Elementary Fortran datatypes
CHARACTER        = __CHARACTER__
LOGICAL          = __LOGICAL__
INTEGER          = __INTEGER__
REAL             = __REAL__
DOUBLE_PRECISION = __DOUBLE_PRECISION__
COMPLEX          = __COMPLEX__
DOUBLE_COMPLEX   = __DOUBLE_COMPLEX__
# Size-specific Fortran datatypes
LOGICAL1  = __LOGICAL1__
LOGICAL2  = __LOGICAL2__
LOGICAL4  = __LOGICAL4__
LOGICAL8  = __LOGICAL8__
INTEGER1  = __INTEGER1__
INTEGER2  = __INTEGER2__
INTEGER4  = __INTEGER4__
INTEGER8  = __INTEGER8__
INTEGER16 = __INTEGER16__
REAL2     = __REAL2__
REAL4     = __REAL4__
REAL8     = __REAL8__
REAL16    = __REAL16__
COMPLEX4  = __COMPLEX4__
COMPLEX8  = __COMPLEX8__
COMPLEX16 = __COMPLEX16__
COMPLEX32 = __COMPLEX32__

# Convenience aliases
UNSIGNED_INT          = __UNSIGNED__
SIGNED_SHORT          = __SHORT__
SIGNED_INT            = __INT__
SIGNED_LONG           = __LONG__
SIGNED_LONG_LONG      = __LONG_LONG__
BOOL                  = __C_BOOL__
SINT8_T               = __INT8_T__
SINT16_T              = __INT16_T__
SINT32_T              = __INT32_T__
SINT64_T              = __INT64_T__
F_BOOL                = __LOGICAL__
F_INT                 = __INTEGER__
F_FLOAT               = __REAL__
F_DOUBLE              = __DOUBLE_PRECISION__
F_COMPLEX             = __COMPLEX__
F_FLOAT_COMPLEX       = __COMPLEX__
F_DOUBLE_COMPLEX      = __DOUBLE_COMPLEX__
