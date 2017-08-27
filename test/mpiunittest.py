import os
import sys
import glob
import unittest
from distutils.versionpredicate import VersionPredicate


class TestCase(unittest.TestCase):

    def assertRaisesMPI(self, IErrClass, callableObj, *args, **kwargs):
        from mpi4py.MPI import Exception as excClass, Get_version
        try:
            callableObj(*args, **kwargs)
        except NotImplementedError:
            if Get_version() >= (2, 0):
                raise self.failureException("raised NotImplementedError")
        except excClass:
            excValue = sys.exc_info()[1]
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
                    "generated error class is '%s' (%d), "
                    "but expected '%s' (%s)" % \
                    (ErrClsName(error_class), error_class,
                     IErrClassName,  IErrClass,)
                    )
        else:
            if hasattr(excClass,'__name__'): excName = excClass.__name__
            else: excName = str(excClass)
            raise self.failureException("%s not raised" % excName)

    failUnlessRaisesMPI = assertRaisesMPI

ErrClsMap = None
def ErrClsName(ierr):
    global ErrClsMap
    if ErrClsMap is None:
        from mpi4py import MPI
        ErrClsMap = {}
        ErrClsMap[MPI.SUCCESS] = 'SUCCESS'
        for entry in dir(MPI):
            if entry.startswith('ERR_'):
                errcls = getattr(MPI, entry)
                ErrClsMap[errcls] = entry
    try:
        return ErrClsMap[ierr]
    except KeyError:
        return '<unknown>'


SkipTest = unittest.SkipTest

skip = unittest.skip

skipIf = unittest.skipIf

skipUnless = unittest.skipUnless

def skipMPI(predicate, *conditions):
    from mpi4py import MPI
    def key(s):
        s = s.replace(' ', '')
        s = s.replace('/', '')
        s = s.replace('-', '')
        s = s.replace('Microsoft', 'MS')
        return s.lower()
    vp = VersionPredicate(key(predicate))
    if vp.name == 'mpi':
        name, version = 'mpi', MPI.Get_version()
        version = version + (0,)
    else:
        name, version = MPI.get_vendor()
    if vp.name == key(name):
        if vp.satisfied_by('%d.%d.%d' % version):
            if not conditions or any(conditions):
                return unittest.skip(str(vp))
    return unittest.skipIf(False, '')

def disable(what, reason):
    return unittest.skip(reason)(what)


def main(*args, **kargs):
    try:
        unittest.main(*args, **kargs)
    except SystemExit:
        pass
