#---------------------------------------------------------------------

cdef extern from *:
    ctypedef unsigned long int size_t

#---------------------------------------------------------------------

cdef extern from "stdlib.h" nogil:
    void* malloc(size_t)
    void* realloc(void*, size_t)
    void free(void*)

#---------------------------------------------------------------------

cdef extern from "string.h" nogil:
    int memcmp(void*, void*, size_t)
    void* memset(void*, int, size_t)
    void* memcpy(void*, void*, size_t)
    void* memmove(void*, void*, size_t)

#---------------------------------------------------------------------

cdef extern from "stdio.h" nogil:
    ctypedef struct FILE
    FILE *stdin, *stdout, *stderr
    int fprintf(FILE *, char *, ...)

#---------------------------------------------------------------------
