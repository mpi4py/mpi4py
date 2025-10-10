Guidelines
==========

Fair play
---------

Summary
+++++++

This section defines Rules of Play for companies and outside developers that
engage with the mpi4py project. It covers:

* Restrictions on use of the mpi4py name.
* How and whether to publish a modified distribution.
* How to make us aware of patched versions.

After reading this section, companies and developers will know what kinds of
behavior the mpi4py developers and contributors would like to see, and which we
consider troublesome, bothersome, and unacceptable.

This document is a close adaptation of `NumPy NEP 36`_.

.. _NumPy NEP 36: https://numpy.org/neps/nep-0036-fair-play.html

Motivation
++++++++++

Occasionally, we learn of modified mpi4py versions and binary distributions
circulated by outsiders. These patched versions can cause problems to mpi4py
users (see, e.g., `mpi4py/mpi4py#508`_). When issues like these arise, our
developers waste time identifying the problematic release, locating
alterations, and determining an appropriate course of action.

In addition, packages on the Python Packaging Index are sometimes named such
that users assume they are sanctioned or maintained by the mpi4py
developers. We wish to reduce the number of such incidents.

.. _mpi4py/mpi4py#508: https://github.com/mpi4py/mpi4py/issues/508

Scope
+++++

This document aims to define a minimal set of rules that, when followed, will
be considered good-faith efforts in line with the expectations of the mpi4py
developers and contributors.

Our hope is that companies and outside developers who feel they need to modify
mpi4py will first consider contributing to the project, or use alternative
mechanisms for patching and extending mpi4py.

When in doubt, please `talk to us first`__. We may suggest an alternative; at
minimum, we'll be informed and we may even grant an exception if deemed
appropriate.

__ https://github.com/mpi4py/mpi4py/discussions/

Fair play rules
+++++++++++++++

1. Do not reuse the mpi4py name for projects not affiliated with the mpi4py
   project.

   At time of writing, there are only a handful of ``mpi4py``-named packages
   developed by the mpi4py project, including ``mpi4py`` and ``mpi4py-fft``. We
   ask that outside packages not include the phrase ``mpi4py``, i.e., avoid
   names such as ``mycompany-mpi4py`` or ``mpi4py-mycompany``.

   To be clear, this rule only applies to modules (package names); it is
   perfectly acceptable to have a *submodule* of your own package named
   ``mycompany.mpi4py``.

2. Do not publish binary mpi4py wheels on PyPI (https://pypi.org/).

   We ask companies and outside developers to not publish binary mpi4py wheels
   in the main Python Package Index (https://pypi.org/) under names such
   ``mpi4py-mpich``, ``mpi4py-openmpi``, or ``mpi4py-vendor_mpi``.

   The usual approaches to build binary Python wheels involve the embedding of
   dependent shared libraries. While such an approach may seem convenient and
   often is, in the particular case of MPI and mpi4py it is ultimately harmful
   to end users. Embedding the MPI shared libraries would prevent the use of
   external, system-provided MPI installations with hardware-specific
   optimizations and site-specific tweaks.

   The MPI 5.0 standard features an Application Binary Interface (ABI) for
   MPI, see [mpi-abi-paper]_ and [mpi-abi-issue]_. Such standardization allows
   for any binary dependent on the MPI library to be used with multiple MPI
   backends. Once MPI implementations provide support for the new MPI ABI, the
   mpi4py project will follow and add support to the binary wheels published
   on PyPI.

   .. [mpi-abi-paper]
      J. Hammond, L. Dalcin, E. Schnetter, M. Pérache, J. B. Besnard,
      J. Brown, G. Brito Gadeschi, S. Byrne, J. Schuchart, and H. Zhou.
      MPI Application Binary Interface Standardization.
      EuroMPI 2023, Bristol, UK, September 2023.
      https://doi.org/10.1145/3615318.3615319

   .. [mpi-abi-issue]
      MPI Forum GitHub Issue: *MPI needs a standard ABI*.
      https://github.com/mpi-forum/mpi-issues/issues/751

3. Do not republish modified versions of mpi4py.

   Modified versions of mpi4py make it very difficult for the developers to
   address bug reports, since we typically do not know which parts of mpi4py
   have been modified.

   If you have to break this rule (and we implore you not to!), then make it
   clear in the ``__version__`` tag that you have modified mpi4py, e.g.::

     >>> print(mpi4py.__version__)
     '4.0.0+mycompany.13`

   We understand that minor patches are often required to make a library work
   inside of a package ecosystem. This is totally acceptable, but we ask that
   no substantive changes are made.

4. Do not extend or modify mpi4py's API.

   If you absolutely have to break the previous rule, please do not add
   additional functions to the namespace, or modify the API of existing
   functions. Having additional functions exposed in distributed versions is
   confusing for users and developers alike.


.. Local variables:
.. fill-column: 79
.. End:
