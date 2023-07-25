from mpi4py import MPI
import mpiunittest as unittest
import sys

ModuleType = type(MPI)
ClassType = type(MPI.Comm)
FunctionType = type(MPI.Init)
StaticMethodType = type(MPI.memory.allocate)
ClassMethodType = type(MPI.Comm.Get_parent)
MethodDescrType = type(MPI.Comm.Get_rank)
GetSetDescrType = type(MPI.Comm.rank)


def getdocstr(mc, docstrings, namespace=None):
    name = getattr(mc, '__name__', None)
    if name is None: return
    if name in ('__builtin__', 'builtins'): return
    if namespace: name = f'{namespace}.{name}'
    if type(mc) in (
        ModuleType,
        ClassType,
    ):
        doc = getattr(mc, '__doc__', None)
        if doc == "<undocumented>": return
        docstrings[name] = doc
        for k, v in vars(mc).items():
            if isinstance(v, (classmethod, staticmethod)):
                v = v.__get__(mc)
            getdocstr(v, docstrings, name)
    elif type(mc) in (
        FunctionType,
        StaticMethodType,
        ClassMethodType,
        MethodDescrType,
        GetSetDescrType,
    ):
        doc = getattr(mc, '__doc__', None)
        if doc == "<undocumented>": return
        if doc is not None:
            sig, _, doc = doc.partition('\n')
        docstrings[name] = doc


@unittest.skipIf(hasattr(sys, 'pypy_version_info'), 'pypy')
class TestDoc(unittest.TestCase):

    def testDoc(self):
        ignore = {'py2f', 'f2py'}
        invalid = False
        missing = False
        docs = { }
        getdocstr(MPI, docs)
        for k in docs:
            doc = docs[k]
            name = k.split('.')[-1]
            if name in ignore:
                continue
            if not doc and name.startswith('_'):
                continue
            if doc is None:
                print (f"'{k}': missing docstring")
                missing = True
                continue
            if not doc.strip():
                print (f"'{k}': empty docstring")
                missing = True
                continue
            if doc.startswith('\n') and not doc.endswith(' '):
                print (f"'{k}': mismatch start and end whitespace")
                invalid  = True
            if not doc.startswith('\n') and doc.endswith(' '):
                print (f"'{k}': mismatch start and end whitespace")
                invalid  = True
            if doc.replace(' ', '').endswith('\n\n'):
                print (f"'{k}': docstring ends with too many newlines")
                invalid  = True
            doc = doc.strip()
            if doc[0] == doc[0].lower():
                print (f"'{k}': docstring starts with lowercase")
                invalid  = True
            if not doc.endswith('.'):
                print (f"'{k}': docstring does not end with '.'")
                invalid  = True
            summary, _, description = doc.partition('\n')
            if not summary.endswith('.'):
                print (f"'{k}': summary line does not end with '.'")
                invalid  = True
        self.assertFalse(missing)
        self.assertFalse(invalid)


if __name__ == '__main__':
    unittest.main()
