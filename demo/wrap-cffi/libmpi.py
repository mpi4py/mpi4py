import os   as _os
import sys  as _sys
import cffi as _cffi

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
    global _customize_compiler_orig
    _customize_compiler_orig = sysconfig.customize_compiler
    if not cc and not ld: return
    if cc: cc = find_executable(cc)
    if ld: ld = find_executable(ld)
    def customize_compiler(compiler):
        _customize_compiler_orig(compiler)
        if cc: compiler.compiler_so[0] = cc
        if ld: compiler.linker_so[0]   = ld
    sysconfig.customize_compiler = customize_compiler

def _ffi_verify_pop():
    from distutils import sysconfig
    global _customize_compiler_orig
    sysconfig.customize_compiler = _customize_compiler_orig
    del _customize_compiler_orig

def _read(filename):
    f = open(filename)
    try:
        return f.read()
    finally:
        f.close()

_wdir  = _os.path.abspath(_os.path.dirname(__file__))
_mpicc = _os.getenv('MPICC', "mpicc")
_mpild = _os.getenv('MPILD', _mpicc)

ffi, mpi = _ffi_create(
_read(_os.path.join(_wdir, "libmpi.h")),
_read(_os.path.join(_wdir, "libmpi.c")),
compiler=_mpicc, linker=_mpild,
#modulename='_cffi_mpi',
)

_sys.modules[__name__+'.mpi'] = mpi

#new = ffi.new
#cast = ffi.cast
#asbuffer = ffi.buffer
#globals().update(mpi.__dict__)

if __name__ == '__main__':
    mpi.MPI_Init(ffi.NULL, ffi.NULL);
    mpi.MPI_Finalize()
