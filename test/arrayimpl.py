from mpi4py import MPI
try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

__all__ = ['TypeMap', 'ArrayTypes']

TypeMap = OrderedDict([
    ('b', MPI.SIGNED_CHAR),
    ('h', MPI.SHORT),
    ('i', MPI.INT),
    ('l', MPI.LONG),
    ('q', MPI.LONG_LONG),
    ('f', MPI.FLOAT),
    ('d', MPI.DOUBLE),
])

import sys
if sys.version_info[:2] < (3,3):
    del TypeMap['q']

if MPI.SIGNED_CHAR == MPI.DATATYPE_NULL:
    del TypeMap['b']

ArrayTypes = []

try:
    import array
except ImportError:
    pass
else:

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
                elif isinstance(shape, int):
                    shape = (shape,)
                else:
                    shape = mkshape(shape)
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

        def flat(self):
            return self
        flat = property(flat)


        def fill(self, value):
            self[:] = array.array(self.typecode,
                                  [value]*len(self))

        def byteswap(self, inplace=False):
            if inplace:
                self.byteswap()
            else:
                ary = Array(list(self), self.typecode, self.shape)
                array.array.byteswap(ary)
                return ary

        def allclose(self, ary, rtol=1.e-5, atol=1.e-8):
            for x, y in zip(self, ary):
                if abs(x-y) > (atol + rtol * abs(y)):
                    return False
            return True

        def max(self):
            return max(self)

        def min(self):
            return min(self)

        def sum(self):
            return sum(self)

        def as_mpi(self):
            return (self, self.mpidtype)

        def as_mpi_c(self, count):
            return (self, count, self.mpidtype)

        def as_mpi_v(self, cnt, dsp):
            return (self, (cnt, dsp), self.mpidtype)

    ArrayTypes.append(Array)
    __all__.append('Array')

try:
    import numpy
except ImportError:
    pass
else:

    class NumPy(numpy.ndarray):

        TypeMap = TypeMap.copy()

        def __new__(cls, arg, typecode, shape=None):
            if isinstance(arg, (int, float, complex)):
                if shape is None: shape = ()
            else:
                if shape is None: shape = len(arg)
            ary = numpy.ndarray.__new__(cls, shape, typecode)
            ary.flat[:] = arg
            try:
                ary.mpidtype = Array.TypeMap[typecode]
            except KeyError:
                ary.mpidtype = MPI.DATATYPE_NULL
            return ary

        def typecode(self):
            return self.dtype.char
        typecode = property(typecode)

        def allclose(self, ary, rtol=1.e-5, atol=1.e-8):
            return numpy.allclose(self, ary, rtol, atol)

        def as_mpi(self):
            return (self, self.mpidtype)

        def as_mpi_c(self, count):
            return (self, count, self.mpidtype)

        def as_mpi_v(self, cnt, dsp):
            return (self, (cnt, dsp), self.mpidtype)

    ArrayTypes.append(NumPy)
    __all__.append('NumPy')
