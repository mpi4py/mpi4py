MPI for Python
==============

:Author:       Lisandro Dalcín
:Contact:      dalcinl@gmail.com
:Web Site:     http://mpi4py.googlecode.com
:Organization: `CIMEC <http://www.cimec.org.ar/>`_
:Address:      PTLC, (3000) Santa Fe, Argentina
:Date:         |today|
:Copyright:    This document has been placed in the public domain.

This document describes the *MPI for Python* package.  *MPI for
Python* provides bindings of the *Message Passing Interface* (MPI)
standard for the Python programming language, allowing any Python
program to exploit multiple processors.
	       
This package is constructed on top of the MPI-1/2 specifications and
provides an object oriented interface which closely follows MPI-2 C++
bindings. It supports point-to-point (sends, receives) and collective
(broadcasts, scatters, gathers) communications of any *picklable*
Python object, as well as optimized communications of Python object
exposing the single-segment buffer interface (NumPy arrays, builtin
bytes/string/array objects)


Contents
========

.. toctree::
   :maxdepth: 2

   intro
   mpi4py
   install
   tutorial
   appendix


.. Indices and tables
.. ==================
.. 
.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
