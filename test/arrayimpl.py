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


__all__ = ['TypeMap', 'ArrayTypes', 'allclose']

TypeMap = OrderedDict([
    ('b', MPI.SIGNED_CHAR),
    ('h', MPI.SHORT),
    ('i', MPI.INT),
    ('l', MPI.LONG),
    ('q', MPI.LONG_LONG),
    ('f', MPI.FLOAT),
    ('d', MPI.DOUBLE),
])

if MPI.SIGNED_CHAR == MPI.DATATYPE_NULL:
    del TypeMap['b']

if sys.version_info[:2] < (3, 3):
    del TypeMap['q']

ArrayTypes = []

def allclose(a, b, rtol=1.e-5, atol=1.e-8):
    try: iter(a)
    except TypeError: a = [a]
    try: iter(b)
    except TypeError: b = [b]
    for x, y in zip(a, b):
        if abs(x-y) > (atol + rtol * abs(y)):
            return False
    return True


if array is not None:

    def product(seq):
        res = 1
        for s in seq:
            res = res * s
        return res
    def mkshape(seq):
        return tuple([int(s) for s in seq])

    class Array(array.array):

        TypeMap = TypeMap.copy()

        def __new__(cls, arg, typecode, shape=None):
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
                if shape is None: shape = (size,)
                else: shape = mkshape(shape)
                assert size == product(shape)
            ary = array.array.__new__(cls, typecode, arg)
            ary.shape = shape
            ary.size  = size
            try:
                ary.mpidtype = Array.TypeMap[typecode]
            except KeyError:
                ary.mpidtype = MPI.DATATYPE_NULL
            return ary

        def flat(self): return self
        flat = property(flat)

        def as_raw(self):
            return self

        def as_mpi(self):
            return (self, self.mpidtype)

        def as_mpi_c(self, count):
            return (self, count, self.mpidtype)

        def as_mpi_v(self, cnt, dsp):
            return (self, (cnt, dsp), self.mpidtype)

    ArrayTypes.append(Array)
    __all__.append('Array')


if numpy is not None:

    class NumPy(object):

        TypeMap = TypeMap.copy()

        def __init__(self, arg, typecode, shape=None):
            if isinstance(arg, (int, float, complex)):
                if shape is None: shape = ()
            else:
                if shape is None: shape = len(arg)
            self.array = ary = numpy.zeros(shape, typecode)
            if isinstance(arg, (int, float, complex)):
                ary.fill(arg)
            else:
                ary[:] = arg
            try:
                self.mpidtype = NumPy.TypeMap[typecode]
            except KeyError:
                self.mpidtype = MPI.DATATYPE_NULL

        def __len__(self): return len(self.array)
        def __getitem__(self, i): return self.array[i]
        def __setitem__(self, i, v): self.array[i] = v
        def typecode(self): return self.array.dtype.char
        typecode = property(typecode)
        def itemsize(self): return self.array.itemsize
        itemsize = property(itemsize)
        def flat(self): return self.array.flat
        flat = property(flat)

        def as_raw(self):
            return self.array

        def as_mpi(self):
            return (self.array, self.mpidtype)

        def as_mpi_c(self, count):
            return (self.array, count, self.mpidtype)

        def as_mpi_v(self, cnt, dsp):
            return (self.array, (cnt, dsp), self.mpidtype)


    ArrayTypes.append(NumPy)
    __all__.append('NumPy')
