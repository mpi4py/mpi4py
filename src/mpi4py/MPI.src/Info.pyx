cdef class Info:
    """
    Info object.
    """

    def __cinit__(self, Info info: Info | None = None):
        cinit(self, info)

    def __dealloc__(self):
        dealloc(self)

    def __richcmp__(self, other, int op):
        if not isinstance(other, Info): return NotImplemented
        return richcmp(self, other, op)

    def __bool__(self) -> bool:
        return nonnull(self)

    def __reduce__(self) -> str | tuple[Any, ...]:
        return reduce_Info(self)

    property handle:
        """MPI handle."""
        def __get__(self) -> int:
            return tohandle(self)

    @classmethod
    def fromhandle(cls, handle: int) -> Info:
        """
        Create object from MPI handle.
        """
        return fromhandle(<MPI_Info> <Py_uintptr_t> handle)

    def free(self) -> None:
        """
        Call `Free` if not null or predefined.
        """
        safefree(self)

    # The Info Object
    # ---------------

    @classmethod
    def Create(
        cls,
        items: (
            Info |
            Mapping[str, str] |
            Iterable[tuple[str, str]] |
            None
        ) = None,
    ) -> Self:
        """
        Create a new info object.
        """
        cdef Info info = <Info>New(cls)
        CHKERR( MPI_Info_create(&info.ob_mpi) )
        if items is None: return info
        cdef object key, value
        try:
            if hasattr(items, 'keys'):
                for key in items.keys():
                    info.Set(key, items[key])
            else:
                for key, value in items:
                    info.Set(key, value)
        except:  # noqa
            CHKERR( MPI_Info_free(&info.ob_mpi) )
            raise
        return info

    @classmethod
    def Create_env(cls, args: Sequence[str] | None = None) -> Self:
        """
        Create a new environment info object.
        """
        cdef int argc = 0
        cdef char **argv = MPI_ARGV_NULL
        cdef Info info = <Info>New(cls)
        args = asarray_argv(args, &argv)
        while argv and argv[argc]: argc += 1
        CHKERR( MPI_Info_create_env(argc, argv, &info.ob_mpi) )
        return info

    def Free(self) -> None:
        """
        Free an info object.
        """
        CHKERR( MPI_Info_free(&self.ob_mpi) )
        if self is __INFO_ENV__: self.ob_mpi = MPI_INFO_ENV

    def Dup(self) -> Self:
        """
        Duplicate an existing info object.
        """
        cdef Info info = <Info>New(type(self))
        CHKERR( MPI_Info_dup(self.ob_mpi, &info.ob_mpi) )
        return info

    def Get(self, key: str) -> str | None:
        """
        Retrieve the value associated with a key.
        """
        cdef char *ckey = NULL
        cdef char *cvalue = NULL
        cdef int buflen = MPI_MAX_INFO_VAL
        cdef int flag = 0
        key = asmpistr(key, &ckey)
        cdef unused = allocate(buflen+1, sizeof(char), &cvalue)
        CHKERR( MPI_Info_get_string(self.ob_mpi, ckey, &buflen, cvalue, &flag) )
        if not flag: return None
        return mpistr(cvalue)

    def Set(self, key: str, value: str) -> None:
        """
        Store a value associated with a key.
        """
        cdef char *ckey = NULL
        cdef char *cvalue = NULL
        key = asmpistr(key, &ckey)
        value = asmpistr(value, &cvalue)
        CHKERR( MPI_Info_set(self.ob_mpi, ckey, cvalue) )

    def Delete(self, key: str) -> None:
        """
        Remove a (key, value) pair from info.
        """
        cdef char *ckey = NULL
        key = asmpistr(key, &ckey)
        CHKERR( MPI_Info_delete(self.ob_mpi, ckey) )

    def Get_nkeys(self) -> int:
        """
        Return the number of currently defined keys in info.
        """
        cdef int nkeys = 0
        CHKERR( MPI_Info_get_nkeys(self.ob_mpi, &nkeys) )
        return nkeys

    def Get_nthkey(self, int n: int) -> str:
        """
        Return the *n*-th defined key in info.
        """
        cdef char ckey[MPI_MAX_INFO_KEY+1]
        ckey[0] = 0  # just in case
        CHKERR( MPI_Info_get_nthkey(self.ob_mpi, n, ckey) )
        ckey[MPI_MAX_INFO_KEY] = 0  # just in case
        return mpistr(ckey)

    # Fortran Handle
    # --------------

    def py2f(self) -> int:
        """
        """
        return MPI_Info_c2f(self.ob_mpi)

    @classmethod
    def f2py(cls, arg: int) -> Info:
        """
        """
        return fromhandle(MPI_Info_f2c(arg))

    # Python mapping emulation
    # ------------------------

    def __len__(self) -> int:
        if not self: return 0
        return self.Get_nkeys()

    def __contains__(self, key: str) -> bool:
        if not self: return False
        cdef char *ckey = NULL
        cdef char cvalue[1]
        cdef int buflen = 0
        cdef int flag = 0
        key = asmpistr(key, &ckey)
        CHKERR( MPI_Info_get_string(self.ob_mpi, ckey, &buflen, cvalue, &flag) )
        return <bint>flag

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    def __getitem__(self, key: str) -> str:
        if not self: raise KeyError(key)
        cdef object value = self.Get(key)
        if value is None: raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: str) -> None:
        if not self: raise KeyError(key)
        self.Set(key, value)

    def __delitem__(self, key: str) -> None:
        if not self: raise KeyError(key)
        if key not in self: raise KeyError(key)
        self.Delete(key)

    def get(self, key: str, default: str | None = None) -> str | None:
        """Retrieve value by key."""
        if not self: return default
        cdef object value = self.Get(key)
        if value is None: return default
        return value

    def keys(self) -> list[str]:
        """Return list of keys."""
        if not self: return []
        cdef list keys = []
        cdef int nkeys = self.Get_nkeys()
        cdef object key
        for k in range(nkeys):
            key = self.Get_nthkey(k)
            keys.append(key)
        return keys

    def values(self) -> list[str]:
        """Return list of values."""
        if not self: return []
        cdef list values = []
        cdef int nkeys = self.Get_nkeys()
        cdef object key, val
        for k in range(nkeys):
            key = self.Get_nthkey(k)
            val = self.Get(key)
            values.append(val)
        return values

    def items(self) -> list[tuple[str, str]]:
        """Return list of items."""
        if not self: return []
        cdef list items = []
        cdef int nkeys = self.Get_nkeys()
        cdef object key, value
        for k in range(nkeys):
            key = self.Get_nthkey(k)
            value = self.Get(key)
            items.append((key, value))
        return items

    def update(
        self,
        items: Info | Mapping[str, str] | Iterable[tuple[str, str]] = (),
        **kwds: str,
    ) -> None:
        """Update contents."""
        if not self: raise KeyError
        cdef object key, value
        if hasattr(items, 'keys'):
            for key in items.keys():
                self.Set(key, items[key])
        else:
            for key, value in items:
                self.Set(key, value)
        for key, value in kwds.items():
            self.Set(key, value)

    def pop(self, key: str, *default: str) -> str:
        """Pop value by key."""
        cdef object value = None
        if self:
            value = self.Get(key)
        if value is not None:
            self.Delete(key)
            return value
        if default:
            value, = default
            return value
        raise KeyError(key)

    def popitem(self) -> tuple[str, str]:
        """Pop first item."""
        if not self: raise KeyError
        cdef object key, value
        cdef int nkeys = self.Get_nkeys()
        if nkeys == 0: raise KeyError
        key = self.Get_nthkey(nkeys - 1)
        value = self.Get(key)
        self.Delete(key)
        return (key, value)

    def copy(self) -> Self:
        """Copy contents."""
        if not self: return <Info>New(type(self))
        return self.Dup()

    def clear(self) -> None:
        """Clear contents."""
        if not self: return None
        cdef object key
        cdef int k = 0, nkeys = self.Get_nkeys()
        while k < nkeys:
            key = self.Get_nthkey(0)
            self.Delete(key)
            k += 1


cdef Info __INFO_NULL__ = def_Info( MPI_INFO_NULL , "INFO_NULL" )
cdef Info __INFO_ENV__  = def_Info( MPI_INFO_ENV  , "INFO_ENV"  )


# Predefined info handles
# -----------------------

INFO_NULL = __INFO_NULL__  #: Null info handle
INFO_ENV  = __INFO_ENV__   #: Environment info handle
