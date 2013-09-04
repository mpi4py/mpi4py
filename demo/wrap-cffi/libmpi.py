import os.path as _pth
import cffi as _cffi

_wdir = _pth.abspath(_pth.dirname(__file__))

def _ffi_create(header, source, **kargs):
    ffi = _cffi.FFI()
    _ffi_define(ffi, header, **kargs)
    lib = _ffi_verify(ffi, source, **kargs)
    return ffi, lib

def _ffi_define(ffi, csource, **kargs):
    opt = kargs.pop('override', False)
    ffi.cdef(csource, opt)

def _ffi_verify(ffi, csource, **kargs):
    cc = kargs.pop('compiler', None)
    ld = kargs.pop('linker',   None)
    _ffi_verify_push(cc, ld)
    try:
        lib =  ffi.verify(csource, **kargs)
    finally:
        _ffi_verify_pop()
    return lib

def _ffi_verify_push(cc, ld):
    from distutils import sysconfig
    from distutils.spawn import find_executable
    global customize_compiler_orig
    customize_compiler_orig = sysconfig.customize_compiler
    if not cc and not ld: return
    def customize_compiler(compiler):
        customize_compiler_orig(compiler)
        if cc:
            compiler.compiler_so[0] = find_executable(cc)
        if ld:
            compiler.linker_so[0]= find_executable(ld)
    sysconfig.customize_compiler = customize_compiler

def _ffi_verify_pop():
    from distutils import sysconfig
    global customize_compiler_orig
    sysconfig.customize_compiler = customize_compiler_orig
    del customize_compiler_orig

def _read(filename):
    f = open(filename)
    try:
        return f.read()
    finally:
        f.close()

ffi, mpi = _ffi_create(
_read(_pth.join(_wdir, "libmpi.h")),
_read(_pth.join(_wdir, "libmpi.c")),
compiler='mpicc', linker='mpicc',
#ext_package='mpi4py',
#modulename='_cffi_mpi',
#tmpdir=_wdir,
#tmpdir='build'
)

import sys as _sys
_sys.modules[__name__+'.mpi'] = mpi
del _sys

#new = ffi.new
#cast = ffi.cast
#asbuffer = ffi.buffer
#globals().update(mpi.__dict__)

#del _sys, _cffi
#del _ffi_setup
#del _ffi_verify
#del _ffi_verify_enter
#del _ffi_verify_exit

if __name__ == '__main__':
    mpi.MPI_Init(ffi.NULL, ffi.NULL);
    mpi.MPI_Finalize()
