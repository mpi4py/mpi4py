# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

"""
Support for building mpi4py with distutils.
"""

# -----------------------------------------------------------------------------

import sys
if sys.version[:3] == '3.0':
    from distutils import version
    version.cmp = lambda a, b : (a > b) - (a < b)
    del version
del sys

# -----------------------------------------------------------------------------

import sys, os, platform, re
from distutils import sysconfig
from distutils.util  import convert_path
from distutils.util  import split_quoted
from distutils.spawn import find_executable
from distutils import log

def fix_config_vars(names, values):
    values = list(values)
    if sys.platform == 'darwin':
        if 'ARCHFLAGS' in os.environ:
            ARCHFLAGS = os.environ['ARCHFLAGS']
            for i, flag in enumerate(list(values)):
                flag, count = re.subn('-arch\s+\w+', ' ', flag)
                if count and ARCHFLAGS:
                    flag = flag + ' ' + ARCHFLAGS
                values[i] = flag
        if 'SDKROOT' in os.environ:
            SDKROOT = os.environ['SDKROOT']
            for i, flag in enumerate(list(values)):
                flag, count = re.subn('-isysroot [^ \t]*', ' ', flag)
                if count and SDKROOT:
                    flag = flag + ' ' + '-isysroot ' + SDKROOT
                values[i] = flag
    return values

def get_config_vars(*names):
    # Core Python configuration
    values = sysconfig.get_config_vars(*names)
    # Do any distutils flags fixup right now
    values = fix_config_vars(names, values)
    return values

def fix_compiler_cmd(cc, mpicc):
    if not mpicc: return cc
    if not cc:    return mpicc
    from os.path import basename
    cc = split_quoted(cc)
    i = 0
    while basename(cc[i]) == 'env':
        i = 1
        while '=' in cc[i]:
            i = i + 1
    cc[i] = mpicc
    return ' '.join(cc)

def fix_linker_cmd(ld, mpild):
    if not mpild: return ld
    if not ld:    return mpild
    from os.path import basename
    ld = split_quoted(ld)
    i = 0
    if (sys.platform.startswith('aix') and
        basename(ld[i]) == 'ld_so_aix'):
        i = i + 1
    while basename(ld[i]) == 'env':
        i = i + 1
        while '=' in ld[i]:
            i = i + 1
    ld[i] = mpild
    return ' '.join(ld)

def split_linker_cmd(ld):
    from os.path import basename
    ld = split_quoted(ld)
    i = 0
    if (sys.platform.startswith('aix') and
        basename(pyld[i]) == 'ld_so_aix'):
        i = i + 1
    while basename(ld[i]) == 'env':
        i = i + 1
        while '=' in ld[i]:
            i = i + 1
    p = i + 1
    ld, flags = ' '.join(ld[:p]), ' '.join(ld[p:])
    return ld, flags

from distutils.unixccompiler import UnixCCompiler
rpath_option_orig = UnixCCompiler.runtime_library_dir_option
def rpath_option(compiler, dir):
    option = rpath_option_orig(compiler, dir)
    if sys.platform.startswith('linux'):
        if option.startswith('-R'):
            option =  option.replace('-R', '-Wl,-rpath,', 1)
        elif option.startswith('-Wl,-R,'):
            option =  option.replace('-Wl,-R,', '-Wl,-rpath,', 1)
    return option
UnixCCompiler.runtime_library_dir_option = rpath_option

def customize_compiler(compiler, lang=None,
                       mpicc=None, mpicxx=None, mpild=None,
                       environ=None):
    if environ is None:
        environ = os.environ
    if compiler.compiler_type == 'unix':
        # Distutils configuration, actually obtained by parsing
        # :file:{prefix}/lib[32|64]/python{X}.{Y}/config/Makefile
        (cc, cxx, ccshared, ld,
         basecflags, opt) = get_config_vars (
            'CC', 'CXX', 'CCSHARED', 'LDSHARED',
            'BASECFLAGS', 'OPT')
        cc  = cc  .replace('-pthread', '')
        cxx = cxx .replace('-pthread', '')
        ld  = ld  .replace('-pthread', '')
        ld, ldshared = split_linker_cmd(ld)
        basecflags, opt = basecflags or '', opt or ''
        ccshared = ccshared or ''
        ldshared = ldshared or ''
        # Compiler command overriding
        if not mpild and (mpicc or mpicxx):
            if lang == 'c':
                mpild = mpicc
            elif lang == 'c++':
                mpild = mpicxx
            else:
                mpild = mpicc or mpicxx
        if mpicc:
            cc = fix_compiler_cmd(cc, mpicc)
        if mpicxx:
            cxx = fix_compiler_cmd(cxx, mpicxx)
        if mpild:
            ld = fix_linker_cmd(ld, mpild)
        # Environment handling
        cppflags = cflags = cxxflags = ldflags = ''
        CPPFLAGS = environ.get('CPPFLAGS', '')
        CFLAGS   = environ.get('CFLAGS',   '')
        CXXFLAGS = environ.get('CXXFLAGS', '')
        LDFLAGS  = environ.get('LDFLAGS',  '')
        if CPPFLAGS:
            cppflags = cppflags + ' ' + CPPFLAGS
            cflags   = cflags   + ' ' + CPPFLAGS
            cxxflags = cxxflags + ' ' + CPPFLAGS
            ldflags  = ldflags  + ' ' + CPPFLAGS
        if CFLAGS:
            cflags   = cflags   + ' ' + CFLAGS
            ldflags  = ldflags  + ' ' + CFLAGS
        if CXXFLAGS:
            cxxflags = cxxflags + ' ' + CXXFLAGS
            ldflags  = ldflags  + ' ' + CXXFLAGS
        if LDFLAGS:
            ldflags  = ldflags  + ' ' + LDFLAGS
        basecflags = environ.get('BASECFLAGS', basecflags)
        opt        = environ.get('OPT',        opt       )
        ccshared   = environ.get('CCSHARED', ccshared)
        ldshared   = environ.get('LDSHARED', ldshared)
        cflags     = ' '.join((basecflags, opt, cflags))
        cxxflags   = ' '.join((basecflags, opt, cxxflags))
        cxxflags = cxxflags.replace('-Wstrict-prototypes', '')
        # Distutils compiler setup
        cpp    = os.environ.get('CPP') or (cc + ' -E')
        cc_so  = cc  + ' ' + ccshared
        cxx_so = cxx + ' ' + ccshared
        ld_so  = ld  + ' ' + ldshared
        compiler.set_executables(
            preprocessor = cpp    + ' ' + cppflags,
            compiler     = cc     + ' ' + cflags,
            compiler_so  = cc_so  + ' ' + cflags,
            compiler_cxx = cxx_so + ' ' + cxxflags,
            linker_so    = ld_so  + ' ' + ldflags,
            linker_exe   = ld     + ' ' + ldflags,
            )
        try: compiler.compiler_cxx.remove('-Wstrict-prototypes')
        except: pass
    if compiler.compiler_type == 'mingw32':
        compiler.set_executables(
            preprocessor = 'gcc -mno-cygwin -E',
            )
    if compiler.compiler_type in ('unix', 'cygwin', 'mingw32'):
        if lang == 'c++':
            def find_cmd_pos(cmd):
                pos = 0
                if os.path.basename(cmd[pos]) == "env":
                    pos = 1
                    while '=' in cmd[pos]:
                        pos = pos + 1
                return pos
            i = find_cmd_pos(compiler.compiler_so)
            j = find_cmd_pos(compiler.compiler_cxx)
            compiler.compiler_so[i] = compiler.compiler_cxx[j]
            try: compiler.compiler_so.remove('-Wstrict-prototypes')
            except: pass
    if compiler.compiler_type == 'msvc':
        if not compiler.initialized:
            compiler.initialize()
        compiler.ldflags_shared.append('/MANIFEST')
        compiler.ldflags_shared_debug.append('/MANIFEST')

# -----------------------------------------------------------------------------

try:
    from mpiconfig import Config
except ImportError:
    from conf.mpiconfig import Config

def configuration(command_obj, verbose=True):
    config = Config()
    config.setup(command_obj)
    if verbose:
        if config.section and config.filename:
            log.info("MPI configuration: [%s] from '%s'",
                     config.section, ','.join(config.filename))
            config.info(log)
    return config

def configure_compiler(compiler, config, lang=None):
    #
    mpicc  = config.get('mpicc')
    mpicxx = config.get('mpicxx')
    mpild  = config.get('mpild')
    customize_compiler(compiler, lang,
                       mpicc=mpicc, mpicxx=mpicxx, mpild=mpild)
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
    if compiler.compiler_type in \
        ('unix', 'intel', 'cygwin', 'mingw32'):
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
    from mpiscanner import Scanner
except ImportError:
    try:
        from conf.mpiscanner import Scanner
    except ImportError:
        class Scanner(object):
            def parse_file(self, *args):
                raise NotImplementedError(
                    "You forgot to grab 'mpiscanner.py'")

class ConfigureMPI(object):

    SRCDIR = 'src'
    SOURCES = [os.path.join('include', 'mpi4py', 'mpi.pxi')]
    DESTDIR = 'src'
    CONFIG_H = 'config.h'
    MISSING_H = 'missing.h'

    def __init__(self, config_cmd):
        self.scanner = Scanner()
        for filename in self.SOURCES:
            fullname = os.path.join(self.SRCDIR, filename)
            self.scanner.parse_file(fullname)
        self.config_cmd = config_cmd

    def run(self):
        results = []
        for name, code in self.scanner.itertests():
            log.info("checking for '%s' ..." % name)
            body = self.gen_one(results, code)
            ok   = self.run_one(body)
            if not ok:
                log.info("**** failed check for '%s'" % name)
            results.append((name, ok))
        return results

    def dump(self, results):
        destdir = self.DESTDIR
        config_h  = os.path.join(destdir, self.CONFIG_H)
        missing_h = os.path.join(destdir, self.MISSING_H)
        log.info("writing '%s'", config_h)
        self.scanner.dump_config_h(config_h, results)
        log.info("writing '%s'", missing_h)
        self.scanner.dump_missing_h(missing_h, None)

    def gen_one(self, results, code):
        #
        configtest_h = "_configtest.h"
        self.config_cmd.temp_files.insert(0, configtest_h)
        fh = open(configtest_h, "w")
        try:
            sep = "/* " + ('-'*72)+ " */\n"
            fh.write(sep)
            self.scanner.dump_config_h(fh, results)
            fh.write(sep)
            self.scanner.dump_missing_h(fh, results)
            fh.write(sep)
        finally:
            fh.close()
        #
        body = ['#include "%s"' % configtest_h,
                'int main(int argc, char **argv) {',
                '  %s' % code,
                '  return 0;',
                '}']
        body = '\n'.join(body) + '\n'
        return body

    def run_one(self, body, lang='c'):
        ok = self.config_cmd.try_link(body, headers=['mpi.h'], lang=lang)
        return ok

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

    ('mpif95=',  None,
     "MPI F95 compiler command, "
     "overridden by environment variable 'MPIF95' "
     "(defaults to 'mpif95' if available)"),

    ('mpicxx=',  None,
     "MPI C++ compiler command, "
     "overridden by environment variable 'MPICXX' "
     "(defaults to 'mpicxx', 'mpiCC', or 'mpic++' if any is available)"),

    ('mpicc=',   None,
     "MPI C compiler command, "
     "overridden by environment variables 'MPICC' "
     "(defaults to 'mpicc' if available)"),

    ('mpi=',     None,
     "specify a configuration section, "
     "and an optional list of configuration files "
     + "(e.g. --mpi=section,file1" + os.path.pathsep + "file2), " +
     "to look for MPI includes/libraries, "
     "overridden by environment variable 'MPICFG' "
     "(defaults to section 'mpi' in configuration file 'mpi.cfg')"),

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

from distutils.core import setup        as fcn_setup
from distutils.core import Distribution as cls_Distribution
from distutils.core import Extension    as cls_Extension
from distutils.core import Command

from distutils.command import config  as cmd_config
from distutils.command import build   as cmd_build
from distutils.command import install as cmd_install
from distutils.command import sdist   as cmd_sdist
from distutils.command import clean   as cmd_clean

from distutils.command import build_py     as cmd_build_py
from distutils.command import build_clib   as cmd_build_clib
from distutils.command import build_ext    as cmd_build_ext
from distutils.command import install_data as cmd_install_data
from distutils.command import install_lib  as cmd_install_lib

from distutils.errors import DistutilsError
from distutils.errors import DistutilsSetupError
from distutils.errors import DistutilsPlatformError
from distutils.errors import DistutilsOptionError
from distutils.errors import CCompilerError

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
    if 'distclass' not in attrs:
        attrs['distclass'] = Distribution
    if 'cmdclass' not in attrs:
        attrs['cmdclass'] = {}
    cmdclass = attrs['cmdclass']
    for cmd in (config, build, install,
                test, clean, sdist,
                build_src, build_py,
                build_clib, build_ext, build_exe,
                install_lib, install_data, install_exe,
                ):
        if cmd.__name__ not in cmdclass:
            cmdclass[cmd.__name__] = cmd
    return fcn_setup(**attrs)

# -----------------------------------------------------------------------------

# A minimalistic MPI program :-)

ConfigTest = """\
int main(int argc, char **argv)
{
  int ierr;
  ierr = MPI_Init(&argc, &argv);
  if (ierr) return -1;
  ierr = MPI_Finalize();
  if (ierr) return -1;
  return 0;
}
"""

class config(cmd_config.config):

    user_options = cmd_config.config.user_options + cmd_mpi_opts

    def initialize_options (self):
        cmd_config.config.initialize_options(self)
        cmd_initialize_mpi_options(self)
        self.noisy = 0

    def finalize_options (self):
        cmd_config.config.finalize_options(self)
        if not self.noisy:
            self.dump_source = 0

    def _clean(self, *a, **kw):
        if sys.platform.startswith('win'):
            for fn in ('_configtest.exe.manifest', ):
                if os.path.exists(fn):
                    self.temp_files.append(fn)
        cmd_config.config._clean(self, *a, **kw)

    def check_header (self, header, headers=None, include_dirs=None):
        if headers is None: headers = []
        log.info("checking for header '%s' ..." % header)
        body = "int main(int n, char**v) { return 0; }"
        ok = self.try_compile(body, list(headers) + [header], include_dirs)
        log.info(ok and 'success!' or 'failure.')
        return ok

    def check_macro (self, macro, headers=None, include_dirs=None):
        log.info("checking for macro '%s' ..." % macro)
        body = ("#ifndef %s\n"
                "#error macro '%s' not defined\n"
                "#endif\n") % (macro, macro)
        body += "int main(int n, char**v) { return 0; }\n"
        ok = self.try_compile(body, headers, include_dirs)
        return ok

    def check_library (self, library, library_dirs=None,
                   headers=None, include_dirs=None,
                   other_libraries=[], lang="c"):
        log.info("checking for library '%s' ..." % library)
        body = "int main(int n, char**v) { return 0; }"
        ok = self.try_link(body,  headers, include_dirs,
                           [library]+other_libraries, library_dirs,
                           lang=lang)
        return ok

    def check_function (self, function,
                        headers=None, include_dirs=None,
                        libraries=None, library_dirs=None,
                        decl=0, call=0, lang="c"):
        log.info("checking for function '%s' ..." % function)
        body = []
        if decl:
            if call: proto = "int %s (void);"
            else:    proto = "int %s;"
            if lang == "c":
                proto = "\n".join([
                        "#ifdef __cplusplus",
                        "extern \"C\"",
                        "#endif", proto])
            body.append(proto % function)
        body.append(    "int main (int n, char**v) {")
        if call:
            body.append("  (void)%s();" % function)
        else:
            body.append("  %s;" % function)
        body.append(    "  return 0;")
        body.append(    "}")
        body = "\n".join(body) + "\n"
        ok = self.try_link(body, headers, include_dirs,
                           libraries, library_dirs, lang=lang)
        return ok

    def check_symbol (self, symbol, type="int",
                      headers=None, include_dirs=None,
                      libraries=None, library_dirs=None,
                      decl=0, lang="c"):
        log.info("checking for symbol '%s' ..." % symbol)
        body = []
        if decl:
            body.append("%s %s;" % (type, symbol))
        body.append("int main (int n, char**v) {")
        body.append("  %s v; v = %s;" % (type, symbol))
        body.append("  return 0;")
        body.append("}")
        body = "\n".join(body) + "\n"
        ok = self.try_link(body, headers, include_dirs,
                           libraries, library_dirs, lang=lang)
        return ok

    check_hdr  = check_header
    check_lib  = check_library
    check_func = check_function
    check_sym  = check_symbol

    def run (self):
        #
        config = configuration(self, verbose=True)
        # test MPI C compiler
        self.compiler = getattr(
            self.compiler, 'compiler_type', self.compiler)
        self._check_compiler()
        configure_compiler(self.compiler, config, lang='c')
        self.try_link(ConfigTest, headers=['mpi.h'], lang='c')
        # test MPI C++ compiler
        self.compiler = getattr(
            self.compiler, 'compiler_type', self.compiler)
        self._check_compiler()
        configure_compiler(self.compiler, config, lang='c++')
        self.try_link(ConfigTest, headers=['mpi.h'], lang='c++')


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

    sub_commands = \
        [('build_src', lambda *args: True)] + \
        cmd_build.build.sub_commands + \
        [('build_exe', has_executables),
         ]


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
        pass


class build_py(cmd_build_py.build_py):

  if sys.version[:3] < '2.4':

    def initialize_options(self):
        self.package_data = None
        cmd_build_py.build_py.initialize_options(self)

    def finalize_options (self):
        cmd_build_py.build_py.finalize_options(self)
        self.package_data = self.distribution.package_data
        self.data_files = self.get_data_files()

    def run(self):
        cmd_build_py.build_py.run(self)
        if self.packages:
            self.build_package_data()

    def get_data_files (self):
        """Generate list of '(package,src_dir,build_dir,filenames)' tuples"""
        data = []
        if not self.packages:
            return data
        for package in self.packages:
            # Locate package source directory
            src_dir = self.get_package_dir(package)

            # Compute package build directory
            build_dir = os.path.join(*([self.build_lib] + package.split('.')))

            # Length of path to strip from found files
            plen = len(src_dir)+1

            # Strip directory from globbed filenames
            filenames = [
                file[plen:] for file in self.find_data_files(package, src_dir)
                ]
            data.append((package, src_dir, build_dir, filenames))
        return data

    def find_data_files (self, package, src_dir):
        """Return filenames for package's data files in 'src_dir'"""
        from glob import glob
        globs = (self.package_data.get('', [])
                 + self.package_data.get(package, []))
        files = []
        for pattern in globs:
            # Each pattern has to be converted to a platform-specific path
            filelist = glob(os.path.join(src_dir, convert_path(pattern)))
            # Files that match more than one pattern are only added once
            files.extend([fn for fn in filelist if fn not in files])
        return files

    def get_package_dir (self, package):
        """Return the directory, relative to the top of the source
           distribution, where package 'package' should be found
           (at least according to the 'package_dir' option, if any)."""
        import string
        path = string.split(package, '.')

        if not self.package_dir:
            if path:
                return os.path.join(*path)
            else:
                return ''
        else:
            tail = []
            while path:
                try:
                    pdir = self.package_dir[string.join(path, '.')]
                except KeyError:
                    tail.insert(0, path[-1])
                    del path[-1]
                else:
                    tail.insert(0, pdir)
                    return os.path.join(*tail)
            else:
                pdir = self.package_dir.get('')
                if pdir is not None:
                    tail.insert(0, pdir)

                if tail:
                    return os.path.join(*tail)
                else:
                    return ''

    def build_package_data (self):
        """Copy data files into build directory"""
        lastdir = None
        for package, src_dir, build_dir, filenames in self.data_files:
            for filename in filenames:
                target = os.path.join(build_dir, filename)
                self.mkpath(os.path.dirname(target))
                self.copy_file(os.path.join(src_dir, filename), target,
                               preserve_mode=False)


# Command class to build libraries

class build_clib(cmd_build_clib.build_clib):

    user_options = [
        ('build-clib-a=', 's',
         "directory to build C/C++ static libraries to"),
        ('build-clib-so=', 's',
         "directory to build C/C++ shared libraries to"),
        ]

    user_options += cmd_build_clib.build_clib.user_options + cmd_mpi_opts

    def initialize_options (self):
        self.libraries = None
        self.libraries_a = []
        self.libraries_so = []

        self.library_dirs = None
        self.rpath = None
        self.link_objects = None

        self.build_lib = None
        self.build_clib_a = None
        self.build_clib_so = None
        cmd_build_clib.build_clib.initialize_options(self)
        cmd_initialize_mpi_options(self)

    def finalize_options (self):
        cmd_build_clib.build_clib.finalize_options(self)
        build_cmd = self.get_finalized_command('build')
        if isinstance(build_cmd,  build):
            cmd_set_undefined_mpi_options(self, 'build')
        #
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'),
                                   ('build_lib', 'build_clib_a'),
                                   ('build_lib', 'build_clib_so'))
        #
        if self.libraries:
            libraries = self.libraries[:]
            self.libraries = []
            self.check_library_list (libraries)
            for i, lib in enumerate(libraries):
                if isinstance(lib, Library):
                    if lib.kind == "static":
                        self.libraries_a.append(lib)
                    else:
                        self.libraries_so.append(lib)
                else:
                    self.libraries.append(lib)

    def check_library_list (self, libraries):
        ListType, TupleType = type([]), type(())
        if not isinstance(libraries, ListType):
            raise DistutilsSetupError(
                "'libraries' option must be a list of "
                "Library instances or 2-tuples")
        for lib in libraries:
            #
            if isinstance(lib, Library):
                lib_name = lib.name
                build_info = lib.__dict__
            elif isinstance(lib, TupleType) and len(lib) == 2:
                lib_name, build_info = lib
            else:
                raise DistutilsSetupError(
                    "each element of 'libraries' option must be an "
                    "Library instance or 2-tuple")
            #
            if not isinstance(lib_name, str):
                raise DistutilsSetupError(
                    "first element of each tuple in 'libraries' "
                    "must be a string (the library name)")
            if '/' in lib_name or (os.sep != '/' and os.sep in lib_name):
                raise DistutilsSetupError(
                    "bad library name '%s': "
                    "may not contain directory separators" % lib[0])
            if not isinstance(build_info, dict):
                raise DistutilsSetupError(
                    "second element of each tuple in 'libraries' "
                    "must be a dictionary (build info)")
            lib_type = build_info.get('kind', 'static')
            if lib_type not in ('static', 'shared', 'dylib'):
                raise DistutilsSetupError(
                    "in 'kind' option (library '%s'), "
                    "'kind' must be one of "
                    " \"static\", \"shared\", \"dylib\"" % lib_name)
            sources = build_info.get('sources')
            if (sources is None or
                type(sources) not in (ListType, TupleType)):
                raise DistutilsSetupError(
                    "in 'libraries' option (library '%s'), "
                    "'sources' must be present and must be "
                    "a list of source filenames" % lib_name)
            depends = build_info.get('depends')
            if (depends is not None and
                type(depends) not in (ListType, TupleType)):
                raise DistutilsSetupError(
                    "in 'libraries' option (library '%s'), "
                    "'depends' must be a list "
                    "of source filenames" % lib_name)

    def run (self):
        cmd_build_clib.build_clib.run(self)
        if (not self.libraries_a and
            not self.libraries_so):
            return
        #
        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler(compiler=self.compiler,
                                     dry_run=self.dry_run,
                                     force=self.force)
        #
        if self.define is not None:
            for (name, value) in self.define:
                self.compiler.define_macro(name, value)
        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)
        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.library_dirs is not None:
            self.compiler.set_library_dirs(self.library_dirs)
        if self.rpath is not None:
            self.compiler.set_runtime_library_dirs(self.rpath)
        if self.link_objects is not None:
            self.compiler.set_link_objects(self.link_objects)
        #
        config = configuration(self, verbose=True)
        configure_compiler(self.compiler, config)
        #
        self.build_libraries(self.libraries)
        self.build_libraries(self.libraries_a)
        self.build_libraries(self.libraries_so)

    def build_libraries (self, libraries):
        for lib in libraries:
            # old-style
            if not isinstance(lib, Library):
                cmd_build_clib.build_clib.build_libraries(self, [lib])
                continue
            # new-style
            try:
                self.build_library(lib)
            except (DistutilsError, CCompilerError):
                if not lib.optional: raise
                e = sys.exc_info()[1]
                self.warn('building library "%s" failed' % lib.name)
                self.warn('%s' % e)

    def config_library (self, lib):
        if lib.configure:
            config_cmd = self.get_finalized_command('config')
            config_cmd.compiler = self.compiler # fix compiler
            return lib.configure(lib, config_cmd)

    def build_library(self, lib):
        from distutils.dep_util import newer_group

        sources = [convert_path(p) for p in lib.sources]
        depends = [convert_path(p) for p in lib.depends]
        depends = sources + depends

        if lib.kind == "static":
            build_dir = self.build_clib_a
        else:
            build_dir = self.build_clib_so
        lib_fullpath = self.get_lib_fullpath(lib, build_dir)

        if not (self.force or newer_group(depends, lib_fullpath, 'newer')):
            log.debug("skipping '%s' %s library (up-to-date)",
                      lib.name, lib.kind)
            return

        ok = self.config_library(lib)
        log.info("building '%s' %s library", lib.name, lib.kind)

        # First, compile the source code to object files in the library
        # directory.  (This should probably change to putting object
        # files in a temporary build directory.)
        macros = lib.define_macros[:]
        for undef in lib.undef_macros:
            macros.append((undef,))

        objects = self.compiler.compile(
            sources,
            depends=lib.depends,
            output_dir=self.build_temp,
            macros=macros,
            include_dirs=lib.include_dirs,
            extra_preargs=None,
            extra_postargs=lib.extra_compile_args,
            debug=self.debug,
            )

        if lib.kind == "static":
            # Now "link" the object files together
            # into a static library.
            self.compiler.create_static_lib(
                objects,
                lib.name,
                output_dir=os.path.dirname(lib_fullpath),
                debug=self.debug,
                )
        else:
            extra_objects = lib.extra_objects[:]
            export_symbols = lib.export_symbols[:]
            extra_link_args = lib.extra_link_args[:]
            objects.extend(extra_objects)
            if (self.compiler.compiler_type == 'msvc' and
                export_symbols is not None):
                output_dir = os.path.dirname(lib_fullpath)
                implib_filename = self.compiler.library_filename(lib.name)
                implib_file = os.path.join(output_dir, lib_fullpath)
                extra_link_args.append ('/IMPLIB:' + implib_file)
            # Detect target language, if not provided
            src_language = self.compiler.detect_language(sources)
            language = (lib.language or src_language)
            # Now "link" the object files together
            # into a shared library.
            self.compiler.link(
                self.compiler.SHARED_LIBRARY,
                objects, lib_fullpath,
                #
                libraries=lib.libraries,
                library_dirs=lib.library_dirs,
                runtime_library_dirs=lib.runtime_library_dirs,
                export_symbols=export_symbols,
                extra_preargs=None,
                extra_postargs=extra_link_args,
                debug=self.debug,
                target_lang=language,
                )
        return

    def get_lib_fullpath (self, lib, build_dir):
        package_dir = (lib.package or '').split('.')
        dest_dir = convert_path(lib.dest_dir or '')
        output_dir = os.path.join(build_dir, *package_dir+[dest_dir])
        lib_type =  lib.kind
        if sys.platform != 'darwin':
            if lib_type == 'dylib':
                lib_type = 'shared'
        compiler = self.compiler # XXX
        lib_fullpath = compiler.library_filename(
            lib.name, lib_type=lib_type, output_dir=output_dir)
        return lib_fullpath

    def get_source_files (self):
        filenames = cmd_build_clib.build_clib.get_source_files(self)
        self.check_library_list(self.libraries)
        self.check_library_list(self.libraries_a)
        self.check_library_list(self.libraries_so)
        for (lib_name, build_info) in self.libraries:
            filenames.extend(build_info.get(sources, []))
        for lib in self.libraries_so + self.libraries_a:
            filenames.extend(lib.sources)
        return filenames

    def get_outputs (self):
        outputs = []
        for lib in self.libraries_a:
            lib_fullpath = self.get_lib_fullpath(lib, self.build_clib_a)
            outputs.append(lib_fullpath)
        for lib in self.libraries_so:
            lib_fullpath = self.get_lib_fullpath(lib, self.build_clib_so)
            outputs.append(lib_fullpath)
        return outputs


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
        #
        if ((sys.platform.startswith('linux') or
             sys.platform.startswith('gnu') or
             sys.platform.startswith('sunos')) and
            sysconfig.get_config_var('Py_ENABLE_SHARED')):
            py_version = sysconfig.get_python_version()
            bad_pylib_dir = os.path.join(sys.prefix, "lib",
                                         "python" + py_version,
                                         "config")
            try:
                self.library_dirs.remove(bad_pylib_dir)
            except ValueError:
                pass
            pylib_dir = sysconfig.get_config_var("LIBDIR")
            if pylib_dir not in self.library_dirs:
                self.library_dirs.append(pylib_dir)
            if pylib_dir not in self.rpath:
                self.rpath.append(pylib_dir)
            if sys.exec_prefix == '/usr':
                self.library_dirs.remove(pylib_dir)
                self.rpath.remove(pylib_dir)

    def run (self):
        if self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command('build_clib')
            if build_clib.libraries:
                build_clib.run()
        cmd_build_ext.build_ext.run(self)

    def build_extensions(self):
        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)
        # parse configuration file and configure compiler
        config = configuration(self, verbose=True)
        configure_compiler(self.compiler, config)
        if self.compiler.compiler_type == "unix":
            so_ext = sysconfig.get_config_var('SO')
            self.compiler.shared_lib_extension = so_ext
        self.config = config # XXX
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
            log.info("defining preprocessor macro '%s'" % macro)
            self.compiler.define_macro(macro, 1)
        # build extensions
        for ext in self.extensions:
            try:
                self.build_extension(ext)
            except (DistutilsError, CCompilerError):
                if not ext.optional: raise
                e = sys.exc_info()[1]
                self.warn('building extension "%s" failed' % ext.name)
                self.warn('%s' % e)

    def config_extension (self, ext):
        configure = getattr(ext, 'configure', None)
        if configure:
            config_cmd = self.get_finalized_command('config')
            config_cmd.compiler = self.compiler # fix compiler
            configure(ext, config_cmd)

    def build_extension (self, ext):
        from distutils.dep_util import newer_group
        fullname = self.get_ext_fullname(ext.name)
        filename = os.path.join(
            self.build_lib, self.get_ext_filename(fullname))
        depends = ext.sources + ext.depends
        if not (self.force or newer_group(depends, filename, 'newer')):
            log.debug("skipping '%s' extension (up-to-date)", ext.name)
            return
        #
        self.config_extension(ext)
        cmd_build_ext.build_ext.build_extension(self, ext)
        #
        # XXX -- this is a Vile HACK!
        if ext.name == 'mpi4py.MPI':
            dest_dir = os.path.dirname(filename)
            self.mkpath(dest_dir)
            mpi_cfg = os.path.join(dest_dir, 'mpi.cfg')
            log.info("writing %s" % mpi_cfg)
            if not self.dry_run:
                self.config.dump(filename=mpi_cfg)

    def get_outputs(self):
        outputs = cmd_build_ext.build_ext.get_outputs(self)
        for ext in self.extensions:
            # XXX -- this is a Vile HACK!
            if ext.name == 'mpi4py.MPI':
                fullname = self.get_ext_fullname(ext.name)
                filename = os.path.join(
                    self.build_lib,
                    self.get_ext_filename(fullname))
                dest_dir = os.path.dirname(filename)
                mpi_cfg = os.path.join(dest_dir, 'mpi.cfg')
                outputs.append(mpi_cfg)
        return outputs


# Command class to build executables

class build_exe(build_ext):

    description = "build binary executable components"

    user_options = [
        ('build-exe=', None,
         "build directory for executable components"),
        ] + build_ext.user_options


    def initialize_options (self):
        build_ext.initialize_options(self)
        self.build_base = None
        self.build_exe  = None

    def finalize_options (self):
        build_ext.finalize_options(self)
        self.configure = None
        self.set_undefined_options('build',
                                   ('build_base','build_base'),
                                   ('build_lib', 'build_exe'))
        #from distutils.util import get_platform
        #plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
        #if hasattr(sys, 'gettotalrefcount') and sys.version[0:3] > '2.5':
        #    plat_specifier += '-pydebug'
        #if self.build_exe is None:
        #    self.build_exe = os.path.join(self.build_base,
        #                                  'exe' + plat_specifier)
        self.executables = self.distribution.executables
        # XXX This is a hack
        self.extensions  = self.distribution.executables
        self.check_extensions_list = self.check_executables_list
        self.build_extension = self.build_executable
        self.get_ext_filename = self.get_exe_filename
        self.build_lib = self.build_exe

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
                    ("in 'executables' option (executable '%s'), " +
                     "'sources' must be present and must be " +
                     "a list of source filenames") % exe.name)

    def get_exe_filename(self, exe_name):
        exe_ext = sysconfig.get_config_var('EXE') or ''
        return exe_name + exe_ext

    def get_exe_fullpath(self, exe, build_dir=None):
        build_dir = build_dir or self.build_exe
        package_dir = (exe.package or '').split('.')
        dest_dir = convert_path(exe.dest_dir or '')
        output_dir = os.path.join(build_dir, *package_dir+[dest_dir])
        exe_filename = self.get_exe_filename(exe.name)
        return os.path.join(output_dir, exe_filename)

    def config_executable (self, exe):
        build_ext.config_extension(self, exe)

    def build_executable (self, exe):
        from distutils.dep_util import newer_group
        sources = list(exe.sources)
        depends = list(exe.depends)
        exe_fullpath = self.get_exe_fullpath(exe)
        depends = sources + depends
        if not (self.force or newer_group(depends, exe_fullpath, 'newer')):
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

        # XXX -- this is a Vile HACK!
        #
        # Remove msvcrXX.dll when building executables with MinGW
        #
        if self.compiler.compiler_type == 'mingw32':
            try: del self.compiler.dll_libraries[:]
            except: pass

        # Now link the object files together into a "shared object" --
        # of course, first we have to figure out all the other things
        # that go into the mix.
        if exe.extra_objects:
            objects.extend(exe.extra_objects)
        extra_args = exe.extra_link_args[:]
        # Get special linker flags for building a executable with
        # bundled Python library, also fix location of needed
        # python.exp file on AIX
        ldshflag = sysconfig.get_config_var('LINKFORSHARED') or ''
        ldshflag = ldshflag.replace('-Xlinker ', '-Wl,')
        if sys.platform == 'darwin': # fix wrong framework paths
            fwkprefix = sysconfig.get_config_var('PYTHONFRAMEWORKPREFIX')
            fwkdir = sysconfig.get_config_var('PYTHONFRAMEWORKDIR')
            if fwkprefix and fwkdir and fwkdir != 'no-framework':
                for flag in split_quoted(ldshflag):
                    if flag.startswith(fwkdir):
                        fwkpath = os.path.join(fwkprefix, flag)
                        ldshflag = ldshflag.replace(flag, fwkpath)
        if sys.platform.startswith('aix'):
            python_lib = sysconfig.get_python_lib(standard_lib=1)
            python_exp = os.path.join(python_lib, 'config', 'python.exp')
            ldshflag = ldshflag.replace('Modules/python.exp', python_exp)
        # Detect target language, if not provided
        language = exe.language or self.compiler.detect_language(sources)
        self.compiler.link(
            self.compiler.EXECUTABLE,
            objects, exe_fullpath,
            output_dir=None,
            libraries=self.get_libraries(exe),
            library_dirs=exe.library_dirs,
            runtime_library_dirs=exe.runtime_library_dirs,
            extra_preargs=split_quoted(ldshflag),
            extra_postargs=extra_args,
            debug=self.debug,
            target_lang=language)

    def get_outputs (self):
        outputs = []
        for exe in self.executables:
            outputs.append(self.get_exe_fullpath(exe))
        return outputs


class install(cmd_install.install):

    user_options = cmd_install.install.user_options + [
        ('single-version-externally-managed', None,
         "setuptools compatibility option"),
    ]
    boolean_options = cmd_install.install.boolean_options + [
        'single-version-externally-managed',
    ]

    def initialize_options(self):
        cmd_install.install.initialize_options(self)
        self.single_version_externally_managed = None
        self.no_compile = None

    def has_lib (self):
        return (cmd_install.install.has_lib(self) and
                self.has_exe())

    def has_exe (self):
        return self.distribution.has_executables()

    sub_commands = \
        cmd_install.install.sub_commands[:] + \
        [('install_exe', has_exe),
         ]

    # XXX disable install_exe subcommand !!!
    del sub_commands[-1]


class install_lib(cmd_install_lib.install_lib):

    def get_outputs(self):
        outputs = cmd_install_lib.install_lib.get_outputs(self)
        for (build_cmd, build_dir) in (('build_clib', 'build_lib'),
                                       ('build_exe',  'build_exe')):
            outs = self._mutate_outputs(1, build_cmd, build_dir,
                                        self.install_dir)
            build_cmd = self.get_finalized_command(build_cmd)
            build_files = build_cmd.get_outputs()
            outputs.extend(outs)
        return outputs


class install_data (cmd_install_data.install_data):

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

    def run (self):
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
                if (os.name == "posix" and
                    exe_filename.startswith("python-")):
                    install_name = exe_filename.replace(
                        "python-","python%s-" % sys.version[:3])
                    link = None
                else:
                    install_name = exe_fullpath
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


class test(Command):
    description = "run the test suite"
    user_options = [
        ('args=', None, "options"),
        ]

    def initialize_options(self):
        self.args = None
    def finalize_options(self):
        if self.args:
            self.args = split_quoted(self.args)
        else:
            self.args = []
    def run(self):
        pass


class sdist(cmd_sdist.sdist):

    def run (self):
        build_src = self.get_finalized_command('build_src')
        build_src.run()
        cmd_sdist.sdist.run(self)


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
            for directory in (self.build_lib,
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

# -----------------------------------------------------------------------------

try:
    import msilib
    Directory_make_short = msilib.Directory.make_short
    def make_short(self, file):
        parts = file.split('.')
        if len(parts) > 1:
            file = '_'.join(parts[:-1])+'.'+parts[-1]
        return Directory_make_short(self, file)
    msilib.Directory.make_short = make_short
except:
    pass

# -----------------------------------------------------------------------------
