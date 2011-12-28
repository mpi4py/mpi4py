Introduction
============

Over the last years, high performance computing has become an
affordable resource to many more researchers in the scientific
community than ever before. The conjunction of quality open source
software and commodity hardware strongly influenced the now widespread
popularity of Beowulf_ class clusters and cluster of workstations.

Among many parallel computational models, message-passing has proven
to be an effective one.  This paradigm is specially suited for (but
not limited to) distributed memory architectures and is used in
today's most demanding scientific and engineering application related
to modeling, simulation, design, and signal processing.  However,
portable message-passing parallel programming used to be a nightmare
in the past because of the many incompatible options developers were
faced to.  Fortunately, this situation definitely changed after the
MPI Forum released its standard specification.

High performance computing is traditionally associated with software
development using compiled languages. However, in typical applications
programs, only a small part of the code is time-critical enough to
require the efficiency of compiled languages. The rest of the code is
generally related to memory management, error handling, input/output,
and user interaction, and those are usually the most error prone and
time-consuming lines of code to write and debug in the whole
development process.  Interpreted high-level languages can be really
advantageous for this kind of tasks.

For implementing general-purpose numerical computations, MATLAB [#]_
is the dominant interpreted programming language. In the open source
side, Octave and Scilab are well known, freely distributed software
packages providing compatibility with the MATLAB language. In this
work, we present MPI for Python, a new package enabling applications
to exploit multiple processors using standard MPI "look and feel" in
Python scripts.

.. [#] MATLAB is a registered trademark of The MathWorks, Inc.


What is MPI?
------------

MPI_, [mpi-using]_ [mpi-ref]_ the *Message Passing Interface*, is a
standardized and portable message-passing system designed to function
on a wide variety of parallel computers. The standard defines the
syntax and semantics of library routines and allows users to write
portable programs in the main scientific programming languages
(Fortran, C, or C++).

Since its release, the MPI specification [mpi-std1]_ [mpi-std2]_ has
become the leading standard for message-passing libraries for parallel
computers.  Implementations are available from vendors of
high-performance computers and from well known open source projects
like MPICH_ [mpi-mpich]_, `Open MPI`_ [mpi-openmpi]_ or LAM_
[mpi-lammpi]_.


What is Python?
---------------

Python_ is a modern, easy to learn, powerful programming language. It
has efficient high-level data structures and a simple but effective
approach to object-oriented programming with dynamic typing and
dynamic binding. It supports modules and packages, which encourages
program modularity and code reuse. Python's elegant syntax, together
with its interpreted nature, make it an ideal language for scripting
and rapid application development in many areas on most platforms.

The Python interpreter and the extensive standard library are
available in source or binary form without charge for all major
platforms, and can be freely distributed. It is easily extended with
new functions and data types implemented in C or C++. Python is also
suitable as an extension language for customizable applications.

Python is an ideal candidate for writing the higher-level parts of
large-scale scientific applications [Hinsen97]_ and driving
simulations in parallel architectures [Beazley97]_ like clusters of
PC's or SMP's. Python codes are quickly developed, easily maintained,
and can achieve a high degree of integration with other libraries
written in compiled languages.


Related Projects
----------------

As this work started and evolved, some ideas were borrowed from well
known MPI and Python related open source projects from the Internet.

* `OOMPI`_

  + It has not relation with Python, but is an excellent object
    oriented approach to MPI.

  + It is a C++ class library specification layered on top of the C
    bindings that encapsulates MPI into a functional class hierarchy.

  + It provides a flexible and intuitive interface by adding some
    abstractions, like *Ports* and *Messages*, which enrich and
    simplify the syntax.

* `Pypar`_

  + Its interface is rather minimal. There is no support for
    communicators or process topologies.

  + It does not require the Python interpreter to be modified or
    recompiled, but does not permit interactive parallel runs.

  + General (*picklable*) Python objects of any type can be
    communicated. There is good support for numeric arrays,
    practically full MPI bandwidth can be achieved.

* `pyMPI`_

  + It rebuilds the Python interpreter providing a built-in module
    for message passing. It does permit interactive parallel runs,
    which are useful for learning and debugging.

  + It provides an interface suitable for basic parallel programing.
    There is not full support for defining new communicators or process
    topologies.

  + General (picklable) Python objects can be messaged between
    processors. There is not support for numeric arrays.

* `Scientific Python`_

  + It provides a collection of Python modules that are
    useful for scientific computing.

  + There is an interface to MPI and BSP (*Bulk Synchronous Parallel
    programming*).

  + The interface is simple but incomplete and does not resemble
    the MPI specification. There is support for numeric arrays.

Additionally, we would like to mention some available tools for
scientific computing and software development with Python.

+ `NumPy`_ is a package that provides array manipulation and
  computational capabilities similar to those found in IDL, MATLAB, or
  Octave. Using NumPy, it is possible to write many efficient
  numerical data processing applications directly in Python without
  using any C, C++ or Fortran code.

+ `SciPy`_ is an open source library of scientific tools for Python,
  gathering a variety of high level science and engineering modules
  together as a single package. It includes modules for graphics and
  plotting, optimization, integration, special functions, signal and
  image processing, genetic algorithms, ODE solvers, and others.

+ `Cython`_ is a language that makes writing C extensions for the
  Python language as easy as Python itself. The Cython language is
  very close to the Python language, but Cython additionally supports
  calling C functions and declaring C types on variables and class
  attributes. This allows the compiler to generate very efficient C
  code from Cython code. This makes Cython the ideal language for
  wrapping for external C libraries, and for fast C modules that speed
  up the execution of Python code.

+ `SWIG`_ is a software development tool that connects programs
  written in C and C++ with a variety of high-level programming
  languages like Perl, Tcl/Tk, Ruby and Python. Issuing header files
  to SWIG is the simplest approach to interfacing C/C++ libraries from
  a Python module.



.. External Links
.. ..............

.. _MPI:       http://www.mpi-forum.org/

.. _MPICH:     http://www.mcs.anl.gov/research/projects/mpich2/

.. _Open MPI:  http://www.open-mpi.org/

.. _LAM:       http://www.lam-mpi.org/

.. _Beowulf:   http://www.beowulf.org/


.. _Python:    http://www.python.org/

.. _NumPy:     http://numpy.scipy.org/

.. _SciPy:     http://www.scipy.org/

.. _Cython:    http://www.cython.org/

.. _SWIG:      http://www.swig.org/


.. _OOMPI:     http://www.osl.iu.edu/research/oompi/

.. _Pypar:     http://pypar.googlecode.com/

.. _pyMPI:     http://sourceforge.net/projects/pympi/

.. _Scientific Python:
               http://dirac.cnrs-orleans.fr/plone/software/scientificpython/


.. References
.. ..........

.. [mpi-std1] MPI Forum. MPI: A Message Passing Interface Standard.
   International Journal of Supercomputer Applications, volume 8,
   number 3-4, pages 159-416, 1994.

.. [mpi-std2] MPI Forum. MPI: A Message Passing Interface Standard.
   High Performance Computing Applications, volume 12, number 1-2,
   pages 1-299, 1998.

.. [mpi-using] William Gropp, Ewing Lusk, and Anthony Skjellum.  Using
   MPI: portable parallel programming with the message-passing
   interface.  MIT Press, 1994.

.. [mpi-ref] Mark Snir, Steve Otto, Steven Huss-Lederman, David
   Walker, and Jack Dongarra.  MPI - The Complete Reference, volume 1,
   The MPI Core.  MIT Press, 2nd. edition, 1998.

.. [mpi-mpich] W. Gropp, E. Lusk, N. Doss, and A. Skjellum.  A
   high-performance, portable implementation of the MPI message
   passing interface standard.  Parallel Computing, 22(6):789-828,
   September 1996.

.. [mpi-openmpi] Edgar Gabriel, Graham E. Fagg, George Bosilca, Thara
   Angskun, Jack J. Dongarra, Jeffrey M. Squyres, Vishal Sahay,
   Prabhanjan Kambadur, Brian Barrett, Andrew Lumsdaine, Ralph
   H. Castain, David J. Daniel, Richard L. Graham, and Timothy
   S. Woodall. Open MPI: Goals, Concept, and Design of a Next
   Generation MPI Implementation. In Proceedings, 11th European
   PVM/MPI Users' Group Meeting, Budapest, Hungary, September 2004.

.. [mpi-lammpi] Greg Burns, Raja Daoud, and James Vaigl.  LAM: An Open
   Cluster Environment for MPI. In Proceedings of Supercomputing
   Symposium, pages 379-386, 1994.

.. [Hinsen97] Konrad Hinsen.  The Molecular Modelling Toolkit: a case
   study of a large scientific application in Python.  In Proceedings
   of the 6th International Python Conference, pages 29-35, San Jose,
   Ca., October 1997.

.. [Beazley97] David M. Beazley and Peter S. Lomdahl.  Feeding a
   large-scale physics application to Python.  In Proceedings of the
   6th International Python Conference, pages 21-29, San Jose, Ca.,
   October 1997.
