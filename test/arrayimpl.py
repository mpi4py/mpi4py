import sys
from mpi4py import MPI
try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict
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
try:
    import numba
    import numba.cuda
    from distutils.version import StrictVersion
    numba_version = StrictVersion(numba.__version__).version
    if numba_version < (0, 48):
        import warnings
        warnings.warn('To test Numba GPU arrays, use Numba v0.48.0+.',
                      RuntimeWarning)
        numba = None
except ImportError:
    numba = None


__all__ = ['allclose', 'subTest']

def allclose(a, b, rtol=1.e-5, atol=1.e-8):
    try: iter(a)
    except TypeError: a = [a]
    try: iter(b)
    except TypeError: b = [b]
    for x, y in zip(a, b):
        if abs(x-y) > (atol + rtol * abs(y)):
            return False
    return True

def make_typemap(entries):
    typemap = OrderedDict(entries)
    for typecode, datatype in entries:
        if datatype == MPI.DATATYPE_NULL:
            del typemap[typecode]
    return typemap

TypeMap = make_typemap([
    ('b', MPI.SIGNED_CHAR),
    ('h', MPI.SHORT),
    ('i', MPI.INT),
    ('l', MPI.LONG),
    ('q', MPI.LONG_LONG),
    ('f', MPI.FLOAT),
    ('d', MPI.DOUBLE),
    ('g', MPI.LONG_DOUBLE),
])

TypeMapBool = make_typemap([
    ('?', MPI.C_BOOL),
])

TypeMapInteger = make_typemap([
    ('b', MPI.SIGNED_CHAR),
    ('h', MPI.SHORT),
    ('i', MPI.INT),
    ('l', MPI.LONG),
    ('q', MPI.LONG_LONG),
])

TypeMapUnsigned = make_typemap([
    ('B', MPI.UNSIGNED_CHAR),
    ('H', MPI.UNSIGNED_SHORT),
    ('I', MPI.UNSIGNED_INT),
    ('L', MPI.UNSIGNED_LONG),
    ('Q', MPI.UNSIGNED_LONG_LONG),
])

TypeMapFloat = make_typemap([
    ('f', MPI.FLOAT),
    ('d', MPI.DOUBLE),
    ('g', MPI.LONG_DOUBLE),
])

TypeMapComplex = make_typemap([
    ('F', MPI.C_FLOAT_COMPLEX),
    ('D', MPI.C_DOUBLE_COMPLEX),
    ('G', MPI.C_LONG_DOUBLE_COMPLEX),
])


ArrayBackends = []

def add_backend(cls):
    ArrayBackends.append(cls)
    return cls

class BaseArray(object):

    backend = None

    TypeMap = TypeMap.copy()
    TypeMap.pop('g', None)
    if sys.version_info[:2] < (3, 3):
        TypeMap.pop('q', None)

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
        return tuple([int(s) for s in shape])

    @add_backend
    class ArrayArray(BaseArray):

        backend = 'array'

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

        backend = 'numpy'

        TypeMap = make_typemap([])
        #TypeMap.update(TypeMapBool)
        TypeMap.update(TypeMapInteger)
        #TypeMap.update(TypeMapUnsigned)
        TypeMap.update(TypeMapFloat)
        TypeMap.update(TypeMapComplex)

        def __init__(self, arg, typecode, shape=None):
            if isinstance(arg, (int, float, complex)):
                if shape is None: shape = ()
            else:
                if shape is None: shape = len(arg)
            self.array = numpy.zeros(shape, typecode)
            if isinstance(arg, (int, float, complex)):
                self.array.fill(arg)
            else:
                self.array[:] = numpy.asarray(arg, typecode)

        @property
        def address(self):
            return self.array.__array_interface__['data'][0]

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


def typestr(typecode, itemsize):
    typestr = ''
    if sys.byteorder == 'little':
        typestr += '<'
    if sys.byteorder == 'big':
        typestr += '>'
    if typecode in '?':
        typestr += 'b'
    if typecode in 'bhilq':
        typestr += 'i'
    if typecode in 'BHILQ':
        typestr += 'u'
    if typecode in 'fdg':
        typestr += 'f'
    if typecode in 'FDG':
        typestr += 'c'
    typestr += str(itemsize)
    return typestr


class BaseFakeGPUArray(object):

    def set_interface(self, shape, readonly=False):
        self.__cuda_array_interface__ = dict(
            version = 0,
            data    = (self.address, readonly),
            typestr = typestr(self.typecode, self.itemsize),
            shape   = shape,
        )

    def as_raw(self):
        return self


if array is not None:

    @add_backend
    class FakeGPUArrayBasic(BaseFakeGPUArray, ArrayArray):

        def __init__(self, arg, typecode, shape=None, readonly=False):
            super(FakeGPUArrayBasic, self).__init__(arg, typecode, shape)
            self.set_interface((len(self),), readonly)


if numpy is not None:

    @add_backend
    class FakeGPUArrayNumPy(BaseFakeGPUArray, ArrayNumPy):

        def __init__(self, arg, typecode, shape=None, readonly=False):
            super(FakeGPUArrayNumPy, self).__init__(arg, typecode, shape)
            self.set_interface(self.array.shape, readonly)


if cupy is not None:

    @add_backend
    class GPUArrayCuPy(BaseArray):

        backend = 'cupy'

        TypeMap = make_typemap([])
        #TypeMap.update(TypeMapBool)
        TypeMap.update(TypeMapInteger)
        #TypeMap.update(TypeMapUnsigned)
        TypeMap.update(TypeMapFloat)
        TypeMap.update(TypeMapComplex)
        try:
            cupy.array(0, 'g')
        except ValueError:
            TypeMap.pop('g', None)
        try:
            cupy.array(0, 'G')
        except ValueError:
            TypeMap.pop('G', None)

        def __init__(self, arg, typecode, shape=None, readonly=False):
            if isinstance(arg, (int, float, complex)):
                if shape is None: shape = ()
            else:
                if shape is None: shape = len(arg)
            self.array = cupy.zeros(shape, typecode)
            if isinstance(arg, (int, float, complex)):
                self.array.fill(arg)
            else:
                self.array[:] = cupy.asarray(arg, typecode)

        @property
        def address(self):
            return self.array.__cuda_array_interface__['data'][0]

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


if numba is not None:

    @add_backend
    class GPUArrayNumba(BaseArray):

        backend = 'numba'

        TypeMap = make_typemap([])
        #TypeMap.update(TypeMapBool)
        TypeMap.update(TypeMapInteger)
        #TypeMap.update(TypeMapUnsigned)
        TypeMap.update(TypeMapFloat)
        TypeMap.update(TypeMapComplex)

        # one can allocate arrays with those types,
        # but the Numba compiler doesn't support them...
        TypeMap.pop('g', None)
        TypeMap.pop('G', None)

        def __init__(self, arg, typecode, shape=None, readonly=False):
            if isinstance(arg, (int, float, complex)):
                if shape is None: shape = ()
            else:
                if shape is None: shape = len(arg)
            self.array = numba.cuda.device_array(shape, typecode)
            if isinstance(arg, (int, float, complex)):
                if self.array.size > 0:
                    self.array[:] = arg
            elif arg == [] or arg == ():
                self.array = numba.cuda.device_array(0, typecode)
            else:
                if self.array.size > 0:
                    self.array[:] = numba.cuda.to_device(arg)

#        def __getitem__(self, i):
#            if isinstance(i, slice):
#                return self.array[i]
#            elif i < self.array.size:
#                return self.array[i]
#            else:
#                raise StopIteration

        @property
        def address(self):
            return self.array.__cuda_array_interface__['data'][0]

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


def subTest(case, skip=(), skiptypecode=()):
    for array in ArrayBackends:
        if array.backend == skip: continue
        if array.backend in skip: continue
        for typecode in array.TypeMap:
            if typecode == skiptypecode: continue
            if typecode in skiptypecode: continue
            with case.subTest(backend=array.backend, typecode=typecode):
                try:
                    yield array, typecode
                except GeneratorExit:
                    return
