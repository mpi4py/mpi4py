import ctypes
import sys
from enum import IntEnum

if hasattr(sys, "pypy_version_info"):
    raise ImportError("unsupported on PyPy")


class DLPackVersion(ctypes.Structure):
    #
    _fields_ = [
        ("major", ctypes.c_uint32),
        ("minor", ctypes.c_uint32),
    ]


class DLDeviceType(IntEnum):
    #
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


class DLDevice(ctypes.Structure):
    #
    _fields_ = [
        ("device_type", ctypes.c_uint),
        ("device_id", ctypes.c_int32),
    ]


class DLDataTypeCode(IntEnum):
    #
    kDLInt = 0
    kDLUInt = 1
    kDLFloat = 2
    kDLOpaqueHandle = 3
    kDLBfloat = 4
    kDLComplex = 5
    kDLBool = 6


class DLDataType(ctypes.Structure):
    #
    _fields_ = [
        ("code", ctypes.c_uint8),
        ("bits", ctypes.c_uint8),
        ("lanes", ctypes.c_uint16),
    ]


class DLTensor(ctypes.Structure):
    #
    _fields_ = [
        ("data", ctypes.c_void_p),
        ("device", DLDevice),
        ("ndim", ctypes.c_int32),
        ("dtype", DLDataType),
        ("shape", ctypes.POINTER(ctypes.c_int64)),
        ("strides", ctypes.POINTER(ctypes.c_int64)),
        ("byte_offset", ctypes.c_uint64),
    ]


DLManagedTensorDeleter = ctypes.CFUNCTYPE(None, ctypes.c_void_p)


class DLManagedTensor(ctypes.Structure):
    #
    _fields_ = [
        ("dl_tensor", DLTensor),
        ("manager_ctx", ctypes.c_void_p),
        ("deleter", DLManagedTensorDeleter),
    ]


DLPACK_FLAG_BITMASK_READ_ONLY = 1 << 0
DLPACK_FLAG_BITMASK_IS_COPIED = 1 << 1

DLManagedTensorVersionedDeleter = ctypes.CFUNCTYPE(None, ctypes.c_void_p)


class DLManagedTensorVersioned(ctypes.Structure):
    #
    _fields_ = [
        ("version", DLPackVersion),
        ("manager_ctx", ctypes.c_void_p),
        ("deleter", DLManagedTensorDeleter),
        ("flags", ctypes.c_uint64),
        ("dl_tensor", DLTensor),
    ]


pyapi = ctypes.pythonapi

DLManagedTensor_p = ctypes.POINTER(DLManagedTensor)
DLManagedTensorVersioned_p = ctypes.POINTER(DLManagedTensorVersioned)

Py_IncRef = pyapi.Py_IncRef
Py_IncRef.restype = None
Py_IncRef.argtypes = [ctypes.py_object]

Py_DecRef = pyapi.Py_DecRef
Py_DecRef.restype = None
Py_DecRef.argtypes = [ctypes.py_object]

PyCapsule_Destructor = ctypes.PYFUNCTYPE(None, ctypes.c_void_p)
PyCapsule_Destructor.from_param = classmethod(
    lambda _cls, arg: (
        ctypes._CFuncPtr.from_param(arg) if arg is not None else None
    )
)

PyCapsule_New = pyapi.PyCapsule_New
PyCapsule_New.restype = ctypes.py_object
PyCapsule_New.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    PyCapsule_Destructor,
]

PyCapsule_IsValid = pyapi.PyCapsule_IsValid
PyCapsule_IsValid.restype = ctypes.c_int
PyCapsule_IsValid.argtypes = [ctypes.py_object, ctypes.c_char_p]

PyCapsule_SetName = pyapi.PyCapsule_SetName
PyCapsule_SetName.restype = ctypes.c_int
PyCapsule_SetName.argtypes = [ctypes.py_object, ctypes.c_char_p]

PyCapsule_GetPointer = pyapi.PyCapsule_GetPointer
PyCapsule_GetPointer.restype = ctypes.c_void_p
PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]

PyCapsule_SetContext = pyapi.PyCapsule_SetContext
PyCapsule_SetContext.restype = ctypes.c_int
PyCapsule_SetContext.argtypes = [ctypes.py_object, ctypes.c_void_p]

PyCapsule_GetContext = pyapi.PyCapsule_GetContext
PyCapsule_GetContext.restype = ctypes.c_void_p
PyCapsule_GetContext.argtypes = [ctypes.py_object]


def make_dl_version(major, minor):
    version = DLPackVersion()
    version.major = major
    version.minor = minor
    return version


def make_dl_datatype(typecode, itemsize):
    code = None
    bits = itemsize * 8
    lanes = 1
    if typecode == "?":
        code = DLDataTypeCode.kDLBool
    if typecode in "bhilqnp":
        code = DLDataTypeCode.kDLInt
    if typecode in "BHILQNP":
        code = DLDataTypeCode.kDLUInt
    if typecode in "efdg":
        code = DLDataTypeCode.kDLFloat
    if typecode in "FDG":
        code = DLDataTypeCode.kDLComplex
    if typecode == "G" and itemsize == 32:
        code = DLDataTypeCode.kDLFloat
        bits //= 2
        lanes *= 2
    datatype = DLDataType()
    datatype.code = code
    datatype.bits = bits
    datatype.lanes = lanes
    return datatype


def make_dl_shape(shape, order=None, strides=None):
    null = ctypes.cast(0, ctypes.POINTER(ctypes.c_int64))
    if isinstance(shape, int):
        shape = [shape]
    ndim = len(shape)
    if ndim == 0:
        shape = null
        strides = null
    else:
        shape = (ctypes.c_int64 * ndim)(*shape)
        if order == "C":
            size = 1
            strides = []
            for i in range(ndim - 1, -1, -1):
                strides.append(size)
                size *= shape[i]
            strides = (ctypes.c_int64 * ndim)(*strides)
        elif order == "F":
            size = 1
            strides = []
            for i in range(ndim):
                strides.append(size)
                size *= shape[i]
            strides = (ctypes.c_int64 * ndim)(*strides)
        elif strides is not None:
            strides = (ctypes.c_int64 * ndim)(*strides)
        else:
            strides = null
    return ndim, shape, strides


def make_dl_tensor(obj):
    try:
        data, size = obj.buffer_info()
        typecode = obj.typecode
        itemsize = obj.itemsize
    except AttributeError:
        data = obj.ctypes.data
        size = obj.size
        typecode = obj.dtype.char
        itemsize = obj.itemsize

    device = DLDevice(DLDeviceType.kDLCPU, 0)
    datatype = make_dl_datatype(typecode, itemsize)
    ndim, shape, strides = make_dl_shape(size)

    dltensor = DLTensor()
    dltensor.data = data if size > 0 else 0
    dltensor.device = device
    dltensor.ndim = ndim
    dltensor.dtype = datatype
    dltensor.shape = shape
    dltensor.strides = strides
    dltensor.byte_offset = 0
    return dltensor


def make_dl_manager_ctx(obj):
    py_obj = ctypes.py_object(obj)
    void_p = ctypes.c_void_p.from_buffer(py_obj)
    return void_p


@DLManagedTensorDeleter
def dl_managed_tensor_deleter(void_p):
    managed = ctypes.cast(void_p, DLManagedTensor_p)
    manager_ctx = managed.contents.manager_ctx
    py_obj = ctypes.cast(manager_ctx, ctypes.py_object)
    obj = py_obj.value
    del obj


@DLManagedTensorVersionedDeleter
def dl_managed_tensor_versioned_deleter(void_p):
    managed = ctypes.cast(void_p, DLManagedTensorVersioned_p)
    manager_ctx = managed.contents.manager_ctx
    py_obj = ctypes.cast(manager_ctx, ctypes.py_object)
    obj = py_obj.value
    del obj


def make_dl_managed_tensor(obj, version=0):
    if hasattr(sys, "getrefcount"):
        rc = sys.getrefcount(obj)
    if version >= 1:
        managed = DLManagedTensorVersioned()
        managed.version = make_dl_version(1, 0)
        managed.manager_ctx = make_dl_manager_ctx(obj)
        managed.deleter = dl_managed_tensor_versioned_deleter
        managed.flags = 0
        managed.dl_tensor = make_dl_tensor(obj)
    else:
        managed = DLManagedTensor()
        managed.dl_tensor = make_dl_tensor(obj)
        managed.manager_ctx = make_dl_manager_ctx(obj)
        managed.deleter = dl_managed_tensor_deleter
    if hasattr(sys, "getrefcount"):
        assert sys.getrefcount(obj) == rc + 1
    return managed


@PyCapsule_Destructor
def py_capsule_destructor(void_p):
    capsule = ctypes.cast(void_p, ctypes.py_object)
    used_py_capsule(capsule)
    nullptr = ctypes.c_void_p(None)
    context = PyCapsule_GetContext(capsule)
    if context != nullptr:
        PyCapsule_SetContext(capsule, nullptr)
        managed = ctypes.cast(context, ctypes.py_object)
        Py_DecRef(managed)


def make_py_capsule(managed, owned=True):
    if isinstance(managed, DLManagedTensorVersioned):
        py_capsule_name = b"dltensor_versioned"
    if isinstance(managed, DLManagedTensor):
        py_capsule_name = b"dltensor"
    destructor = None
    if owned:
        destructor = py_capsule_destructor
    pointer = ctypes.byref(managed)
    capsule = PyCapsule_New(pointer, py_capsule_name, destructor)
    if owned:
        context = ctypes.c_void_p.from_buffer(ctypes.py_object(managed))
        if sys.implementation.name == "cpython":
            assert context.value == id(managed)
        Py_IncRef(managed)
        PyCapsule_SetContext(capsule, context)
    return capsule


_used = {
    b"dltensor" + prefix: b"used_dltensor" + prefix
    for prefix in (b"_versioned", b"")
}


def used_py_capsule(capsule):
    for py_capsule_name, dl_managed_tensor_type_p in (
        (b"dltensor_versioned", DLManagedTensorVersioned_p),
        (b"dltensor", DLManagedTensor_p),
    ):
        if PyCapsule_IsValid(capsule, py_capsule_name):
            pointer = PyCapsule_GetPointer(capsule, py_capsule_name)
            managed = ctypes.cast(pointer, dl_managed_tensor_type_p)
            deleter = managed.contents.deleter
            if deleter:
                deleter(managed)
            PyCapsule_SetName(capsule, _used[py_capsule_name])
            break
