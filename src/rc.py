# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
# Id:      $Id$


# thread_level = None                 -> Non-threaded MPI
# thread_level = { 0 | "single"     } -> MPI_THREAD_SINGLE
# thread_level = { 1 | "funneled"   } -> MPI_THREAD_FUNNELED
# thread_level = { 2 | "serialized" } -> MPI_THREAD_SERIALIZED
# thread_level = { 3 | "multiple"   } -> MPI_THREAD_MULTIPLE

thread_level = "multiple"
