# -----------------------------------------------------------------------------

# From dlpack.h (as of v0.8)

cdef extern from * nogil:
    ctypedef unsigned char      uint8_t
    ctypedef unsigned short     uint16_t
    ctypedef signed   int       int32_t
    ctypedef unsigned int       uint32_t
    ctypedef signed   long long int64_t
    ctypedef unsigned long long uint64_t

ctypedef struct DLPackVersion:
    uint32_t major
    uint32_t minor

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
    kDLOneAPI = 14
    kDLWebGPU = 15
    kDLHexagon = 16
    kDLMAIA = 17

ctypedef struct DLDevice:
    DLDeviceType device_type
    int32_t device_id

ctypedef enum DLDataTypeCode:
    kDLInt = 0
    kDLUInt = 1
    kDLFloat = 2
    kDLOpaqueHandle = 3
    kDLBfloat = 4
    kDLComplex = 5
    kDLBool = 6

ctypedef struct DLDataType:
    uint8_t code
    uint8_t bits
    uint16_t lanes

ctypedef struct DLTensor:
    void *data
    DLDevice device
    int32_t ndim
    DLDataType dtype
    int64_t *shape
    int64_t *strides
    uint64_t byte_offset

ctypedef struct DLManagedTensor:
    DLTensor dl_tensor
    void *manager_ctx
    void (*deleter)(DLManagedTensor *)

ctypedef enum:
    DLPACK_FLAG_BITMASK_READ_ONLY = (1UL << 0UL)
    DLPACK_FLAG_BITMASK_IS_COPIED = (1UL << 1UL)

ctypedef struct DLManagedTensorVersioned:
    DLPackVersion version
    void *manager_ctx
    void (*deleter)(DLManagedTensorVersioned *)
    uint64_t flags
    DLTensor dl_tensor

# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    void* PyCapsule_GetPointer(object, const char[]) except? NULL
    int PyCapsule_SetName(object, const char[]) except -1
    int PyCapsule_IsValid(object, const char[])

# -----------------------------------------------------------------------------

cdef inline int dlpack_check_version(
    const DLPackVersion *version,
    unsigned version_major,
) except -1:
    if version == NULL: return 0
    if version.major >= version_major: return 0
    raise BufferError("dlpack: unexpected version")

cdef inline int dlpack_is_contig(
    const DLTensor *dltensor,
    char order,
) noexcept nogil:
    cdef int i, ndim = dltensor.ndim
    cdef int64_t *shape = dltensor.shape
    cdef int64_t *strides = dltensor.strides
    cdef int64_t start, step, index, dim, size = 1
    if strides == NULL:
        return order != c'F' or ndim <= 1
    if order == c'F':
        start = 0
        step = 1
    else:
        start = ndim - 1
        step = -1
    for i in range(ndim):
        index = start + step * i
        dim = shape[index]
        if dim > 1 and size != strides[index]:
            return 0
        size *= dim
    return 1

cdef inline int dlpack_check_shape(const DLTensor *dltensor) except -1:
    cdef int i, ndim = dltensor.ndim
    if ndim < 0:
        raise BufferError("dlpack: number of dimensions is negative")
    if ndim > 0 and dltensor.shape == NULL:
        raise BufferError("dlpack: shape is NULL")
    for i in range(ndim):
        if dltensor.shape[i] < 0:
            raise BufferError("dlpack: shape item is negative")
    if dltensor.strides != NULL:
        for i in range(ndim):
            if dltensor.strides[i] < 0:
                raise BufferError("dlpack: strides item is negative")
    return 0

cdef inline int dlpack_check_contig(const DLTensor *dltensor) except -1:
    if dlpack_is_contig(dltensor, c'C'): return 0
    if dlpack_is_contig(dltensor, c'F'): return 0
    raise BufferError("dlpack: buffer is not contiguous")

cdef inline void *dlpack_get_data(
    const DLTensor *dltensor,
) noexcept nogil:
    return <char*> dltensor.data + dltensor.byte_offset

cdef inline Py_ssize_t dlpack_get_size(
    const DLTensor *dltensor,
) noexcept nogil:
    cdef int i, ndim = dltensor.ndim
    cdef int64_t *shape = dltensor.shape
    cdef Py_ssize_t bits = dltensor.dtype.bits
    cdef Py_ssize_t lanes = dltensor.dtype.lanes
    cdef Py_ssize_t size = 1
    for i in range(ndim):
        size *= <Py_ssize_t> shape[i]
    size *= (bits * lanes + 7) // 8
    return size

cdef inline char *dlpack_get_format(
    const DLTensor *dltensor,
) noexcept nogil:
    cdef unsigned int code = dltensor.dtype.code
    cdef unsigned int bits = dltensor.dtype.bits
    if dltensor.dtype.lanes != 1:
        if code == kDLFloat and dltensor.dtype.lanes == 2:
            if bits == 8*sizeof(float):       return b"Zf"
            if bits == 8*sizeof(double):      return b"Zd"
            if bits == 8*sizeof(long double): return b"Zg"
        return b"B"
    if code == kDLBool:
        if bits == 8: return b"?"
    if code == kDLInt:
        if bits == 8*sizeof(char):      return b"b"
        if bits == 8*sizeof(short):     return b"h"
        if bits == 8*sizeof(int):       return b"i"
        if bits == 8*sizeof(long):      return b"l"
        if bits == 8*sizeof(long long): return b"q"  # ~> long
    if code == kDLUInt:
        if bits == 8*sizeof(char):      return b"B"
        if bits == 8*sizeof(short):     return b"H"
        if bits == 8*sizeof(int):       return b"I"
        if bits == 8*sizeof(long):      return b"L"
        if bits == 8*sizeof(long long): return b"Q"  # ~> long
    if code == kDLFloat:
        if bits ==  8*sizeof(float)//2:    return b"e"
        if bits ==  8*sizeof(float):       return b"f"
        if bits ==  8*sizeof(double):      return b"d"
        if bits ==  8*sizeof(long double): return b"g"
    if code == kDLComplex:
        if bits ==  8*2*sizeof(float)//2:    return b"Ze"
        if bits ==  8*2*sizeof(float):       return b"Zf"
        if bits ==  8*2*sizeof(double):      return b"Zd"
        if bits ==  8*2*sizeof(long double): return b"Zg"  # ~> uncovered
    return BYTE_FMT

cdef inline Py_ssize_t dlpack_get_itemsize(
    const DLTensor *dltensor,
) noexcept nogil:
    cdef unsigned int code = dltensor.dtype.code
    cdef unsigned int bits = dltensor.dtype.bits
    if dltensor.dtype.lanes != 1:
        if code == kDLFloat and dltensor.dtype.lanes == 2:
            if (
                bits == 8*sizeof(float) or
                bits == 8*sizeof(double) or
                bits == 8*sizeof(long double)
            ):
                return <Py_ssize_t> bits // 8 * 2
        bits = 1
    return <Py_ssize_t> (bits + 7) // 8

# -----------------------------------------------------------------------------

cdef int Py_CheckDLPackBuffer(object obj) noexcept:
    try:    return <bint>hasattr(obj, '__dlpack__')
    except: return 0  # ~> uncovered  # noqa

cdef int Py_GetDLPackBuffer(object obj, Py_buffer *view, int flags) except -1:
    cdef unsigned version_major = 1
    cdef const char *capsulename = b"dltensor_versioned"
    cdef const char *usedcapsulename  = b"used_dltensor_versioned"
    cdef uint64_t READONLY = DLPACK_FLAG_BITMASK_READ_ONLY
    cdef object dlpack
    cdef object dlpack_device
    cdef tuple max_version
    cdef unsigned device_type
    cdef int device_id
    cdef object capsule
    cdef void *pointer
    cdef DLManagedTensorVersioned *managed1 = NULL
    cdef DLManagedTensor *managed0 = NULL
    cdef const DLPackVersion *dlversion
    cdef const DLTensor *dltensor
    cdef void *buf
    cdef Py_ssize_t size
    cdef Py_ssize_t itemsize
    cdef char *format
    cdef bint readonly

    try:
        dlpack = obj.__dlpack__
        dlpack_device = obj.__dlpack_device__
    except AttributeError:
        raise NotImplementedError("dlpack: missing support")

    device_type, device_id = dlpack_device()
    <void> device_id  # unused

    try:  # DLPack v1.0+
        max_version = (version_major, 0)
        if device_type == kDLCPU:
            capsule = dlpack(max_version=max_version, copy=False)
        else:
            capsule = dlpack(stream=-1, max_version=max_version, copy=False)
    except TypeError:  # DLPack v0.x
        version_major = 0
        capsulename = b"dltensor"
        usedcapsulename = b"used_dltensor"
        if device_type == kDLCPU:
            capsule = dlpack()
        else:
            capsule = dlpack(stream=-1)

    if not PyCapsule_IsValid(capsule, capsulename):
        raise BufferError("dlpack: invalid capsule object")
    pointer = PyCapsule_GetPointer(capsule, capsulename)
    if version_major >= 1:
        managed1  = <DLManagedTensorVersioned*> pointer
        dlversion = &managed1.version
        dltensor  = &managed1.dl_tensor
        readonly  = (managed1.flags & READONLY) == READONLY
    else:
        managed0  = <DLManagedTensor*> pointer
        dlversion = NULL
        dltensor  = &managed0.dl_tensor
        readonly  = 0

    try:
        dlpack_check_version(dlversion, version_major)
        dlpack_check_shape(dltensor)
        dlpack_check_contig(dltensor)
        buf = dlpack_get_data(dltensor)
        size = dlpack_get_size(dltensor)
        itemsize = dlpack_get_itemsize(dltensor)
        format = dlpack_get_format(dltensor)
    finally:
        if managed1 != NULL:
            if managed1.deleter != NULL:
                managed1.deleter(managed1)
        if managed0 != NULL:
            if managed0.deleter != NULL:
                managed0.deleter(managed0)
        PyCapsule_SetName(capsule, usedcapsulename)
        del capsule

    if PYPY and readonly and ((flags & PyBUF_WRITABLE) == PyBUF_WRITABLE):
        raise BufferError("Object is not writable")  # ~> pypy

    PyBuffer_FillInfo(view, obj, buf, size, readonly, flags)

    if (flags & PyBUF_FORMAT) == PyBUF_FORMAT:
        view.format = format
        if view.format != BYTE_FMT:
            view.itemsize = itemsize

    return <int> device_type

# -----------------------------------------------------------------------------
