import re
import os


def version():
    p = os.path
    here = p.dirname(__file__)
    srcdir = p.abspath(p.join(here, p.pardir, 'src'))
    with open(p.join(srcdir, 'mpi4py', '__init__.py')) as f:
        m = re.search(r"__version__\s*=\s*'(.*)'", f.read())
    return m.groups()[0]


if __name__ == '__main__':
    print(version())
