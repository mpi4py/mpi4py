# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Entry point for MPI workers."""
from . import _worker

if __name__ == '__main__':
    _worker.server_main()
