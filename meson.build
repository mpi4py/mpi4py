project(
  'mpi4py',
  'c', 'cython',
  version: run_command(
    find_program('python3'),
    files('conf' / 'getversion.py'),
    check: true,
  ).stdout().strip(),
  license: 'BSD-2-Clause',
  meson_version: '>=1.0.0',
)

# ---

fs = import('fs')
py = import('python').find_installation('python3', pure: false)

srcdir = 'src'
dstdir = py.get_install_dir(pure: false)

# ---

mpi = dependency('', required: false)
compiler = meson.get_compiler('c')

configtest_c = '''
#include <mpi.h>
int main(int argc, char *argv[])
{
  MPI_Init(&argc, &argv);
  MPI_Finalize();
  return 0;
}
'''
advise = '''
Set environment variable `CC=mpicc` and try again.'''
if not compiler.has_header('mpi.h', dependencies: [mpi])
  error('MPI C header file "mpi.h" not found.', advise)
endif
if not compiler.has_function('MPI_Init', dependencies: [mpi])
  error('MPI C function MPI_Init not found.', advise)
endif
if not compiler.has_function('MPI_Finalize', dependencies: [mpi])
  error('MPI C function MPI_Finalize not found.', advise)
endif
if not compiler.compiles(configtest_c, dependencies: [mpi])
  error('Cannot compile basic MPI program.', advise)
endif
if not compiler.links(configtest_c, dependencies: [mpi])
  error('Cannot link basic MPI program.', advise)
endif


# ---

echo = [py, '-c', 'import sys; print(*sys.argv[1:], sep=chr(10))']
copy = [py, '-c', 'import shutil, sys; shutil.copy(*sys.argv[1:])']

install_intelmpi_pth = (
  host_machine.system() == 'windows' and
  compiler.has_header_symbol('mpi.h', 'I_MPI_VERSION')
)
custom_target(
  input: files('conf' / 'intelmpi.pth'),
  output: 'intelmpi.pth',
  command: copy + ['@INPUT@', '@OUTPUT0@'],
  install: install_intelmpi_pth,
  install_dir: dstdir,
)

mpicc = compiler.cmd_array()[0]
mpicc = find_program(mpicc).full_path()
mpi_cfg = ['[mpi]', 'mpicc = @0@'.format(mpicc)]
custom_target(
  output: 'mpi.cfg',
  capture: true,
  command: echo + mpi_cfg,
  install: true,
  install_dir: dstdir / 'mpi4py',
)

executable(
  'python-mpi',
  sources: srcdir / 'python.c',
  implicit_include_directories: false,
  dependencies: [py.dependency(embed: true), mpi],
  install: true,
  install_dir: dstdir / 'mpi4py' / 'bin',
)

cython = files('conf' / 'cythonize.py')
MPI_ch = custom_target(
  'MPI.[ch]',
  input: srcdir / 'mpi4py' / 'MPI.pyx',
  output: ['MPI.c', 'MPI.h', 'MPI_api.h'],
  command: [py, cython, '@INPUT@', '--output-file', '@OUTPUT0@'],
  install: true,
  install_dir: [false, dstdir / 'mpi4py', dstdir / 'mpi4py']
)

py.extension_module(
  'MPI',
  sources: MPI_ch[0],
  include_directories: [srcdir],
  implicit_include_directories: false,
  dependencies: [mpi],
  subdir: 'mpi4py',
  install: true,
)

package = {
  'mpi4py': [
    '__init__.py',
    '__main__.py',
    'bench.py',
    'run.py',
    'typing.py',
    '__init__.pxd',
    'libmpi.pxd',
    'MPI.pxd',
    'py.typed',
  ],
  'mpi4py.futures': [
    '__init__.py',
    '__main__.py',
    '_base.py',
    '_lib.py',
    'pool.py',
    'server.py',
    'aplus.py',
  ],
  'mpi4py.util': [
    '__init__.py',
    'pkl5.py',
    'dtlib.py',
    'pool.py',
  ],
}

foreach pkg, src : package
  subdir = join_paths(pkg.split('.'))
  sources = []
  foreach fn : src
    sources += srcdir / subdir / fn
    if fn.endswith('.py')
      pyi = srcdir / subdir / fn + 'i'
      if fs.exists(pyi)
        sources += pyi
      endif
    endif
  endforeach
  py.install_sources(
    sources,
    pure: false,
    subdir: subdir,
  )
endforeach

install_subdir(
  srcdir / 'mpi4py' / 'include',
  install_dir: dstdir / 'mpi4py',
)

# ---
