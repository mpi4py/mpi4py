#---------------------------------------------------------------------

cdef extern from *:
    ctypedef unsigned long size_t

#---------------------------------------------------------------------

cdef extern from "stdlib.h":
    void* malloc(size_t)
    void* realloc(void*, size_t)
    void free(void*)

#---------------------------------------------------------------------

cdef extern from "string.h":
    int memcmp(void*, void*, size_t)
    void* memset(void*, int, size_t)
    void* memcpy(void*, void*, size_t)
    void* memmove(void*, void*, size_t)

#---------------------------------------------------------------------
