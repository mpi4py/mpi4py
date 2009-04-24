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
DISTRIBUTE_DFLT_DARG = MPI_DISTRIBUTE_DFLT_DARG  #: Default distribution argument


# Combiner values for datatype decoding
# -------------------------------------
COMBINER_NAMED            = MPI_COMBINER_NAMED
COMBINER_DUP              = MPI_COMBINER_DUP
COMBINER_CONTIGUOUS       = MPI_COMBINER_CONTIGUOUS
COMBINER_VECTOR           = MPI_COMBINER_VECTOR
COMBINER_HVECTOR          = MPI_COMBINER_HVECTOR
COMBINER_HVECTOR_INTEGER  = MPI_COMBINER_HVECTOR_INTEGER  #: from Fortran call
COMBINER_INDEXED          = MPI_COMBINER_INDEXED
COMBINER_HINDEXED_INTEGER = MPI_COMBINER_HINDEXED_INTEGER #: from Fortran call
COMBINER_HINDEXED         = MPI_COMBINER_HINDEXED
COMBINER_INDEXED_BLOCK    = MPI_COMBINER_INDEXED_BLOCK
COMBINER_STRUCT           = MPI_COMBINER_STRUCT
COMBINER_STRUCT_INTEGER   = MPI_COMBINER_STRUCT_INTEGER   #: from Fortran call
COMBINER_SUBARRAY         = MPI_COMBINER_SUBARRAY
COMBINER_DARRAY           = MPI_COMBINER_DARRAY
COMBINER_RESIZED          = MPI_COMBINER_RESIZED
COMBINER_F90_REAL         = MPI_COMBINER_F90_REAL
COMBINER_F90_COMPLEX      = MPI_COMBINER_F90_COMPLEX
COMBINER_F90_INTEGER      = MPI_COMBINER_F90_INTEGER


cdef class Datatype:

    """
    Datatype
    """

    def __cinit__(self):
        self.ob_mpi = MPI_DATATYPE_NULL

    def __dealloc__(self):
        if not (self.flags & PyMPI_OWNED): return
        CHKERR( del_Datatype(&self.ob_mpi) )

    def __richcmp__(self, other, int op):
        if not isinstance(self,  Datatype): return NotImplemented
        if not isinstance(other, Datatype): return NotImplemented
        cdef Datatype s = self, o = other
        if   op == 2: return (s.ob_mpi == o.ob_mpi)
        elif op == 3: return (s.ob_mpi != o.ob_mpi)
        else: raise TypeError(S("only '==' and '!='"))

    def __nonzero__(self):
        return self.ob_mpi != MPI_DATATYPE_NULL

    # Datatype Accessors
    # ------------------

    def Get_extent(self):
        """
        Return lower bound and extent of datatype
        """
        cdef MPI_Aint lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent(self.ob_mpi, &lb, &extent) )
        return (lb, extent)

    property extent:
        """extent"""
        def __get__(self):
            cdef MPI_Aint lb = 0, extent = 0
            CHKERR( MPI_Type_get_extent(self.ob_mpi, &lb, &extent) )
            return extent

    property lb:
        """lower bound"""
        def __get__(self):
            cdef MPI_Aint lb = 0, extent = 0
            CHKERR( MPI_Type_get_extent(self.ob_mpi, &lb, &extent) )
            return lb

    property ub:
        """upper bound"""
        def __get__(self):
            cdef MPI_Aint lb = 0, extent = 0
            CHKERR( MPI_Type_get_extent(self.ob_mpi, &lb, &extent) )
            return lb + extent

    def Get_size(self):
        """
        Return the number of bytes occupied
        by entries in the datatype
        """
        cdef int size = 0
        CHKERR( MPI_Type_size(self.ob_mpi, &size) )
        return size

    property size:
        """size (in bytes)"""
        def __get__(self):
            cdef int size = 0
            CHKERR( MPI_Type_size(self.ob_mpi, &size) )
            return size

    # Datatype Constructors
    # ---------------------

    def Dup(self):
        """
        Duplicate a datatype
        """
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_dup(self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    Create_dup = Dup #: convenience alias

    def Create_contiguous(self, int count):
        """
        Create a contiguous datatype
        """
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_contiguous(count, self.ob_mpi,
                                    &datatype.ob_mpi) )
        return datatype

    def Create_vector(self, int count, int blocklength, int stride):
        """
        Create a vector (strided) datatype
        """
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_vector(count, blocklength, stride,
                                self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    def Create_hvector(self, int count, int blocklength, Aint stride):
        """
        Create a vector (strided) datatype
        """
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_create_hvector(count, blocklength, stride,
                                        self.ob_mpi,
                                        &datatype.ob_mpi) )
        return datatype

    def Create_indexed(self, blocklengths, displacements):
        """
        Create an indexed datatype
        """
        cdef int count = len(displacements)
        cdef int *iblen=NULL
        tmp1 = asarray_int(blocklengths,  &iblen, count)
        cdef int *idisp=NULL
        tmp2 = asarray_int(displacements, &idisp, count)
        #
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_indexed(count, iblen, idisp,
                                 self.ob_mpi, &datatype.ob_mpi) )
        return datatype

    def Create_indexed_block(self, int blocklength, displacements):
        """
        Create an indexed datatype
        with constant-sized blocks
        """
        cdef int count = len(displacements)
        cdef int *idisp=NULL
        tmp2 = asarray_int(displacements, &idisp, count)
        #
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_create_indexed_block(count, blocklength,
                                              idisp, self.ob_mpi,
                                              &datatype.ob_mpi) )
        return datatype

    def Create_hindexed(self, blocklengths, displacements):
        """
        Create an indexed datatype
        with displacements in bytes
        """
        cdef int count = len(displacements)
        cdef int *iblen=NULL
        tmp1 = asarray_int(blocklengths, &iblen, count)
        cdef MPI_Aint *idisp=NULL
        tmp2 = asarray_Aint(displacements, &idisp, count)
        #
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_create_hindexed(count, iblen, idisp,
                                         self.ob_mpi,
                                         &datatype.ob_mpi) )
        return datatype

    def Create_subarray(self, sizes, subsizes, starts,
                        int order=ORDER_C):
        """
        Create a datatype for a subarray of
        a regular, multidimensional array
        """
        cdef int ndims = len(sizes)
        cdef int *isizes = NULL
        tmp1 = asarray_int(sizes, &isizes, ndims)
        cdef int *isubsizes = NULL
        tmp2 = asarray_int(subsizes, &isubsizes, ndims)
        cdef int *istarts = NULL
        tmp3 = asarray_int(starts, &istarts, ndims)
        cdef int iorder = MPI_ORDER_C
        if order is not None: iorder = order
        #
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_create_subarray(ndims, isizes,
                                         isubsizes, istarts,
                                         iorder, self.ob_mpi,
                                         &datatype.ob_mpi) )
        return datatype

    def Create_darray(self, int size, int rank,
                      gsizes, distribs, dargs, psizes,
                      int order=ORDER_C):
        """
        Create a datatype representing an HPF-like
        distributed array on Cartesian process grids
        """
        cdef int ndims = len(gsizes)
        cdef int *igsizes=NULL
        tmp1 = asarray_int(gsizes, &igsizes, ndims)
        cdef int *idistribs=NULL
        tmp2 = asarray_int(distribs, &idistribs, ndims)
        cdef int *idargs=NULL
        tmp3 = asarray_int(dargs, &idargs, ndims)
        cdef int *ipsizes=NULL
        tmp4 = asarray_int(psizes, &ipsizes, ndims)
        cdef int iorder = MPI_ORDER_C
        if order is not None: iorder = order
        #
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_create_darray(size, rank, ndims, igsizes,
                                       idistribs, idargs, ipsizes,
                                       iorder, self.ob_mpi,
                                       &datatype.ob_mpi) )
        return datatype

    @classmethod
    def Create_struct(cls, blocklengths, displacements, datatypes):
        """
        Create an datatype from a general set of
        block sizes, displacements and datatypes
        """
        cdef int count = len(displacements)
        cdef int *iblen=NULL
        tmp1 = asarray_int(blocklengths, &iblen, count)
        cdef MPI_Aint *idisp=NULL
        tmp2 = asarray_Aint(displacements, &idisp, count)
        cdef MPI_Datatype *itype=NULL
        tmp3 = asarray_Datatype(datatypes, &itype, count)
        #
        cdef Datatype datatype = cls()
        CHKERR( MPI_Type_create_struct(count, iblen, idisp, itype,
                                       &datatype.ob_mpi) )
        return datatype

    # Parametrized and size-specific Fortran Datatypes
    # ------------------------------------------------

    @classmethod
    def Create_f90_integer(cls, int r):
        """
        Return a bounded integer datatype
        """
        cdef Datatype datatype = cls()
        CHKERR( MPI_Type_create_f90_integer(r, &datatype.ob_mpi) )
        return datatype

    @classmethod
    def Create_f90_real(cls, int p, int r):
        """
        Return a bounded real datatype
        """
        cdef Datatype datatype = cls()
        CHKERR( MPI_Type_create_f90_real(p, r, &datatype.ob_mpi) )
        return datatype

    @classmethod
    def Create_f90_complex(cls, int p, int r):
        """
        Return a bounded complex datatype
        """
        cdef Datatype datatype = cls()
        CHKERR( MPI_Type_create_f90_complex(p, r, &datatype.ob_mpi) )
        return datatype

    @classmethod
    def Match_size(cls, int typeclass, int size):
        """
        Find a datatype matching a specified size in bytes
        """
        cdef Datatype datatype = cls()
        CHKERR( MPI_Type_match_size(typeclass, size, &datatype.ob_mpi) )
        return datatype

    # Use of Derived Datatypes
    # ------------------------

    def Commit(self):
        """
        Commit the datatype
        """
        CHKERR( MPI_Type_commit(&self.ob_mpi) )
        return self

    def Free(self):
        """
        Free the datatype
        """
        CHKERR( MPI_Type_free(&self.ob_mpi) )

    # Datatype Resizing
    # -----------------

    def Create_resized(self, Aint lb, Aint extent):
        """
        Create a datatype with a new lower bound and extent
        """
        cdef Datatype datatype = type(self)()
        CHKERR( MPI_Type_create_resized(self.ob_mpi,
                                        lb, extent,
                                        &datatype.ob_mpi) )
        return datatype

    Resized = Create_resized #: compatibility alias

    def Get_true_extent(self):
        """
        Return the true lower bound and extent of a datatype
        """
        cdef MPI_Aint lb = 0, extent = 0
        CHKERR( MPI_Type_get_true_extent(self.ob_mpi,
                                         &lb, &extent) )
        return (lb, extent)

    property true_extent:
        """true extent"""
        def __get__(self):
            cdef MPI_Aint lb = 0, extent = 0
            CHKERR( MPI_Type_get_true_extent(self.ob_mpi,
                                             &lb, &extent) )
            return extent

    property true_lb:
        """true lower bound"""
        def __get__(self):
            cdef MPI_Aint lb = 0, extent = 0
            CHKERR( MPI_Type_get_true_extent(self.ob_mpi,
                                             &lb, &extent) )
            return lb

    property true_ub:
        """true upper bound"""
        def __get__(self):
            cdef MPI_Aint lb = 0, extent = 0
            CHKERR( MPI_Type_get_true_extent(self.ob_mpi, &lb,
                                             &extent) )
            return lb + extent

    # Decoding a Datatype
    # -------------------

    def Get_envelope(self):
        """
        Return information on the number and type of input arguments
        used in the call that created a datatype
        """
        cdef int ni = 0, na = 0, nd = 0, combiner = MPI_UNDEFINED
        CHKERR( MPI_Type_get_envelope(self.ob_mpi, &ni, &na, &nd, &combiner) )
        return (ni, na, nd, combiner)

    def Get_contents(self):
        """
        Retrieve the actual arguments used in the call that created a
        datatype
        """
        cdef int ni = 0, na = 0, nd = 0, combiner = MPI_UNDEFINED
        CHKERR( MPI_Type_get_envelope(self.ob_mpi, &ni, &na, &nd, &combiner) )
        cdef int *i = NULL
        cdef MPI_Aint *a = NULL
        cdef MPI_Datatype *d = NULL
        cdef object tmp1 = allocate(ni*sizeof(int), <void**>&i)
        cdef object tmp2 = allocate(na*sizeof(MPI_Aint), <void**>&a)
        cdef object tmp3 = allocate(nd*sizeof(MPI_Datatype), <void**>&d)
        CHKERR( MPI_Type_get_contents(self.ob_mpi, ni, na, nd, i, a, d) )
        cdef int k = 0
        cdef object integers  = [i[k] for k from 0 <= k < ni]
        cdef object addresses = [a[k] for k from 0 <= k < na]
        cdef object datatypes = [new_Datatype(d[k]) for k from 0 <= k < nd]
        return (integers, addresses, datatypes)

    def decode(self):
        """
        Convenience method for decoding a datatype
        """
        # get the datatype envelope
        cdef int ni = 0, na = 0, nd = 0, combiner = MPI_UNDEFINED
        CHKERR( MPI_Type_get_envelope(self.ob_mpi, &ni, &na, &nd, &combiner) )
        # return self immediatly for named datatypes
        if combiner == MPI_COMBINER_NAMED: return self
        # get the datatype contents
        cdef int *i = NULL
        cdef MPI_Aint *a = NULL
        cdef MPI_Datatype *d = NULL
        cdef object tmp1 = allocate(ni*sizeof(int), <void**>&i)
        cdef object tmp2 = allocate(na*sizeof(MPI_Aint), <void**>&a)
        cdef object tmp3 = allocate(nd*sizeof(MPI_Datatype), <void**>&d)
        CHKERR( MPI_Type_get_contents(self.ob_mpi, ni, na, nd, i, a, d) )
        # manage in advance the contained datatypes
        cdef int k = 0, s1, e1, s2, e2, s3, e3, s4, e4
        cdef object oldtype
        if (combiner == MPI_COMBINER_STRUCT or
            combiner == MPI_COMBINER_STRUCT_INTEGER):
            oldtype = [new_Datatype(d[k]) for k from 0 <= k < nd]
        elif (combiner != MPI_COMBINER_F90_INTEGER and
              combiner != MPI_COMBINER_F90_REAL and
              combiner != MPI_COMBINER_F90_COMPLEX):
            oldtype = new_Datatype(d[0])
        # dispatch depending on the combiner value
        if combiner == <int>MPI_COMBINER_DUP:
            return (oldtype, S("DUP"), {})
        elif combiner == <int>MPI_COMBINER_CONTIGUOUS:
            return (oldtype, S("CONTIGUOUS"),
                    {S("count") : i[0]})
        elif combiner == <int>MPI_COMBINER_VECTOR:
            return (oldtype, S("VECTOR"),
                    {S("count")       : i[0],
                     S("blocklength") : i[1],
                     S("stride")      : i[2]})
        elif (combiner == <int>MPI_COMBINER_HVECTOR or
              combiner == <int>MPI_COMBINER_HVECTOR_INTEGER):
            return (oldtype, S("HVECTOR"),
                    {S("count")       : i[0],
                     S("blocklength") : i[1],
                     S("stride")      : a[0]})
        elif combiner == <int>MPI_COMBINER_INDEXED:
            s1 =      1; e1 =   i[0]
            s2 = i[0]+1; e2 = 2*i[0]
            return (oldtype, S("INDEXED"),
                    {S("blocklengths")  : [i[k] for k from s1 <= k <= e1],
                     S("displacements") : [i[k] for k from s2 <= k <= e2]})
        elif (combiner == <int>MPI_COMBINER_HINDEXED or
              combiner == <int>MPI_COMBINER_HINDEXED_INTEGER):
            s1 = 1; e1 = i[0]
            s2 = 0; e2 = i[0]-1
            return (oldtype, S("HINDEXED"),
                    {S("blocklengths")  : [i[k] for k from s1 <= k <= e1],
                     S("displacements") : [a[k] for k from s2 <= k <= e2]})
        elif combiner == <int>MPI_COMBINER_INDEXED_BLOCK:
            s2 = 2; e2 = i[0]+1
            return (oldtype, S("INDEXED_BLOCK"),
                    {S("blocklength")   : i[1],
                     S("displacements") : [i[k] for k from s2 <= k <= e2]})
        elif (combiner == <int>MPI_COMBINER_STRUCT or
              combiner == <int>MPI_COMBINER_STRUCT_INTEGER):
            s1 = 1; e1 = i[0]
            s2 = 0; e2 = i[0]-1
            return (Datatype, S("STRUCT"),
                    {S("blocklengths")  : [i[k] for k from s1 <= k <= e1],
                     S("displacements") : [a[k] for k from s2 <= k <= e2],
                     S("datatypes")     : oldtype})
        elif combiner == <int>MPI_COMBINER_SUBARRAY:
            s1 =        1; e1 =   i[0]
            s2 =   i[0]+1; e2 = 2*i[0]
            s3 = 2*i[0]+1; e3 = 3*i[0]
            return (oldtype, S("SUBARRAY"),
                    {S("sizes")    : [i[k] for k from s1 <= k <= e1],
                     S("subsizes") : [i[k] for k from s2 <= k <= e2],
                     S("starts")   : [i[k] for k from s3 <= k <= e3],
                     S("order")    : i[3*i[0]+1]})
        elif combiner == <int>MPI_COMBINER_DARRAY:
            s1 =        3; e1 =   i[2]+2
            s2 =   i[2]+3; e2 = 2*i[2]+2
            s3 = 2*i[2]+3; e3 = 3*i[2]+2
            s4 = 3*i[2]+3; e4 = 4*i[2]+2
            return (oldtype, S("DARRAY"),
                    {S("size")     : i[0],
                     S("rank")     : i[1],
                     S("gsizes")   : [i[k] for k from s1 <= k <= e1],
                     S("distribs") : [i[k] for k from s2 <= k <= e2],
                     S("dargs")    : [i[k] for k from s3 <= k <= e3],
                     S("psizes")   : [i[k] for k from s4 <= k <= e4],
                     S("order")    : i[4*i[2]+3]})
        elif combiner == <int>MPI_COMBINER_RESIZED:
            return (oldtype, S("RESIZED"),
                    {S("lb")     : a[0],
                     S("extent") : a[1]})
        elif combiner == <int>MPI_COMBINER_F90_INTEGER:
            return (Datatype, S("F90_INTEGER"),
                    {S("r") : i[0]})
        elif combiner == <int>MPI_COMBINER_F90_REAL:
            return (Datatype, S("F90_REAL"),
                    {S("p") : i[0],
                     S("r") : i[1]})
        elif combiner == <int>MPI_COMBINER_F90_COMPLEX:
            return (Datatype, S("F90_COMPLEX"),
                    {S("p") : i[0],
                     S("r") : i[1]})


    # Pack and Unpack
    # ---------------

    def Pack(self, inbuf, outbuf, int position, Comm comm not None):
        """
        Pack into contiguous memory according to datatype.
        """
        cdef MPI_Aint lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent(self.ob_mpi, &lb, &extent) )
        #
        cdef void *ibptr = NULL, *obptr = NULL
        cdef MPI_Aint iblen = 0, oblen = 0
        cdef ob1 = asbuffer_r(inbuf,  &ibptr, &iblen)
        cdef ob2 = asbuffer_w(outbuf, &obptr, &oblen)
        cdef int icount = <int>(iblen/extent), osize = <int>oblen
        #
        CHKERR( MPI_Pack(ibptr, icount, self.ob_mpi, obptr, osize,
                         &position, comm.ob_mpi) )
        return position

    def Unpack(self, inbuf, int position, outbuf, Comm comm not None):
        """
        Unpack from contiguous memory according to datatype.
        """
        cdef MPI_Aint lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent(self.ob_mpi, &lb, &extent) )
        #
        cdef void *ibptr = NULL, *obptr = NULL
        cdef MPI_Aint iblen = 0, oblen = 0
        cdef ob1 = asbuffer_r(inbuf,  &ibptr, &iblen)
        cdef ob2 = asbuffer_w(outbuf, &obptr, &oblen)
        cdef int isize = <int>iblen, ocount = <int>(oblen/extent)
        #
        CHKERR( MPI_Unpack(ibptr, isize, &position, obptr, ocount,
                           self.ob_mpi, comm.ob_mpi) )
        return position

    def Pack_size(self, int count, Comm comm not None):
        """
        Returns the upper bound on the amount of space (in bytes)
        needed to pack a message according to datatype.
        """
        cdef int size = 0
        CHKERR( MPI_Pack_size(count, self.ob_mpi,
                              comm.ob_mpi, &size) )
        return size

    # Canonical Pack and Unpack
    # -------------------------

    def Pack_external(self, datarep, inbuf, outbuf, Aint position):
        """
        Pack into contiguous memory according to datatype,
        using a portable data representation (**external32**).
        """
        cdef char *cdatarep = NULL
        datarep = asmpistr(datarep, &cdatarep, NULL)
        cdef MPI_Aint lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent(self.ob_mpi, &lb, &extent) )
        #
        cdef void *ibptr = NULL, *obptr = NULL
        cdef MPI_Aint iblen = 0, oblen = 0
        cdef ob1 = asbuffer_r(inbuf,  &ibptr, &iblen)
        cdef ob2 = asbuffer_w(outbuf, &obptr, &oblen)
        cdef int icount = <int>(iblen/extent)
        cdef MPI_Aint osize = <int>oblen
        #
        CHKERR( MPI_Pack_external(cdatarep, ibptr, icount,
                                  self.ob_mpi,
                                  obptr, osize, &position) )
        return position

    def Unpack_external(self, datarep, inbuf, Aint position, outbuf):
        """
        Unpack from contiguous memory according to datatype,
        using a portable data representation (**external32**).
        """
        cdef char *cdatarep = NULL
        datarep = asmpistr(datarep, &cdatarep, NULL)
        cdef MPI_Aint lb = 0, extent = 0
        CHKERR( MPI_Type_get_extent(self.ob_mpi, &lb, &extent) )
        #
        cdef void *ibptr = NULL, *obptr = NULL
        cdef MPI_Aint iblen = 0, oblen = 0
        cdef ob1 = asbuffer_r(inbuf,  &ibptr, &iblen)
        cdef ob2 = asbuffer_w(outbuf, &obptr, &oblen)
        cdef MPI_Aint isize = iblen,
        cdef int ocount = <int>(oblen/extent)
        #
        CHKERR( MPI_Unpack_external(cdatarep, ibptr, isize, &position,
                                    obptr, ocount, self.ob_mpi) )
        return position

    def Pack_external_size(self, datarep, int count):
        """
        Returns the upper bound on the amount of space (in bytes)
        needed to pack a message according to datatype,
        using a portable data representation (**external32**).
        """
        cdef char *cdatarep = NULL
        cdef MPI_Aint size = 0
        datarep = asmpistr(datarep, &cdatarep, NULL)
        CHKERR( MPI_Pack_external_size(cdatarep, count,
                                       self.ob_mpi, &size) )
        return size

    # Naming Objects
    # --------------

    def Get_name(self):
        """
        Get the print name for this datatype
        """
        cdef char name[MPI_MAX_OBJECT_NAME+1]
        cdef int nlen = 0
        CHKERR( MPI_Type_get_name(self.ob_mpi, name, &nlen) )
        return tompistr(name, nlen)

    def Set_name(self, name):
        """
        Set the print name for this datatype
        """
        cdef char *cname = NULL
        name = asmpistr(name, &cname, NULL)
        CHKERR( MPI_Type_set_name(self.ob_mpi, cname) )

    property name:
        """datatype name"""
        def __get__(self):
            return self.Get_name()
        def __set__(self, value):
            self.Set_name(value)

    # Fortran Handle
    # --------------

    def py2f(self):
        """
        """
        return MPI_Type_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg):
        """
        """
        cdef Datatype datatype = cls()
        datatype.ob_mpi = MPI_Type_f2c(arg)
        return datatype



# Address Function
# ----------------

def Get_address(location):
    """
    Get the address of a location in memory
    """
    cdef void *baseptr = NULL
    asmemory(location, &baseptr, NULL)
    cdef MPI_Aint address = 0
    CHKERR( MPI_Get_address(baseptr, &address) )
    return address



cdef Datatype __DATATYPE_NULL__      = new_Datatype( MPI_DATATYPE_NULL      )

cdef Datatype __CHAR__               = new_Datatype( MPI_CHAR               )
cdef Datatype __WCHAR__              = new_Datatype( MPI_WCHAR              )
cdef Datatype __SIGNED_CHAR__        = new_Datatype( MPI_SIGNED_CHAR        )
cdef Datatype __UNSIGNED_CHAR__      = new_Datatype( MPI_UNSIGNED_CHAR      )
cdef Datatype __SHORT__              = new_Datatype( MPI_SHORT              )
cdef Datatype __UNSIGNED_SHORT__     = new_Datatype( MPI_UNSIGNED_SHORT     )
cdef Datatype __INT__                = new_Datatype( MPI_INT                )
cdef Datatype __UNSIGNED__           = new_Datatype( MPI_UNSIGNED           )
cdef Datatype __LONG__               = new_Datatype( MPI_LONG               )
cdef Datatype __UNSIGNED_LONG__      = new_Datatype( MPI_UNSIGNED_LONG      )
cdef Datatype __FLOAT__              = new_Datatype( MPI_FLOAT              )
cdef Datatype __DOUBLE__             = new_Datatype( MPI_DOUBLE             )
cdef Datatype __LONG_DOUBLE__        = new_Datatype( MPI_LONG_DOUBLE        )
cdef Datatype __BYTE__               = new_Datatype( MPI_BYTE               )
cdef Datatype __PACKED__             = new_Datatype( MPI_PACKED             )

cdef Datatype __SHORT_INT__          = new_Datatype( MPI_SHORT_INT          )
cdef Datatype __TWOINT__             = new_Datatype( MPI_2INT               )
cdef Datatype __LONG_INT__           = new_Datatype( MPI_LONG_INT           )
cdef Datatype __FLOAT_INT__          = new_Datatype( MPI_FLOAT_INT          )
cdef Datatype __DOUBLE_INT__         = new_Datatype( MPI_DOUBLE_INT         )
cdef Datatype __LONG_DOUBLE_INT__    = new_Datatype( MPI_LONG_DOUBLE_INT    )

cdef Datatype __LONG_LONG__          = new_Datatype( MPI_LONG_LONG          )
cdef Datatype __UNSIGNED_LONG_LONG__ = new_Datatype( MPI_UNSIGNED_LONG_LONG )
cdef Datatype __LONG_LONG_INT__      = new_Datatype( MPI_LONG_LONG_INT      )

cdef Datatype __CHARACTER__          = new_Datatype( MPI_CHARACTER          )
cdef Datatype __LOGICAL__            = new_Datatype( MPI_LOGICAL            )
cdef Datatype __INTEGER__            = new_Datatype( MPI_INTEGER            )
cdef Datatype __REAL__               = new_Datatype( MPI_REAL               )
cdef Datatype __DOUBLE_PRECISION__   = new_Datatype( MPI_DOUBLE_PRECISION   )
cdef Datatype __F_COMPLEX__          = new_Datatype( MPI_COMPLEX            )
cdef Datatype __F_DOUBLE_COMPLEX__   = new_Datatype( MPI_DOUBLE_COMPLEX     )

cdef Datatype __UB__                 = new_Datatype( MPI_UB                 )
cdef Datatype __LB__                 = new_Datatype( MPI_LB                 )


# Predefined datatype handles
# ---------------------------

DATATYPE_NULL      = __DATATYPE_NULL__  #: Null datatype handle
# Elementary datatypes
CHAR               = __CHAR__
WCHAR              = __WCHAR__
SIGNED_CHAR        = __SIGNED_CHAR__
UNSIGNED_CHAR      = __UNSIGNED_CHAR__
SHORT              = __SHORT__
UNSIGNED_SHORT     = __UNSIGNED_SHORT__
INT                = __INT__
UNSIGNED           = __UNSIGNED__
LONG               = __LONG__
UNSIGNED_LONG      = __UNSIGNED_LONG__
FLOAT              = __FLOAT__
DOUBLE             = __DOUBLE__
LONG_DOUBLE        = __LONG_DOUBLE__
BYTE               = __BYTE__
PACKED             = __PACKED__
# Datatypes for reduction operations
SHORT_INT          = __SHORT_INT__
TWOINT             = __TWOINT__
LONG_INT           = __LONG_INT__
FLOAT_INT          = __FLOAT_INT__
DOUBLE_INT         = __DOUBLE_INT__
LONG_DOUBLE_INT    = __LONG_DOUBLE_INT__
# Optional datatypes
LONG_LONG          = __LONG_LONG__
UNSIGNED_LONG_LONG = __UNSIGNED_LONG_LONG__
LONG_LONG_INT      = __LONG_LONG_INT__
# Fortran datatypes
CHARACTER          = __CHARACTER__
LOGICAL            = __LOGICAL__
INTEGER            = __INTEGER__
REAL               = __REAL__
DOUBLE_PRECISION   = __DOUBLE_PRECISION__
F_COMPLEX          = __F_COMPLEX__
F_DOUBLE_COMPLEX   = __F_DOUBLE_COMPLEX__
# Special datatypes (for constructing derived datatypes)
UB                 = __UB__  #: upper-bound marker (deprecated in MPI-2)
LB                 = __LB__  #: lower-bound marker (deprecated in MPI-2)
# Convenience aliases (not in the MPI-1/MPI-2 stardards)
UNSIGNED_INT       = __UNSIGNED__
INT_INT            = __TWOINT__
