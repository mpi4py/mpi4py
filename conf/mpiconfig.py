import sys, os, platform

from distutils.util  import split_quoted
from distutils.spawn import find_executable
from distutils import log as dulog

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

try:
    from configparser import ConfigParser
    from configparser import Error as ConfigParserError
except ImportError:
    from ConfigParser import ConfigParser
    from ConfigParser import Error as ConfigParserError

class Config(object):

    def __init__(self, logger=None):
        self.log = logger or dulog
        self.section  = None
        self.filename = None
        self.compiler_info = OrderedDict((
                ('mpicc'  , None),
                ('mpicxx' , None),
                ('mpifort', None),
                ('mpif90' , None),
                ('mpif77' , None),
                ('mpild'  , None),
                ))
        self.library_info = OrderedDict((
            ('define_macros'        , []),
            ('undef_macros'         , []),
            ('include_dirs'         , []),

            ('libraries'            , []),
            ('library_dirs'         , []),
            ('runtime_library_dirs' , []),

            ('extra_compile_args'   , []),
            ('extra_link_args'      , []),
            ('extra_objects'        , []),
            ))

    def __bool__(self):
        for v in self.compiler_info.values():
            if v:
                return True
        for v in self.library_info.values():
            if v:
                return True
        return False

    __nonzero__ = __bool__

    def get(self, k, d=None):
        if k in self.compiler_info:
            return self.compiler_info[k]
        if k in self.library_info:
            return self.library_info[k]
        return d

    def info(self, log=None):
        if log is None: log = self.log
        mpicc   = self.compiler_info.get('mpicc')
        mpicxx  = self.compiler_info.get('mpicxx')
        mpifort = self.compiler_info.get('mpifort')
        mpif90  = self.compiler_info.get('mpif90')
        mpif77  = self.compiler_info.get('mpif77')
        mpild   = self.compiler_info.get('mpild')
        if mpicc:
            log.info("MPI C compiler:    %s", mpicc)
        if mpicxx:
            log.info("MPI C++ compiler:  %s", mpicxx)
        if mpifort:
            log.info("MPI F compiler:    %s", mpifort)
        if mpif90:
            log.info("MPI F90 compiler:  %s", mpif90)
        if mpif77:
            log.info("MPI F77 compiler:  %s", mpif77)
        if mpild:
            log.info("MPI linker:        %s", mpild)

    def update(self, config, **more):
        if hasattr(config, 'keys'):
            config = config.items()
        for option, value in config:
            if option in self.compiler_info:
                self.compiler_info[option] = value
            if option in self.library_info:
                self.library_info[option] = value
        if more:
            self.update(more)

    def setup(self, options, environ=None):
        if environ is None: environ = os.environ
        self.setup_library_info(options, environ)
        self.setup_compiler_info(options, environ)

    def setup_library_info(self, options, environ):
        filename = section = None
        mpiopt = getattr(options, 'mpi', None)
        mpiopt = environ.get('MPICFG', mpiopt)
        if mpiopt:
            if ',' in mpiopt:
                section, filename = mpiopt.split(',', 1)
            elif os.path.isfile(mpiopt):
                filename = mpiopt
            else:
                section = mpiopt
        if not filename: filename = "mpi.cfg"
        if not section:  section  = "mpi"

        mach = platform.machine()
        arch = platform.architecture()[0]
        plat = sys.platform
        osnm = os.name
        if   'linux' == plat[:5]: plat = 'linux'
        elif 'sunos' == plat[:5]: plat = 'solaris'
        elif 'win'   == plat[:3]: plat = 'windows'
        suffixes = []
        suffixes.append(plat+'-'+mach)
        suffixes.append(plat+'-'+arch)
        suffixes.append(plat)
        suffixes.append(osnm+'-'+mach)
        suffixes.append(osnm+'-'+arch)
        suffixes.append(osnm)
        suffixes.append(mach)
        suffixes.append(arch)
        sections  = [section+"-"+s for s in suffixes]
        sections += [section]
        self.load(filename, sections)
        if not self:
            if os.name == 'posix':
                self._setup_posix()
            if sys.platform == 'win32':
                self._setup_windows()

    def _setup_posix(self):
        pass

    def _setup_windows(self):
        # Microsoft MPI (v7, v6, v5, v4)
        def msmpi_ver():
            try:
                try:
                    import winreg
                except ImportError:
                    import _winreg as winreg
                HKLM = winreg.HKEY_LOCAL_MACHINE
                subkey = "SOFTWARE\Microsoft\MPI"
                with winreg.OpenKey(HKLM, subkey) as key:
                    for i in range(winreg.QueryInfoKey(key)[1]):
                        name, value, type = winreg.EnumValue(key, i)
                        if name != "Version": continue
                        major, minor = value.split('.')[:2]
                        return (int(major), int(minor))
            except: pass
            return (1, 0)
        def setup_msmpi(MSMPI_INC, MSMPI_LIB):
            from os.path import join, isfile
            ok = (MSMPI_INC and isfile(join(MSMPI_INC, 'mpi.h')) and
                  MSMPI_LIB and isfile(join(MSMPI_LIB, 'msmpi.lib')))
            if not ok: return False
            MSMPI_VER = '0x%d%02d' % msmpi_ver()
            MSMPI_INC = os.path.normpath(MSMPI_INC)
            MSMPI_LIB = os.path.normpath(MSMPI_LIB)
            self.library_info.update(
                define_macros=[('MSMPI_VER', MSMPI_VER)],
                include_dirs=[MSMPI_INC],
                library_dirs=[MSMPI_LIB],
                libraries=['msmpi'])
            self.section = 'msmpi'
            self.filename = [os.path.dirname(MSMPI_INC)]
            return True
        arch = platform.architecture()[0][:2]
        # Look for Microsoft MPI in the environment
        MSMPI_INC = os.environ.get('MSMPI_INC')
        MSMPI_LIB = os.environ.get('MSMPI_LIB'+arch)
        if setup_msmpi(MSMPI_INC, MSMPI_LIB): return
        # Look for Microsoft MPI v7/v6/v5 in default install path
        for ProgramFiles in ('ProgramFiles', 'ProgramFiles(x86)'):
            ProgramFiles = os.environ.get(ProgramFiles, '')
            archdir = {'32':'x86', '64':'x64'}[arch]
            MSMPI_DIR = os.path.join(ProgramFiles, 'Microsoft SDKs', 'MPI')
            MSMPI_INC = os.path.join(MSMPI_DIR, 'Include')
            MSMPI_LIB = os.path.join(MSMPI_DIR, 'Lib', archdir)
            if setup_msmpi(MSMPI_INC, MSMPI_LIB): return
        # Look for Microsoft HPC Pack 2012 R2 in default install path
        for ProgramFiles in ('ProgramFiles', 'ProgramFiles(x86)'):
            ProgramFiles = os.environ.get(ProgramFiles, '')
            archdir = {'32':'i386', '64':'amd64'}[arch]
            MSMPI_DIR = os.path.join(ProgramFiles, 'Microsoft MPI')
            MSMPI_INC = os.path.join(MSMPI_DIR, 'Inc')
            MSMPI_LIB = os.path.join(MSMPI_DIR, 'Lib', archdir)
            if setup_msmpi(MSMPI_INC, MSMPI_LIB): return

        # Microsoft MPI (legacy) and others
        from glob import glob
        ProgramFiles = os.environ.get('ProgramFiles', '')
        CCP_HOME = os.environ.get('CCP_HOME', '')
        for (name, prefix, suffix) in (
            ('msmpi',    CCP_HOME,     ''),
            ('msmpi',    ProgramFiles, 'Microsoft HPC Pack 2012 R2'),
            ('msmpi',    ProgramFiles, 'Microsoft HPC Pack 2012'),
            ('msmpi',    ProgramFiles, 'Microsoft HPC Pack 2012 SDK'),
            ('msmpi',    ProgramFiles, 'Microsoft HPC Pack 2008 R2'),
            ('msmpi',    ProgramFiles, 'Microsoft HPC Pack 2008'),
            ('msmpi',    ProgramFiles, 'Microsoft HPC Pack 2008 SDK'),
            ):
            mpi_dir = os.path.join(prefix, suffix)
            if not mpi_dir or not os.path.isdir(mpi_dir): continue
            define_macros = []
            include_dir = os.path.join(mpi_dir, 'include')
            library = 'mpi'
            library_dir = os.path.join(mpi_dir, 'lib')
            if name == 'msmpi':
                include_dir = os.path.join(mpi_dir, 'inc')
                library = 'msmpi'
                arch = platform.architecture()[0]
                if arch == '32bit':
                    library_dir = os.path.join(library_dir, 'i386')
                if arch == '64bit':
                    library_dir = os.path.join(library_dir, 'amd64')
                if not os.path.isdir(include_dir):
                    include_dir = os.path.join(mpi_dir, 'include')
            self.library_info.update(
                define_macros=define_macros,
                include_dirs=[include_dir],
                libraries=[library],
                library_dirs=[library_dir],
                )
            self.section = name
            self.filename = [mpi_dir]
            break


    def setup_compiler_info(self, options, environ):
        def find_exe(cmd, path=None):
            if not cmd: return None
            parts = split_quoted(cmd)
            exe, args = parts[0], parts[1:]
            if not os.path.isabs(exe) and path:
                exe = os.path.basename(exe)
            exe = find_executable(exe, path)
            if not exe: return None
            return ' '.join([exe]+args)
        COMPILERS = (
            ('mpicc',   ['mpicc',   'mpcc_r']),
            ('mpicxx',  ['mpicxx',  'mpic++', 'mpiCC', 'mpCC_r']),
            ('mpifort', ['mpifort', 'mpif90', 'mpif77', 'mpfort_r']),
            ('mpif90',  ['mpif90',  'mpf90_r']),
            ('mpif77',  ['mpif77',  'mpf77_r']),
            ('mpild',   []),
            )
        #
        compiler_info = {}
        PATH = environ.get('PATH', '')
        for name, _ in COMPILERS:
            cmd = (environ.get(name.upper()) or
                   getattr(options, name, None) or
                   self.compiler_info.get(name) or
                   None)
            if cmd:
                exe = find_exe(cmd, path=PATH)
                if exe:
                    path = os.path.dirname(exe)
                    PATH = path + os.path.pathsep + PATH
                    compiler_info[name] = exe
                else:
                    self.log.error("error: '%s' not found", cmd)
        #
        if not self and not compiler_info:
            for name, candidates in COMPILERS:
                for cmd in candidates:
                    cmd = find_exe(cmd)
                    if cmd:
                        compiler_info[name] = cmd
                        break
        #
        self.compiler_info.update(compiler_info)


    def load(self, filename="mpi.cfg", section='mpi'):
        if isinstance(filename, str):
            filenames = filename.split(os.path.pathsep)
        else:
            filenames = list(filename)
        if isinstance(section, str):
            sections = section.split(',')
        else:
            sections = list(section)
        #
        try:
            parser = ConfigParser(dict_type=OrderedDict)
        except TypeError:
            parser = ConfigParser()
        try:
            read_ok = parser.read(filenames)
        except ConfigParserError:
            self.log.error(
                "error: parsing configuration file/s '%s'",
                os.path.pathsep.join(filenames))
            return None
        for section in sections:
            if parser.has_section(section):
                break
            section = None
        if not section:
            self.log.error(
                "error: section/s '%s' not found in file/s '%s'",
                ','.join(sections), os.path.pathsep.join(filenames))
            return None
        parser_items = list(parser.items(section, vars=None))
        #
        compiler_info = type(self.compiler_info)()
        for option, value in parser_items:
            if option in self.compiler_info:
                compiler_info[option] = value
        #
        pathsep = os.path.pathsep
        expanduser = os.path.expanduser
        expandvars = os.path.expandvars
        library_info = type(self.library_info)()
        for k, v in parser_items:
            if k in ('define_macros',
                     'undef_macros',
                     ):
                macros = [e.strip() for e in v.split(',')]
                if k == 'define_macros':
                    for i, m in enumerate(macros):
                        try: # -DFOO=bar
                            idx = m.index('=')
                            macro = (m[:idx], m[idx+1:] or None)
                        except ValueError: # -DFOO
                            macro = (m, None)
                        macros[i] = macro
                library_info[k] = macros
            elif k in ('include_dirs',
                       'library_dirs',
                       'runtime_dirs',
                       'runtime_library_dirs',
                       ):
                if k == 'runtime_dirs': k = 'runtime_library_dirs'
                pathlist = [p.strip() for p in v.split(pathsep)]
                library_info[k] = [expanduser(expandvars(p))
                                   for p in pathlist if p]
            elif k == 'libraries':
                library_info[k] = [e.strip() for e in split_quoted(v)]
            elif k in ('extra_compile_args',
                       'extra_link_args',
                       ):
                library_info[k] = split_quoted(v)
            elif k == 'extra_objects':
                library_info[k] = [expanduser(expandvars(e))
                                   for e in split_quoted(v)]
            elif hasattr(self, k):
                library_info[k] = v.strip()
            else:
                pass
        #
        self.section = section
        self.filename = read_ok
        self.compiler_info.update(compiler_info)
        self.library_info.update(library_info)
        return compiler_info, library_info, section, read_ok

    def dump(self, filename=None, section='mpi'):
        # prepare configuration values
        compiler_info   = self.compiler_info.copy()
        library_info = self.library_info.copy()
        for k in library_info:
            if k in ('define_macros',
                     'undef_macros',
                     ):
                macros = library_info[k]
                if k == 'define_macros':
                    for i, (m, v) in enumerate(macros):
                        if v is None:
                            macros[i] = m
                        else:
                            macros[i] = '%s=%s' % (m, v)
                library_info[k] = ','.join(macros)
            elif k in ('include_dirs',
                       'library_dirs',
                       'runtime_library_dirs',
                       ):
                library_info[k] = os.path.pathsep.join(library_info[k])
            elif isinstance(library_info[k], list):
                library_info[k] = ' '.join(library_info[k])
        # fill configuration parser
        try:
            parser = ConfigParser(dict_type=OrderedDict)
        except TypeError:
            parser = ConfigParser()
        parser.add_section(section)
        for option, value in compiler_info.items():
            if not value: continue
            parser.set(section, option, value)
        for option, value in library_info.items():
            if not value: continue
            parser.set(section, option, value)
        # save configuration file
        if filename is None:
            parser.write(sys.stdout)
        elif hasattr(filename, 'write'):
            parser.write(filename)
        elif isinstance(filename, str):
            with open(filename, 'w') as f:
                parser.write(f)
        return parser


if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("--mpi",     type="string")
    parser.add_option("--mpicc",   type="string")
    parser.add_option("--mpicxx",  type="string")
    parser.add_option("--mpifort", type="string")
    parser.add_option("--mpif90",  type="string")
    parser.add_option("--mpif77",  type="string")
    parser.add_option("--mpild",   type="string")
    (opts, args) = parser.parse_args()

    log = dulog.Log(dulog.INFO)
    cfg = Config(log)
    cfg.setup(opts)
    cfg.dump()
