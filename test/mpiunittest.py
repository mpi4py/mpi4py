import os
import sys
import glob
import unittest


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


class VersionPredicate:

    def __init__(self, versionPredicateStr):
        import re
        re_validPkg = re.compile(r"(?i)^\s*([a-z_]\w*(?:\.[a-z_]\w*)*)(.*)")
        re_paren = re.compile(r"^\s*\((.*)\)\s*$")
        re_splitCmp = re.compile(r"^\s*(<=|>=|<|>|!=|==)\s*([^\s,]+)\s*$")

        def splitUp(pred):
            res = re_splitCmp.match(pred)
            if not res:
                raise ValueError("bad package restriction syntax: %r" % pred)
            comp, verStr = res.groups()
            version = tuple(map(int, verStr.split(".")))
            return (comp, version)

        versionPredicateStr = versionPredicateStr.strip()
        if not versionPredicateStr:
            raise ValueError("empty package restriction")
        match = re_validPkg.match(versionPredicateStr)
        if not match:
            raise ValueError("bad package name in %r" % versionPredicateStr)
        self.name, paren = match.groups()
        paren = paren.strip()
        if paren:
            match = re_paren.match(paren)
            if not match:
                raise ValueError("expected parenthesized list: %r" % paren)
            str = match.groups()[0]
            self.pred = [splitUp(aPred) for aPred in str.split(",")]
            if not self.pred:
                raise ValueError("empty parenthesized list in %r"
                                 % versionPredicateStr)
        else:
            self.pred = []

    def __str__(self):
        if self.pred:
            seq = [cond + " " + str(ver) for cond, ver in self.pred]
            return self.name + " (" + ", ".join(seq) + ")"
        else:
            return self.name

    def satisfied_by(self, version):
        import operator
        compmap = {"<": operator.lt, "<=": operator.le, "==": operator.eq,
                   ">": operator.gt, ">=": operator.ge, "!=": operator.ne}
        version = tuple(map(int, version.split(".")))
        for cond, ver in self.pred:
            if not compmap[cond](version, ver):
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
    vp = VersionPredicate(key(predicate))
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


def main(*args, **kargs):
    from main import main
    try:
        main(*args, **kargs)
    except SystemExit:
        pass
