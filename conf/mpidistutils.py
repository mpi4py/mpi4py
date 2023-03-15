# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""
Support for building mpi4py with distutils/setuptools.
"""
# ruff: noqa: E402

# -----------------------------------------------------------------------------

import os
import re
import sys
import glob
import shlex
import platform
import warnings
import contextlib

from distutils import log
from distutils import sysconfig
from distutils.util import convert_path
from distutils.file_util import copy_file

# Fix missing variables PyPy's  distutils.sysconfig
if hasattr(sys, 'pypy_version_info'):
    config_vars = sysconfig.get_config_vars()
    for name in ('prefix', 'exec_prefix'):
        if name not in config_vars:
            config_vars[name] = os.path.normpath(getattr(sys, name))
    if sys.platform == 'darwin' and 'LDSHARED' in config_vars:
        if '-undefined' not in config_vars['LDSHARED']:
            config_vars['LDSHARED'] += ' -undefined dynamic_lookup'

# Workaround distutils.cygwinccompiler.get_versions()
# failing when the compiler path contains spaces
from distutils import cygwinccompiler as cygcc
if hasattr(cygcc, 'get_versions'):
    cygcc_get_versions = cygcc.get_versions
    def get_versions():
        import distutils.spawn
        find_executable_orig  = distutils.spawn.find_executable
        def find_executable(exe):
            exe = find_executable_orig(exe)
            if exe and ' ' in exe:
                exe = f'"{exe}"'
            return exe
        distutils.spawn.find_executable = find_executable
        versions = cygcc_get_versions()
        distutils.spawn.find_executable = find_executable_orig
        return versions
    cygcc.get_versions = get_versions

# Workaround distutils.ccompiler.CCompiler._fix_lib_args
from distutils.ccompiler import CCompiler
cc_fix_compile_args_orig = getattr(CCompiler, '_fix_compile_args', None)
cc_fix_lib_args_orig = getattr(CCompiler, '_fix_lib_args', None)
def cc_fix_compile_args(self, out_dir, macros, inc_dirs):
    macros = macros or []
    inc_dirs = inc_dirs or []
    return cc_fix_compile_args_orig(self, out_dir, macros, inc_dirs)
def cc_fix_lib_args(self, libs, lib_dirs, rt_lib_dirs):
    libs = libs or []
    lib_dirs = lib_dirs or []
    rt_lib_dirs = rt_lib_dirs or []
    return cc_fix_lib_args_orig(self, libs, lib_dirs, rt_lib_dirs)
CCompiler._fix_compile_args = cc_fix_compile_args
CCompiler._fix_lib_args = cc_fix_lib_args

# Normalize linker flags for runtime library dirs
from distutils.unixccompiler import UnixCCompiler
rpath_option_orig = UnixCCompiler.runtime_library_dir_option
def rpath_option(compiler, dir):
    option = rpath_option_orig(compiler, dir)
    if sys.platform == 'linux':
        if option.startswith('-R'):
            option =  option.replace('-R', '-Wl,-rpath,', 1)
        elif option.startswith('-Wl,-R,'):
            option =  option.replace('-Wl,-R,', '-Wl,-rpath,', 1)
    return option
UnixCCompiler.runtime_library_dir_option = rpath_option

def _fix_env(cmd, i):
    while os.path.basename(cmd[i]) == 'env':
        i = i + 1
        while '=' in cmd[i]:
            i = i + 1
    return i

def _fix_xcrun(cmd, i):
    if os.path.basename(cmd[i]) == 'xcrun':
        del cmd[i]
        while True:
            if cmd[i] == '-sdk':
                del cmd[i:i+2]
                continue
            if cmd[i] == '-log':
                del cmd[i]
                continue
            break
    return i

def fix_compiler_cmd(cc, mpicc):
    if not mpicc:
        return
    i = 0
    i = _fix_env(cc, i)
    i = _fix_xcrun(cc, i)
    while os.path.basename(cc[i]) == 'ccache':
        i = i + 1
    cc[i:i+1] = shlex.split(mpicc)

def fix_linker_cmd(ld, mpild):
    if not mpild:
        return
    i = 0
    if (sys.platform.startswith('aix') and
        os.path.basename(ld[i]) == 'ld_so_aix'):
        i = 1
    i = _fix_env(ld, i)
    i = _fix_xcrun(ld, i)
    while os.path.basename(ld[i]) == 'ccache':
        del ld[i]
    ld[i:i+1] = shlex.split(mpild)

def customize_compiler(
    compiler, lang=None,
    mpicc=None,
    mpicxx=None,
    mpild=None,
):
    sysconfig.customize_compiler(compiler)
    if compiler.compiler_type == 'unix':
        ld = compiler.linker_exe
        for envvar in ('LDFLAGS', 'CFLAGS', 'CPPFLAGS'):
            if envvar in os.environ:
                ld += shlex.split(os.environ[envvar])
    if sys.platform == 'darwin':
        badcflags = ['-mno-fused-madd']
        for attr in (
            'preprocessor',
            'compiler', 'compiler_cxx', 'compiler_so',
            'linker_so', 'linker_exe',
        ):
            compiler_cmd = getattr(compiler, attr, None)
            if compiler_cmd is None:
                continue
            for flag in badcflags:
                while flag in compiler_cmd:
                    compiler_cmd.remove(flag)
    if compiler.compiler_type == 'unix':
        # Compiler command overriding
        if mpicc:
            fix_compiler_cmd(compiler.compiler, mpicc)
            if lang in ('c', None):
                fix_compiler_cmd(compiler.compiler_so, mpicc)
        if mpicxx:
            fix_compiler_cmd(compiler.compiler_cxx, mpicxx)
            if lang == 'c++':
                fix_compiler_cmd(compiler.compiler_so, mpicxx)
        if mpild:
            for ld in [compiler.linker_so, compiler.linker_exe]:
                fix_linker_cmd(ld, mpild)
    if compiler.compiler_type == 'cygwin':
        compiler.set_executables(
            preprocessor = 'gcc -mcygwin -E',
            )
    if compiler.compiler_type == 'mingw32':
        compiler.set_executables(
            preprocessor = 'gcc -mno-cygwin -E',
            )
    if compiler.compiler_type in ('unix', 'cygwin', 'mingw32'):
        badcxxflags = [ '-Wimplicit', '-Wstrict-prototypes']
        for flag in badcxxflags:
            while flag in compiler.compiler_cxx:
                compiler.compiler_cxx.remove(flag)
            if lang == 'c++':
                while flag in compiler.compiler_so:
                    compiler.compiler_so.remove(flag)
    if compiler.compiler_type == 'mingw32':
        # Remove msvcrXX.dll
        del compiler.dll_libraries[:]
        # https://bugs.python.org/issue12641
        if compiler.gcc_version >= '4.4':
            for attr in (
                'preprocessor',
                'compiler', 'compiler_cxx', 'compiler_so',
                'linker_so', 'linker_exe',
            ):
                with contextlib.suppress(Exception):
                    getattr(compiler, attr).remove('-mno-cygwin')
        # Add required define and compiler flags for AMD64
        if platform.architecture()[0] == '64bit':
            for attr in (
                'preprocessor',
                'compiler', 'compiler_cxx', 'compiler_so',
                'linker_so', 'linker_exe',
            ):
                getattr(compiler, attr).insert(1, '-DMS_WIN64')
                getattr(compiler, attr).insert(1, '-m64')

# -----------------------------------------------------------------------------

from mpiconfig import Config

def configuration(command_obj, verbose=True):
    config = Config(log)
    config.setup(command_obj)
    if verbose:
        if config.section and config.filename:
            config.log.info(
                "MPI configuration: [%s] from '%s'",
                config.section, ','.join(config.filename),
            )
            config.info()
    return config

def configure_compiler(compiler, config, lang=None):
    #
    mpicc  = config.get('mpicc')
    mpicxx = config.get('mpicxx')
    mpild  = config.get('mpild')
    if not mpild and (mpicc or mpicxx):
        if lang == 'c':
            mpild = mpicc
        if lang == 'c++':
            mpild = mpicxx
        if not mpild:
            mpild = mpicc or mpicxx
    #
    customize_compiler(
        compiler, lang,
        mpicc=mpicc,
        mpicxx=mpicxx,
        mpild=mpild,
    )
    #
    for k, v in config.get('define_macros', []):
        compiler.define_macro(k, v)
    for v in config.get('undef_macros', []):
        compiler.undefine_macro(v)
    for v in config.get('include_dirs', []):
        compiler.add_include_dir(v)
    for v in config.get('libraries', []):
        compiler.add_library(v)
    for v in config.get('library_dirs', []):
        compiler.add_library_dir(v)
    for v in config.get('runtime_library_dirs', []):
        compiler.add_runtime_library_dir(v)
    for v in config.get('extra_objects', []):
        compiler.add_link_object(v)
    if compiler.compiler_type in (
        'unix', 'intel', 'cygwin', 'mingw32',
    ):
        cc_args = config.get('extra_compile_args', [])
        ld_args = config.get('extra_link_args', [])
        compiler.compiler += cc_args
        compiler.compiler_so += cc_args
        compiler.compiler_cxx += cc_args
        compiler.linker_so += ld_args
        compiler.linker_exe += ld_args
    return compiler

# -----------------------------------------------------------------------------

try:
    from mpiapigen import Generator
except ImportError:
    class Generator:
        def parse_file(self, *args):
            raise NotImplementedError(
                "You forgot to grab 'mpiapigen.py'")


@contextlib.contextmanager
def capture_stderr(filename=os.devnull):
    stream = sys.stderr
    file_obj = None
    fno_save = None
    try:
        file_obj = open(filename, 'w')
        fno_save = os.dup(stream.fileno())
        os.dup2(file_obj.fileno(), stream.fileno())
        yield
    finally:
        if file_obj is not None:
            file_obj.close()
        if fno_save is not None:
            os.dup2(fno_save, stream.fileno())


class ConfigureMPI:

    SRCDIR = 'src'
    SOURCES = [os.path.join('mpi4py', 'libmpi.pxd')]
    DESTDIR = os.path.join('src', 'lib-mpi')
    CONFIG_H = os.path.join('config', 'config.h')
    MISSING_H = 'missing.h'

    CONFIGTEST_H = """\
/* _configtest.h */

#if !defined(MPIAPI)
#  define MPIAPI
#endif

"""

    def __init__(self, config_cmd):
        self.generator = Generator()
        for filename in self.SOURCES:
            fullname = os.path.join(self.SRCDIR, filename)
            self.generator.parse_file(fullname)
        self.config_cmd = config_cmd

    def run(self):
        results = []
        with open('_configtest.h', 'w') as f:
            f.write(self.CONFIGTEST_H)
        for node in self.generator:
            name = node.name
            testcode = node.config()
            confcode = node.missing(guard=False)
            log.info("checking for '%s'...", name)
            ok = self.run_test(testcode)
            if not ok:
                log.info("**** failed check for '%s'", name)
                with open('_configtest.h', 'a') as f:
                    f.write(confcode)
            results.append((name, ok))
        try:
            os.remove('_configtest.h')
        except OSError:
            pass
        return results

    def gen_test(self, code):
        body = [
            '#include "_configtest.h"',
            'int main(int argc, char **argv) {',
            '\n'.join(['  ' + line for line in code.split('\n')]),
            '  (void)argc; (void)argv;',
            '  return 0;',
            '}',
        ]
        body = '\n'.join(body) + '\n'
        return body

    def run_test(self, code, lang='c'):
        level = log.set_threshold(log.WARN)
        log.set_threshold(level)
        if not self.config_cmd.noisy:
            level = log.set_threshold(log.WARN)
        try:
            body = self.gen_test(code)
            headers = ['stdlib.h', 'mpi.h']
            ok = self.config_cmd.try_link(body, headers=headers, lang=lang)
            return ok
        finally:
            log.set_threshold(level)

    def dump(self, results):
        destdir = self.DESTDIR
        config_h  = os.path.join(destdir, self.CONFIG_H)
        missing_h = os.path.join(destdir, self.MISSING_H)
        log.info("writing '%s'", config_h)
        self.generator.dump_config_h(config_h, results)
        log.info("writing '%s'", missing_h)
        self.generator.dump_missing_h(missing_h, None)

# -----------------------------------------------------------------------------

cmd_mpi_opts = [

    ('mpild=',   None,
     "MPI linker command, "
     "overridden by environment variable 'MPILD' "
     "(defaults to 'mpicc' or 'mpicxx' if any is available)"),

    ('mpif77=',  None,
     "MPI F77 compiler command, "
     "overridden by environment variable 'MPIF77' "
     "(defaults to 'mpif77' if available)"),

    ('mpif90=',  None,
     "MPI F90 compiler command, "
     "overridden by environment variable 'MPIF90' "
     "(defaults to 'mpif90' if available)"),

    ('mpifort=',  None,
     "MPI Fortran compiler command, "
     "overridden by environment variable 'MPIFORT' "
     "(defaults to 'mpifort' if available)"),

    ('mpicxx=',  None,
     "MPI C++ compiler command, "
     "overridden by environment variable 'MPICXX' "
     "(defaults to 'mpicxx', 'mpiCC', or 'mpic++' if any is available)"),

    ('mpicc=',   None,
     "MPI C compiler command, "
     "overridden by environment variables 'MPICC' "
     "(defaults to 'mpicc' if available)"),

    ('mpi=',     None,
     "specify a ini-style configuration file and section "
     "(e.g. --mpi=filename or --mpi=filename:section), "
     "to look for MPI includes/libraries, "
     "overridden by environment variable 'MPICFG' "
     "(defaults to configuration file 'mpi.cfg' and section 'mpi')"),

    ('configure', None,
     "exhaustive test for checking missing MPI constants/types/functions"),

    ]

def cmd_get_mpi_options(cmd_opts):
    optlist = []
    for (option, _, _) in cmd_opts:
        if option[-1] == '=':
            option = option[:-1]
        option = option.replace('-','_')
        optlist.append(option)
    return optlist

def cmd_initialize_mpi_options(cmd):
    mpiopts = cmd_get_mpi_options(cmd_mpi_opts)
    for op in mpiopts:
        setattr(cmd, op, None)

def cmd_set_undefined_mpi_options(cmd, basecmd):
    mpiopts = cmd_get_mpi_options(cmd_mpi_opts)
    optlist = tuple(zip(mpiopts, mpiopts))
    cmd.set_undefined_options(basecmd, *optlist)

# -----------------------------------------------------------------------------

try:
    import setuptools
except ImportError:
    setuptools = None

def import_command(cmd):
    from importlib import import_module
    try:
        if not setuptools:
            raise ImportError
        return import_module('setuptools.command.' + cmd)
    except ImportError:
        return import_module('distutils.command.' + cmd)

if setuptools:
    from setuptools import Distribution as cls_Distribution
    from setuptools import Extension    as cls_Extension
    from setuptools import Command
else:
    from distutils.core import Distribution as cls_Distribution
    from distutils.core import Extension    as cls_Extension
    from distutils.core import Command

cmd_config  = import_command('config')
cmd_build   = import_command('build')
cmd_install = import_command('install')
cmd_clean   = import_command('clean')

cmd_build_ext    = import_command('build_ext')
cmd_install_lib  = import_command('install_lib')
cmd_install_data = import_command('install_data')

from distutils.errors import DistutilsError
from distutils.errors import DistutilsSetupError
from distutils.errors import DistutilsPlatformError
from distutils.errors import CCompilerError

try:
    from packaging.version import Version
except ImportError:
    try:
        from setuptools.extern.packaging.version import Version
    except ImportError:
        from distutils.version import StrictVersion as Version
try:
    from setuptools import dep_util
except ImportError:
    from distutils import dep_util

# -----------------------------------------------------------------------------

# Distribution class supporting a 'executables' keyword

class Distribution(cls_Distribution):

    def __init__ (self, attrs=None):
        # support for pkg data
        self.package_data = {}
        # PEP 314
        self.provides = None
        self.requires = None
        self.obsoletes = None
        # supports 'executables' keyword
        self.executables = None
        cls_Distribution.__init__(self, attrs)

    def has_executables(self):
        return self.executables and len(self.executables) > 0

    def is_pure (self):
        return (cls_Distribution.is_pure(self) and
                not self.has_executables())

# Extension class

class Extension(cls_Extension):
    def __init__ (self, **kw):
        optional = kw.pop('optional', None)
        configure = kw.pop('configure', None)
        cls_Extension.__init__(self, **kw)
        self.optional = optional
        self.configure = configure

# Library class

class Library(Extension):
    def __init__ (self, **kw):
        kind = kw.pop('kind', "static")
        package = kw.pop('package', None)
        dest_dir = kw.pop('dest_dir', None)
        Extension.__init__(self, **kw)
        self.kind = kind
        self.package = package
        self.dest_dir = dest_dir

# Executable class

class Executable(Extension):
    def __init__ (self, **kw):
        package = kw.pop('package', None)
        dest_dir = kw.pop('dest_dir', None)
        Extension.__init__(self, **kw)
        self.package = package
        self.dest_dir = dest_dir

# setup function

def setup(**attrs):
    if setuptools:
        from setuptools import setup as fcn_setup
    else:
        from distutils.core import setup as fcn_setup
    if 'distclass' not in attrs:
        attrs['distclass'] = Distribution
    if 'cmdclass' not in attrs:
        attrs['cmdclass'] = {}
    cmdclass = attrs['cmdclass']
    for cmd in (
        config, build, install, clean,
        build_src, build_ext, build_exe,
        install_lib, install_data, install_exe,
    ):
        if cmd.__name__ not in cmdclass:
            cmdclass[cmd.__name__] = cmd
    return fcn_setup(**attrs)

# --------------------------------------------------------------------

# Cython

def cython_req():
    confdir = os.path.dirname(__file__)
    basename = 'requirements-build-cython.txt'
    with open(os.path.join(confdir, basename)) as f:
        m = re.search(r'cython\s*>=+\s*(.*)', f.read().strip())
    cython_version = m.groups()[0]
    return cython_version


def cython_chk(VERSION, verbose=True):
    #
    def warn(message):
        if not verbose:
            return
        ruler, ws, nl = "*"*80, " " ,"\n"
        pyexe = sys.executable
        advise = f"$ {pyexe} -m pip install --upgrade cython"
        def printer(*s): print(*s, file=sys.stderr)
        printer(ruler, nl)
        printer(ws, message, nl)
        printer(ws, ws, advise, nl)
        printer(ruler)
    #
    try:
        import Cython
    except ImportError:
        warn("You need Cython to generate C source files.")
        return False
    #
    CYTHON_VERSION = Cython.__version__
    m = re.match(r"(\d+\.\d+(?:\.\d+)?).*", CYTHON_VERSION)
    if not m:
        warn("Cannot parse Cython version string {!r}"
             .format(CYTHON_VERSION))
        return False
    REQUIRED = Version(VERSION)
    PROVIDED = Version(m.groups()[0])
    if PROVIDED < REQUIRED:
        warn("You need Cython >= {} (you have version {})"
             .format(VERSION, CYTHON_VERSION))
        return False
    #
    if verbose:
        log.info("using Cython %s", CYTHON_VERSION)
    return True


def cython_run(
    source, target=None,
    depends=(), includes=(),
    workdir=None, force=False,
    VERSION="0.0",
):
    if target is None:
        target = os.path.splitext(source)[0]+'.c'
    cwd = os.getcwd()
    try:
        if workdir:
            os.chdir(workdir)
        alldeps = [source]
        for dep in depends:
            alldeps += glob.glob(dep)
        if not (force or dep_util.newer_group(alldeps, target)):
            log.debug("skipping '%s' -> '%s' (up-to-date)",
                      source, target)
            return
    finally:
        os.chdir(cwd)
    require = f'Cython >= {VERSION}'
    if not cython_chk(VERSION, verbose=False) and setuptools:
        if sys.modules.get('Cython'):
            removed = getattr(sys.modules['Cython'], '__version__', '')
            log.info("removing Cython %s from sys.modules", removed)
            pkgname = re.compile(r'cython(\.|$)', re.IGNORECASE)
            for modname in list(sys.modules.keys()):
                if pkgname.match(modname):
                    del sys.modules[modname]
        try:
            install_setup_requires = setuptools._install_setup_requires
            with warnings.catch_warnings():
                category = setuptools.SetuptoolsDeprecationWarning
                warnings.simplefilter('ignore', category)
                log.info("fetching build requirement '%s'", require)
                install_setup_requires({'setup_requires': [require]})
        except Exception:
            log.info("failed to fetch build requirement '%s'", require)
    if not cython_chk(VERSION):
        raise DistutilsError(f"missing build requirement {require!r}")
    #
    log.info("cythonizing '%s' -> '%s'", source, target)
    from cythonize import cythonize
    args = []
    if workdir:
        args += ['--working', workdir]
    args += [source]
    if target:
        args += ['--output-file', target]
    err = cythonize(args)
    if err:
        raise DistutilsError(f"Cython failure: {source!r} -> {target!r}")

# -----------------------------------------------------------------------------

# A minimalistic MPI program :-)

ConfigTest = """\
int main(int argc, char **argv)
{
  int ierr;
  (void)argc; (void)argv;
  ierr = MPI_Init(&argc, &argv);
  if (ierr) return -1;
  ierr = MPI_Finalize();
  if (ierr) return -1;
  return 0;
}
"""

class config(cmd_config.config):

    user_options = cmd_config.config.user_options + cmd_mpi_opts

    def initialize_options(self):
        cmd_config.config.initialize_options(self)
        cmd_initialize_mpi_options(self)
        self.noisy = 0

    def finalize_options(self):
        cmd_config.config.finalize_options(self)
        if not self.noisy:
            self.dump_source = 0

    def _clean(self, *a, **kw):
        if sys.platform.startswith('win'):
            for fn in ('_configtest.exe.manifest', ):
                if os.path.exists(fn):
                    self.temp_files.append(fn)
        cmd_config.config._clean(self, *a, **kw)

    def check_header(
        self, header, headers=None, include_dirs=None,
    ):
        if headers is None:
            headers = []
        log.info("checking for header '%s' ...", header)
        body = "int main(int n, char**v) { (void)n; (void)v; return 0; }"
        ok = self.try_compile(body, [*headers, header], include_dirs)
        log.info(ok and 'success!' or 'failure.')
        return ok

    def check_macro(
        self, macro, headers=None, include_dirs=None,
    ):
        log.info("checking for macro '%s' ...", macro)
        body = [
            f"#ifndef {macro}",
            f"#error macro '{macro}' not defined",
            r"#endif",
            r"int main(int n, char**v) { (void)n; (void)v; return 0; }"
        ]
        body = "\n".join(body) + "\n"
        ok = self.try_compile(body, headers, include_dirs)
        return ok

    def check_library(
        self, library, library_dirs=None,
        headers=None, include_dirs=None,
        other_libraries=(), lang="c",
    ):
        if sys.platform == "darwin":
            self.compiler.linker_exe.append('-flat_namespace')
            self.compiler.linker_exe.append('-undefined')
            self.compiler.linker_exe.append('suppress')
        log.info("checking for library '%s' ...", library)
        body = "int main(int n, char**v) { (void)n; (void)v; return 0; }"
        ok = self.try_link(
            body,  headers, include_dirs,
            [library, *other_libraries], library_dirs,
            lang=lang,
        )
        if sys.platform == "darwin":
            self.compiler.linker_exe.remove('-flat_namespace')
            self.compiler.linker_exe.remove('-undefined')
            self.compiler.linker_exe.remove('suppress')
        return ok

    def check_function(
        self, function,
        headers=None, include_dirs=None,
        libraries=None, library_dirs=None,
        decl=0, call=0, lang="c",
    ):
        log.info("checking for function '%s' ...", function)
        body = []
        if decl:
            if call:
                proto = f"int {function} (void);"
            else:
                proto = f"int {function};"
            if lang == "c":
                proto = "\n".join([
                    "#ifdef __cplusplus",
                    "extern {}".format('"C"'),
                    "#endif",
                    proto
                ])
            body.append(proto)
        body.append(    r"int main (int n, char**v) {")
        if call:
            body.append(f"  (void){function}();")
        else:
            body.append(f"  {function};")
        body.append(    r"  (void)n; (void)v;")
        body.append(    r"  return 0;")
        body.append(    r"}")
        body = "\n".join(body) + "\n"
        ok = self.try_link(
            body, headers, include_dirs,
            libraries, library_dirs,
            lang=lang,
        )
        return ok

    def check_symbol(
        self, symbol, type="int",
        headers=None, include_dirs=None,
        libraries=None, library_dirs=None,
        decl=0, lang="c",
    ):
        log.info("checking for symbol '%s' ...", symbol)
        body = []
        if decl:
            body.append(f"{type} {symbol};")
        body.append(r"int main (int n, char**v) {")
        body.append(f"  {type} s; s = {symbol}; (void)s;")
        body.append(r"  (void)n; (void)v;")
        body.append(r"  return 0;")
        body.append(r"}")
        body = "\n".join(body) + "\n"
        ok = self.try_link(
            body, headers, include_dirs,
            libraries, library_dirs,
            lang=lang,
        )
        return ok

    def check_function_call(
        self, function, args='',
        headers=None, include_dirs=None,
        libraries=None, library_dirs=None,
        lang="c",
    ):
        log.info("checking for function '%s' ...", function)
        body = []
        body.append(r"int main (int n, char**v) {")
        body.append(f"  (void){function}({args});")
        body.append(r"  (void)n; (void)v;")
        body.append(r"  return 0;")
        body.append(r"}")
        body = "\n".join(body) + "\n"
        ok = self.try_link(
            body, headers, include_dirs,
            libraries, library_dirs,
            lang=lang,
        )
        return ok

    def run(self):
        config = configuration(self, verbose=True)
        # test MPI C compiler
        self.compiler = getattr(self.compiler, 'compiler_type', self.compiler)
        self._check_compiler()
        configure_compiler(self.compiler, config, lang='c')
        self.try_link(ConfigTest, headers=['mpi.h'], lang='c')
        # test MPI C++ compiler
        self.compiler = getattr(self.compiler, 'compiler_type', self.compiler)
        self._check_compiler()
        configure_compiler(self.compiler, config, lang='c++')
        self.try_link(ConfigTest, headers=['mpi.h'], lang='c++')



def configure_dl(ext, config_cmd):
    log.info("checking for dlopen() availability ...")
    dlfcn = config_cmd.check_header('dlfcn.h')
    libdl = config_cmd.check_library('dl')
    libs = ['dl'] if libdl else None
    dlopen = config_cmd.check_function(
        'dlopen', libraries=libs, decl=1, call=1,
    )
    if dlfcn:
        ext.define_macros += [('HAVE_DLFCN_H', 1)]
    if dlopen:
        ext.define_macros += [('HAVE_DLOPEN', 1)]


def configure_mpi(ext, config_cmd):
    from textwrap import dedent
    headers = ['stdlib.h', 'mpi.h']
    #
    log.info("checking for MPI compile and link ...")
    ConfigTest = dedent("""\
    int main(int argc, char **argv)
    {
      (void)MPI_Init(&argc, &argv);
      (void)MPI_Finalize();
      return 0;
    }
    """)
    errmsg = "Cannot {} MPI programs. Check your configuration!!!"
    ok = config_cmd.try_compile(ConfigTest, headers=headers)
    if not ok:
        raise DistutilsPlatformError(errmsg.format("compile"))
    ok = config_cmd.try_link(ConfigTest, headers=headers)
    if not ok:
        raise DistutilsPlatformError(errmsg.format("link"))
    #
    log.info("checking for missing MPI functions/symbols ...")
    impls = ("OPEN_MPI", "MSMPI_VER")
    tests = [f"defined({macro})" for macro in impls]
    tests += ["(defined(MPICH_NAME)&&(MPICH_NAME>=3))"]
    tests += ["(defined(MPICH_NAME)&&(MPICH_NAME==2))"]
    tests = "||".join(tests)
    ConfigTest = dedent(f"""\
    #if !({tests})
    #error "Unknown MPI implementation"
    #endif
    """)
    config = os.environ.get('MPI4PY_BUILD_CONFIGURE') or None
    if not config:
        with capture_stderr():
            ok = config_cmd.try_compile(ConfigTest, headers=headers)
        config = not ok
    if config:
        guard = "HAVE_CONFIG_H"
        with capture_stderr():
            ok = config_cmd.check_macro(guard)
        config = not ok
        if config:
            configure = ConfigureMPI(config_cmd)
            with capture_stderr():
                results = configure.run()
            configure.dump(results)
            ext.define_macros += [(guard, 1)]
    else:
        for function, arglist in (
            ('MPI_Type_create_f90_integer',   '0,(MPI_Datatype*)0'),
            ('MPI_Type_create_f90_real',    '0,0,(MPI_Datatype*)0'),
            ('MPI_Type_create_f90_complex', '0,0,(MPI_Datatype*)0'),
            ('MPI_Status_c2f', '(MPI_Status*)0,(MPI_Fint*)0'),
            ('MPI_Status_f2c', '(MPI_Fint*)0,(MPI_Status*)0'),
        ):
            ok = config_cmd.check_function_call(
                function, arglist, headers=headers,
            )
            if not ok:
                macro = 'PyMPI_MISSING_' + function
                ext.define_macros += [(macro, 1)]
    #
    if os.name == 'posix':
        configure_dl(ext, config_cmd)


def configure_pyexe(exe, config_cmd):
    if sys.platform.startswith('win'):
        return
    if (sys.platform == 'darwin' and
        ('Anaconda' in sys.version or
         'Continuum Analytics' in sys.version)):
        py_version = sysconfig.get_python_version()
        py_abiflags = getattr(sys, 'abiflags', '')
        exe.libraries += ['python' + py_version + py_abiflags]
        return
    #
    pyver = sys.version_info[:2]
    cfg_vars = sysconfig.get_config_vars()
    libraries = []
    library_dirs = []
    runtime_dirs = []
    link_args = []
    py_enable_shared = cfg_vars.get('Py_ENABLE_SHARED')
    if pyver >= (3, 8) or not py_enable_shared:
        py_version = sysconfig.get_python_version()
        py_abiflags = getattr(sys, 'abiflags', '')
        libraries = ['python' + py_version + py_abiflags]
        if hasattr(sys, 'pypy_version_info'):
            py_tag = py_version[0].replace('2', '')
            libraries = [f'pypy{py_tag}-c']
    if sys.platform == 'darwin':
        fwkdir = cfg_vars.get('PYTHONFRAMEWORKDIR')
        if (fwkdir and fwkdir != 'no-framework' and
            fwkdir in cfg_vars.get('LINKFORSHARED', '')):
            del libraries[:]
    #
    libdir = shlex.split(cfg_vars.get('LIBDIR', ''))
    libpl = shlex.split(cfg_vars.get('LIBPL', ''))
    if py_enable_shared:
        library_dirs += libdir
        if sys.exec_prefix != '/usr':
            runtime_dirs += libdir
    else:
        library_dirs += libdir
        library_dirs += libpl
    for var in ('LIBS', 'MODLIBS', 'SYSLIBS', 'LDLAST'):
        link_args += shlex.split(cfg_vars.get(var, ''))
    #
    exe.libraries += libraries
    exe.library_dirs += library_dirs
    exe.runtime_library_dirs += runtime_dirs
    exe.extra_link_args += link_args


class build(cmd_build.build):

    user_options = cmd_build.build.user_options + cmd_mpi_opts

    def initialize_options(self):
        cmd_build.build.initialize_options(self)
        cmd_initialize_mpi_options(self)

    def finalize_options(self):
        cmd_build.build.finalize_options(self)
        config_cmd = self.get_finalized_command('config')
        if isinstance(config_cmd, config):
            cmd_set_undefined_mpi_options(self, 'config')

    def has_executables (self):
        return self.distribution.has_executables()

    sub_commands = [
        ('build_src', lambda *args: True),
         *cmd_build.build.sub_commands,
        ('build_exe', has_executables),
    ]

    # XXX disable build_exe subcommand !!!
    del sub_commands[-1]


class build_src(Command):

    description = "build C sources from Cython files"

    user_options = [
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
    ]

    boolean_options = ['force']

    def initialize_options(self):
        self.force = False

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('force', 'force'),
                                   )
    def run(self):
        sources = getattr(self, 'sources', [])
        require = cython_req()
        for source in sources:
            cython_run(
                **source,
                force=self.force,
                VERSION=require,
            )


# Command class to build extension modules

class build_ext(cmd_build_ext.build_ext):

    user_options = cmd_build_ext.build_ext.user_options + cmd_mpi_opts

    def initialize_options(self):
        cmd_build_ext.build_ext.initialize_options(self)
        cmd_initialize_mpi_options(self)

    def finalize_options(self):
        cmd_build_ext.build_ext.finalize_options(self)
        build_cmd = self.get_finalized_command('build')
        if isinstance(build_cmd,  build):
            cmd_set_undefined_mpi_options(self, 'build')

    def run(self):
        self.build_sources()
        cmd_build_ext.build_ext.run(self)

    def build_sources(self):
        if self.get_command_name() == 'build_ext':
            if 'build_src' in self.distribution.cmdclass:
                self.run_command('build_src')

    def build_extensions(self):
        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)
        # parse configuration file and configure compiler
        self.config = configuration(self, verbose=True)
        configure_compiler(self.compiler, self.config)
        # extra configuration, check for all MPI symbols
        if self.configure:
            log.info('testing for missing MPI symbols')
            config_cmd = self.get_finalized_command('config')
            config_cmd.compiler = self.compiler # fix compiler
            configure = ConfigureMPI(config_cmd)
            results = configure.run()
            configure.dump(results)
            #
            macro = 'HAVE_CONFIG_H'
            log.info("defining preprocessor macro '%s'", macro)
            self.compiler.define_macro(macro, 1)
        # build extensions
        for ext in self.extensions:
            try:
                self.build_extension(ext)
            except (DistutilsError, CCompilerError):
                if not ext.optional:
                    raise
                e = sys.exc_info()[1]
                self.warn(f'{e}')
                exe = isinstance(ext, Executable)
                knd = 'executable' if exe else 'extension'
                self.warn(f'building optional {knd} "{ext.name}" failed')

    def config_extension (self, ext):
        configure = getattr(ext, 'configure', None)
        if not configure:
            return
        config_cmd = self.get_finalized_command('config')
        config_cmd.compiler = self.compiler # fix compiler
        configure(ext, config_cmd)

    def build_extension (self, ext):
        fullname = self.get_ext_fullname(ext.name)
        filename = os.path.join(
            self.build_lib, self.get_ext_filename(fullname))
        depends = ext.sources + ext.depends
        if not (self.force or
                dep_util.newer_group(depends, filename, 'newer')):
            log.debug("skipping '%s' extension (up-to-date)", ext.name)
            return
        #
        self.config_extension(ext)
        cmd_build_ext.build_ext.build_extension(self, ext)
        #
        if ext.name == 'mpi4py.MPI':
            dest_dir = os.path.dirname(filename)
            self.mkpath(dest_dir)
            mpi_cfg = os.path.join(dest_dir, 'mpi.cfg')
            log.info("writing %s", mpi_cfg)
            if not self.dry_run:
                self.config.dump(filename=mpi_cfg)
        #
        if ext.name == 'mpi4py.MPI' and sys.platform == 'win32':
            config_cmd = self.get_finalized_command('config')
            with capture_stderr():
                headers = ['stdlib.h', 'mpi.h']
                intelmpi = config_cmd.check_macro('I_MPI_VERSION', headers)
            if intelmpi:
                confdir = os.path.dirname(__file__)
                pthfile = 'intelmpi.pth'
                source = os.path.join(confdir, pthfile)
                target = os.path.join(self.build_lib, pthfile)
                if os.path.exists(source):
                    log.info("writing %s", target)
                    copy_file(
                        source, target,
                        verbose=False,
                        dry_run=self.dry_run,
                    )

    def copy_extensions_to_source(self):
        build_py = self.get_finalized_command('build_py')
        cmd_build_ext.build_ext.copy_extensions_to_source(self)
        for ext in self.extensions:
            if ext.name == 'mpi4py.MPI':
                fullname = self.get_ext_fullname(ext.name)
                filename = self.get_ext_filename(fullname)
                dirname = os.path.dirname(filename)
                dest_dir = os.path.join(self.build_lib, dirname)
                regular_file = os.path.join(dest_dir, 'mpi.cfg')
                package = fullname.rpartition('.')[0]
                package_dir = build_py.get_package_dir(package)
                inplace_file = os.path.join(package_dir, 'mpi.cfg')
                self.copy_file(regular_file, inplace_file, level=self.verbose)

    def get_outputs(self):
        outputs = cmd_build_ext.build_ext.get_outputs(self)
        for ext in self.extensions:
            if ext.name == 'mpi4py.MPI':
                fullname = self.get_ext_fullname(ext.name)
                filename = self.get_ext_filename(fullname)
                dirname = os.path.dirname(filename)
                dest_dir = os.path.join(self.build_lib, dirname)
                output_file = os.path.join(dest_dir, 'mpi.cfg')
                outputs.append(output_file)
            if ext.name == 'mpi4py.MPI' and sys.platform == 'win32':
                pthfile = 'intelmpi.pth'
                output_file = os.path.join(self.build_lib, pthfile)
                if os.path.exists(output_file):
                    outputs.append(output_file)
        return outputs


# Command class to build executables

class build_exe(build_ext):

    description = "build binary executable components"

    user_options = [
        ('build-exe=', None,
         "build directory for executable components"),
        *build_ext.user_options,
    ]


    def initialize_options (self):
        build_ext.initialize_options(self)
        self.build_base = None
        self.build_exe  = None
        self.inplace = None

    def finalize_options (self):
        build_ext.finalize_options(self)
        self.configure = None
        self.set_undefined_options('build',
                                   ('build_base','build_base'),
                                   ('build_lib', 'build_exe'))
        self.set_undefined_options('build_ext',
                                   ('inplace', 'inplace'))
        self.executables = self.distribution.executables
        # XXX This is a hack
        self.extensions  = self.distribution.executables
        self.get_ext_filename = self.get_exe_filename
        self.check_extensions_list = self.check_executables_list
        self.build_extension = self.build_executable
        self.copy_extensions_to_source = self.copy_executables_to_source
        self.build_lib = self.build_exe

    def get_exe_filename(self, exe_name):
        exe_ext = sysconfig.get_config_var('EXE') or ''
        return exe_name + exe_ext

    def check_executables_list (self, executables):
        ListType, TupleType = type([]), type(())
        if type(executables) is not ListType:
            raise DistutilsSetupError(
                "'executables' option must be a list of Executable instances")
        for exe in executables:
            if not isinstance(exe, Executable):
                raise DistutilsSetupError(
                    "'executables' items must be Executable instances")
            if (exe.sources is None or
                type(exe.sources) not in (ListType, TupleType)):
                raise DistutilsSetupError(
                    f"in 'executables' option (executable '{exe.name}'), "
                    "'sources' must be present and must be "
                    "a list of source filenames"
                )

    def get_exe_fullpath(self, exe, build_dir=None):
        build_dir = build_dir or self.build_exe
        package_dir = (exe.package or '').split('.')
        dest_dir = convert_path(exe.dest_dir or '')
        output_dir = os.path.join(build_dir, *[*package_dir, dest_dir])
        exe_filename = self.get_exe_filename(exe.name)
        return os.path.join(output_dir, exe_filename)

    def config_executable (self, exe):
        build_ext.config_extension(self, exe)

    def build_executable (self, exe):
        sources = list(exe.sources)
        depends = list(exe.depends)
        exe_fullpath = self.get_exe_fullpath(exe)
        depends = sources + depends
        if not (self.force or
                dep_util.newer_group(depends, exe_fullpath, 'newer')):
            log.debug("skipping '%s' executable (up-to-date)", exe.name)
            return

        self.config_executable(exe)
        log.info("building '%s' executable", exe.name)

        # Next, compile the source code to object files.

        # XXX not honouring 'define_macros' or 'undef_macros' -- the
        # CCompiler API needs to change to accommodate this, and I
        # want to do one thing at a time!

        macros = exe.define_macros[:]
        for undef in exe.undef_macros:
            macros.append((undef,))

        # Two possible sources for extra compiler arguments:
        #   - 'extra_compile_args' in Extension object
        #   - CFLAGS environment variable (not particularly
        #     elegant, but people seem to expect it and I
        #     guess it's useful)
        # The environment variable should take precedence, and
        # any sensible compiler will give precedence to later
        # command line args.  Hence we combine them in order:
        extra_args = exe.extra_compile_args[:]

        objects =  self.compiler.compile(
            sources,
            output_dir=self.build_temp,
            macros=macros,
            include_dirs=exe.include_dirs,
            debug=self.debug,
            extra_postargs=extra_args,
            depends=exe.depends)
        self._built_objects = objects[:]

        # Now link the object files together into a "shared object" --
        # of course, first we have to figure out all the other things
        # that go into the mix.
        if exe.extra_objects:
            objects.extend(exe.extra_objects)
        extra_args = exe.extra_link_args[:]
        # Get special linker flags for building a executable with
        # bundled Python library, also fix location of needed
        # python.exp file on AIX
        ldflags = sysconfig.get_config_var('PY_LDFLAGS') or ''
        linkshared = sysconfig.get_config_var('LINKFORSHARED') or ''
        linkshared = linkshared.replace('-Xlinker ', '-Wl,')
        if sys.platform == 'darwin': # fix wrong framework paths
            fwkprefix = sysconfig.get_config_var('PYTHONFRAMEWORKPREFIX')
            fwkdir = sysconfig.get_config_var('PYTHONFRAMEWORKDIR')
            if fwkprefix and fwkdir and fwkdir != 'no-framework':
                for flag in shlex.split(linkshared):
                    if flag.startswith(fwkdir):
                        fwkpath = os.path.join(fwkprefix, flag)
                        linkshared = linkshared.replace(flag, fwkpath)
        if sys.platform.startswith('aix'):
            python_lib = sysconfig.get_python_lib(standard_lib=1)
            python_exp = os.path.join(python_lib, 'config', 'python.exp')
            linkshared = linkshared.replace('Modules/python.exp', python_exp)
        # Detect target language, if not provided
        language = exe.language or self.compiler.detect_language(sources)
        self.compiler.link(
            self.compiler.EXECUTABLE,
            objects, exe_fullpath,
            output_dir=None,
            libraries=self.get_libraries(exe),
            library_dirs=exe.library_dirs,
            runtime_library_dirs=exe.runtime_library_dirs,
            extra_preargs=shlex.split(ldflags) + shlex.split(linkshared),
            extra_postargs=extra_args,
            debug=self.debug,
            target_lang=language)

    def copy_executables_to_source(self):
        build_py = self.get_finalized_command('build_py')
        root_dir = build_py.get_package_dir('')
        for exe in self.executables:
            src = self.get_exe_fullpath(exe)
            dest = self.get_exe_fullpath(exe, root_dir)
            self.mkpath(os.path.dirname(dest))
            copy_file(
                src, dest,
                verbose=self.verbose,
                dry_run=self.dry_run
            )

    def get_outputs (self):
        outputs = []
        for exe in self.executables:
            outputs.append(self.get_exe_fullpath(exe))
        return outputs


class install(cmd_install.install):

    def initialize_options(self):
        with warnings.catch_warnings():
            if setuptools:
                category = setuptools.SetuptoolsDeprecationWarning
                warnings.simplefilter('ignore', category)
            cmd_install.install.initialize_options(self)
        self.old_and_unmanageable = True

    def run(self):
        cmd_install.install.run(self)

    def has_lib (self):
        return (cmd_install.install.has_lib(self) and
                self.has_exe())

    def has_exe (self):
        return self.distribution.has_executables()

    sub_commands = [
        *cmd_install.install.sub_commands,
        ('install_exe', has_exe),
    ]

    # XXX disable install_exe subcommand !!!
    del sub_commands[-1]


class install_lib(cmd_install_lib.install_lib):

    def get_outputs(self):
        outputs = cmd_install_lib.install_lib.get_outputs(self)
        for (build_cmd, build_dir) in (
            ('build_exe',  'build_exe'),
        ):
            cmd_obj = self.get_finalized_command(build_cmd)
            build_files = cmd_obj.get_outputs()
            exe_outputs = self._mutate_outputs(
                self.distribution.has_executables(),
                build_cmd, build_dir,
                self.install_dir,
            )
            for src, dest in zip(build_files, exe_outputs):
                if os.path.exists(src):
                    outputs.append(dest)
        return outputs


class install_data(cmd_install_data.install_data):

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                   )


class install_exe(cmd_install_lib.install_lib):

    description = "install binary executable components"

    user_options = [
        ('install-dir=', 'd', "directory to install to"),
        ('build-dir=','b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ('skip-build', None, "skip the build steps"),
        ]

    boolean_options = ['force', 'skip-build']
    negative_opt = { }

    def initialize_options (self):
        self.install_dir = None
        self.build_dir = None
        self.force = 0
        self.skip_build = None

    def finalize_options (self):
        self.set_undefined_options('build_exe',
                                   ('build_exe', 'build_dir'))
        self.set_undefined_options('install',
                                   ('force', 'force'),
                                   ('skip_build', 'skip_build'),
                                   ('install_scripts', 'install_dir'))

    def run(self):
        self.build()
        self.install()

    def build (self):
        if not self.skip_build:
            if self.distribution.has_executables():
                self.run_command('build_exe')

    def install (self):
        self.outfiles = []
        if self.distribution.has_executables():
            build_exe = self.get_finalized_command('build_exe')
            for exe in build_exe.executables:
                exe_fullpath = build_exe.get_exe_fullpath(exe)
                exe_filename = os.path.basename(exe_fullpath)
                if exe_filename.startswith("python-") and os.name == 'posix':
                    x, y = sys.version_info[:2]
                    install_name = exe_filename.replace(
                        "python-", f"python{x}.{y}-")
                    link = None
                else:
                    install_name = exe_filename
                    link = None
                source = exe_fullpath
                target = os.path.join(self.install_dir, install_name)
                self.mkpath(self.install_dir)
                out, done = self.copy_file(source, target, link=link)
                self.outfiles.append(out)

    def get_outputs (self):
        return self.outfiles

    def get_inputs (self):
        inputs = []
        if self.distribution.has_executables():
            build_exe = self.get_finalized_command('build_exe')
            inputs.extend(build_exe.get_outputs())
        return inputs


class clean(cmd_clean.clean):

    description = "clean up temporary files from 'build' command"
    user_options = \
        cmd_clean.clean.user_options[:2] + [
        ('build-exe=', None,
         "build directory for executable components "
         "(default: 'build_exe.build-exe')"),
        ] + cmd_clean.clean.user_options[2:]

    def initialize_options(self):
        cmd_clean.clean.initialize_options(self)
        self.build_exe  = None

    def finalize_options(self):
        cmd_clean.clean.finalize_options(self)
        self.set_undefined_options('build_exe',
                                   ('build_exe', 'build_exe'))

    def run(self):
        from distutils.dir_util import remove_tree

        # remove the build/temp.<plat> directory
        # (unless it's already gone)
        if os.path.exists(self.build_temp):
            remove_tree(self.build_temp, dry_run=self.dry_run)
        else:
            log.debug("'%s' does not exist -- can't clean it",
                      self.build_temp)

        if self.all:
            # remove build directories
            for directory in (
                self.build_lib,
                self.build_exe,
                self.build_scripts,
                self.bdist_base,
            ):
                if os.path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                else:
                    log.debug("'%s' does not exist -- can't clean it",
                              directory)

        # just for the heck of it, try to remove the base build directory:
        # we might have emptied it right now, but if not we don't care
        if not self.dry_run:
            try:
                os.rmdir(self.build_base)
                log.info("removing '%s'", self.build_base)
            except OSError:
                pass

        if self.all:
            # remove the <package>.egg_info directory
            try:
                egg_info = self.get_finalized_command('egg_info').egg_info
                if os.path.exists(egg_info):
                    remove_tree(egg_info, dry_run=self.dry_run)
                else:
                    log.debug("'%s' does not exist -- can't clean it",
                              egg_info)
            except DistutilsError:
                pass

# -----------------------------------------------------------------------------

if setuptools:
    with contextlib.suppress(Exception):
        from setuptools.command import egg_info as mod_egg_info
        _FileList = mod_egg_info.FileList
        class FileList(_FileList):
            def process_template_line(self, line):
                level = log.set_threshold(log.ERROR)
                try:
                    _FileList.process_template_line(self, line)
                finally:
                    log.set_threshold(level)
        mod_egg_info.FileList = FileList

# -----------------------------------------------------------------------------
