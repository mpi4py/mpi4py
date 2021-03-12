# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Convert NumPy and MPI datatypes."""
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements

from .. import MPI

try:
    from numpy import dtype as _np_dtype
except ImportError:  # pragma: no cover
    pass


def _get_datatype(dtype):
    # pylint: disable=protected-access
    return MPI._typedict.get(dtype.char)


def _get_typecode(datatype):
    # pylint: disable=protected-access
    return MPI._typecode(datatype)


def _is_aligned(datatype, offset=0):
    """Dermine whether an MPI datatype is aligned."""
    if datatype.is_predefined:
        if offset == 0:
            return True
        typecode = _get_typecode(datatype)
        combiner = datatype.combiner
        is_complex = any((
            typecode in ('F', 'D', 'G'),
            typecode in ('c4', 'c8', 'c16', 'c32'),
            combiner == MPI.COMBINER_F90_COMPLEX,
        ))
        typesize = datatype.Get_size() or 1
        if is_complex:
            typesize //= 2
        return offset % typesize == 0

    combiner = datatype.combiner
    basetype, _, info = datatype.decode()
    types, disps = [basetype], [0]
    try:
        if combiner == MPI.COMBINER_RESIZED:
            disps = [info['extent']]
        if combiner == MPI.COMBINER_STRUCT:
            types = info['datatypes']
            disps = info['displacements']
        if combiner == MPI.COMBINER_HVECTOR:
            disps = [info['stride'] if info['count'] > 1 else 0]
        if combiner == MPI.COMBINER_HINDEXED:
            disps = info['displacements']
        if combiner == MPI.COMBINER_HINDEXED_BLOCK:
            disps = info['displacements']
        return all(
            _is_aligned(t, offset + d)
            for t, d in zip(types, disps)
        )
    finally:
        for _tp in types:
            if not _tp.is_predefined:
                _tp.Free()


def from_numpy_dtype(dtype):
    """Convert NumPy datatype to MPI."""
    try:
        dtype = _np_dtype(dtype)
    except NameError:  # pragma: no cover
        # pylint: disable=raise-missing-from
        raise RuntimeError("NumPy is not available")

    if dtype.hasobject:
        raise ValueError("NumPy datatype with object entries")
    if not dtype.isnative:
        raise ValueError("NumPy datatype with non-native byteorder")

    # struct data type
    fields = dtype.fields
    if fields:
        blocklengths = []
        displacements = []
        datatypes = []
        try:
            for name in dtype.names:
                ftype, fdisp = fields[name]
                blocklengths.append(1)
                displacements.append(fdisp)
                datatypes.append(from_numpy_dtype(ftype))
            datatype = MPI.Datatype.Create_struct(
                blocklengths, displacements, datatypes,
            )
        finally:
            for mtp in datatypes:
                mtp.Free()
        try:
            return datatype.Create_resized(0, dtype.itemsize)
        finally:
            datatype.Free()

    # subarray data type
    subdtype = dtype.subdtype
    if subdtype:
        base, shape = subdtype
        datatype = from_numpy_dtype(base)
        try:
            if len(shape) == 1:
                return datatype.Create_contiguous(shape[0])
            starts = (0,) * len(shape)
            return datatype.Create_subarray(shape, shape, starts)
        finally:
            datatype.Free()

    # elementary data type
    datatype = _get_datatype(dtype)
    if datatype is None:
        raise ValueError("cannot convert NumPy datatype to MPI")
    return datatype.Dup()


def to_numpy_dtype(datatype):
    """Convert MPI datatype to NumPy."""

    def mpi2npy(datatype, count):
        dtype = to_numpy_dtype(datatype)
        return dtype if count == 1 else (dtype, count)

    def np_dtype(spec):
        try:
            return _np_dtype(spec)
        except NameError:  # pragma: no cover
            return spec

    if datatype == MPI.DATATYPE_NULL:
        raise ValueError("cannot convert null MPI datatype to NumPy")

    combiner = datatype.combiner

    # predefined datatype
    if combiner == MPI.COMBINER_NAMED:
        typecode = _get_typecode(datatype)
        if typecode is not None:
            return np_dtype(typecode)
        raise ValueError("cannot convert MPI datatype to NumPy")

    # user-defined datatype
    basetype, _, info = datatype.decode()
    datatypes = [basetype]
    try:
        # duplicated datatype
        if combiner == MPI.COMBINER_DUP:
            return to_numpy_dtype(basetype)

        # contiguous datatype
        if combiner == MPI.COMBINER_CONTIGUOUS:
            dtype = to_numpy_dtype(basetype)
            count = info['count']
            return np_dtype((dtype, (count,)))

        # subarray datatype
        if combiner == MPI.COMBINER_SUBARRAY:
            dtype = to_numpy_dtype(basetype)
            sizes = info['sizes']
            subsizes = info['subsizes']
            starts = info['starts']
            order = info['order']
            assert subsizes == sizes
            assert min(starts) == max(starts) == 0
            if order == MPI.ORDER_FORTRAN:
                sizes = sizes[::-1]
            return np_dtype((dtype, tuple(sizes)))

        # struct datatype
        aligned = True
        if combiner == MPI.COMBINER_RESIZED:
            if basetype.combiner == MPI.COMBINER_STRUCT:
                aligned = _is_aligned(basetype, info['extent'])
                combiner = MPI.COMBINER_STRUCT
                _, _, info = basetype.decode()
                datatypes.pop().Free()
        if combiner == MPI.COMBINER_STRUCT:
            datatypes = info['datatypes']
            blocklengths = info['blocklengths']
            displacements = info['displacements']
            names = list(map('f{}'.format, range(len(datatypes))))
            formats = list(map(mpi2npy, datatypes, blocklengths))
            offsets = displacements
            itemsize = datatype.extent
            aligned &= all(map(_is_aligned, datatypes, offsets))
            return np_dtype(
                {
                    'names': names,
                    'formats': formats,
                    'offsets': offsets,
                    'itemsize': itemsize,
                    'aligned': aligned,
                }
            )

        # vector datatype
        combiner_vector = (
            MPI.COMBINER_VECTOR,
            MPI.COMBINER_HVECTOR,
        )
        if combiner in combiner_vector:
            dtype = to_numpy_dtype(basetype)
            count = info['count']
            blocklength = info['blocklength']
            stride = info['stride']
            if combiner == MPI.COMBINER_VECTOR:
                stride *= basetype.extent
                aligned = _is_aligned(basetype)
            if combiner == MPI.COMBINER_HVECTOR:
                stride = stride if count > 1 else 0
                aligned = _is_aligned(basetype, stride)
            names = list(map('f{0}'.format, range(count)))
            formats = [(dtype, (blocklength,))] * count
            offsets = [stride * i for i in range(count)]
            itemsize = datatype.extent
            return np_dtype(
                {
                    'names': names,
                    'formats': formats,
                    'offsets': offsets,
                    'itemsize': itemsize,
                    'aligned': aligned,
                }
            )

        # indexed datatype
        combiner_indexed = (
            MPI.COMBINER_INDEXED,
            MPI.COMBINER_HINDEXED,
            MPI.COMBINER_INDEXED_BLOCK,
            MPI.COMBINER_HINDEXED_BLOCK,
        )
        if combiner in combiner_indexed:
            dtype = to_numpy_dtype(basetype)
            stride = 1
            aligned = _is_aligned(basetype)
            displacements = info['displacements']
            if combiner in combiner_indexed[:2]:
                blocklengths = info['blocklengths']
            if combiner in combiner_indexed[2:]:
                blocklengths = [info['blocklength']] * len(displacements)
            if combiner in combiner_indexed[0::2]:
                stride = basetype.extent
            if combiner in combiner_indexed[1::2]:
                aligned &= all(_is_aligned(basetype, d) for d in displacements)
            names = list(map('f{}'.format, range(len(displacements))))
            formats = [(dtype, (blen,)) for blen in blocklengths]
            offsets = [disp * stride for disp in displacements]
            return np_dtype(
                {
                    'names': names,
                    'formats': formats,
                    'offsets': offsets,
                    'aligned': aligned,
                }
            )

        # Fortran 90 datatype
        combiner_f90 = (
            MPI.COMBINER_F90_INTEGER,
            MPI.COMBINER_F90_REAL,
            MPI.COMBINER_F90_COMPLEX,
        )
        if combiner in combiner_f90:
            datatypes.pop()
            typesize = datatype.Get_size()
            typecode = 'ifc'[combiner_f90.index(combiner)]
            return np_dtype('{0}{1:d}'.format(typecode, typesize))

        raise ValueError("cannot convert MPI datatype to NumPy")
    finally:
        for _tp in datatypes:
            if not _tp.is_predefined:
                _tp.Free()
