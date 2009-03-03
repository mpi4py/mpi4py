#---------------------------------------------------------------------

cdef extern from *:
    ctypedef unsigned long int size_t

#---------------------------------------------------------------------

cdef extern from * nogil: # "stdlib.h"
    void* malloc(size_t)
    void* realloc(void*, size_t)
    void free(void*)

#---------------------------------------------------------------------

cdef extern from * nogil: # "string.h"
    int memcmp(void*, void*, size_t)
    void* memset(void*, int, size_t)
    void* memcpy(void*, void*, size_t)
    void* memmove(void*, void*, size_t)

#---------------------------------------------------------------------

cdef extern from * nogil: # "stdio.h"
    ctypedef struct FILE
    FILE *stdin, *stdout, *stderr
    int fprintf(FILE *, char *, ...)

#---------------------------------------------------------------------
