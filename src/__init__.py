# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

"""
This is the **MPI for Python** package.

What is MPI?
============

MPI, the *Message Passing Interface*, is a standardized and portable
message-passing system designed to function on a wide variety of
parallel computers. The standard defines the syntax and semantics of
library routines and allows users to write portable programs in the
main scientific programming languages (Fortran, C, or C++).

Since its release, the MPI specification has become the leading
standard for message-passing libraries for parallel computers.
Implementations are available from vendors of high-performance
computers and from well known open source projects.

Package Structure
=================

Modules:

- MPI: Message Passing Interface

"""

__author__    = 'Lisandro Dalcin'
__credits__   = 'MPI Forum, MPICH Team, Open MPI Team.'
__version__   = '1.0.0'

# --------------------------------------------------------------------

__all__ = ['MPI',]

# --------------------------------------------------------------------

def get_include():
    """
    Return the directory in the package that contains header files.

    Extension modules that need to compile against mpi4py should use
    this function to locate the appropriate include directory. Using
    Python distutils (or perhaps NumPy distutils)::

      import mpi4py
      Extension('extension_name', ...
                include_dirs=[..., mpi4py.get_include()])

    """
    from os.path import dirname, join
    return join(dirname(__file__), 'include')

# --------------------------------------------------------------------
