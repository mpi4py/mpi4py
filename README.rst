==============
MPI for Python
==============

.. image::  https://github.com/mpi4py/mpi4py/workflows/ci/badge.svg?branch=master
   :target: https://github.com/mpi4py/mpi4py/actions/
.. image::  https://dev.azure.com/mpi4py/mpi4py/_apis/build/status/mpi4py.mpi4py?branchName=master
   :target: https://dev.azure.com/mpi4py/mpi4py/_build
.. image::  https://ci.appveyor.com/api/projects/status/whh5xovp217h0f7n?svg=true
   :target: https://ci.appveyor.com/project/mpi4py/mpi4py
.. image::  https://circleci.com/gh/mpi4py/mpi4py.svg?style=shield
   :target: https://circleci.com/gh/mpi4py/mpi4py
.. image::  https://travis-ci.com/mpi4py/mpi4py.svg?branch=master
   :target: https://travis-ci.com/mpi4py/mpi4py
.. image::  https://scan.coverity.com/projects/mpi4py-mpi4py/badge.svg
   :target: https://scan.coverity.com/projects/mpi4py-mpi4py
.. image::  https://codecov.io/gh/mpi4py/mpi4py/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/mpi4py/mpi4py
.. image::  https://readthedocs.org/projects/mpi4py/badge/?version=latest
   :target: https://mpi4py.readthedocs.org/en/latest/

Overview
--------

This package provides Python bindings for the *Message Passing
Interface* (`MPI <https://www.mpi-forum.org/>`_) standard. It is
implemented on top of the MPI specification and exposes an API which
grounds on the standard MPI-2 C++ bindings.

Dependencies
------------

* `Python <https://www.python.org/>`_ 2.7, 3.5 or above,
  or `PyPy <https://www.pypy.org/>`_ 2.0 or above.

* An MPI implementation like `MPICH <https://www.mpich.org/>`_ or
  `Open MPI <https://www.open-mpi.org/>`_ built with shared/dynamic
  libraries.

* To work with the in-development version, you need to install `Cython
  <https://cython.org/>`_.

Testsuite
---------

The testsuite is run periodically on

* `GitHub Actions <https://github.com/mpi4py/mpi4py/actions/>`_

* `Azure Pipelines <https://dev.azure.com/mpi4py/mpi4py>`_

* `AppVeyor <https://ci.appveyor.com/project/mpi4py/mpi4py>`_

* `Circle CI <https://circleci.com/gh/mpi4py/mpi4py>`_

* `Travis CI <https://travis-ci.com/mpi4py/mpi4py>`_

* `Fedora Jenkins <http://jenkins.fedorainfracloud.org/job/mpi4py/>`_
