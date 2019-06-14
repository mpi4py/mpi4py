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


__all__ = ['ArrayTypes', 'allclose']

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


class BaseArray(object):

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


class BaseArrayBasic(BaseArray):

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


class BaseArrayNumPy(BaseArray):

    TypeMap = make_typemap([])
    #TypeMap.update(TypeMapBool)
    TypeMap.update(TypeMapInteger)
    #TypeMap.update(TypeMapUnsigned)
    TypeMap.update(TypeMapFloat)
    TypeMap.update(TypeMapComplex)

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


ArrayTypes = []

def export(cls):
    ArrayTypes.append(cls)
    __all__.append(cls.__name__)
    return cls


if array is not None:

    def product(seq):
        res = 1
        for s in seq:
            res = res * s
        return res

    def mkshape(shape):
        return tuple([int(s) for s in shape])

    @export
    class ArrayBasic(BaseArrayBasic):

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


if numpy is not None:

    @export
    class ArrayNumPy(BaseArrayNumPy):

        def __init__(self, arg, typecode, shape=None):
            if isinstance(arg, (int, float, complex)):
                if shape is None: shape = ()
            else:
                if shape is None: shape = len(arg)
            self.array = numpy.zeros(shape, typecode)
            if isinstance(arg, (int, float, complex)):
                self.array.fill(arg)
            else:
                self.array[:] = arg







