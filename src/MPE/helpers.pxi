# -----------------------------------------------------------------------------

if 0: raise RuntimeError # do not remove this line !!
cdef extern from *:
    void __Pyx_Raise(object, object, void*)

cdef inline int CHKERR(int ierr) except -1:
    if ierr:
        __Pyx_Raise(RuntimeError, ("error code: %d" % ierr), NULL)
        return -1
    return 0

# -----------------------------------------------------------------------------

cdef object LOGFILENAME = b"Unknown"

cdef inline char* LogFileName(object logfilename) except NULL:
    global LOGFILENAME
    cdef char *clogfilename = NULL
    if logfilename:
        if not isinstance(logfilename, bytes):
            logfilename = logfilename.encode()
        clogfilename = logfilename
        LOGFILENAME  = logfilename
    else:
        if NULL == <void*>LOGFILENAME:
            clogfilename = b"Unknown"
        else:
            clogfilename = LOGFILENAME
    return clogfilename

# -----------------------------------------------------------------------------

cdef inline int isReady() nogil:
    return (MPELog.Initialized() == 1)

cdef inline int assert_ready() except -1:
    cdef initialized = MPELog.Initialized()
    if initialized == 0:
        __Pyx_Raise(RuntimeError, ("MPE is not initialized"), NULL)
        return -1
    elif initialized == 2:
        __Pyx_Raise(RuntimeError, ("MPE has finalized"), NULL)
        return -1
    return 1

# -----------------------------------------------------------------------------

cdef inline int pack_arglist(object arglist, char bytebuf[]) except -1:
    cdef int  pos    = 0
    cdef char token  = 0
    cdef int  count  = 0
    cdef char *data  = NULL
    #
    cdef long   idata = 0
    cdef double fdata = 0
    cdef char*  sdata = NULL
    #
    bytebuf[0] = 0
    for arg in arglist:
        #
        if isinstance(arg, int):
            if sizeof(long) == 4:
                token = c'd'
            else:
                token = c'l'
            idata = arg
            count = 1
            data = <char*>&idata
        elif isinstance(arg, float):
            token = c'E'
            fdata = arg
            count = 1
            data = <char*>&fdata
        elif isinstance(arg, str):
            token = c's'
            sdata = arg
            count = <int>len(arg)
            data = <char*>sdata
        else:
            token = 0
            count = 0
            data  = NULL
            continue
        #
        CHKERR( MPELog.packBytes(bytebuf, &pos, token, count, data) )
    return 0

# -----------------------------------------------------------------------------

#cdef colornames = ["white", "black", "red", "yellow", "green",
#                   "cyan", "blue", "magenta", "aquamarine",
#                   "forestgreen", "orange", "marroon", "brown",
#                   "pink", "coral", "gray" ]
