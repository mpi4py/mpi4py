import os
import sys
import glob
import unittest
from collections import namedtuple


class TestCase(unittest.TestCase):

    def assertRaisesMPI(self, IErrClass, callableObj, *args, **kwargs):
        from mpi4py import MPI
        excClass = MPI.Exception
        try:
            callableObj(*args, **kwargs)
        except NotImplementedError:
            if MPI.Get_version() < (2, 0):
                raise self.failureException("raised NotImplementedError")
        except excClass as excValue:
            error_class = excValue.Get_error_class()
            if isinstance(IErrClass, (list, tuple)):
                match = (error_class in IErrClass)
            else:
                match = (error_class == IErrClass)
            if not match:
                if isinstance(IErrClass, (list, tuple)):
                    IErrClassName = [ErrClsName(e) for e in IErrClass]
                    IErrClassName = type(IErrClass)(IErrClassName)
                else:
                    IErrClassName = ErrClsName(IErrClass)
                raise self.failureException(
                    "generated error class is '{}' ({}), "
                    "but expected '{}' ({})".format(
                        ErrClsName(error_class), error_class,
                        IErrClassName, IErrClass,
                    )
                )
        else:
            raise self.failureException(f"{excClass.__name__} not raised")


ErrClsMap = {}


def ErrClsName(ierr):
    if not ErrClsMap:
        from mpi4py import MPI
        ErrClsMap[MPI.SUCCESS] = 'SUCCESS'
        for entry in dir(MPI):
            if entry.startswith('ERR_'):
                errcls = getattr(MPI, entry)
                ErrClsMap[errcls] = entry
    try:
        return ErrClsMap[ierr]
    except KeyError:
        return '<unknown>'


_Version = namedtuple("_Version", ["major", "minor", "patch"])


def _parse_version(version):
    version = tuple(map(int, version.split('.'))) + (0, 0, 0)
    return _Version(*version[:3])


class _VersionPredicate:

    def __init__(self, versionPredicateStr):
        import re
        re_name = re.compile(r"(?i)^([a-z_]\w*(?:\.[a-z_]\w*)*)(.*)$")
        re_pred = re.compile(r"^(<=|>=|<|>|!=|==)(.*)$")

        def split(item):
            m = re_pred.match(item)
            op, version = m.groups()
            version = _parse_version(version)
            return op, version

        vpstr = versionPredicateStr.replace(' ', '')
        m = re_name.match(vpstr)
        name, plist = m.groups()
        if plist:
            assert plist[0] == '(' and plist[-1] == ')'
            plist = plist[1:-1]
        pred = [split(p) for p in plist.split(',') if p]
        self.name = name
        self.pred = pred

    def __str__(self):
        if self.pred:
            items = [f"{op}{'.'.join(map(str, ver))}" for op, ver in self.pred]
            return f"{self.name}({','.join(items)})"
        else:
            return self.name

    def satisfied_by(self, version):
        from operator import lt, le, gt, ge, eq, ne
        opmap = {'<': lt, '<=': le, '>': gt, '>=': ge, '==': eq, '!=': ne}
        version = _parse_version(version)
        for op, ver in self.pred:
            if not opmap[op](version, ver):
                return False
        return True


def mpi_predicate(predicate):
    from mpi4py import MPI
    def key(s):
        s = s.replace(' ', '')
        s = s.replace('/', '')
        s = s.replace('-', '')
        s = s.replace('Microsoft', 'MS')
        return s.lower()
    vp = _VersionPredicate(key(predicate))
    if vp.name == 'mpi':
        name, version = 'mpi', MPI.Get_version()
        version = version + (0,)
    else:
        name, version = MPI.get_vendor()
    if vp.name == key(name):
        if vp.satisfied_by('%d.%d.%d' % version):
            return vp
    return None


def is_mpi_gpu(predicate, array):
    if array.backend in ('cupy', 'numba', 'dlpack-cupy'):
        if mpi_predicate(predicate):
            return True
    return False


SkipTest = unittest.SkipTest

skip = unittest.skip

skipIf = unittest.skipIf

skipUnless = unittest.skipUnless


def skipMPI(predicate, *conditions):
    version = mpi_predicate(predicate)
    if version:
        if not conditions or any(conditions):
            return unittest.skip(str(version))
    return unittest.skipIf(False, '')


def disable(what, reason):
    return unittest.skip(reason)(what)


def main(*args, **kwargs):
    from main import main
    try:
        main(*args, **kwargs)
    except SystemExit:
        pass
