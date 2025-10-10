# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

project(
  'mpi4py',
  'c',  # 'cython',
  version: run_command(
    find_program('python3'),
    files('conf' / 'metadata.py'), 'version',
    check: true,
  ).stdout().strip(),
  license: 'BSD-3-Clause',
  meson_version: '>=1.5.1',
)

# ---

fs = import('fs')
py = import('python').find_installation('python3', pure: false)

srcdir = 'src'
dstdir = py.get_install_dir(pure: false)

# ---

mpi = dependency('mpi', required: true)
pyembed = py.dependency(embed: true, disabler: true)
compiler = meson.get_compiler('c')

# ---

cython = [py, files('conf' / 'cythonize.py')]
cython_flags = ['--3str', '--cleanup', '3']
MPI_ch = custom_target(
  'MPI.[ch]',
  input: srcdir / 'mpi4py' / 'MPI.pyx',
  output: ['MPI.c', 'MPI.h', 'MPI_api.h'],
  command: [cython, cython_flags, '@INPUT@', '--output-file', '@OUTPUT0@'],
  install: true,
  install_dir: [false, dstdir / 'mpi4py', dstdir / 'mpi4py']
)

mpiabi = get_option('mpiabi')
pysabi = get_option('pysabi')
ext_args = {}
if mpiabi
  ext_args += {'c_args': ['-DPYMPIABI=1']}
endif
if pysabi != ''
  ext_args += {'limited_api': pysabi}
endif

py.extension_module(
  'MPI',
  sources: MPI_ch[0],
  include_directories: [srcdir],
  implicit_include_directories: false,
  dependencies: [mpi],
  subdir: 'mpi4py',
  install: true,
  kwargs: ext_args,
)

executable(
  'python-mpi',
  sources: srcdir / 'python.c',
  implicit_include_directories: false,
  dependencies: [pyembed, mpi],
  install: true,
  install_dir: dstdir / 'mpi4py' / 'bin',
)

package = {
  'mpi4py': [
    '__init__.py',
    '__main__.py',
    'bench.py',
    'run.py',
    'typing.py',
    '_mpiabi.py',
    '__init__.pxd',
    'libmpi.pxd',
    'MPI.pxd',
  ],
  'mpi4py.futures': [
    '__init__.py',
    '__main__.py',
    '_base.py',
    '_core.py',
    'pool.py',
    'util.py',
    'server.py',
    'aplus.py',
  ],
  'mpi4py.util': [
    '__init__.py',
    'pkl5.py',
    'dtlib.py',
    'pool.py',
    'sync.py',
  ],
}

foreach pkg, src : package
  subdir = join_paths(pkg.split('.'))
  sources = []
  foreach fn : src
    sources += srcdir / subdir / fn
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

if true
  foreach pkg, src : package
    subdir = join_paths(pkg.split('.'))
    sources = []
    if not pkg.contains('.')
      sources += srcdir / subdir / 'py.typed'
      sources += srcdir / subdir / 'MPI.pyi'
    endif
    foreach fn : src
      if fn.endswith('.py')
        sources += srcdir / subdir / fn + 'i'
      endif
    endforeach
    py.install_sources(
      sources,
      pure: false,
      subdir: subdir,
    )
  endforeach
endif

if host_machine.system() == 'windows'
  mpidllpath = ['_mpi_dll_path.py', 'mpi.pth']
  foreach fn : mpidllpath
    if fs.exists(srcdir / fn)
      py.install_sources(
        srcdir / fn,
        pure: false,
        subdir: '',
      )
    endif
  endforeach
endif

# ---
