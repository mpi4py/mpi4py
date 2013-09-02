# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""
Runtime configuration parameters
"""

initialize = True
"""
Automatic MPI initialization at import.

* Any of ``{True, "yes", 1}``: initialize MPI at import.
* Any of ``{False, "no", 0}``: do not initialize MPI at import.
"""


threaded = True
"""
Request for thread support at MPI initialization.

* Any of ``{True, "yes", 1}``: initialize MPI with ``MPI_Init_thread()``.
* Any of ``{False, "no", 0}``: initialize MPI with ``MPI_Init()``.
"""


thread_level = "multiple"
"""
Level of thread support to request at MPI initialization.

* ``"single"``     : use ``MPI_THREAD_SINGLE``.
* ``"funneled"``   : use ``MPI_THREAD_FUNNELED``.
* ``"serialized"`` : use ``MPI_THREAD_SERIALIZED``.
* ``"multiple"``   : use ``MPI_THREAD_MULTIPLE``.
"""


finalize = None
"""
Automatic MPI finalization at exit.

* ``None``: Finalize MPI  at exit iff it was initialized at import.
* Any of ``{True, "yes", 1}``: call ``MPI_Finalize()`` at exit.
* Any of ``{False, "no", 0}``: do not call ``MPI_Finalize()`` at exit.
"""
