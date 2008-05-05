cdef class Info:

    """
    Info
    """

    def __cinit__(self):
        self.ob_mpi = MPI_INFO_NULL

    def __dealloc__(self):
        cdef int ierr = 0
        ierr = _del_Info(&self.ob_mpi); CHKERR(ierr)

    def __richcmp__(Info self, Info other, int op):
        if   op == 2: return (self.ob_mpi == other.ob_mpi)
        elif op == 3: return (self.ob_mpi != other.ob_mpi)
        else: raise TypeError("only '==' and '!='")

    def __nonzero__(self):
        return self.ob_mpi != MPI_INFO_NULL

    def __bool__(self):
        return self.ob_mpi != MPI_INFO_NULL

    def Create(cls):
        """
        Create a new, empty info object
        """
        cdef Info info = cls()
        CHKERR( MPI_Info_create(&info.ob_mpi) )
        return info

    Create = classmethod(Create)

    def Free(self):
        """
        Free a info object
        """
        CHKERR( MPI_Info_free(&self.ob_mpi) )

    def Dup(self):
        """
        Duplicate an existing info object, creating a new object, with
        the same (key, value) pairs and the same ordering of keys
        """
        cdef Info info = Info()
        CHKERR( MPI_Info_dup(self.ob_mpi, &info.ob_mpi) )
        return info

    def Get(self, char key[], int maxlen=-1):
        """
        Retrieve the value associated with a key
        """
        if maxlen < 0: maxlen = MPI_MAX_INFO_VAL
        if maxlen > MPI_MAX_INFO_VAL: maxlen = MPI_MAX_INFO_VAL
        cdef char *value = NULL
        cdef object tmp = allocate((maxlen+1), <void**>&value)
        cdef int flag = 0
        CHKERR( MPI_Info_get(self.ob_mpi, key, maxlen, value, &flag) )
        value[maxlen] = 0 # just in case
        if not flag: return (None, False)
        else:        return (value, True)

    def Set(self, char key[], char *value):
        """
        Add the (key,value) pair to info, and overrides the value if a
        value for the same key was previously set
        """
        CHKERR( MPI_Info_set(self.ob_mpi, key, value) )

    def Delete(self, char key[]):
        """
        Remove a (key,value) pair from info
        """
        CHKERR( MPI_Info_delete(self.ob_mpi, key) )

    def Get_nkeys(self):
        """
        Return the number of currently defined keys in info
        """
        cdef int nkeys = 0
        CHKERR( MPI_Info_get_nkeys(self.ob_mpi, &nkeys) )
        return nkeys

    def Get_nthkey(self, int n):
        """
        Return the nth defined key in info. Keys are numbered in the
        range [0, N) where N is the value returned by
        `Info.Get_nkeys()`
        """
        cdef char key[MPI_MAX_INFO_KEY+1]
        CHKERR( MPI_Info_get_nthkey(self.ob_mpi, n, key) )
        return key

    def __len__(self):
        if not self: return 0
        return self.Get_nkeys()

    def __contains__(self, char key[]):
        if not self: return False
        cdef int dummy = 0
        cdef bint haskey = 0
        CHKERR( MPI_Info_get_valuelen(self.ob_mpi, key,
                                      &dummy, &haskey) )
        return haskey

    def keys(self):
        """info keys"""
        if not self: return []
        cdef int nkeys = self.Get_nkeys()
        return [self.Get_nthkey(k) for k from 0 <= k < nkeys]

    def values(self):
        """info values"""
        if not self: return []
        cdef int nkeys = self.Get_nkeys()
        values = []
        for k from 0 <= k < nkeys:
            key = self.Get_nthkey(k)
            val, _ = self.Get(key)
            values.append(val)
        return values

    def items(self):
        """info items"""
        if not self: return []
        cdef int nkeys = self.Get_nkeys()
        items = []
        for k from 0 <= k < nkeys:
            key = self.Get_nthkey(k)
            val, _ = self.Get(key)
            items.append((key, val))
        return items

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, char key[]):
        if not self: raise KeyError(key)
        value, haskey = self.Get(key)
        if not haskey: raise KeyError(key)
        return value

    def __setitem__(self, char key[], char *value):
        if not self: raise KeyError(key)
        self.Set(key, value)

    def __delitem__(self, char key[]):
        if not self: raise KeyError(key)
        if key not in self: raise KeyError(key)
        self.Delete(key)



# Null info handle
# ----------------

INFO_NULL = _new_Info(MPI_INFO_NULL)
