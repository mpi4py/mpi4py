cdef class Group:
    """
    Group of processes.
    """

    def __cinit__(self, Group group: Group | None = None):
        cinit(self, group)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Group): return NotImplemented
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
    def fromhandle(cls, handle: int) -> Group:
        """
        Create object from MPI handle.
        """
        return fromhandle(<MPI_Group> <Py_uintptr_t> handle)

    # Group Accessors
    # ---------------

    def Get_size(self) -> int:
        """
        Return the number of processes in a group.
        """
        cdef int size = -1
        CHKERR( MPI_Group_size(self.ob_mpi, &size) )
        return size

    property size:
        """Number of processes."""
        def __get__(self) -> int:
            return self.Get_size()

    def Get_rank(self) -> int:
        """
        Return the rank of this process in a group.
        """
        cdef int rank = -1
        CHKERR( MPI_Group_rank(self.ob_mpi, &rank) )
        return rank

    property rank:
        """Rank of this process."""
        def __get__(self) -> int:
            return self.Get_rank()

    def Translate_ranks(
        self,
        ranks: Sequence[int] | None = None,
        Group group: Group | None = None,
    ) -> list[int]:
        """
        Translate ranks in a group to those in another group.
        """
        cdef MPI_Group group1 = MPI_GROUP_NULL
        cdef MPI_Group group2 = MPI_GROUP_NULL
        cdef int n = 0, *iranks1 = NULL, *iranks2 = NULL
        #
        cdef unused1 = None
        if ranks is not None:
            unused1 = getarray(ranks, &n, &iranks1)
        else:
            CHKERR( MPI_Group_size(self.ob_mpi, &n) )
            unused1 = newarray(n, &iranks1)
            for i in range(n): iranks1[i] = i
        cdef unused2 = newarray(n, &iranks2)
        #
        group1 = self.ob_mpi
        if group is not None:
            group2 = group.ob_mpi
        else:
            CHKERR( MPI_Comm_group(MPI_COMM_WORLD, &group2) )
        try:
            CHKERR( MPI_Group_translate_ranks(
                group1, n, iranks1, group2, iranks2) )
        finally:
            if group is None:
                CHKERR( MPI_Group_free(&group2) )
        #
        cdef object ranks2 = [iranks2[i] for i in range(n)]
        return ranks2

    def Compare(self, Group group: Group) -> int:
        """
        Compare two groups.
        """
        cdef int flag = MPI_UNEQUAL
        CHKERR( MPI_Group_compare(
            self.ob_mpi, group.ob_mpi, &flag) )
        return flag

    # Group Constructors
    # ------------------

    def Dup(self) -> Self:
        """
        Duplicate a group.
        """
        cdef Group group = <Group>New(type(self))
        CHKERR( MPI_Group_union(self.ob_mpi, MPI_GROUP_EMPTY, &group.ob_mpi) )
        return group

    @classmethod
    def Union(cls, Group group1: Group, Group group2: Group) -> Self:
        """
        Create a new group from the union of two existing groups.
        """
        cdef Group group = <Group>New(cls)
        CHKERR( MPI_Group_union(
                group1.ob_mpi, group2.ob_mpi, &group.ob_mpi) )
        return group

    @classmethod
    def Intersection(cls, Group group1: Group, Group group2: Group) -> Self:
        """
        Create a new group from the intersection of two existing groups.
        """
        cdef Group group = <Group>New(cls)
        CHKERR( MPI_Group_intersection(
                group1.ob_mpi, group2.ob_mpi, &group.ob_mpi) )
        return group

    Intersect = Intersection

    @classmethod
    def Difference(cls, Group group1: Group, Group group2: Group) -> Self:
        """
        Create a new group from the difference of two existing groups.
        """
        cdef Group group = <Group>New(cls)
        CHKERR( MPI_Group_difference(
                group1.ob_mpi, group2.ob_mpi, &group.ob_mpi) )
        return group

    def Incl(self, ranks: Sequence[int]) -> Self:
        """
        Create a new group by including listed members.
        """
        cdef int n = 0, *iranks = NULL
        ranks = getarray(ranks, &n, &iranks)
        cdef Group group = <Group>New(type(self))
        CHKERR( MPI_Group_incl(self.ob_mpi, n, iranks, &group.ob_mpi) )
        return group

    def Excl(self, ranks: Sequence[int]) -> Self:
        """
        Create a new group by excluding listed members.
        """
        cdef int n = 0, *iranks = NULL
        ranks = getarray(ranks, &n, &iranks)
        cdef Group group = <Group>New(type(self))
        CHKERR( MPI_Group_excl(self.ob_mpi, n, iranks, &group.ob_mpi) )
        return group

    def Range_incl(self, ranks: Sequence[tuple[int, int, int]]) -> Self:
        """
        Create a new group by including ranges of members.
        """
        cdef int *p = NULL, (*ranges)[3]# = NULL ## XXX cython fails
        ranges = NULL
        cdef int n = <int>len(ranks)
        cdef unused1 = allocate(n, sizeof(int[3]), &ranges)
        for i in range(n):
            p = <int*> ranges[i]
            p[0], p[1], p[2] = ranks[i]
        cdef Group group = <Group>New(type(self))
        CHKERR( MPI_Group_range_incl(self.ob_mpi, n, ranges, &group.ob_mpi) )
        return group

    def Range_excl(self, ranks: Sequence[tuple[int, int, int]]) -> Self:
        """
        Create a new group by excluding ranges of members.
        """
        cdef int *p = NULL, (*ranges)[3]# = NULL ## XXX cython fails
        ranges = NULL
        cdef int n = <int>len(ranks)
        cdef unused1 = allocate(n, sizeof(int[3]), &ranges)
        for i in range(n):
            p = <int*> ranges[i]
            p[0], p[1], p[2] = ranks[i]
        cdef Group group = <Group>New(type(self))
        CHKERR( MPI_Group_range_excl(self.ob_mpi, n, ranges, &group.ob_mpi) )
        return group

    @classmethod
    def Create_from_session_pset(
        cls,
        Session session: Session,
        pset_name: str,
    ) -> Self:
        """
        Create a new group from session and process set.
        """
        cdef char *cname = NULL
        pset_name = asmpistr(pset_name, &cname)
        cdef Group group = <Group>New(cls)
        CHKERR( MPI_Group_from_session_pset(
            session.ob_mpi, cname, &group.ob_mpi) )
        return group

    # Group Destructor
    # ----------------

    def Free(self) -> None:
        """
        Free a group.
        """
        CHKERR( MPI_Group_free(&self.ob_mpi) )
        if self is __GROUP_EMPTY__: self.ob_mpi = MPI_GROUP_EMPTY

    # Fortran Handle
    # --------------

    def py2f(self) -> int:
        """
        """
        return MPI_Group_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg: int) -> Group:
        """
        """
        return fromhandle(MPI_Group_f2c(arg))


cdef Group __GROUP_NULL__  = def_Group ( MPI_GROUP_NULL  , "GROUP_NULL"  )
cdef Group __GROUP_EMPTY__ = def_Group ( MPI_GROUP_EMPTY , "GROUP_EMPTY" )


# Predefined group handles
# ------------------------

GROUP_NULL  = __GROUP_NULL__   #: Null group handle
GROUP_EMPTY = __GROUP_EMPTY__  #: Empty group handle
