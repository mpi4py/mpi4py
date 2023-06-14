# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Entry point for MPI workers."""


def main():
    """Entry point for worker processes."""
    # pylint: disable=import-outside-toplevel
    from . import _core
    _core.server_main()


if __name__ == '__main__':
    main()
