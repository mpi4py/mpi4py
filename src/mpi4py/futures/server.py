# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Entry point for MPI workers."""
from . import _lib

if __name__ == '__main__':
    _lib.server_main()
