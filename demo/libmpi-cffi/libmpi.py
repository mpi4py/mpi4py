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
    _compiler_push(cc, ld)
    try:
        lib =  ffi.verify(csource, **kargs)
    finally:
        _compiler_pop()
    return lib

def _compiler_push(cc, ld):
    from distutils import sysconfig
    from distutils.spawn import find_executable
    if not cc and not ld: return
    if cc: cc = find_executable(cc)
    if ld: ld = find_executable(ld)
    def customize_compiler(compiler):
        _compiler_push.customize_compiler(compiler)
        if cc: compiler.compiler_so[0] = cc
        if ld: compiler.linker_so[0]   = ld
        if _sys.platform == 'darwin':
            while '-mno-fused-madd' in compiler.compiler_so:
                compiler.compiler_so.remove('-mno-fused-madd')
            while '-mno-fused-madd' in compiler.linker_so:
                compiler.linker_so.remove('-mno-fused-madd')
    sysconfig.get_config_vars()
    _compiler_push.customize_compiler = sysconfig.customize_compiler
    sysconfig.customize_compiler = customize_compiler

def _compiler_pop():
    from distutils import sysconfig
    sysconfig.customize_compiler = _compiler_push.customize_compiler

def _read(filename):
    srcdir = _os.path.abspath(_os.path.dirname(__file__))
    f = open(_os.path.join(srcdir, filename))
    try:
        return f.read()
    finally:
        f.close()


_mpicc = _os.getenv('MPICC', "mpicc")
_mpild = _os.getenv('MPILD', _mpicc)

ffi, mpi = _ffi_create(
_read("libmpi.h"),
_read("libmpi.c"),
compiler=_mpicc,
linker=_mpild,
)


_sys.modules[__name__+'.mpi'] = mpi

#new = ffi.new
#cast = ffi.cast
#asbuffer = ffi.buffer
#globals().update(mpi.__dict__)

if __name__ == '__main__':
    mpi.MPI_Init(ffi.NULL, ffi.NULL);
    mpi.MPI_Finalize()
