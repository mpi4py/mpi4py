.. _tutorial:

Tutorial
========

.. currentmodule:: mpi4py.MPI

.. warning::

   Under construction. Contributions very welcome!

*MPI for Python* supports convenient, *pickle*-based communication of
generic Python object as well as fast, near C-speed, direct array data
communication of buffer-provider objects (e.g., NumPy arrays).

* Communication of generic Python objects

  You have to use methods with **all-lowercase** names, like
  `Comm.send`, `Comm.recv`, `Comm.bcast`, `Comm.scatter`,
  `Comm.gather` . An object to be sent is passed as a parameter to the
  communication call, and the received object is simply the return
  value.

  The `Comm.isend` and `Comm.irecv` methods return `Request`
  instances; completion of these methods can be managed using the
  `Request.test` and `Request.wait` methods.

  The `Comm.recv` and `Comm.irecv` methods may be passed a buffer
  object that can be repeatedly used to receive messages avoiding
  internal memory allocation. This buffer must be sufficiently large
  to accommodate the transmitted messages; hence, any buffer passed to
  `Comm.recv` or `Comm.irecv` must be at least as long as the
  *pickled* data transmitted to the receiver.

  Collective calls like `Comm.scatter`, `Comm.gather`,
  `Comm.allgather`, `Comm.alltoall` expect a single value or a
  sequence of `Comm.size` elements at the root or all process. They
  return a single value, a list of `Comm.size` elements, or `None`.

  .. note::

     *MPI for Python* uses the **highest** :ref:`protocol version
     <pickle-protocols>` available in the Python runtime (see the
     :data:`~pickle.HIGHEST_PROTOCOL` constant in the :mod:`pickle`
     module).  The default protocol can be changed at import time by
     setting the :envvar:`MPI4PY_PICKLE_PROTOCOL` environment
     variable, or at runtime by assigning a different value to the
     :attr:`~mpi4py.MPI.Pickle.PROTOCOL` attribute of the
     :obj:`~mpi4py.MPI.pickle` object within the :mod:`~mpi4py.MPI`
     module.

* Communication of buffer-like objects

  You have to use method names starting with an **upper-case** letter,
  like `Comm.Send`, `Comm.Recv`, `Comm.Bcast`, `Comm.Scatter`,
  `Comm.Gather`.

  In general, buffer arguments to these calls must be explicitly
  specified by using a 2/3-list/tuple like ``[data, MPI.DOUBLE]``, or
  ``[data, count, MPI.DOUBLE]`` (the former one uses the byte-size of
  ``data`` and the extent of the MPI datatype to define ``count``).

  For vector collectives communication operations like
  `Comm.Scatterv` and `Comm.Gatherv`, buffer arguments are
  specified as ``[data, count, displ, datatype]``, where ``count`` and
  ``displ`` are sequences of integral values.

  Automatic MPI datatype discovery for NumPy/GPU arrays and PEP-3118
  buffers is supported, but limited to basic C types (all C/C99-native
  signed/unsigned integral types and single/double precision
  real/complex floating types) and availability of matching datatypes
  in the underlying MPI implementation. In this case, the
  buffer-provider object can be passed directly as a buffer argument,
  the count and MPI datatype will be inferred.

  If mpi4py is built against a GPU-aware MPI implementation, GPU
  arrays can be passed to upper-case methods as long as they have
  either the ``__dlpack__`` and ``__dlpack_device__`` methods or the
  ``__cuda_array_interface__`` attribute that are compliant with the
  respective standard specifications. Moreover, only C-contiguous or
  Fortran-contiguous GPU arrays are supported. It is important to note
  that GPU buffers must be fully ready before any MPI routines operate
  on them to avoid race conditions. This can be ensured by using the
  synchronization API of your array library. mpi4py does not have
  access to any GPU-specific functionality and thus cannot perform
  this operation automatically for users.


Running Python scripts with MPI
-------------------------------

Most MPI programs can be run with the command :program:`mpiexec`. In
practice, running Python programs looks like::

  $ mpiexec -n 4 python script.py

to run the program with 4 processors.


Point-to-Point Communication
----------------------------

* Python objects (:mod:`pickle` under the hood)::

   from mpi4py import MPI

   comm = MPI.COMM_WORLD
   rank = comm.Get_rank()

   if rank == 0:
       data = {'a': 7, 'b': 3.14}
       comm.send(data, dest=1, tag=11)
   elif rank == 1:
       data = comm.recv(source=0, tag=11)

* Python objects with non-blocking communication::

   from mpi4py import MPI

   comm = MPI.COMM_WORLD
   rank = comm.Get_rank()

   if rank == 0:
       data = {'a': 7, 'b': 3.14}
       req = comm.isend(data, dest=1, tag=11)
       req.wait()
   elif rank == 1:
       req = comm.irecv(source=0, tag=11)
       data = req.wait()

* NumPy arrays (the fast way!)::

   from mpi4py import MPI
   import numpy

   comm = MPI.COMM_WORLD
   rank = comm.Get_rank()

   # passing MPI datatypes explicitly
   if rank == 0:
       data = numpy.arange(1000, dtype='i')
       comm.Send([data, MPI.INT], dest=1, tag=77)
   elif rank == 1:
       data = numpy.empty(1000, dtype='i')
       comm.Recv([data, MPI.INT], source=0, tag=77)

   # automatic MPI datatype discovery
   if rank == 0:
       data = numpy.arange(100, dtype=numpy.float64)
       comm.Send(data, dest=1, tag=13)
   elif rank == 1:
       data = numpy.empty(100, dtype=numpy.float64)
       comm.Recv(data, source=0, tag=13)


Collective Communication
------------------------

* Broadcasting a Python dictionary::

   from mpi4py import MPI

   comm = MPI.COMM_WORLD
   rank = comm.Get_rank()

   if rank == 0:
       data = {'key1' : [7, 2.72, 2+3j],
               'key2' : ( 'abc', 'xyz')}
   else:
       data = None
   data = comm.bcast(data, root=0)

* Scattering Python objects::

   from mpi4py import MPI

   comm = MPI.COMM_WORLD
   size = comm.Get_size()
   rank = comm.Get_rank()

   if rank == 0:
       data = [(i+1)**2 for i in range(size)]
   else:
       data = None
   data = comm.scatter(data, root=0)
   assert data == (rank+1)**2

* Gathering Python objects::

   from mpi4py import MPI

   comm = MPI.COMM_WORLD
   size = comm.Get_size()
   rank = comm.Get_rank()

   data = (rank+1)**2
   data = comm.gather(data, root=0)
   if rank == 0:
       for i in range(size):
           assert data[i] == (i+1)**2
   else:
       assert data is None

* Broadcasting a NumPy array::

   from mpi4py import MPI
   import numpy as np

   comm = MPI.COMM_WORLD
   rank = comm.Get_rank()

   if rank == 0:
       data = np.arange(100, dtype='i')
   else:
       data = np.empty(100, dtype='i')
   comm.Bcast(data, root=0)
   for i in range(100):
       assert data[i] == i

* Scattering NumPy arrays::

   from mpi4py import MPI
   import numpy as np

   comm = MPI.COMM_WORLD
   size = comm.Get_size()
   rank = comm.Get_rank()

   sendbuf = None
   if rank == 0:
       sendbuf = np.empty([size, 100], dtype='i')
       sendbuf.T[:,:] = range(size)
   recvbuf = np.empty(100, dtype='i')
   comm.Scatter(sendbuf, recvbuf, root=0)
   assert np.allclose(recvbuf, rank)

* Gathering NumPy arrays::

   from mpi4py import MPI
   import numpy as np

   comm = MPI.COMM_WORLD
   size = comm.Get_size()
   rank = comm.Get_rank()

   sendbuf = np.zeros(100, dtype='i') + rank
   recvbuf = None
   if rank == 0:
       recvbuf = np.empty([size, 100], dtype='i')
   comm.Gather(sendbuf, recvbuf, root=0)
   if rank == 0:
       for i in range(size):
           assert np.allclose(recvbuf[i,:], i)

* Parallel matrix-vector product::

   from mpi4py import MPI
   import numpy

   def matvec(comm, A, x):
       m = A.shape[0] # local rows
       p = comm.Get_size()
       xg = numpy.zeros(m*p, dtype='d')
       comm.Allgather([x,  MPI.DOUBLE],
                      [xg, MPI.DOUBLE])
       y = numpy.dot(A, xg)
       return y


MPI-IO
------

* Collective I/O with NumPy arrays::

    from mpi4py import MPI
    import numpy as np
     
    amode = MPI.MODE_WRONLY|MPI.MODE_CREATE
    comm = MPI.COMM_WORLD
    fh = MPI.File.Open(comm, "./datafile.contig", amode)
    
    buffer = np.empty(10, dtype=np.int)
    buffer[:] = comm.Get_rank()
    
    offset = comm.Get_rank()*buffer.nbytes
    fh.Write_at_all(offset, buffer)
    
    fh.Close()

* Non-contiguous Collective I/O with NumPy arrays and datatypes::

    from mpi4py import MPI
    import numpy as np

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    amode = MPI.MODE_WRONLY|MPI.MODE_CREATE
    fh = MPI.File.Open(comm, "./datafile.noncontig", amode)

    item_count = 10

    buffer = np.empty(item_count, dtype='i')
    buffer[:] = rank

    filetype = MPI.INT.Create_vector(item_count, 1, size)
    filetype.Commit()

    displacement = MPI.INT.Get_size()*rank
    fh.Set_view(displacement, filetype=filetype)

    fh.Write_all(buffer)
    filetype.Free()
    fh.Close()


Dynamic Process Management
--------------------------

* Compute Pi - Master (or parent, or client) side::

   #!/usr/bin/env python
   from mpi4py import MPI
   import numpy
   import sys

   comm = MPI.COMM_SELF.Spawn(sys.executable,
                              args=['cpi.py'],
                              maxprocs=5)

   N = numpy.array(100, 'i')
   comm.Bcast([N, MPI.INT], root=MPI.ROOT)
   PI = numpy.array(0.0, 'd')
   comm.Reduce(None, [PI, MPI.DOUBLE],
               op=MPI.SUM, root=MPI.ROOT)
   print(PI)

   comm.Disconnect()

* Compute Pi - Worker (or child, or server) side::

   #!/usr/bin/env python
   from mpi4py import MPI
   import numpy

   comm = MPI.Comm.Get_parent()
   size = comm.Get_size()
   rank = comm.Get_rank()

   N = numpy.array(0, dtype='i')
   comm.Bcast([N, MPI.INT], root=0)
   h = 1.0 / N; s = 0.0
   for i in range(rank, N, size):
       x = h * (i + 0.5)
       s += 4.0 / (1.0 + x**2)
   PI = numpy.array(s * h, dtype='d')
   comm.Reduce([PI, MPI.DOUBLE], None,
               op=MPI.SUM, root=0)

   comm.Disconnect()


CUDA-aware MPI + Python GPU arrays
----------------------------------

* Reduce-to-all CuPy arrays::

   from mpi4py import MPI
   import cupy as cp

   comm = MPI.COMM_WORLD
   size = comm.Get_size()
   rank = comm.Get_rank()

   sendbuf = cp.arange(10, dtype='i')
   recvbuf = cp.empty_like(sendbuf)
   assert hasattr(sendbuf, '__cuda_array_interface__')
   assert hasattr(recvbuf, '__cuda_array_interface__')
   cp.cuda.get_current_stream().synchronize()
   comm.Allreduce(sendbuf, recvbuf)

   assert cp.allclose(recvbuf, sendbuf*size)


One-Sided Communications
------------------------

* Read from (write to) the enitre RMA window::
  
    import numpy as np
    from mpi4py import MPI
    from mpi4py.util import dtlib

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    datatype = MPI.FLOAT
    np_dtype = dtlib.to_numpy_dtype(datatype)
    itemsize = datatype.Get_size()

    N = 10
    win_size = N * itemsize if rank == 0 else 0
    win = MPI.Win.Allocate(win_size, comm=comm)

    buf = np.empty(N, dtype=np_dtype)
    if rank == 0:
        buf.fill(42)
        win.Lock(rank=0)
        win.Put(buf, target_rank=0)
        win.Unlock(rank=0)
        comm.Barrier()
    else:
        comm.Barrier()
        win.Lock(rank=0)
        win.Get(buf, target_rank=0)
        win.Unlock(rank=0)
        assert np.all(buf == 42)

* Accessing a part of the RMA window using :data:`target` argument.
  Target is defined as ``[offset, length, datatype]``::

    import numpy as np
    from mpi4py import MPI
    from mpi4py.util import dtlib

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    datatype = MPI.FLOAT
    np_dtype = dtlib.to_numpy_dtype(datatype)
    itemsize = datatype.Get_size()

    N = comm.Get_size() + 1
    win_size = N * itemsize if rank == 0 else 0
    win = MPI.Win.Allocate(
        size=win_size,
        disp_unit=itemsize,
        comm=comm,
    )
    if rank == 0:
        mem = np.frombuffer(win, dtype=np_dtype)
        mem[:] = np.arange(len(mem), dtype=np_dtype)
    comm.Barrier()

    buf = np.zeros(3, dtype=np_dtype)
    target = (rank, 2, datatype)
    win.Lock(rank=0)
    win.Get(buf, target_rank=0, target=target)
    win.Unlock(rank=0)
    assert np.all(buf == [rank, rank+1, 0])


Wrapping with SWIG
------------------

* C source:

  .. sourcecode:: c

      /* file: helloworld.c */
      void sayhello(MPI_Comm comm)
      {
        int size, rank;
        MPI_Comm_size(comm, &size);
        MPI_Comm_rank(comm, &rank);
        printf("Hello, World! "
               "I am process %d of %d.\n",
               rank, size);
      }

* SWIG interface file:

  .. sourcecode:: c

      // file: helloworld.i
      %module helloworld
      %{
      #include <mpi.h>
      #include "helloworld.c"
      }%

      %include mpi4py/mpi4py.i
      %mpi4py_typemap(Comm, MPI_Comm);
      void sayhello(MPI_Comm comm);

* Try it in the Python prompt::

      >>> from mpi4py import MPI
      >>> import helloworld
      >>> helloworld.sayhello(MPI.COMM_WORLD)
      Hello, World! I am process 0 of 1.


Wrapping with F2Py
------------------

* Fortran 90 source:

  .. sourcecode:: fortran

      ! file: helloworld.f90
      subroutine sayhello(comm)
        use mpi
        implicit none
        integer :: comm, rank, size, ierr
        call MPI_Comm_size(comm, size, ierr)
        call MPI_Comm_rank(comm, rank, ierr)
        print *, 'Hello, World! I am process ',rank,' of ',size,'.'
      end subroutine sayhello
      
* Compiling example using f2py ::

      $ f2py -c --f90exec=mpif90 helloworld.f90 -m helloworld

* Try it in the Python prompt::

      >>> from mpi4py import MPI
      >>> import helloworld
      >>> fcomm = MPI.COMM_WORLD.py2f()
      >>> helloworld.sayhello(fcomm)
      Hello, World! I am process 0 of 1.
