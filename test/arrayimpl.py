import itertools
import platform
import sys
import warnings

from mpi4py import MPI

try:
    import array
except ImportError:
    array = None

try:
    import numpy
except ImportError:
    numpy = None

try:
    import cupy
except ImportError:
    cupy = None
else:
    cupy_version = tuple(map(int, cupy.__version__.split(".", 2)[:2]))

try:
    import numba
    import numba.cuda
except ImportError:
    numba = None
else:
    numba_version = tuple(map(int, numba.__version__.split(".", 2)[:2]))
    if numba_version < (0, 48):
        try:
            warnings.warn(
                "To test Numba GPU arrays, use Numba v0.48.0+.",
                RuntimeWarning,
                stacklevel=1,
            )
        except RuntimeWarning:
            pass
        del numba_version
        numba = None


__all__ = ["loop", "test"]


def make_typemap(entries):
    return {
        typecode: datatype
        for typecode, datatype in entries
        if datatype != MPI.DATATYPE_NULL
    }


TypeMap = make_typemap([
    ("b", MPI.SIGNED_CHAR),
    ("h", MPI.SHORT),
    ("i", MPI.INT),
    ("l", MPI.LONG),
    ("q", MPI.LONG_LONG),
    ("f", MPI.FLOAT),
    ("d", MPI.DOUBLE),
    ("g", MPI.LONG_DOUBLE),
])

TypeMapBool = make_typemap([
    ("?", MPI.C_BOOL),
])

TypeMapInteger = make_typemap([
    ("b", MPI.SIGNED_CHAR),
    ("h", MPI.SHORT),
    ("i", MPI.INT),
    ("l", MPI.LONG),
    ("q", MPI.LONG_LONG),
])

TypeMapUnsigned = make_typemap([
    ("B", MPI.UNSIGNED_CHAR),
    ("H", MPI.UNSIGNED_SHORT),
    ("I", MPI.UNSIGNED_INT),
    ("L", MPI.UNSIGNED_LONG),
    ("Q", MPI.UNSIGNED_LONG_LONG),
])

TypeMapFloat = make_typemap([
    ("f", MPI.FLOAT),
    ("d", MPI.DOUBLE),
    ("g", MPI.LONG_DOUBLE),
])

TypeMapComplex = make_typemap([
    ("F", MPI.C_FLOAT_COMPLEX),
    ("D", MPI.C_DOUBLE_COMPLEX),
    ("G", MPI.C_LONG_DOUBLE_COMPLEX),
])

if (
    MPI.get_vendor() == ("MPICH", (5, 0, 0))
    and platform.system() == "Darwin"
    and platform.machine() == "arm64"
):
    del TypeMap["g"]
    del TypeMapFloat["g"]
    del TypeMapComplex["G"]

ArrayBackends = []


def add_backend(cls):
    ArrayBackends.append(cls)
    return cls


class BaseArray:
    #
    backend = None

    TypeMap = TypeMap.copy()
    TypeMap.pop("g", None)

    def __len__(self):
        return len(self.array)

    def __getitem__(self, i):
        return self.array[i]

    def __setitem__(self, i, v):
        self.array[i] = v

    @property
    def mpidtype(self):
        try:
            return self.TypeMap[self.typecode]
        except KeyError:
            return MPI.DATATYPE_NULL

    def as_raw(self):
        return self.array

    def as_mpi(self):
        return (self.as_raw(), self.mpidtype)

    def as_mpi_c(self, count):
        return (self.as_raw(), count, self.mpidtype)

    def as_mpi_v(self, cnt, dsp):
        return (self.as_raw(), (cnt, dsp), self.mpidtype)


if array is not None:

    def product(seq):
        res = 1
        for s in seq:
            res = res * s
        return res

    def mkshape(shape):
        return tuple(int(s) for s in shape)

    @add_backend
    class ArrayArray(BaseArray):
        backend = "array"

        def __init__(self, arg, typecode, shape=None):
            if isinstance(arg, (int, float)):
                if shape is None:
                    shape = ()
                else:
                    try:
                        shape = mkshape(shape)
                    except TypeError:
                        shape = (int(shape),)
                size = product(shape)
                arg = [arg] * size
            else:
                size = len(arg)
                if shape is None:
                    shape = (size,)
                else:
                    shape = mkshape(shape)
                assert size == product(shape)
            self.array = array.array(typecode, arg)

        @property
        def address(self):
            return self.array.buffer_info()[0]

        @property
        def typecode(self):
            return self.array.typecode

        @property
        def itemsize(self):
            return self.array.itemsize

        @property
        def flat(self):
            return self.array

        @property
        def size(self):
            return self.array.buffer_info()[1]


if numpy is not None:

    @add_backend
    class ArrayNumPy(BaseArray):
        backend = "numpy"

        TypeMap = make_typemap([])
        TypeMap.update(TypeMapBool)
        TypeMap.update(TypeMapInteger)
        TypeMap.update(TypeMapUnsigned)
        TypeMap.update(TypeMapFloat)
        TypeMap.update(TypeMapComplex)

        def __init__(self, arg, typecode, shape=None):
            if isinstance(arg, (int, float, complex)):
                if shape is None:
                    shape = ()
            else:
                if shape is None:
                    shape = len(arg)
            self.array = numpy.zeros(shape, typecode)
            if isinstance(arg, (int, float, complex)):
                arg = numpy.asarray(arg).astype(typecode)
                self.array.fill(arg)
            else:
                arg = numpy.asarray(arg).astype(typecode)
                self.array[...] = arg

        @property
        def address(self):
            return self.array.__array_interface__["data"][0]

        @property
        def typecode(self):
            return self.array.dtype.char

        @property
        def itemsize(self):
            return self.array.itemsize

        @property
        def flat(self):
            return self.array.flat

        @property
        def size(self):
            return self.array.size


try:
    import dlpackimpl as dlpack
except ImportError:
    dlpack = None


class BaseDLPackCPU:
    #
    def __dlpack_device__(self):
        return (dlpack.DLDeviceType.kDLCPU, 0)

    def __dlpack__(self, stream=None):
        assert stream is None
        managed = dlpack.make_dl_managed_tensor(self.array)
        capsule = dlpack.make_py_capsule(managed, owned=True)
        return capsule

    def as_raw(self):
        return self


if dlpack is not None and array is not None:

    @add_backend
    class DLPackArray(BaseDLPackCPU, ArrayArray):
        backend = "dlpack-array"

        def __init__(self, arg, typecode, shape=None):
            super().__init__(arg, typecode, shape)


if dlpack is not None and numpy is not None:

    @add_backend
    class DLPackNumPy(BaseDLPackCPU, ArrayNumPy):
        backend = "dlpack-numpy"

        def __init__(self, arg, typecode, shape=None):
            super().__init__(arg, typecode, shape)


def typestr(typecode, itemsize):
    typestr = ""
    if sys.byteorder == "little":
        typestr += "<"
    if sys.byteorder == "big":
        typestr += ">"
    if typecode == "?":
        typestr += "b"
    if typecode in "bhilq":
        typestr += "i"
    if typecode in "BHILQ":
        typestr += "u"
    if typecode in "fdg":
        typestr += "f"
    if typecode in "FDG":
        typestr += "c"
    typestr += str(itemsize)
    return typestr


class BaseFakeGPUArray:
    #
    def set_interface(self, shape, readonly=False):
        self.__cuda_array_interface__ = {
            "version": 0,
            "data": (self.address, readonly),
            "typestr": typestr(self.typecode, self.itemsize),
            "shape": shape,
        }

    def as_raw(self):
        return self


if array is not None:

    @add_backend
    class FakeGPUArrayBasic(BaseFakeGPUArray, ArrayArray):
        def __init__(self, arg, typecode, shape=None, readonly=False):
            super().__init__(arg, typecode, shape)
            self.set_interface((len(self),), readonly)


if numpy is not None:

    @add_backend
    class FakeGPUArrayNumPy(BaseFakeGPUArray, ArrayNumPy):
        def __init__(self, arg, typecode, shape=None, readonly=False):
            super().__init__(arg, typecode, shape)
            self.set_interface(self.array.shape, readonly)


if cupy is not None:

    @add_backend
    class GPUArrayCuPy(BaseArray):
        backend = "cupy"

        TypeMap = make_typemap([])
        if cupy_version >= (11, 6):
            TypeMap.update(TypeMapBool)
        TypeMap.update(TypeMapInteger)
        TypeMap.update(TypeMapUnsigned)
        TypeMap.update(TypeMapFloat)
        TypeMap.update(TypeMapComplex)
        try:
            cupy.array(0, "g")
        except ValueError:
            TypeMap.pop("g", None)
        try:
            cupy.array(0, "G")
        except ValueError:
            TypeMap.pop("G", None)

        def __init__(self, arg, typecode, shape=None, readonly=False):
            if isinstance(arg, (int, float, complex)):
                if shape is None:
                    shape = ()
            else:
                if shape is None:
                    shape = len(arg)
            self.array = cupy.zeros(shape, typecode)
            if isinstance(arg, (int, float, complex)):
                self.array.fill(arg)
            else:
                self.array[:] = cupy.asarray(arg, typecode)
            del readonly  # self.array.flags.readonly = readonly

        @property
        def address(self):
            return self.array.__cuda_array_interface__["data"][0]

        @property
        def typecode(self):
            return self.array.dtype.char

        @property
        def itemsize(self):
            return self.array.itemsize

        @property
        def flat(self):
            return self.array.ravel()

        @property
        def size(self):
            return self.array.size

        def as_raw(self):
            cupy.cuda.get_current_stream().synchronize()
            return self.array


if cupy is not None:
    # Note: we do not create a BaseDLPackGPU class because each GPU library
    # has its own way to get device ID etc, so we have to reimplement the
    # DLPack support anyway

    @add_backend
    class DLPackCuPy(GPUArrayCuPy):
        backend = "dlpack-cupy"
        has_dlpack = None
        dev_type = None

        def __init__(self, arg, typecode, shape=None):
            super().__init__(arg, typecode, shape)
            self.has_dlpack = hasattr(self.array, "__dlpack_device__")
            # TODO(leofang): test CUDA managed memory?
            if cupy.cuda.runtime.is_hip:
                self.dev_type = dlpack.DLDeviceType.kDLROCM
            else:
                self.dev_type = dlpack.DLDeviceType.kDLCUDA

        def __dlpack_device__(self):
            if self.has_dlpack:
                return self.array.__dlpack_device__()
            else:
                return (self.dev_type, self.array.device.id)

        def __dlpack__(self, stream=None):
            cupy.cuda.get_current_stream().synchronize()
            if self.has_dlpack:
                return self.array.__dlpack__(stream=-1)
            else:
                return self.array.toDlpack()

        def as_raw(self):
            return self


if numba is not None:

    @add_backend
    class GPUArrayNumba(BaseArray):
        backend = "numba"

        TypeMap = make_typemap([])
        TypeMap.update(TypeMapBool)
        TypeMap.update(TypeMapInteger)
        TypeMap.update(TypeMapUnsigned)
        TypeMap.update(TypeMapFloat)
        TypeMap.update(TypeMapComplex)

        # one can allocate arrays with those types,
        # but the Numba compiler doesn't support them...
        TypeMap.pop("g", None)
        TypeMap.pop("G", None)

        def __init__(self, arg, typecode, shape=None, readonly=False):
            if isinstance(arg, (int, float, complex)):
                if shape is None:
                    shape = ()
            else:
                if shape is None:
                    shape = len(arg)
            self.array = numba.cuda.device_array(shape, typecode)
            if isinstance(arg, (int, float, complex)):
                if self.array.size > 0:
                    self.array[:] = arg
            elif arg == [] or arg == ():
                self.array = numba.cuda.device_array(0, typecode)
            else:
                if self.array.size > 0:
                    self.array[:] = numba.cuda.to_device(arg)
            del readonly  # self.array.flags.readonly = readonly

        # def __getitem__(self, i):
        #     if isinstance(i, slice):
        #         return self.array[i]
        #     elif i < self.array.size:
        #         return self.array[i]
        #     else:
        #         raise StopIteration

        @property
        def address(self):
            return self.array.__cuda_array_interface__["data"][0]

        @property
        def typecode(self):
            return self.array.dtype.char

        @property
        def itemsize(self):
            return self.array.dtype.itemsize

        @property
        def flat(self):
            if self.array.ndim <= 1:
                return self.array
            else:
                return self.array.ravel()

        @property
        def size(self):
            return self.array.size

        def as_raw(self):
            # numba by default always runs on the legacy default stream
            numba.cuda.default_stream().synchronize()
            return self.array


def loop(*args):
    loop.array = None
    loop.typecode = None
    for array in ArrayBackends:
        loop.array = array
        for typecode in array.TypeMap:
            loop.typecode = typecode
            if not args:
                yield array, typecode
            else:
                for prod in itertools.product(*args):
                    yield (array, typecode, *prod)
    del loop.array
    del loop.typecode


def test(case, **kargs):
    return case.subTest(
        typecode=loop.typecode,
        backend=loop.array.backend,
        **kargs,
    )


def scalar(arg):
    return loop.array(arg, loop.typecode, 1)[0]
