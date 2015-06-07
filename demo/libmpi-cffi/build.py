import os
import cffi

ffi = cffi.FFI()
with open("libmpi.c.in") as f:
    ffi.set_source("libmpi", f.read())
with open("libmpi.h") as f:
    ffi.cdef(f.read())

class mpicompiler(object):

    from cffi import ffiplatform

    def __init__(self, cc, ld=None):
        self.cc = cc
        self.ld = ld if ld else cc
        self.ffi_compile = self.ffiplatform.compile

    def __enter__(self):
        self.ffiplatform.compile = self.compile

    def __exit__(self, *args):
        self.ffiplatform.compile = self.ffi_compile

    def configure(self, compiler):
        from distutils.util import split_quoted
        from distutils.spawn import find_executable
        def fix_command(command, cmd):
            if not cmd: return
            cmd = split_quoted(cmd)
            exe = find_executable(cmd[0])
            if not exe: return
            command[0] = exe
            command += cmd[1:]
        fix_command(compiler.compiler_so, self.cc)
        fix_command(compiler.linker_so, self.ld)

    def compile(self, *args, **kargs):
        from distutils.command import build_ext
        customize_compiler_orig = build_ext.customize_compiler
        def customize_compiler(compiler):
            customize_compiler_orig(compiler)
            self.configure(compiler)
        build_ext.customize_compiler = customize_compiler
        try:
            return self.ffi_compile(*args, **kargs)
        finally:
            build_ext.customize_compiler = customize_compiler_orig

if __name__ == '__main__':
    cc = os.environ.get('MPICC', 'mpicc')
    ld = os.environ.get('MPILD')
    with mpicompiler(cc, ld):
        ffi.compile()
