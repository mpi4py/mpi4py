from mpi4py import MPI
import mpiunittest as unittest
import sys

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
    if namespace: name = f'{namespace}.{name}'
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


@unittest.skipIf(hasattr(sys, 'pypy_version_info'), 'pypy')
class TestDoc(unittest.TestCase):

    def testDoc(self):
        missing = False
        docs = { }
        getdocstr(MPI, docs)
        for k in docs:
            if not k.startswith('_'):
                doc = docs[k]
                if doc is None:
                    print (f"'{k}': missing docstring")
                    missing = True
                else:
                    doc = doc.strip()
                    if not doc:
                        print (f"'{k}': empty docstring")
                        missing = True
                    if 'mpi4py.MPI' in doc:
                        print (f"'{k}': bad format docstring")
        self.assertFalse(missing)


if __name__ == '__main__':
    unittest.main()
