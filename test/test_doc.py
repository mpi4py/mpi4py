from mpi4py import MPI
import mpiunittest as unittest
import sys, types

ModuleType = type(MPI)
ClassType = type(MPI.Comm)
FunctionType = type(MPI.Init)
MethodDescrType = type(MPI.Comm.Get_rank)
GetSetDescrType = type(MPI.Comm.rank)

def getdocstr(mc, docstrings, namespace=None):
    name = getattr(mc, '__name__', None)
    if name is None: return
    if name in ('__builtin__', 'builtins'): return
    if name.startswith('_'): return
    if namespace: name = '%s.%s' % (namespace, name)
    if type(mc) in (ModuleType, ClassType):
        doc = getattr(mc, '__doc__', None)
        if doc == "<undocumented>": return
        docstrings[name] = doc
        for k, v in vars(mc).items():
            if isinstance(v, staticmethod):
                v = v.__get__(object)
            getdocstr(v, docstrings, name)
    elif type(mc) in (FunctionType, MethodDescrType, GetSetDescrType):
        doc = getattr(mc, '__doc__', None)
        if doc == "<undocumented>": return
        docstrings[name] = doc

class TestDoc(unittest.TestCase):

    @unittest.skipIf(hasattr(sys, 'pypy_version_info'), 'pypy')
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
                    if 'mpi4py.MPI' in doc:
                        print ("'%s': bad format docstring" % k)
        self.assertFalse(missing)


if __name__ == '__main__':
    unittest.main()
