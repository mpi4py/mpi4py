# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

"""
Support for building mpi4py with distutils.
"""

# -----------------------------------------------------------------------------

# Environmental variables to look for configuration
MPICC_ENV  = ['MPICC']
MPICXX_ENV = ['MPICXX']
MPILD_ENV  = ['MPILD']
MPICFG_ENV = ['MPICFG']

# Default values to use for configuration
MPICC  = ['mpicc']
MPICXX = ['mpicxx', 'mpic++', 'mpiCC']
MPILD  = MPICC + MPICXX
MPICFG = ('mpi', 'mpi.cfg')

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

def fix_compiler_cmd(mpicc, pycc):
    if not pycc:  return mpicc
    if not mpicc: return pycc
    pycc = split_quoted(pycc)
    i = 0
    if os.path.basename(pycc[0]) == 'env':
        i = 1
        while '=' in pycc[i]:
            i = i + 1
    pycc[i] = mpicc
    mpicc   = ' '.join(pycc)
    return mpicc

def fix_linker_cmd(mpild, pyld):
    if not pyld:  return mpild
    if not mpild: return pyld
    aix_fixup = (sys.platform.startswith('aix') and
                 'ld_so_aix' in pyld)
    pyld = split_quoted(pyld)
    i = 0
    if os.path.basename(pyld[0]) == 'env':
        i = 1
        while '=' in pyld[i]:
            i = i + 1
    if aix_fixup:
        i = i + 1
    pyld[i] = mpild
    mpild   = ' '.join(pyld)
    return mpild

from distutils.unixccompiler import UnixCCompiler
rpath_option_orig = UnixCCompiler.runtime_library_dir_option
def rpath_option(compiler, dir):
    option = rpath_option_orig(compiler, dir)
    if sys.platform.startswith('linux'):
        if option.startswith('-R'):
            option =  option.replace('-R', '-Wl,-rpath,', 1)
        elif option.startswith('-Wl,-R'):
            option =  option.replace('-Wl,-R', '-Wl,-rpath,', 1)
    return option
UnixCCompiler.runtime_library_dir_option = rpath_option

def customize_compiler(compiler,
                       mpicc=None, mpicxx=None, mpild=None,
                       environ=None):
    if environ is None:
        environ = os.environ
    if compiler.compiler_type == 'unix':
        # Distutils configuration, actually obtained by parsing
        # :file:{prefix}/lib[32|64]/python{X}.{Y}/config/Makefile
        (cc, cxx, ccshared,
         basecflags, optcflags,
         ld_so, so_ext) = \
         get_config_vars('CC', 'CXX', 'CCSHARED',
                         'BASECFLAGS', 'OPT',
                         'LDSHARED', 'SO')
        cc    = cc    .replace('-pthread', '')
        cxx   = cxx   .replace('-pthread', '')
        ld_so = ld_so .replace('-pthread', '')
        cppflags = ''
        cflags   = ''
        cxxflags = ''
        ldflags  = ''
        # Compiler command overriding
        if mpicc:
            cc  = fix_compiler_cmd(mpicc,  cc)
        if mpicxx:
            cxx = fix_compiler_cmd(mpicxx, cxx)
        if mpild:
            ld_so = fix_linker_cmd(mpild,  ld_so)
        elif (mpicc or mpicxx):
            mpild = mpicc or mpicxx
            ld_so = fix_linker_cmd(mpild, ld_so)
        # Environment handling
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
        ccshared   = environ.get('CCSHARED',   ccshared   or '')
        basecflags = environ.get('BASECFLAGS', basecflags or '')
        optcflags  = environ.get('OPTCFLAGS',  optcflags  or '')
        cflags     = (basecflags + ' ' +
                      optcflags  + ' ' +
                      cflags)
        cxxflags   = (basecflags + ' ' +
                      optcflags  + ' ' +
                      cxxflags)
        cxxflags = cxxflags.replace('-Wstrict-prototypes', '')
        # Distutils compiler setup
        cpp    = os.environ.get('CPP') or (cc + ' -E')
        cc_so  = cc  + ' ' + ccshared
        cxx_so = cxx + ' ' + ccshared
        ld_exe = mpild or cc
        compiler.set_executables(
            preprocessor = cpp    + ' ' + cppflags,
            compiler     = cc     + ' ' + cflags,
            compiler_so  = cc_so  + ' ' + cflags,
            compiler_cxx = cxx_so + ' ' + cxxflags,
            linker_so    = ld_so  + ' ' + ldflags,
            linker_exe   = ld_exe + ' ' + ldflags,
            )
        compiler.shared_lib_extension = so_ext
        try: compiler.compiler_cxx.remove('-Wstrict-prototypes')
        except: pass
    if compiler.compiler_type == 'mingw32':
        compiler.set_executables(
            preprocessor = 'gcc -mno-cygwin -E',
            )

def find_mpi_compiler(name,
                      envvars,
                      command,
                      config,
                      default,
                      executables,
                      path=None):
    """
    Find MPI compiler wrappers
    """
    # 1.- search in environment
    if envvars:
        if isinstance(envvars, str):
            envvars = (envvars,)
        for var in envvars:
            value = os.environ.get(var)
            if value:
                return value
    # 2.- search in distutils command instance
    if command:
        value = getattr(command, name, None)
        if value:
            return value
    # 3.- search in configuration dict
    if config:
        value = config.get(name, None)
        if value:
            return value
    # 4.- use default value
    if default:
        return default
    # 5.- search executable in path
    if executables:
        if isinstance(executables, str):
            executables = (executables,)
        for exe in executables:
            try:
                bits = split_quoted(exe)
                cmd, args = bits[0], ' '.join(bits[1:])
            except:
                cmd, args = exe, ''
            cmd = find_executable(cmd, path)
            if cmd is not None:
                if args:
                    cmd = cmd + ' ' + args
                return cmd
    # nothing found
    return None

# -----------------------------------------------------------------------------

try:
    from ConfigParser import ConfigParser
    from ConfigParser import Error as ConfigParserError
except ImportError:
    from configparser import ConfigParser
    from configparser import Error as ConfigParserError


def _config_parser(section, filenames, raw=False, vars=None):
    """
    Returns a dictionary of options obtained by parsing configuration
    files.
    """
    parser = ConfigParser()
    try:
        parser.read(filenames.split(os.path.pathsep))
    except ConfigParserError:
        log.error("error: parsing configuration file/s '%s'", filenames)
        return None
    if sys.platform.startswith('win'):
        if parser.has_section(section+'-win'):
            section = section+'-win'
    elif sys.platform.startswith('darwin'):
        if parser.has_section(section+'-osx'):
            section = section+'-osx'
    if not parser.has_section(section):
        log.error("error: section '%s' not found "
                  "in configuration file/s '%s'", section, filenames)
        return None
    config_info = {}
    for k, v in parser.items(section, raw, vars):
        if k in ('define_macros',
                 'undef_macros',
                 'libraries'):
            config_info[k] = [e.strip() for e in split_quoted(v)]
        elif k in ('include_dirs',
                   'library_dirs',
                   'runtime_library_dirs',):
            pathsep = os.path.pathsep
            pathlist = [p.strip() for p in v.split(pathsep)]
            expanduser = os.path.expanduser
            expandvars = os.path.expandvars
            config_info[k] = [expanduser(expandvars(p))
                              for p in pathlist if p]
        elif k == 'extra_objects':
            expanduser = os.path.expanduser
            expandvars = os.path.expandvars
            config_info[k] = [expanduser(expandvars(e))
                              for e in split_quoted(v)]
        elif k in ('extra_compile_args',
                   'extra_link_args'):
            config_info[k] = split_quoted(v)
        else:
            config_info[k] = v.strip()
    if 'define_macros' in config_info:
        macros = []
        for m in config_info['define_macros'] :
            try: # "-DFOO=bar"
                idx = m.index('=')
                macro = (m[:idx], m[idx+1:] or None)
            except ValueError: # bare "-DFOO"
                macro = (m, None)
            macros.append(macro)
        config_info['define_macros'] = macros
    return config_info


def find_mpi_config(section, envvars=None, defaults=None):
    if not section and envvars:
        # look in environment
        if isinstance(envvars, str):
            envvars = (envvars,)
        for var in envvars:
            section = os.environ.get(var, None)
            if section: break
    filenames = ''
    if section and ',' in section:
        section, filenames = section.split(',', 1)
    if defaults:
        if not section:
            section = defaults[0]
        if not filenames:
            fname = defaults[1]
            if os.path.exists(fname):
                filenames = fname
    # parse configuration
    if section and filenames:
        config_info = _config_parser(section, filenames)
        return section, filenames, config_info
    else:
        return section, filenames, None

# -----------------------------------------------------------------------------

def configuration(command_obj, verbose=True):
    # user-provided
    section, filenames, config_info = \
        find_mpi_config(getattr(command_obj, 'mpi', None),
                        MPICFG_ENV, MPICFG)
    if config_info:
        if verbose:
            log.info("MPI configuration: "
                     "from section '[%s]' in file/s '%s'",
                     section, filenames)
        return config_info
    # Windows
    if sys.platform.startswith('win'):
        ProgramFiles = os.environ.get('ProgramFiles', '')
        for (name, install_suffix) in (
            ('mpich2', 'MPICH2'),
            #('openmpi', 'OpenMPI'),
            ('deinompi', 'DeinoMPI'),
            ('msmpi', 'Microsoft HPC Pack 2008 SDK'),
            ):
            mpi_dir = os.path.join(ProgramFiles, install_suffix)
            if os.path.isdir(mpi_dir):
                if verbose:
                    log.info("MPI configuration: "
                             "directory '%s'", mpi_dir)
                define_macros = []
                include_dir = os.path.join(mpi_dir, 'include')
                library = 'mpi'
                library_dir = os.path.join(mpi_dir, 'lib')
                if name == 'msmpi':
                    define_macros = [('MS_MPI', 1)]
                    library = 'msmpi'
                    bits = platform.architecture()[0]
                    if bits == '32bit':
                        library_dir = os.path.join(library_dir, 'i386')
                    elif bits == '64bit':
                        library_dir = os.path.join(library_dir, 'amd64')
                config_info = dict(define_macros=define_macros,
                                   include_dirs=[include_dir],
                                   libraries=[library],
                                   library_dirs=[library_dir],)
                return config_info
    # nothing found
    return {}


def configure_compiler(compiler, config_info, command_obj=None, verbose=True):
    #
    mpicc = find_mpi_compiler(
        'mpicc', MPICC_ENV, command_obj, config_info, None, MPICC)
    if verbose:
        log.info("MPI C compiler:    %s", mpicc or 'not found')
    #
    mpicxx = find_mpi_compiler(
        'mpicxx', MPICXX_ENV, command_obj, config_info, None, MPICXX)
    if verbose:
        log.info("MPI C++ compiler:  %s", mpicxx or 'not found')
    #
    mpild = mpicc or mpicxx # default
    mpild = find_mpi_compiler(
        'mpild', MPILD_ENV, command_obj, config_info, mpild, MPILD)
    if verbose:
        log.info("MPI linker:        %s", mpild or 'not found')
    #
    customize_compiler(compiler, mpicc=mpicc, mpicxx=mpicxx, mpild=mpild)
    #
    if config_info:
        for k, v in config_info.get('define_macros', []):
            compiler.define_macro(k, v)
        for v in config_info.get('undef_macros', []):
            compiler.undefine_macro(v)
        for v in config_info.get('include_dirs', []):
            compiler.add_include_dir(v)
        for v in config_info.get('libraries', []):
            compiler.add_library(v)
        for v in config_info.get('library_dirs', []):
            compiler.add_library_dir(v)
        for v in config_info.get('runtime_library_dirs', []):
            compiler.add_runtime_library_dir(v)
        for v in config_info.get('extra_objects', []):
            compiler.add_link_object(v)
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

class Configure(object):

    SRCDIR = 'src'
    SOURCES = [os.path.join('include', 'mpi4py', 'mpi.pxi')]
    DESTDIR = 'src'
    CONFIG_H = 'config.h'
    MISSING_H = 'missing.h'

    def __init__(self, config_cmd, verbose=True):
        self.scanner = Scanner()
        for filename in self.SOURCES:
            fullname = os.path.join(self.SRCDIR, filename)
            self.scanner.parse_file(fullname)
        self.config_cmd = config_cmd
        self.verbose = verbose

    def run(self):
        results = []
        for name, code in self.scanner.itertests():
            if self.verbose:
                log.info("checking for '%s' ..." % name)
            body = self.gen_one(results, code)
            ok   = self.run_one(body)
            if not ok:
                if self.verbose:
                    log.info("**** failed check for '%s'" % name)
            results.append((name, ok))
        return results

    def dump(self, results):
        destdir = self.DESTDIR
        config_h  = os.path.join(destdir, self.CONFIG_H)
        missing_h = os.path.join(destdir, self.MISSING_H)
        if self.verbose:
            log.info("writing '%s'", config_h)
        self.scanner.dump_config_h(config_h, results)
        if self.verbose:
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

from distutils.core import setup as fcn_setup
from distutils.core import Distribution as cls_Distribution
from distutils.extension import Extension as cls_Extension

from distutils.command import config as cmd_config
from distutils.command import build as cmd_build
from distutils.command import install as cmd_install
from distutils.command import clean as cmd_clean

from distutils.command import build_py as cmd_build_py
from distutils.command import build_clib as cmd_build_clib
from distutils.command import build_ext as cmd_build_ext
from distutils.command import install_data as cmd_install_data
from distutils.command import install_lib as cmd_install_lib

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

# Extension class

class Extension(cls_Extension):
    def __init__ (self, **kw):
        optional = kw.pop('optional', None)
        cls_Extension.__init__(self, **kw)
        self.optional = optional

# Executable class

class Executable(Extension):
    pass

# setup function

def setup(**attrs):
    if 'distclass' not in attrs:
        attrs['distclass'] = Distribution
    if 'cmdclass' not in attrs:
        attrs['cmdclass'] = {}
    cmdclass = attrs['cmdclass']
    for cmd in (config, build, install, clean,
                build_py, build_clib, build_ext, build_exe,
                install_data, install_exe,
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
  ierr = MPI_Finalize();
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
        log.info(ok and 'succes!' or 'failure.')
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

    check_hdr  = check_header
    check_lib  = check_library
    check_func = check_function

    def run (self):
        # test configuration in specified section and file
        config_info = configuration(self, verbose=True)
        # test MPI C compiler
        mpicc = find_mpi_compiler(
            'mpicc', MPICC_ENV, self, config_info, None, MPICC)
        log.info("MPI C compiler:    %s", mpicc  or 'not found')
        self.compiler = getattr(self.compiler, 'compiler_type',
                                self.compiler)
        self._check_compiler()
        compiler_obj = self.compiler
        customize_compiler(compiler_obj, mpicc=mpicc)
        self.try_link(ConfigTest, headers=['mpi.h'], lang='c')
        # test MPI C++ compiler
        mpicxx = find_mpi_compiler(
            'mpicxx', MPICXX_ENV, self, config_info, None, MPICXX)
        log.info("MPI C++ compiler:  %s", mpicxx or 'not found')
        self.compiler = getattr(self.compiler, 'compiler_type',
                                self.compiler)
        self._check_compiler()
        compiler_obj = self.compiler
        customize_compiler(compiler_obj, mpicxx=mpicxx)
        if compiler_obj.compiler_type in ('unix', 'cygwin', 'mingw32'):
            try: compiler_obj.compiler_cxx.remove('-Wstrict-prototypes')
            except: pass
            try: compiler_obj.compiler_so.remove('-Wstrict-prototypes')
            except: pass
            compiler_obj.compiler_so[0] = compiler_obj.compiler_cxx[0]
            compiler_obj.linker_exe[0]  = compiler_obj.compiler_cxx[0]
        self.try_link(ConfigTest, headers=['mpi.h'], lang='c++')

# -----------------------------------------------------------------------------

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
        cmd_build.build.sub_commands + \
        [('build_exe', has_executables),
         ]

# -----------------------------------------------------------------------------

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
                return apply(os.path.join, path)
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
                    return apply(os.path.join, tail)
            else:
                pdir = self.package_dir.get('')
                if pdir is not None:
                    tail.insert(0, pdir)

                if tail:
                    return apply(os.path.join, tail)
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

# -----------------------------------------------------------------------------

class build_clib(cmd_build_clib.build_clib):

    user_options = [
        ('build-clib-so', 'l',
         "directory to build C/C++ shared libraries to"),
        ]

    user_options += cmd_build_clib.build_clib.user_options + cmd_mpi_opts

    def initialize_options (self):
        self.libraries_a = []
        self.libraries_so = []
        self.library_dirs = None
        self.runtime_library_dirs = None

        self.build_clib_so = None
        cmd_build_clib.build_clib.initialize_options(self)
        cmd_initialize_mpi_options(self)

    def finalize_options (self):
        cmd_build_clib.build_clib.finalize_options(self)
        build_cmd = self.get_finalized_command('build')
        if isinstance(build_cmd,  build):
            cmd_set_undefined_mpi_options(self, 'build')
        #
        self.library_dirs = []
        self.runtime_library_dirs = []
        self.set_undefined_options('build',
                                   ('build_lib', 'build_clib_so'))
        #
        self.check_library_list (self.libraries)
        for library in self.libraries:
            lib_name, build_info = library
            lib_type = build_info.get('kind', 'static')
            if lib_type == 'static':
                self.libraries_a.append(library)
            else:
                self.libraries_so.append(library)
         # XXX This is a hack
        self.libraries[:] = self.libraries_a

    def run (self):
        if (not self.libraries and
            not self.libraries_a and
            not self.libraries_so):
            return
        #
        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler(compiler=self.compiler,
                                     dry_run=self.dry_run,
                                     force=self.force)
        #
        if self.define is not None:
            for (name,value) in self.define:
                self.compiler.define_macro(name, value)
        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)
        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.library_dirs is not None:
            self.compiler.set_library_dirs(self.library_dirs)
        #
        config_info = configuration(self, verbose=True)
        try: # Py2.7+ & Py3.2+
            compiler_obj = self.compiler_obj
        except AttributeError:
            compiler_obj = self.compiler
        configure_compiler(compiler_obj, config_info, self)
        #
        if self.libraries_a:
            self.config_static_libraries(self.libraries_a, config_info)
            self.build_static_libraries(self.libraries_a)
        if self.libraries_so:
            self.config_shared_libraries(self.libraries_so, config_info)
            self.build_shared_libraries(self.libraries_so)

    def check_library_list (self, libraries):
        cmd_build_clib.build_clib.check_library_list(self, libraries)
        ListType, TupleType = type([]), type(())
        for (lib_name, build_info) in libraries:
            kind = build_info.get('kind', 'static')
            if kind not in ('static', 'shared', 'dylib'):
                raise DistutilsSetupError(
                    "in 'kind' option (library '%s'), "
                    "'kind' must be one of "
                    " \"static\", \"shared\", \"dylib\"" % lib_name)
            sources = build_info.get('sources')
            if sources is None or type(sources) not in (ListType, TupleType):
                raise DistutilsSetupError(
                    "in 'libraries' option (library '%s'), "
                    "'sources' must be present and must be "
                    "a list of source filenames" % lib_name)
            depends = build_info.get('depends')
            if depends is not None:
                if type(depends) not in (ListType, TupleType):
                    raise DistutilsSetupError(
                        "in 'libraries' option (library '%s'), "
                        "'depends' must be a list "
                        "of source filenames" % lib_name)

    def config_static_libraries (self, libraries):
        for (lib_name, build_info) in libraries:
            for attr in ('extra_compile_args',):
                extra_args = config_info.get(attr)
                if extra_args:
                    build_info.setdefault(attr,[]).extend(extra_args)

    def build_static_libraries (self, libraries):
        cmd_build_clib.build_clib.build_libraries(self, libraries)

    def config_shared_libraries (self, libraries, config_info):
        for library in libraries:
            (lib_name, build_info) = library
            for attr in ('extra_compile_args',
                         'extra_link_args',):
                extra_args = config_info.get(attr)
                if extra_args:
                    build_info.setdefault(attr, []).extend(extra_args)

    def build_shared_libraries (self, libraries):
        for (lib_name, build_info) in libraries:
            library = (lib_name, build_info)
            optional = build_info.get('optional')
            try:
                self.build_shared_library(library)
            except (DistutilsError, CCompilerError):
                if not optional:
                    raise
                e = sys.exc_info()[1]
                self.warn('building shared library "%s" failed' % lib_name)
                self.warn('%s' % e)

    def config_shared_library(self, library):
        (lib_name, build_info) = library
        try:
            compiler_obj = self.compiler_obj
        except AttributeError:
            compiler_obj = self.compiler
        config_cmd = self.get_finalized_command('config')
        config_cmd.compiler = compiler_obj # fix compiler
        ok = True
        if lib_name == 'mpe':
            ok = config_cmd.check_library('mpe')
        if lib_name == 'vt':
            ok = config_cmd.check_library('vt.mpi')
        if not ok:
            build_info['libraries'] = []
            build_info['extra_link_args'] = []

    def build_shared_library (self, library):
        from distutils.dep_util import newer_group

        try: # Py2.7+ & Py3.2+
            compiler_obj = self.compiler_obj
        except AttributeError:
            compiler_obj = self.compiler

        (lib_name, build_info) = library

        sources = [convert_path(p) for p in build_info.get('sources',[])]
        depends = [convert_path(p) for p in build_info.get('depends',[])]
        depends = sources + depends

        output_dir = convert_path(build_info.get('output_dir', ''))
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(self.build_clib_so, output_dir)

        lib_type = build_info['kind']
        if sys.platform != 'darwin':
            if lib_type == 'dylib':
                lib_type = 'shared'
        lib_filename = compiler_obj.library_filename(
            lib_name, lib_type=lib_type, output_dir=output_dir)

        if not (self.force or newer_group(depends, lib_filename, 'newer')):
            log.debug("skipping '%s' shared library (up-to-date)", lib_name)
            return

        self.config_shared_library(library)
        log.info("building '%s' shared library", lib_name)

        # First, compile the source code to object files in the library
        # directory.  (This should probably change to putting object
        # files in a temporary build directory.)
        objects = compiler_obj.compile(
            sources,
            depends=build_info.get('depends'),
            output_dir=self.build_temp,
            macros=build_info.get('macros', []),
            include_dirs=build_info.get('include_dirs'),
            extra_preargs=None,
            extra_postargs=build_info.get('extra_compile_args'),
            debug=self.debug,
            )

        extra_objects = build_info.get('extra_objects', [])
        objects.extend(extra_objects)
        export_symbols = build_info.get('export_symbols')
        extra_link_args = build_info.get('extra_link_args', [])
        if (compiler_obj.compiler_type == 'msvc' and
            export_symbols is not None):
            implib_filename = compiler_obj.library_filename(lib_name)
            implib_file = os.path.join(output_dir, implib_filename)
            extra_link_args.append ('/IMPLIB:' + implib_file)

        # Detect target language, if not provided
        language = (build_info.get('language') or
                    self.compiler.detect_language(sources))

        # Now "link" the object files together into a shared library.
        compiler_obj.link(
            compiler_obj.SHARED_LIBRARY,
            objects, lib_filename,
            #
            libraries=build_info.get('libraries'),
            library_dirs=build_info.get('library_dirs'),
            runtime_library_dirs=build_info.get('runtime_library_dirs'),
            export_symbols=export_symbols,
            extra_preargs=None,
            extra_postargs=extra_link_args,
            debug=self.debug,
            target_lang=language,
            )


# --------------------------------------------------------------------

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

    def build_extensions(self):
        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)
        # parse configuration file and configure compiler
        config_info = configuration(self, verbose=True)
        try: # Py2.7+ & Py3.2+
            compiler_obj = self.compiler_obj
        except AttributeError:
            compiler_obj = self.compiler
        configure_compiler(compiler_obj, config_info, self)
        config_cmd = self.get_finalized_command('config')
        config_cmd.compiler = compiler_obj # fix compiler
        # extra configuration, check for all MPI symbols
        if self.configure:
            log.info('testing for missing MPI symbols')
            config_obj = Configure(config_cmd)
            results = config_obj.run()
            config_obj.dump(results)
            #
            macro = 'PyMPI_HAVE_CONFIG_H'
            log.info("defining preprocessor macro '%s'" % macro)
            compiler_obj.define_macro(macro, 1)
        # configure extensions
        self.config_extensions(config_info)
        # and finally build extensions
        for ext in self.extensions:
            try:
                self.build_extension(ext)
            except (DistutilsError, CCompilerError):
                if not ext.optional:
                    raise
                e = sys.exc_info()[1]
                self.warn('building extension "%s" failed' % ext.name)
                self.warn('%s' % e)

    def config_extensions (self, config_info):
        from distutils.dep_util import newer_group
        for ext in self.extensions:
            fullname = self.get_ext_fullname(ext.name)
            ext_filename = os.path.join(
                self.build_lib, self.get_ext_filename(fullname))
            depends = ext.sources + ext.depends
            if not (self.force or
                    newer_group(depends, ext_filename, 'newer')):
                    continue
            self.config_extension (ext, config_info)

    def config_extension (self, ext, config_info):
        try:
            compiler_obj = self.compiler_obj
        except AttributeError:
            compiler_obj = self.compiler
        config_cmd = self.get_finalized_command('config')
        config_cmd.compiler = compiler_obj # fix compiler
        #
        if ext.name == 'mpi4py.MPI':
            log.info("checking for MPI compile and link ...")
            ok = config_cmd.try_link(ConfigTest,
                                     headers=['stdlib.h', 'mpi.h'])
            if not ok:
                raise DistutilsPlatformError(
                   "Cannot compile/link MPI programs. "
                   "Check your configuration!!!")
        #
        if ext.name == 'mpi4py.MPE':
            log.info("checking for MPE availability ...")
            ok = (config_cmd.check_header("mpe.h",
                                          headers=["stdlib.h",
                                                   "mpi.h",])
                  and
                  config_cmd.check_func("MPE_Init_log",
                                        headers=["stdlib.h",
                                                 "mpi.h",
                                                 "mpe.h"],
                                        libraries=['mpe'],
                                        decl=0, call=1)
                  )
            if not ok:
                ext.define_macros[:] = []
                ext.libraries[:] = []
                ext.extra_link_args[:] = []
        #
        if ext.name == 'mpi4py.dl':
            log.info("checking for dlopen availability ...")
            ok = config_cmd.check_header("dlfcn.h")
            if not ok :
                ext.define_macros[:] = []
            ok = config_cmd.check_library('dl')
            if not ok:
                ext.libraries[:] = []
        #
        extra_args = config_info.get('extra_compile_args')
        if extra_args:
            ext.extra_compile_args.extend(extra_args)
        extra_args = config_info.get('extra_link_args')
        if extra_args:
            ext.extra_link_args.extend(extra_args)


# -----------------------------------------------------------------------------

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
                                   ('build_base','build_base'))
        from distutils.util import get_platform
        plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
        if hasattr(sys, 'gettotalrefcount') and sys.version[0:3] > '2.5':
            plat_specifier += '-pydebug'
        if self.build_exe is None:
            self.build_exe = os.path.join(self.build_base,
                                          'exe' + plat_specifier)
        self.executables = self.distribution.executables
        # XXX This is a hack
        self.extensions  = self.distribution.executables
        self.check_extensions_list = self.check_executables_list
        self.build_extension = self.build_executable

    def check_executables_list (self, executables):
        ListType = type([])
        if type(executables) is not ListType:
            raise DistutilsSetupError(
                "'executables' option must be a list of Executable instances")
        for exe in executables:
            if not isinstance(exe, Executable):
                raise DistutilsSetupError(
                    "'executables' items must be Executable instances")

    def get_outputs (self):
        exe_extension = sysconfig.get_config_var('EXE') or ''
        outputs = []
        for exe in self.executables:
            exe_filename = os.path.join(self.build_exe, exe.name)
            outputs.append(exe_filename + exe_extension)
        return outputs

    def build_executable (self, exe):
        from distutils.dep_util import newer_group
        ListType, TupleType = type([]), type(())
        sources = exe.sources
        if sources is None or type(sources) not in (ListType, TupleType):
            raise DistutilsSetupError(
                ("in 'executables' option (executable '%s'), " +
                 "'sources' must be present and must be " +
                 "a list of source filenames") % exe.name
                )
        sources = list(sources)
        exe_filename = os.path.join(self.build_exe, exe.name)
        exe_extension = sysconfig.get_config_var('EXE') or ''
        depends = sources + exe.depends
        if not (self.force or
                newer_group(depends, exe_filename+exe_extension, 'newer')):
            log.debug("skipping '%s' executable (up-to-date)", exe.name)
            return
        else:
            log.info("building '%s' executable", exe.name)

        # Next, compile the source code to object files.

        try: # Py2.7+ & Py3.2+
            compiler_obj = self.compiler_obj
        except AttributeError:
            compiler_obj = self.compiler

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
        extra_args = exe.extra_compile_args or []
        extra_args = extra_args[:]

        objects =  compiler_obj.compile(sources,
                                        output_dir=self.build_temp,
                                        macros=macros,
                                        include_dirs=exe.include_dirs,
                                        debug=self.debug,
                                        extra_postargs=extra_args,
                                        depends=exe.depends)

        # XXX -- this is a Vile HACK!
        #
        # The setup.py script for Python on Unix needs to be able to
        # get this list so it can perform all the clean up needed to
        # avoid keeping object files around when cleaning out a failed
        # build of an extension module.  Since Distutils does not
        # track dependencies, we have to get rid of intermediates to
        # ensure all the intermediates will be properly re-built.
        #
        self._built_objects = objects[:]

        # XXX -- this is a Vile HACK!
        #
        # Remove msvcrXX.dll when building executables with MinGW
        #
        if compiler_obj.compiler_type == 'mingw32':
            try: del compiler_obj.dll_libraries[:]
            except: pass

        # Now link the object files together into a "shared object" --
        # of course, first we have to figure out all the other things
        # that go into the mix.
        if exe.extra_objects:
            objects.extend(exe.extra_objects)
        extra_args = exe.extra_link_args or []
        extra_args = extra_args[:]
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
                        ldshflag = ldshflag.replace(fwkdir, fwkpath)
        if sys.platform.startswith('aix'):
            python_lib = sysconfig.get_python_lib(standard_lib=1)
            python_exp = os.path.join(python_lib, 'config', 'python.exp')
            ldshflag = ldshflag.replace('Modules/python.exp', python_exp)
        # Detect target language, if not provided
        language = exe.language or compiler_obj.detect_language(sources)
        compiler_obj.link_executable(
            objects, exe_filename,
            output_dir=None,
            libraries=self.get_libraries(exe),
            library_dirs=exe.library_dirs,
            runtime_library_dirs=exe.runtime_library_dirs,
            extra_preargs=split_quoted(ldshflag),
            extra_postargs=extra_args,
            debug=self.debug,
            target_lang=language)

# -----------------------------------------------------------------------------

class install(cmd_install.install):

    def has_exe (self):
        return self.distribution.has_executables()

    sub_commands = \
        cmd_install.install.sub_commands[:] + \
        [('install_exe', has_exe),
         ]

    # XXX disable install_exe subcommand !!!
    del sub_commands[-1]

# -----------------------------------------------------------------------------

class install_data (cmd_install_data.install_data):

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                   )

# -----------------------------------------------------------------------------

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
        if os.path.isdir(self.build_dir):
            self.outfiles = self.copy_tree(self.build_dir, self.install_dir)
        else:
            self.warn("'%s' does not exist -- no executables to install" %
                      self.build_dir)
            self.outfiles = None

    def get_outputs (self):
        return self.outfiles

    def get_inputs (self):
        inputs = []
        if self.distribution.has_executables():
            build_exe = self.get_finalized_command('build_exe')
            inputs.extend(build_exe.get_outputs())
        return inputs

# -----------------------------------------------------------------------------

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
                              self.bdist_base,
                              self.build_scripts):
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
