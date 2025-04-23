import os
import pathlib
import shlex
import shutil

import cffi


def _read_text(filename):
    return pathlib.Path(filename).read_text(encoding="utf-8")


ffi = cffi.FFI()
ffi.set_source("libmpi", _read_text("libmpi.c.in"))
ffi.cdef(_read_text("libmpi.h"))


class mpicompiler:
    from cffi import ffiplatform

    def __init__(self, cc, ld=None):
        self.cc = cc
        self.ld = ld or cc
        self.ffi_compile = self.ffiplatform.compile

    def __enter__(self):
        self.ffiplatform.compile = self.compile

    def __exit__(self, *args):
        self.ffiplatform.compile = self.ffi_compile

    def configure(self, compiler):
        def fix_command(command, cmd):
            if not cmd:
                return
            cmd = shlex.split(cmd)
            exe = shutil.which(cmd[0])
            if not exe:
                return
            command[0] = exe
            command += cmd[1:]

        fix_command(compiler.compiler_so, self.cc)
        fix_command(compiler.linker_so, self.ld)

    def compile(self, *args, **kwargs):
        from distutils.command import build_ext

        customize_compiler_orig = build_ext.customize_compiler

        def customize_compiler(compiler):
            customize_compiler_orig(compiler)
            self.configure(compiler)

        build_ext.customize_compiler = customize_compiler
        try:
            return self.ffi_compile(*args, **kwargs)
        finally:
            build_ext.customize_compiler = customize_compiler_orig


if __name__ == "__main__":
    cc = os.environ.get("MPICC", "mpicc")
    ld = os.environ.get("MPILD")
    with mpicompiler(cc, ld):
        ffi.compile()
