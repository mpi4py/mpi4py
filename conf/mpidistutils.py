# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
# Id:      $Id$

"""
Support for building mpi4py with distutils.
"""

# --------------------------------------------------------

# Environmental variables to look for configuration
MPICC_ENV  = ['MPICC']
MPICXX_ENV = ['MPICXX']
MPICFG_ENV = ['MPI_CFG']

# Default values to use for configuration
MPICC  = ['mpicc']
MPICXX = ['mpicxx', 'mpiCC', 'mpic++']
MPICFG = ('mpi', 'mpi.cfg')

# --------------------------------------------------------

import sys, os
from distutils import sysconfig
from distutils.spawn import find_executable
from distutils import log


def customize_compiler(compiler, environ=None):
    """
    Do any platform-specific customization of a CCompiler instance.

    Mainly needed on Unix, so we can plug in the information that
    varies across Unices and is stored in Python's Makefile.
    """
    from distutils.sysconfig import get_config_vars
    if environ is None:
        environ = os.environ

    if compiler.compiler_type == 'unix':
        (cc, cxx, opt,
         basecflags, cflags, ccshared,
         ldshared, so_ext) = \
            get_config_vars('CC', 'CXX',
                            'BASECFLAGS', 'OPT', 'CFLAGS',
                            'CCSHARED', 'LDSHARED', 'SO')

        if 'CC' in environ:
            cc = environ['CC']
        if 'CXX' in environ:
            cxx = environ['CXX']
        if 'LDSHARED' in environ:
            ldshared = environ['LDSHARED']
        if 'CPP' in environ:
            cpp = environ['CPP']
        else:
            cpp = cc + " -E"           # not always
        if 'LDFLAGS' in environ:
            ldshared = ldshared + ' ' + environ['LDFLAGS']
        if 'CFLAGS' in environ:
            cflags = basecflags + ' ' + opt + ' ' + environ['CFLAGS']
            ldshared = ldshared + ' ' + environ['CFLAGS']
        if 'CPPFLAGS' in environ:
            cpp = cpp + ' ' + environ['CPPFLAGS']
            cflags = cflags + ' ' + environ['CPPFLAGS']
            ldshared = ldshared + ' ' + environ['CPPFLAGS']

        cc_cmd = cc + ' ' + cflags
        compiler.set_executables(
            preprocessor=cpp,
            compiler=cc_cmd,
            compiler_so=cc_cmd + ' ' + ccshared,
            compiler_cxx=cxx,
            linker_so=ldshared,
            linker_exe=cc)

        compiler.shared_lib_extension = so_ext

def customize_mpi_environ(mpicc, mpicxx=None, environ=None):
    """
    Replace normal compilers with MPI compilers
    """
    if environ is None:
        environ = dict(os.environ)
    if mpicc: # C compiler
        environ['CC'] = mpicc
    if mpicxx: # C++ compiler
        environ['CXX'] = mpicxx
    mpild = mpicc or mpicxx
    if mpild: # linker for shared
        ldshared = sysconfig.get_config_var('LDSHARED')
        if not ldshared:
            environ['LDSHARED'] = mpild
        else:
            if sys.platform.startswith('aix') \
                   and 'ld_so_aix' in ldshared:
                ldshared = ldshared.split(' ', 2)
            else:
                ldshared = ldshared.split(' ', 1)
            if len(ldshared) == 1: # just linker, no flags
                environ['LDSHARED'] = mpild
            elif len(ldshared) == 2: # linker and flags
                environ['LDSHARED'] = mpild + ' ' + ldshared[1]
            else: # assume using special linker script
                environ['LDSHARED'] = ldshared[0] + ' '  + \
                                      mpild       + ' '  + \
                                      ldshared[2]
    return environ

def _find_mpi_compiler(envvars, executables, path=None):
    """
    Find MPI compilers in environment and path.
    """
    # search in environment
    if envvars:
        if isinstance(envvars, str):
            envvars = (envvars,)
        for var in envvars:
            cmd = os.environ.get(var)
            if cmd is not None: return cmd
    # search in path
    if executables:
        if isinstance(executables, str):
            executables = (executables,)
        for exe in executables:
            try:
                cmd, args = exe.split(' ', 1)
            except ValueError:
                cmd, args = exe, None
            cmd = find_executable(cmd, path)
            if cmd is not None:
                if args is not None:
                    cmd = cmd + ' ' + args
                return cmd
    # nothing found
    return None


# --------------------------------------------------------

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
        parser.read(filenames.split(','))
    except ConfigParserError:
        log.error("error: parsing configuration file/s '%s'", filenames)
        return None
    if not parser.has_section(section):
        log.error("error: section '%s' not found "
                  "in configuration file/s '%s'", section, filenames)
        return None
    config_info = {}
    for k, v in parser.items(section, raw, vars):
        if k in ('define_macros',
                 'undef_macros',):
            config_info[k] = [m.strip() for m in v.split()]
        elif k in ('include_dirs',
                   'library_dirs',
                   'runtime_library_dirs',):
            pathsep = os.path.pathsep
            config_info[k] = [p.strip() for p in v.split(pathsep)]
        elif k == 'libraries':
            config_info[k] = [l.strip() for l in v.split()]
        elif k in ('extra_compile_args',
                   'extra_link_args',
                   'extra_objects',):
            config_info[k] = [e.strip() for e in v.split()]
        else:
            config_info[k] = v.strip()
        #config_info[k] = v.replace('\\',' ').split()
    if 'define_macros' in config_info:
        macros = []
        for m in config_info['define_macros'] :
            try: # "-DFOO=blah"
                idx = m.index("=")
                macro = (m[:idx], m[idx+1:] or None)
            except ValueError: # bare "-DFOO"
                macro = (m, None)
            macros.append(macro)
        config_info['define_macros'] = macros
    return config_info


def _find_mpi_config(section, filenames,
                     envvars=None, defaults=None):
    if not section and not filenames and envvars:
        # look in environment
        if isinstance(envvars, str):
            envvars = (envvars,)
        for var in envvars:
            if var in os.environ:
                section, filenames = os.environ[var], None
                break
    if section and ',' in section:
        section, filenames = section.split(',', 1)
    if defaults:
        if not section:
            section = defaults[0]
        if not filenames:
            fname = defaults[1]
            if os.path.exists(fname):
                filenames = fname
    # parse configuraration
    if section and filenames:
        config_info = _config_parser(section, filenames)
        return section, filenames, config_info
    else:
        return section, filenames, None


def _configure(extension, confdict):
    if confdict is None: return
    for key, value in confdict.items():
        if hasattr(extension, key):
            item = getattr(extension, key)
            if type(item) is list:
                if type(value) is list:
                    for v in value:
                        if v not in item:
                            item.append(v)
                else:
                    if value not in item:
                        item.append(value)
            else:
                setattr(extension, key, value)

# --------------------------------------------------------

from distutils.command import config as cmd_config
from distutils.command import build as cmd_build
from distutils.command import build_ext as cmd_build_ext
from distutils.command import install_data as cmd_install_data
from distutils.command import sdist as cmd_sdist

from distutils.errors import DistutilsPlatformError
from distutils.errors import DistutilsOptionError


ConfigTest = """\
int main(int argc, char **argv) {
  MPI_Init(&argc,&argv);
  MPI_Finalize();
  return 0;
}
"""

try: from mpiscanner import Scanner
except ImportError: Scanner = object
class Configure(Scanner):
    SRCDIR = os.path.join('src', 'mpi4py')
    SOURCES = [os.path.join('include', 'mpi4py', 'mpi.pxi')]
    DESTDIR = os.path.join('src')
    CONFIG_H = 'config.h'
    MISSING_H = 'missing.h'
    def __init__(self):
        Scanner.__init__(self)
        for filename in self.SOURCES:
            fullname = os.path.join(self.SRCDIR, filename)
            self.parse_file(fullname)

    def write_headers(self, results, config_h=None, missing_h=None):
        if config_h is None:
            config_h = os.path.join(self.DESTDIR, self.CONFIG_H)
        if missing_h is None:
            missing_h = os.path.join(self.DESTDIR, self.MISSING_H)
        log.info("writing '%s'" % config_h)
        self.dump_config_h(config_h, results)
        log.info("writing '%s'" % missing_h)
        self.dump_missing_h(missing_h, None)


cmd_mpi_opts = [

    ('mpicc=',   None,
     "MPI C compiler command, "
     "overrides environmental variables 'MPICC' "
     "(defaults to 'mpicc' if available)"),

    ('mpicxx=',  None,
     "MPI C++ compiler command, "
     "overrides environmental variables 'MPICXX' "
     "(defaults to 'mpicxx', 'mpiCC', or 'mpic++' if any is available)"),

    ('mpi=',     None,
     "specify a configuration section, "
     "and an optional comma-separated list of configuration files "
     "(e.g. --mpi=section,file1,file2,file3),"
     "to look for MPI includes/libraries, "
     "overrides environmental variables 'MPICFG' "
     "(defaults to section 'mpi' in configuration file 'mpi.cfg')"),

    ('mpi-cfg=', None,
     "specify a configuration file to look for MPI includes/libraries "
     "(defaults to 'mpi.cfg')"),

    ('try-mpi-2', None,
     "test for availability of MPI 2 features"),

    ('thread-level=', None,
     "initialize MPI with support for threads"),

    ]

def _cmd_opts_names(cmd_opts):
    optlist = []
    for (option, _, _) in cmd_opts:
        if option[-1] == "=":
            option = option[:-1]
        option = option.replace('-','_')
        optlist.append(option)
    return optlist

def _thread_level(thread_level):
    if not thread_level:
        return None
    thread_level = thread_level.lower()
    if thread_level == 'none':
        return None
    valid_levels = ['single', 'funneled', 'serialized', 'multiple']
    if thread_level not in valid_levels:
        raise DistutilsOptionError(
            ("thread-level must be one of " + ','.join(valid_levels))
            )
    return thread_level


class config(cmd_config.config):

    user_options = cmd_config.config.user_options + cmd_mpi_opts

    def initialize_options(self):
        cmd_config.config.initialize_options(self)
        self.noisy = 0
        mpiopts = _cmd_opts_names(cmd_mpi_opts)
        for op in mpiopts:
            setattr(self, op, None)

    def finalize_options(self):
        cmd_config.config.finalize_options(self)
        if not self.noisy:
            self.dump_source = 0
        self.thread_level = _thread_level(self.thread_level)

    def find_mpi_compiler(self, envvars, executables, path=None):
        return _find_mpi_compiler(envvars, executables, path)

    def run(self):
        # test configuration in specified section and file
        if self.mpi or self.mpi_cfg:
            sct, fn, cfg = _find_mpi_config(self.mpi, self.mpi_cfg,
                                            MPICFG_ENV, MPICFG)
            log.info("MPI configuration: "
                     "section '%s' from file/s '%s'", sct, fn)
            _configure(self, cfg)
        # test MPI C compiler
        mpicc = self.mpicc
        if mpicc is None:
            mpicc = self.find_mpi_compiler(MPICC_ENV, MPICC)
        if mpicc:
            log.info("MPI C compiler:    %s", mpicc  or 'not found')
            self.compiler = None
            self._check_compiler()
            environ = customize_mpi_environ(mpicc, None)
            customize_compiler(self.compiler, environ)
            self.try_link(ConfigTest, headers=['mpi.h'], lang='c')
        # test MPI C++ compiler
        mpicxx = self.mpicxx
        if mpicxx is None:
            mpicxx = self.find_mpi_compiler(MPICXX_ENV, MPICXX)
        if mpicxx:
            log.info("MPI C++ compiler:  %s", mpicxx or 'not found')
            self.compiler = None
            self._check_compiler()
            environ = customize_mpi_environ(None, mpicxx)
            customize_compiler(self.compiler, environ)
            if self.compiler.compiler_type in ('unix', 'cygwin', 'mingw32'):
                self.compiler.compiler_so[0] = mpicxx
                self.compiler.linker_exe[0] = mpicxx
            self.try_link(ConfigTest, headers=['mpi.h'], lang='c++')
        # and now some MPI specific stuff
        return # XXX for the future
        macro = None
        if   self.check_macro('MPICH_NAME'): macro = 'MPICH_SKIP_MPICXX'
        elif self.check_macro('OPEN_MPI'):   macro = 'OMPI_SKIP_MPICXX'
        elif self.check_macro('LAM_MPI'):    macro = 'MPIPP_H'
        if macro:
            log.info("defining preprocessor macro '%s'" % macro)
            self.compiler.define_macro(macro, None)


    def configure(self, compiler, config_info):
        self.compiler = compiler
        _configure(self, config_info)
        configure = Configure()
        results = []
        for name, code in configure.itertests():
            ok = self.check_configtest(code)
            results.append((name, ok))
        return configure.write_headers(results)

    def check_macro(self, macro, lang='c'):
        body = ['#ifndef %s' %macro,
                '#error "macro %s not defined"' % macro,
                '#endif']
        body = '\n'.join(body) + '\n'
        return self.try_compile(body, headers=['mpi.h'], lang=lang,
                                include_dirs=self.include_dirs)

    def check_configtest(self, code, lang='c'):
        body = ['int main(void) {'
                '  %s' % code,
                '  return 0;',
                '}']
        body = '\n'.join(body) + '\n'
        return self.try_link(body, headers=['mpi.h'], lang=lang,
                             include_dirs=self.include_dirs)


class build(cmd_build.build):

    user_options = cmd_build.build.user_options + cmd_mpi_opts

    def initialize_options(self):
        cmd_build.build.initialize_options(self)
        mpiopts = _cmd_opts_names(cmd_mpi_opts)
        for op in mpiopts:
            setattr(self, op, None)

    def finalize_options(self):
        cmd_build.build.finalize_options(self)
        config_cmd = self.get_finalized_command('config')
        if isinstance(config_cmd,  config):
            mpiopts = _cmd_opts_names(cmd_mpi_opts)
            optlist = tuple(zip(mpiopts, mpiopts))
            self.set_undefined_options('config', *optlist)
        self.thread_level = _thread_level(self.thread_level)


class build_ext(cmd_build_ext.build_ext):

    user_options = cmd_build_ext.build_ext.user_options + cmd_mpi_opts

    def initialize_options(self):
        cmd_build_ext.build_ext.initialize_options(self)
        mpiopts = _cmd_opts_names(cmd_mpi_opts)
        for op in mpiopts:
            setattr(self, op, None)

    def finalize_options(self):
        cmd_build_ext.build_ext.finalize_options(self)
        import sys, os
        if (sys.platform.startswith('linux') or \
            sys.platform.startswith('gnu')) and \
            sysconfig.get_config_var('Py_ENABLE_SHARED'):
            try:
                py_version = sysconfig.get_python_version()
                bad_pylib_dir = os.path.join(sys.prefix, "lib",
                                             "python" + py_version,
                                             "config")
                self.library_dirs.remove(bad_pylib_dir)
            except ValueError:
                pass
            pylib_dir = sysconfig.get_config_var("LIBDIR")
            if pylib_dir not in self.library_dirs:
                self.library_dirs.append(pylib_dir)
        build_cmd = self.get_finalized_command('build')
        if isinstance(build_cmd,  build):
            mpiopts = _cmd_opts_names(cmd_mpi_opts)
            optlist = tuple(zip(mpiopts, mpiopts))
            self.set_undefined_options('build', *optlist)
        self.thread_level = _thread_level(self.thread_level)

    def build_extensions(self):
        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)
        # parse configuration file and  configure compiler
        config_info = self.configure_extensions()
        mpicc = mpicxx = None
        if config_info:
            mpicc = config_info.get('mpicc')
            mpicxx = config_info.get('mpicxx')
        compiler = self.configure_compiler(mpicc=mpicc, mpicxx=mpicxx)
        # extra configuration, MPI 2 features
        if self.try_mpi_2:
            log.info('testing for missing MPI-2 features')
            config_cmd = self.get_finalized_command('config')
            config_cmd.configure(compiler, config_info)
            macro = 'PyMPI_HAVE_CONFIG_H'
            self.compiler.define_macro(macro, None)
            log.info("defining preprocessor macro '%s'" % macro)
        # extra configuration, MPI thread level support
        if self.thread_level:
            levels = ['single', 'funneled', 'serialized', 'multiple']
            mname = 'PyMPI_MPI_THREAD_LEVEL'
            value = levels.index(self.thread_level)
            self.compiler.define_macro(mname, value)
            log.info("defining preprocessor macro '%s=%d'" % (mname, value))
        # and finally build extensions
        for ext in self.extensions:
            self.build_extension(ext)

    def configure_compiler(self, compiler=None, mpicc=None, mpicxx=None):
        mpicc, mpicxx = self.mpicc or mpicc, self.mpicxx or mpicxx
        if mpicc is None:
            mpicc = self.find_mpi_compiler(MPICC_ENV, MPICC)
        if mpicxx is None:
            mpicxx = self.find_mpi_compiler(MPICXX_ENV, MPICXX)
        if compiler is None:
            compiler = self.compiler
        log.info("MPI C compiler:    %s", mpicc  or 'not found')
        log.info("MPI C++ compiler:  %s", mpicxx or 'not found')
        environ = customize_mpi_environ(mpicc, mpicxx)
        customize_compiler(compiler, environ)
        return compiler

    def find_mpi_compiler(self, envvars, executables, path=None):
        return _find_mpi_compiler(envvars, executables, path)

    def configure_extensions(self):
        config_info = self.find_mpi_config(self.mpi, self.mpi_cfg,
                                           MPICFG_ENV, MPICFG)
        if config_info:
            for ext in self.extensions:
                self.configure_extension(ext, config_info)
        return config_info

    def find_mpi_config(self, section, filenames,
                        envvars=None, defaults=None):
        # parse configuration file
        sect, fnames, cfg_info = _find_mpi_config(section, filenames,
                                                  envvars, defaults)
        if cfg_info:
            log.info("MPI configuration: "
                     "from section '%s' in file/s '%s'", sect, fnames)
        return cfg_info

    def configure_extension(self, extension, config_info):
        _configure(extension, config_info)


class install_data (cmd_install_data.install_data):

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                   )

# --------------------------------------------------------

from distutils.core import Distribution as cls_Distribution
from distutils.extension import Extension
from distutils.core import Command

from distutils.command import install_lib as cmd_install_lib

# Distribution class supporting a 'executables' keyword

class Distribution(cls_Distribution):

    def __init__ (self, attrs=None):
        # PEP 314
        self.provides = None
        self.requires = None
        self.obsoletes = None
        # supports 'executables' keyword
        self.executables = None
        cls_Distribution.__init__(self, attrs)

    def has_executables(self):
        return self.executables and len(self.executables) > 0


# Executable class

class Executable(Extension):

    pass


# Command class to build executables

_build_ext = build_ext

class build_exe(_build_ext):

    description = "build binary executable components"

    user_options = [
        ('build-exe=', None,
         "build directory for executable components"),
        ] + _build_ext.user_options


    def initialize_options (self):
        _build_ext.initialize_options(self)
        self.build_base = None
        self.build_exe  = None

    def finalize_options (self):
        _build_ext.finalize_options(self)
        self.try_mpi_2 = None
        self.set_undefined_options('build',
                                   ('build_base','build_base'))
        from distutils.util import get_platform
        plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
        if self.build_exe is None:
            self.build_exe = os.path.join(self.build_base,
                                          'exe' + plat_specifier)
        # a bit of hack
        self.executables = self.distribution.executables
        self.extensions  = self.distribution.executables

    def get_exe_filename (self, exe_name):
        import string
        exe_path = string.split(exe_name, '.')
        # OS/2 has an 8 character module (extension) limit :-(
        if os.name == "os2":
            exe_path[len(exe_path) - 1] = exe_path[len(exe_path) - 1][:8]
        return apply(os.path.join, exe_path) + sysconfig.get_config_var('EXE')

    def get_ext_filename (self, ext_name):
        return self.get_exe_filename(ext_name)


    def build_extension (self, ext):
        from types import ListType, TupleType
        from distutils.dep_util import newer_group
        sources = ext.sources
        if sources is None or type(sources) not in (ListType, TupleType):
            raise DistutilsSetupError(
                ("in 'executable' option (extension '%s'), " +
                 "'sources' must be present and must be " +
                 "a list of source filenames") % ext.name
                )
        sources = list(sources)
        fullname = self.get_ext_fullname(ext.name)
        ext_filename = os.path.join(self.build_exe,
                                    self.get_ext_filename(fullname))
        depends = sources + ext.depends
        if not (self.force or newer_group(depends, ext_filename, 'newer')):
            log.debug("skipping '%s' executable (up-to-date)", ext.name)
            return
        else:
            log.info("building '%s' executable", ext.name)

        # Next, compile the source code to object files.

        # XXX not honouring 'define_macros' or 'undef_macros' -- the
        # CCompiler API needs to change to accommodate this, and I
        # want to do one thing at a time!

        # Two possible sources for extra compiler arguments:
        #   - 'extra_compile_args' in Extension object
        #   - CFLAGS environment variable (not particularly
        #     elegant, but people seem to expect it and I
        #     guess it's useful)
        # The environment variable should take precedence, and
        # any sensible compiler will give precedence to later
        # command line args.  Hence we combine them in order:
        extra_args = ext.extra_compile_args or []
        extra_args = extra_args[:]

        macros = ext.define_macros[:]
        for undef in ext.undef_macros:
            macros.append((undef,))

        objects = self.compiler.compile(sources,
                                        output_dir=self.build_temp,
                                        macros=macros,
                                        include_dirs=ext.include_dirs,
                                        debug=self.debug,
                                        extra_postargs=extra_args,
                                        depends=ext.depends)

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

        # Now link the object files together into a "shared object" --
        # of course, first we have to figure out all the other things
        # that go into the mix.
        if ext.extra_objects:
            objects.extend(ext.extra_objects)
        extra_args = ext.extra_link_args or []
        extra_args = extra_args[:]
        # Get special linker flags for building a executable with
        # bundled Python library, also fix location of needed
        # python.exp file on AIX
        ldshflag = sysconfig.get_config_var('LINKFORSHARED') or ''
        if sys.platform.startswith('aix'):
            python_lib = sysconfig.get_python_lib(standard_lib=1)
            python_exp = os.path.join(python_lib, 'config', 'python.exp')
            ldshflag = ldshflag.replace('Modules/python.exp', python_exp)
        extra_args.extend(ldshflag.split())
        # Detect target language, if not provided
        language = ext.language or self.compiler.detect_language(sources)
        self.compiler.link_executable(
            objects, ext_filename,
            output_dir=None,
            libraries=self.get_libraries(ext),
            library_dirs=ext.library_dirs,
            runtime_library_dirs=ext.runtime_library_dirs,
            extra_preargs=None,
            extra_postargs=extra_args,
            debug=self.debug,
            target_lang=language)


# Command class to install executables

class install_exe(cmd_install_lib.install_lib):

    description = "install binary executable components"

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('force', 'force'),
                                   ('skip_build', 'skip_build'))
        self.set_undefined_options('build_exe',
                                   ('build_exe', 'build_dir'))
        if os.name == 'posix':
            bindir = 'install_scripts'
        else:
            bindir = 'install_data'
        self.set_undefined_options('install',
                                   (bindir, 'install_dir'))

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
            self.warn("'%s' does not exist -- no executable to install" %
                      self.build_dir)
            self.outfiles = None

    def get_outputs (self):
        return self.outfiles


# Command class to clean executable

class clean_exe(Command):

    description = "clean up output of 'build_exe' command"

    user_options = [
        ('build-base=', 'b',
         "base build directory (default: 'build.build-base')"),
        ('build-exe=', None,
         "build directory for executable components "
         "(default: 'build_exe.build-exe')"),
        ('all', 'a',
         "remove all build output, not just temporary by-products")
        ]

    boolean_options = ['all']

    def initialize_options(self):
        self.build_base = None
        self.build_exe  = None
        self.all        = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'))
        self.set_undefined_options('build_exe',
                                   ('build_exe', 'build_exe'))
        self.set_undefined_options('clean',
                                   ('all', 'all'))

    def run (self):
        from distutils.dir_util import remove_tree
        if self.all:
            directory = self.build_exe
            if os.path.exists(directory):
                remove_tree(directory, dry_run=self.dry_run)
            else:
                log.warn("'%s' does not exist -- can't clean it",
                         directory)

# --------------------------------------------------------
