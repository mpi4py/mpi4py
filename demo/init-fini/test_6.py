from importlib import import_module
from os import environ
from warnings import catch_warnings

from mpi4py import rc

ATTRS = {a for a in dir(rc) if not a.startswith("_")}
VALUE = -123456789

for attr in ATTRS:
    environ.pop(f"MPI4PY_RC_{attr.upper()}", None)
    setattr(rc, attr, VALUE)

with catch_warnings(record=True) as warnings:
    import_module("mpi4py.MPI")

template = "mpi4py.rc.{}: unexpected value {}"
expected = sorted({template.format(attr, repr(VALUE)) for attr in ATTRS})
messages = sorted({str(entry.message) for entry in warnings})
assert messages == expected, "\n" + "\n".join(messages)
