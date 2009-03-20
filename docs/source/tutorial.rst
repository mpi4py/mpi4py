.. _tutorial:

Tutorial
========

.. warning:: Under construction. Contributions very welcome!


Point-to-Point
--------------

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

   if rank == 0:
      data = numpy.arange(1000, dtype='i')
      comm.Send([data, MPI.INT], dest=1, tag=77)
   elif rank == 1:
      data = numpy.empty(1000, dtype='i')
      comm.Recv([data, MPI.INT], source=0, tag=77)


Collectives
-----------

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

   #! /usr/bin/env python
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

   #! /usr/bin/env python
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

* C source::

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

* SWIG interface file::

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

* Fortran 90 source::

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
