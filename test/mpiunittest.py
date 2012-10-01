import sys, os, glob
import unittest

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

    if sys.version_info < (2,4):
        assertTrue  = unittest.TestCase.failUnless
        assertFalse = unittest.TestCase.failIf

ErrClsMap = None
def ErrClsName(ierr):
    global ErrClsMap
    if ErrClsMap is None:
        from mpi4py import MPI
        ErrClsMap = {}
        ErrClsMap[MPI.SUCCESS] = 'SUCCESS'
        for entry in dir(MPI):
            if 'ERR_' in entry:
                errcls = getattr(MPI, entry)
                ErrClsMap[errcls] = entry
    try:
        return ErrClsMap[ierr]
    except KeyError:
        return '<unknown>'


def find_tests(pattern='test_*.py', directory=None, exclude=()):
    if directory is None: directory = os.path.split(__file__)[0]
    pattern = os.path.join(directory, pattern)
    test_list = []
    for test_file in glob.glob(pattern):
        filename = os.path.basename(test_file)
        modulename = os.path.splitext(filename)[0]
        if modulename not in exclude:
            test = __import__(modulename)
            test_list.append(test)
    return test_list


def main(*args, **kargs):
    try:
        unittest.main(*args, **kargs)
    except SystemExit:
        pass
