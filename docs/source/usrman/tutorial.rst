.. _tutorial:

Tutorial
========

.. warning::

   Under construction. Contributions very welcome!

*MPI for Python* supports convenient, *pickle*-based communication of
generic Python object as well as fast, near C-speed, direct array data
communication of buffer-provider objects (e.g., NumPy arrays).

* Communication of generic Python objects

  You have to use **all-lowercase** methods (of the :class:`Comm`
  class), like :meth:`send()`, :meth:`recv()`, :meth:`bcast()`. Note
  that :meth:`isend()` is available, but :meth:`irecv()` is not.

  Collective calls like :meth:`scatter()`, :meth:`gather()`,
  :meth:`allgather()`, :meth:`alltoall()` expect/return a sequence of
  :attr:`Comm.size` elements at the root or all process. They return a
  single value, a list of :attr:`Comm.size` elements, or
  :const:`None`.

  Global reduction operations :meth:`reduce()` and :meth:`allreduce()`
  are naively implemented, the reduction is actually done at the
  designated root process or all processes.

* Communication of buffer-provider objects

  You have to use method names starting with an **upper-case** letter
  (of the :class:`Comm` class), like :meth:`Send()`, :meth:`Recv()`,
  :meth:`Bcast()`.

  In general, buffer arguments to these calls must be explicitly
  specified by using a 2/3-list/tuple like ``[data, MPI.DOUBLE]``, or
  ``[data, count, MPI.DOUBLE]`` (the former one uses the byte-size of
  ``data`` and the extent of the MPI datatype to define the
  ``count``).

  Automatic MPI datatype discovery for NumPy arrays and PEP-3118
  buffers is supported, but limited to basic C types (all C/C99-native
  signed/unsigned integral types and single/double precision
  real/complex floating types) and availability of matching datatypes
  in the underlying MPI implementation. In this case, the
  buffer-provider object can be passed directly as a buffer argument,
  the count and MPI datatype will be inferred.


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

* NumPy arrays (the fast way!)::

   from mpi4py import MPI
   import numpy

   comm = MPI.COMM_WORLD
   rank = comm.Get_rank()

   # pass explicit MPI datatypes
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


Dynamic Process Management
--------------------------

Compute Pi
++++++++++

* Master (or parent, or client) side::

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

* Worker (or child, or server) side::

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

* Try it in the Python prompt::

      >>> from mpi4py import MPI
      >>> import helloworld
      >>> fcomm = MPI.COMM_WORLD.py2f()
      >>> helloworld.sayhello(fcomm)
      Hello, World! I am process 0 of 1.
