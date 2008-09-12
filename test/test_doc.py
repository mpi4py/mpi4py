import types
from mpi4py import MPI
import mpiunittest as unittest

ModuleType = type(MPI)
ClassType = type(MPI.Comm)
FunctionType = type(MPI.Init)
MethodDescrType = type(MPI.Comm.Get_rank)
GetSetDescrType = type(MPI.Comm.rank)

def getdocstr(mc, docstrings):
    if type(mc) in (ModuleType, ClassType):
        name = getattr(mc, '__name__')
        if name in ('__builtin__', 'builtin'): return
        doc = getattr(mc, '__doc__', None)
        docstrings[name] = doc
        for k, v in vars(mc).items():
            getdocstr(v, docstrings)
    elif type(mc) in (FunctionType, MethodDescrType, GetSetDescrType):
        name = getattr(mc, '__name__')
        if name in ('__builtin__', 'builtin'): return
        doc = getattr(mc, '__doc__', None)
        docstrings[name] = doc

class TestDoc(unittest.TestCase):

    def testDoc(self):
        missing = False
        docs = { }
        getdocstr(MPI, docs)
        for k in docs:
            if not k.startswith('_'):
                doc = docs[k]
                if doc is None:
                    print ("'%s': missing docstring" % k)
                    missing = True
                else:
                    doc = doc.strip()
                    if not doc:
                        print ("'%s': empty docstring" % k)
                        missing = True
        self.assertFalse(missing)


if __name__ == '__main__':
    unittest.main()
