__doc__ = u"""
Multi-Processing Environment
"""

# -----------------------------------------------------------------------------

include "mpe-log.pxi"
include "helpers.pxi"

# -----------------------------------------------------------------------------

cdef class Log:

    @classmethod
    def init(cls, filename=None):
        initialize()
        cls.setFileName(filename)

    @classmethod
    def finish(cls):
        CHKERR( finalize() )

    @classmethod
    def setFileName(cls, filename):
        cdef char *cfilename = b"Unknown"
        filename = toBytes(filename,  &cfilename)
        strncpy(logFileName, cfilename, 255)[255] = 0

    @classmethod
    def syncClocks(cls):
        if not isReady(): return
        CHKERR( MPELog.SyncClocks() )

    @classmethod
    def start(cls):
        if not isReady(): return
        CHKERR( MPELog.Start() )

    @classmethod
    def stop(cls):
        if not isReady(): return
        CHKERR( MPELog.Stop() )

    @classmethod
    def State(cls, name=None, color=None):
        cdef LogState state = LogState()
        cdef char *cname = NULL
        cdef char *ccolor = b"red"
        name  = toBytes(name,  &cname)
        color = toBytes(color, &ccolor)
        #
        if not isReady(): return state
        if 1: state.commID = 2 # MPI_COMM_WORLD
        else: state.commID = 1 # MPI_COMM_SELF
        CHKERR( MPELog.newState(state.commID,
                                cname, ccolor, NULL,
                                state.stateID) )
        state.isActive = 1
        return state

    @classmethod
    def Event(cls, name=None, color=None):
        cdef LogEvent event = LogEvent()
        cdef char *cname = NULL
        cdef char *ccolor = b"blue"
        name  = toBytes(name,  &cname)
        color = toBytes(color, &ccolor)
        #
        if not isReady(): return
        if 1: event.commID = 2 # MPI_COMM_WORLD
        else: event.commID = 1 # MPI_COMM_SELF
        CHKERR( MPELog.newEvent(event.commID,
                                cname, ccolor, NULL,
                                event.eventID) )
        event.isActive = 1
        return event


cdef class LogState:

    cdef int commID
    cdef int stateID[2]
    cdef int isActive

    def __cinit__(self):
        self.commID = 0
        self.stateID[0] = 0
        self.stateID[1] = 0
        self.isActive = 0

    def __enter__(self):
        self.enter()
        return self

    def __exit__(self, *exc):
        self.exit()

    def enter(self):
        if not isReady(): return
        if not self.commID: return
        if not self.isActive: return
        CHKERR( MPELog.logEvent(self.commID, self.stateID[0], NULL) )

    def exit(self):
        if not isReady(): return
        if not self.commID: return
        if not self.isActive: return
        CHKERR( MPELog.logEvent(self.commID, self.stateID[1], NULL) )

    property stateID:
        def __get__(self):
            return (self.stateID[0], self.stateID[1])

    property active:
        def __get__(self):
            return <bint> self.isActive
        def __set__(self, bint active):
            self.isActive = active


cdef class LogEvent:

    cdef int commID
    cdef int eventID[1]
    cdef int isActive

    def __cinit__(self):
        self.commID = 0
        self.eventID[0] = 0
        self.isActive = 0

    def __call__(self):
        self.log()

    def log(self):
        if not isReady(): return
        if not self.commID: return
        if not self.isActive: return
        CHKERR( MPELog.logEvent(self.commID, self.eventID[0], NULL) )

    property eventID:
        def __get__(self):
            return self.eventID[0]

    property active:
        def __get__(self):
            return <bint> self.isActive
        def __set__(self, bint active):
            self.isActive = active

# -----------------------------------------------------------------------------
