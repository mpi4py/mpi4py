#------------------------------------------------------------------------------

cdef extern from * nogil:
    ctypedef unsigned char      uint8_t
    ctypedef unsigned short     uint16_t
    ctypedef signed   long long int64_t
    ctypedef unsigned long long uint64_t

ctypedef enum DLDeviceType:
    kDLCPU = 1
    kDLCUDA = 2
    kDLCUDAHost = 3
    kDLOpenCL = 4
    kDLVulkan = 7
    kDLMetal = 8
    kDLVPI = 9
    kDLROCM = 10
    kDLROCMHost = 11
    kDLExtDev = 12
    kDLCUDAManaged = 13

ctypedef struct DLDevice:
  DLDeviceType device_type
  int device_id

ctypedef enum DLDataTypeCode:
    kDLInt = 0
    kDLUInt = 1
    kDLFloat = 2
    kDLOpaqueHandle = 3
    kDLBfloat = 4
    kDLComplex = 5

ctypedef struct DLDataType:
    uint8_t code
    uint8_t bits
    uint16_t lanes

ctypedef struct DLTensor:
    void *data
    DLDevice device
    int ndim
    DLDataType dtype
    int64_t *shape
    int64_t *strides
    uint64_t byte_offset

ctypedef struct DLManagedTensor:
    DLTensor dl_tensor
    void *manager_ctx
    void (*deleter)(DLManagedTensor *)

#------------------------------------------------------------------------------

cdef extern from "Python.h":
    void* PyCapsule_GetPointer(object, const char[]) except? NULL
    int PyCapsule_SetName(object, const char[]) except -1
    int PyCapsule_IsValid(object, const char[])

#------------------------------------------------------------------------------

cdef inline int dlpack_is_contig(const DLTensor *dltensor, char order) nogil:
    cdef int i, ndim = dltensor.ndim
    cdef int64_t *shape = dltensor.shape
    cdef int64_t *strides = dltensor.strides
    cdef int64_t start, step, index, size = 1
    if strides == NULL:
        if ndim > 1 and order == c'F':
            return 0
        return 1
    if order == c'F':
        start = 0
        step = 1
    else:
        start = ndim - 1
        step = -1
    for i from 0 <= i < ndim:
        index = start + step * i
        if size != strides[index]:
            return 0
        size *= shape[index]
    return 1

cdef inline int dlpack_check_shape(const DLTensor *dltensor) except -1:
    cdef int i, ndim = dltensor.ndim
    if ndim < 0:
        raise BufferError("dlpack: number of dimensions is negative")
    if ndim > 0 and dltensor.shape == NULL:
        raise BufferError("dlpack: shape is NULL")
    for i from 0 <= i < ndim:
        if dltensor.shape[i] < 0:
            raise BufferError("dlpack: shape item is negative")
    if dltensor.strides != NULL:
        for i from 0 <= i < ndim:
            if dltensor.strides[i] < 0:
                raise BufferError("dlpack: strides item is negative")
    return 0

cdef inline int dlpack_check_contig(const DLTensor *dltensor) except -1:
    if dltensor.strides == NULL: return 0
    if dlpack_is_contig(dltensor, c'C'): return 0
    if dlpack_is_contig(dltensor, c'F'): return 0
    raise BufferError("dlpack: buffer is not contiguous")

cdef inline void *dlpack_get_data(const DLTensor *dltensor) nogil:
    return <char*> dltensor.data + dltensor.byte_offset

cdef inline Py_ssize_t dlpack_get_size(const DLTensor *dltensor) nogil:
    cdef int i, ndim = dltensor.ndim
    cdef int64_t *shape = dltensor.shape
    cdef Py_ssize_t bits = dltensor.dtype.bits
    cdef Py_ssize_t lanes = dltensor.dtype.lanes
    cdef Py_ssize_t size = 1
    for i from 0 <= i < ndim:
        size *= <Py_ssize_t> shape[i]
    size *= (bits * lanes + 7) // 8
    return size

cdef inline char *dlpack_get_format(const DLTensor *dltensor) nogil:
    cdef unsigned int code = dltensor.dtype.code
    cdef unsigned int bits = dltensor.dtype.bits
    if dltensor.dtype.lanes != 1: return BYTE_FMT
    if code == kDLInt:
        if bits == 1*8: return b"i1"
        if bits == 2*8: return b"i2"
        if bits == 4*8: return b"i4"
        if bits == 8*8: return b"i8"
    if code == kDLUInt:
        if bits == 1*8: return b"u1"
        if bits == 2*8: return b"u2"
        if bits == 4*8: return b"u4"
        if bits == 8*8: return b"u8"
    if code == kDLFloat:
       if bits ==  2*8: return b"f2"
       if bits ==  4*8: return b"f4"
       if bits ==  8*8: return b"f8"
       if bits == 12*8: return b"f12"
       if bits == 16*8: return b"f16"
    if code == kDLComplex:
       if bits ==  4*8: return b"c4"
       if bits ==  8*8: return b"c8"
       if bits == 16*8: return b"c16"
       if bits == 24*8: return b"c24"
       if bits == 32*8: return b"c32"
    return BYTE_FMT

cdef inline Py_ssize_t dlpack_get_itemsize(const DLTensor *dltensor) nogil:
    if dltensor.dtype.lanes != 1: return 1
    return (dltensor.dtype.bits + 7) // 8

#------------------------------------------------------------------------------

cdef int Py_CheckDLPackBuffer(object obj):
    try: return <bint>hasattr(obj, '__dlpack__')
    except: return 0

cdef int Py_GetDLPackBuffer(object obj, Py_buffer *view, int flags) except -1:
    cdef object dlpack
    cdef object dlpack_device
    cdef int device_type
    cdef int device_id
    cdef object capsule
    cdef DLManagedTensor *managed
    cdef const DLTensor *dltensor
    cdef void *buf
    cdef Py_ssize_t size
    cdef bint readonly
    cdef bint fixnull

    try:
        dlpack = obj.__dlpack__
    except AttributeError:
        raise NotImplementedError("dlpack: missing __dlpack__ method")

    try:
        dlpack_device = obj.__dlpack_device__
    except AttributeError:
        dlpack_device = None
    if dlpack_device is not None:
        device_type, device_id = dlpack_device()
    else:
        device_type, devide_id = kDLCPU, 0
    if device_type == kDLCPU:
        capsule = dlpack()
    else:
        capsule = dlpack(stream=-1)
    if not PyCapsule_IsValid(capsule, b"dltensor"):
        raise BufferError("dlpack: invalid capsule object")

    managed = <DLManagedTensor*> PyCapsule_GetPointer(capsule, b"dltensor")
    dltensor = &managed.dl_tensor

    try:
        dlpack_check_shape(dltensor)
        dlpack_check_contig(dltensor)

        buf = dlpack_get_data(dltensor)
        size = dlpack_get_size(dltensor)
        readonly = 0

        fixnull = (buf == NULL and size == 0)
        if fixnull: buf = &fixnull
        PyBuffer_FillInfo(view, obj, buf, size, readonly, flags)
        if fixnull: view.buf = NULL

        if (flags & PyBUF_FORMAT) == PyBUF_FORMAT:
            view.format = dlpack_get_format(dltensor)
            if view.format != BYTE_FMT:
                view.itemsize = dlpack_get_itemsize(dltensor)
    finally:
        if managed.deleter != NULL:
            managed.deleter(managed)
        PyCapsule_SetName(capsule, b"used_dltensor")
        del capsule
    return 0

#------------------------------------------------------------------------------
