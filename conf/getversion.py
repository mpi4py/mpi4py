import re
import os


def version():
    p = os.path
    here = p.dirname(__file__)
    srcdir = p.abspath(p.join(here, p.pardir, 'src'))
    with open(p.join(srcdir, 'mpi4py', '__init__.py')) as f:
        m = re.search(r"__version__\s*=\s*'(.*)'", f.read())
    version = m.groups()[0]
    local_version = os.environ.get('MPI4PY_LOCAL_VERSION')
    if local_version:
        version = '{version}+{local_version}'.format(**vars())
    return version


if __name__ == '__main__':
    print(version())
