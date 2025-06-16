import logging
import os
import platform
import shlex
import shutil
import sys
from collections import OrderedDict
from configparser import ConfigParser, Error as ConfigParserError
from types import SimpleNamespace

# ruff: noqa: PTH112, PTH113, PTH117, PTH118, PTH119
# ruff: noqa: PTH120, PTH123

_logger = logging.getLogger("mpiconfig")
_logger.setLevel(logging.INFO)

# ruff: noqa: G010
_log = SimpleNamespace()
_log.log = _logger.log
_log.debug = _logger.debug
_log.info = _logger.info
_log.warn = _logger.warning
_log.error = _logger.error
_log.fatal = _logger.fatal


class Config:
    def __init__(self, log=None):
        self.log = log or _log
        self.section = None
        self.filename = None
        self.compiler_info = OrderedDict((
            ("mpicc", None),
            ("mpicxx", None),
            ("mpild", None),
        ))
        self.library_info = OrderedDict((
            ("define_macros", []),
            ("undef_macros", []),
            ("include_dirs", []),
            ("libraries", []),
            ("library_dirs", []),
            ("runtime_library_dirs", []),
            ("extra_compile_args", []),
            ("extra_link_args", []),
            ("extra_objects", []),
        ))

    def __bool__(self):
        for v in self.compiler_info.values():
            if v:
                return True
        for v in self.library_info.values():
            if v:
                return True
        return False

    def get(self, k, d=None):
        if k in self.compiler_info:
            return self.compiler_info[k]
        if k in self.library_info:
            return self.library_info[k]
        return d

    def info(self, log=None):
        if log is None:
            log = self.log
        mpicc = self.compiler_info.get("mpicc")
        mpicxx = self.compiler_info.get("mpicxx")
        mpild = self.compiler_info.get("mpild")
        if mpicc:
            log.info("MPI C compiler:    %s", mpicc)
        if mpicxx:
            log.info("MPI C++ compiler:  %s", mpicxx)
        if mpild:
            log.info("MPI linker:        %s", mpild)

    def update(self, config, **more):
        if hasattr(config, "keys"):
            config = config.items()
        for option, value in config:
            if option in self.compiler_info:
                self.compiler_info[option] = value
            if option in self.library_info:
                self.library_info[option] = value
        if more:
            self.update(more)

    def setup(self, options, environ=None):
        if environ is None:
            environ = os.environ
        self.setup_library_info(options, environ)
        self.setup_compiler_info(options, environ)

    def setup_library_info(self, options, environ):
        filename = section = None
        mpiopt = getattr(options, "mpi", None)
        mpiopt = environ.get("MPICFG", mpiopt)
        mpiopt = environ.get("MPI4PY_BUILD_MPICFG", mpiopt)
        if mpiopt:
            if "," in mpiopt:
                section, filename = mpiopt.split(",", 1)
            elif ":" in mpiopt:
                filename, section = mpiopt.split(":", 1)
            elif os.path.isfile(mpiopt):
                filename = mpiopt
            else:
                section = mpiopt
        if not filename:
            filename = "mpi.cfg"
        if not section:
            section = "mpi"

        mach = platform.machine()
        arch = platform.architecture(None)[0]
        plat = sys.platform
        osnm = os.name
        if plat.startswith("linux"):
            plat = "linux"
        elif plat.startswith("sunos"):
            plat = "solaris"
        elif plat.startswith("win"):
            plat = "windows"
        suffixes = []
        suffixes.extend((
            plat + "-" + mach,
            plat + "-" + arch,
            plat,
            osnm + "-" + mach,
            osnm + "-" + arch,
            osnm,
            mach,
            arch,
        ))
        sections = [section + "-" + s for s in suffixes]
        sections += [section]
        self.load(filename, sections)
        if not self:
            self._setup_mpiabi()
        if not self:
            if os.name == "posix":
                self._setup_posix()
            if sys.platform == "win32":
                self._setup_windows()

    def _setup_mpiabi(self):
        MPI_ABI_STUBS = os.environ.get("MPI_ABI_STUBS")
        if MPI_ABI_STUBS:
            self.load("mpi.cfg", "mpiabi")
            self.filename = [MPI_ABI_STUBS]

    def _setup_posix(self):
        pass

    def _setup_windows(self):
        if self._setup_windows_impi():
            return
        if self._setup_windows_msmpi():
            return

    def _setup_windows_impi(self):
        I_MPI_ROOT = os.environ.get("I_MPI_ROOT")
        if not I_MPI_ROOT:
            return None
        IMPI_INC = os.path.join(I_MPI_ROOT, "include")
        IMPI_LIB = os.path.join(I_MPI_ROOT, "lib")
        kind = os.environ.get("I_MPI_LIBRARY_KIND") or "release"
        for subdirs in (("mpi", kind), (kind,)):
            if os.path.isdir(os.path.join(IMPI_LIB, *subdirs)):
                IMPI_LIB = os.path.join(IMPI_LIB, *subdirs)
                break
        ok = (
            os.path.isdir(I_MPI_ROOT)
            and os.path.isfile(os.path.join(IMPI_INC, "mpi.h"))
            and os.path.isfile(os.path.join(IMPI_LIB, "impi.lib"))
        )
        if not ok:
            return False
        IMPI_INC = os.path.normpath(IMPI_INC)
        IMPI_LIB = os.path.normpath(IMPI_LIB)
        self.library_info.update(
            include_dirs=[IMPI_INC],
            library_dirs=[IMPI_LIB],
            libraries=["impi"],
        )
        self.section = "impi"
        self.filename = [os.path.dirname(IMPI_INC)]
        return True

    def _setup_windows_msmpi(self):
        # Microsoft MPI (v7, v6, v5, v4)
        def msmpi_ver():
            try:
                try:
                    import winreg
                except ImportError:
                    import _winreg as winreg
                HKLM = winreg.HKEY_LOCAL_MACHINE
                subkey = r"SOFTWARE\Microsoft\MPI"
                with winreg.OpenKey(HKLM, subkey) as key:
                    for i in range(winreg.QueryInfoKey(key)[1]):
                        name, value, _type = winreg.EnumValue(key, i)
                        if name != "Version":
                            continue
                        major, minor = value.split(".")[:2]
                        return (int(major), int(minor))
            except Exception:  # noqa: S110
                pass
            MSMPI_VER = os.environ.get("MSMPI_VER")
            if MSMPI_VER:
                try:
                    major, minor = MSMPI_VER.split(".")[:2]
                    return (int(major), int(minor))
                except Exception:
                    raise RuntimeError(
                        f"invalid environment: MSMPI_VER={MSMPI_VER}"
                    ) from None
            return None

        def setup_msmpi(MSMPI_INC, MSMPI_LIB):
            from os.path import isfile, join

            ok = (
                MSMPI_INC
                and isfile(join(MSMPI_INC, "mpi.h"))
                and MSMPI_LIB
                and isfile(join(MSMPI_LIB, "msmpi.lib"))
            )
            if not ok:
                return False
            version = msmpi_ver()
            if version is not None:
                major, minor = version
                MSMPI_VER = hex((major << 8) | (minor & 0xFF))
                self.library_info.update(
                    define_macros=[("MSMPI_VER", MSMPI_VER)],
                )
            MSMPI_INC = os.path.normpath(MSMPI_INC)
            MSMPI_LIB = os.path.normpath(MSMPI_LIB)
            self.library_info.update(
                include_dirs=[MSMPI_INC],
                library_dirs=[MSMPI_LIB],
                libraries=["msmpi"],
            )
            self.section = "msmpi"
            self.filename = [os.path.dirname(MSMPI_INC)]
            return True

        arch = platform.architecture(None)[0][:2]
        # Look for Microsoft MPI in the environment
        MSMPI_INC = os.environ.get("MSMPI_INC")
        MSMPI_LIB = os.environ.get("MSMPI_LIB" + arch)
        MSMPI_LIB = MSMPI_LIB or os.environ.get("MSMPI_LIB")
        if setup_msmpi(MSMPI_INC, MSMPI_LIB):
            return True
        # Look for Microsoft MPI v7/v6/v5 in default install path
        for ProgramFiles in ("ProgramFiles", "ProgramFiles(x86)"):
            ProgramFiles = os.environ.get(ProgramFiles, "")
            archdir = {"32": "x86", "64": "x64"}[arch]
            MSMPI_DIR = os.path.join(ProgramFiles, "Microsoft SDKs", "MPI")
            MSMPI_INC = os.path.join(MSMPI_DIR, "Include")
            MSMPI_LIB = os.path.join(MSMPI_DIR, "Lib", archdir)
            if setup_msmpi(MSMPI_INC, MSMPI_LIB):
                return True
        # Look for Microsoft HPC Pack 2012 R2 in default install path
        for ProgramFiles in ("ProgramFiles", "ProgramFiles(x86)"):
            ProgramFiles = os.environ.get(ProgramFiles, "")
            archdir = {"32": "i386", "64": "amd64"}[arch]
            MSMPI_DIR = os.path.join(ProgramFiles, "Microsoft MPI")
            MSMPI_INC = os.path.join(MSMPI_DIR, "Inc")
            MSMPI_LIB = os.path.join(MSMPI_DIR, "Lib", archdir)
            if setup_msmpi(MSMPI_INC, MSMPI_LIB):
                return True
        # Microsoft MPI (legacy) and others
        ProgramFiles = os.environ.get("ProgramFiles", "")
        CCP_HOME = os.environ.get("CCP_HOME", "")
        for name, prefix, suffix in (
            ("msmpi", CCP_HOME, ""),
            ("msmpi", ProgramFiles, "Microsoft HPC Pack 2012 R2"),
            ("msmpi", ProgramFiles, "Microsoft HPC Pack 2012"),
            ("msmpi", ProgramFiles, "Microsoft HPC Pack 2012 SDK"),
            ("msmpi", ProgramFiles, "Microsoft HPC Pack 2008 R2"),
            ("msmpi", ProgramFiles, "Microsoft HPC Pack 2008"),
            ("msmpi", ProgramFiles, "Microsoft HPC Pack 2008 SDK"),
        ):
            mpi_dir = os.path.join(prefix, suffix)
            if not mpi_dir or not os.path.isdir(mpi_dir):
                continue
            define_macros = []
            include_dir = os.path.join(mpi_dir, "include")
            library = "mpi"
            library_dir = os.path.join(mpi_dir, "lib")
            if name == "msmpi":
                include_dir = os.path.join(mpi_dir, "inc")
                library = "msmpi"
                arch = platform.architecture(None)[0]
                if arch == "32bit":
                    library_dir = os.path.join(library_dir, "i386")
                if arch == "64bit":
                    library_dir = os.path.join(library_dir, "amd64")
                if not os.path.isdir(include_dir):
                    include_dir = os.path.join(mpi_dir, "include")
            self.library_info.update(
                define_macros=define_macros,
                include_dirs=[include_dir],
                libraries=[library],
                library_dirs=[library_dir],
            )
            self.section = name
            self.filename = [mpi_dir]
            return True
        return None

    def setup_compiler_info(self, options, environ):
        def find_exe(cmd, path=None):
            if not cmd:
                return None
            parts = shlex.split(cmd)
            exe, args = parts[0], parts[1:]
            if not os.path.isabs(exe) and path:
                exe = os.path.basename(exe)
            exe = shutil.which(exe, path=path)
            if not exe:
                return None
            return " ".join([exe, *args])

        COMPILERS = (
            ("mpicc", ["mpicc"]),
            ("mpicxx", ["mpicxx", "mpic++", "mpiCC"]),
            ("mpild", []),
        )
        #
        compiler_info = {}
        PATH = environ.get("PATH", "")
        for name, _ in COMPILERS:
            cmd = (
                environ.get(f"MPI4PY_BUILD_{name.upper()}")
                or environ.get(name.upper())
                or getattr(options, name, None)
                or self.compiler_info.get(name)
                or None
            )
            if cmd:
                exe = find_exe(cmd, path=PATH)
                if exe:
                    path = os.path.dirname(exe)
                    PATH = path + os.path.pathsep + PATH
                    compiler_info[name] = exe
                else:
                    self.log.warn("warning: %s='%s' not found", name, cmd)
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

    def load(self, filename="mpi.cfg", section="mpi"):
        if isinstance(filename, str):
            filenames = filename.split(os.path.pathsep)
        else:
            filenames = list(filename)
        if isinstance(section, str):
            sections = section.split(",")
        else:
            sections = list(section)
        #
        parser = ConfigParser(dict_type=OrderedDict)
        try:
            read_ok = parser.read(filenames)
        except ConfigParserError:
            read_ok = None
        if read_ok is None:
            self.log.error(
                "error: parsing configuration file/s '%s'",
                os.path.pathsep.join(filenames),
            )
            return None
        for section in sections:
            if parser.has_section(section):
                break
            section = None
        if not section:
            self.log.error(
                "error: section/s '%s' not found in file/s '%s'",
                ",".join(sections),
                os.path.pathsep.join(filenames),
            )
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
            if k in (
                "define_macros",
                "undef_macros",
            ):
                macros = [e.strip() for e in v.split(",")]
                if k == "define_macros":
                    for i, m in enumerate(macros):
                        name, _, value = m.partition("=")
                        macros[i] = (name, value or None)
                library_info[k] = macros
            elif k in (
                "include_dirs",
                "library_dirs",
                "rpath",
                "runtime_dirs",
                "runtime_library_dirs",
            ):
                if k in ("rpath", "runtime_dirs"):
                    k = "runtime_library_dirs"
                pathlist = [p.strip() for p in v.split(pathsep)]
                library_info[k] = [
                    expanduser(expandvars(p)) for p in pathlist if p
                ]
            elif k == "libraries":
                library_info[k] = [e.strip() for e in shlex.split(v)]
            elif k in (
                "extra_compile_args",
                "extra_link_args",
            ):
                library_info[k] = shlex.split(v)
            elif k == "extra_objects":
                library_info[k] = [
                    expanduser(expandvars(e)) for e in shlex.split(v)
                ]
            elif hasattr(self, k):
                library_info[k] = v.strip()
        #
        self.section = section
        self.filename = read_ok
        self.compiler_info.update(compiler_info)
        self.library_info.update(library_info)
        return compiler_info, library_info, section, read_ok

    def dump(self, filename=None, section="mpi"):
        # prepare configuration values
        compiler_info = self.compiler_info.copy()
        library_info = self.library_info.copy()
        for k in library_info:
            if k in (
                "define_macros",
                "undef_macros",
            ):
                macros = library_info[k]
                if k == "define_macros":
                    for i, (m, v) in enumerate(macros):
                        if v is None:
                            macros[i] = m
                        else:
                            macros[i] = f"{m}={v}"
                library_info[k] = ",".join(macros)
            elif k in (
                "include_dirs",
                "library_dirs",
                "runtime_library_dirs",
            ):
                library_info[k] = os.path.pathsep.join(library_info[k])
            elif isinstance(library_info[k], list):
                library_info[k] = " ".join(library_info[k])
        # fill configuration parser
        parser = ConfigParser(dict_type=OrderedDict)
        parser.add_section(section)
        for option, value in compiler_info.items():
            if not value:
                continue
            parser.set(section, option, value)
        for option, value in library_info.items():
            if not value:
                continue
            parser.set(section, option, value)
        # save configuration file
        if filename is None:
            parser.write(sys.stdout)
        elif hasattr(filename, "write"):
            parser.write(filename)
        elif isinstance(filename, str):
            with open(filename, "w", encoding="utf-8") as f:
                parser.write(f)
        return parser


if __name__ == "__main__":
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("--mpi", type="string")
    parser.add_option("--mpicc", type="string")
    parser.add_option("--mpicxx", type="string")
    parser.add_option("--mpild", type="string")
    opts, args = parser.parse_args()

    cfg = Config()
    cfg.setup(opts)
    cfg.dump()
