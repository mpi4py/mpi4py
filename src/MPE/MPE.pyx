__doc__ = u"""
Multi-Processing Environment
"""

# -----------------------------------------------------------------------------

include "mpelog.pxi"
include "helpers.pxi"

# -----------------------------------------------------------------------------

cdef class Log:

    @classmethod
    def Init(cls, filename=None):
        global MPELog_INIT
        global MPELog_EXIT
        cdef char *cfilename = NULL
        cfilename = LogFileName(filename)
        if MPELog_INIT:
            CHKERR( MPELog.Init() )
            if not MPELog_EXIT:
                import atexit
                atexit.register(Log.Finish)
                MPELog_EXIT = 1

    @classmethod
    def Finish(cls):
        cdef char *cfilename = NULL
        cfilename = LogFileName(None)
        if MPELog_INIT:
            CHKERR( MPELog.Finish(cfilename) )

    @classmethod
    def Start(cls):
        assert_ready()
        CHKERR( MPELog.Start() )

    @classmethod
    def Stop(cls):
        assert_ready()
        CHKERR( MPELog.Stop() )

    @classmethod
    def Sync(cls):
        assert_ready()
        CHKERR( MPELog.SyncClocks() )

    @classmethod
    def State(cls, name=None, color=None):
        cdef LogState state = LogState()
        #
        cdef char *cname = NULL
        cdef char *ccolor = b"red"
        if name  is not None: 
            if not isinstance(name, bytes):
                name = name.encode()
            cname = name
        if color is not None: 
            if not isinstance(color, bytes):
                color = color.encode()
            ccolor = color
        #
        assert_ready()
        #
        if 1: state.commID = 2
        else: state.commID = 1
        CHKERR( MPELog.newState(state.commID,
                                cname, ccolor, NULL,
                                state.stateID) )
        state.isActive = 1
        #
        return state

    @classmethod
    def Event(cls, name=None, color=None):
        cdef LogEvent event = LogEvent()
        #
        cdef char *cname = NULL
        cdef char *ccolor = b"blue"
        if name  is not None: 
            if not isinstance(name, bytes):
                name = name.encode()
            cname = name
        if color is not None: 
            if not isinstance(color, bytes):
                color = color.encode()
            ccolor = color
        #
        assert_ready()
        #
        if 1: event.commID = 2
        else: event.commID = 1
        CHKERR( MPELog.newEvent(event.commID,
                                cname, ccolor, NULL,
                                event.eventID) )
        event.isActive = 1
        #
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
