#------------------------------------------------------------------------------

# CUDA array interface for interoperating Python CUDA GPU libraries
# See http://numba.pydata.org/numba-doc/latest/cuda/cuda_array_interface.html

cdef inline int cuda_is_contig(tuple shape,
                               tuple strides,
                               Py_ssize_t itemsize,
                               char order) except -1:
    cdef Py_ssize_t i, ndim = len(shape)
    cdef Py_ssize_t start, step, index
    if order == c'F':
        start = 0
        step = 1
    else:
        start = ndim - 1
        step = -1
    for i from 0 <= i < ndim:
        index = start + step * i
        if itemsize != <Py_ssize_t>strides[index]:
            return 0
        itemsize *= <Py_ssize_t>shape[index]
    return 1

cdef inline char* cuda_get_format(char typekind, Py_ssize_t itemsize) nogil:
   if typekind == c'b':
       if itemsize ==  1: return b"b1"
       if itemsize ==  2: return b"b2"
       if itemsize ==  4: return b"b4"
       if itemsize ==  8: return b"b8"
   if typekind == c'i':
       if itemsize ==  1: return b"i1"
       if itemsize ==  2: return b"i2"
       if itemsize ==  4: return b"i4"
       if itemsize ==  8: return b"i8"
   if typekind == c'u':
       if itemsize ==  1: return b"u1"
       if itemsize ==  2: return b"u2"
       if itemsize ==  4: return b"u4"
       if itemsize ==  8: return b"u8"
   if typekind == c'f':
       if itemsize ==  2: return b"f2"
       if itemsize ==  4: return b"f4"
       if itemsize ==  8: return b"f8"
       if itemsize == 12: return b"f12"
       if itemsize == 16: return b"f16"
   if typekind == c'c':
       if itemsize ==  4: return b"c4"
       if itemsize ==  8: return b"c8"
       if itemsize == 16: return b"c16"
       if itemsize == 24: return b"c24"
       if itemsize == 32: return b"c32"
   return BYTE_FMT

cdef int Py_CheckCUDABuffer(object obj):
    try: return <bint>hasattr(obj, '__cuda_array_interface__')
    except: return 0

cdef int Py_GetCUDABuffer(object obj, Py_buffer *view, int flags) except -1:
    cdef dict cuda_array_interface
    cdef tuple data
    cdef str   typestr
    cdef tuple shape
    cdef tuple strides
    cdef list descr
    cdef object dev_ptr, mask
    cdef void *buf = NULL
    cdef bint readonly = 0
    cdef Py_ssize_t s, size = 1
    cdef Py_ssize_t itemsize = 1
    cdef char typekind = c'u'
    cdef bint fixnull = 0

    try:
        cuda_array_interface = obj.__cuda_array_interface__
    except AttributeError:
        raise NotImplementedError("missing CUDA array interface")

    # mandatory
    data = cuda_array_interface['data']
    typestr = cuda_array_interface['typestr']
    shape = cuda_array_interface['shape']

    # optional
    strides = cuda_array_interface.get('strides')
    descr = cuda_array_interface.get('descr')
    mask = cuda_array_interface.get('mask')

    dev_ptr, readonly = data
    for s in shape: size *= s
    if dev_ptr is None and size == 0: dev_ptr = 0 # XXX
    buf = PyLong_AsVoidPtr(dev_ptr)
    typekind = <char>ord(typestr[1])
    itemsize = <Py_ssize_t>int(typestr[2:])

    if mask is not None:
        raise NotImplementedError(
            "__cuda_array_interface__: "
            "cannot handle masked arrays"
        )
    if size < 0:
        raise BufferError(
            "__cuda_array_interface__: "
            "buffer with negative size (shape:%s, size:%d)"
            % (shape, size)
        )
    if (strides is not None and
        not cuda_is_contig(shape, strides, itemsize, c'C') and
        not cuda_is_contig(shape, strides, itemsize, c'F')):
        raise BufferError(
            "__cuda_array_interface__: "
            "buffer is not contiguous (shape:%s, strides:%s, itemsize:%d)"
            % (shape, strides, itemsize)
        )
    if descr is not None and (len(descr) != 1 or descr[0] != ('', typestr)):
        PyErr_WarnEx(RuntimeWarning,
                     b"__cuda_array_interface__: "
                     b"ignoring 'descr' key", 1)

    fixnull = (buf == NULL and size == 0)
    if fixnull: buf = &fixnull
    PyBuffer_FillInfo(view, obj, buf, size*itemsize, readonly, flags)
    if fixnull: view.buf = NULL

    if (flags & PyBUF_FORMAT) == PyBUF_FORMAT:
        view.format = cuda_get_format(typekind, itemsize)
        if view.format != BYTE_FMT:
            view.itemsize = itemsize
    return 0

#------------------------------------------------------------------------------

cdef int Py_CheckGPUBuffer(object obj):
    return Py_CheckCUDABuffer(obj)

cdef int Py_GetGPUBuffer(object obj, Py_buffer *view, int flags) except -1:
    return Py_GetCUDABuffer(obj, view, flags)

#------------------------------------------------------------------------------
