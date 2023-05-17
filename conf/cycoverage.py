import os
from coverage.plugin import (
    CoveragePlugin,
    FileTracer,
    FileReporter
)
from coverage.files import (
    canonical_filename,
)

CYTHON_EXTENSIONS = {".pxd", ".pyx", ".pxi"}


class CythonCoveragePlugin(CoveragePlugin):

    def configure(self, config):
        config.get_option("report:exclude_lines")

    def file_tracer(self, filename):
        filename = canonical_filename(os.path.abspath(filename))
        _, ext = os.path.splitext(filename)
        if ext in CYTHON_EXTENSIONS:
            return CythonFileTracer(filename)
        return None

    def file_reporter(self, filename):
        filename = canonical_filename(os.path.abspath(filename))
        _, ext = os.path.splitext(filename)
        if ext in CYTHON_EXTENSIONS:
            return CythonFileReporter(filename)
        return None


class CythonFileTracer(FileTracer):

    def __init__(self, source_file):
        super().__init__()
        self.source_file = source_file

    def source_filename(self):
        return self.source_file



class CythonFileReporter(FileReporter):

    def __init__(self, filename):
        super().__init__(filename)

    def lines(self):
        _setup_lines()
        return self._get_lines(CODE_LINES)

    def excluded_lines(self):
        _setup_lines()
        return self._get_lines(EXCL_LINES)

    def _get_lines(self, lines_map):
        key = os.path.relpath(self.filename, SRCDIR)
        lines = lines_map.get(key, {})
        return set(lines)

TOPDIR = os.path.dirname(__file__)
SRCDIR = os.path.join(os.path.dirname(TOPDIR), 'src')
CODE_LINES = None
EXCL_LINES = None

def _setup_lines():
    global CODE_LINES, EXCL_LINES
    if CODE_LINES is None or EXCL_LINES is None:
        source = os.path.join(SRCDIR, 'mpi4py', 'MPI.c')
        CODE_LINES, EXCL_LINES = _parse_cfile_lines(source)


def _parse_cfile_lines(c_file):
    import re
    from collections import defaultdict

    match_source_path_line = re.compile(r' */[*] +"(.*)":([0-9]+)$').match
    match_current_code_line = re.compile(r' *[*] (.*) # <<<<<<+$').match
    match_comment_end = re.compile(r' *[*]/$').match
    match_trace_line = re.compile(r' *__Pyx_TraceLine\(([0-9]+),').match
    not_executable = re.compile(
        '|'.join([
            r'\s*c(?:type)?def\s+'
            r'(?:(?:public|external)\s+)?'
            r'(?:struct|union|enum|class)'
            r'(\s+[^:]+|)\s*:',
        ])
    ).match
    excluded_line_patterns = [
        r'.*\s*#> TODO$',
        r'.*\s*#> no cover$',
        r'.*\s*#> unreachable$',
        r'.*\s*#> pypy$',
        r'.*\s*#> big-endian$',
        r'.*\s*#> i386$',
        r'.*\s*#> 32bit$',
        r'.*\s*#> win32$',
        r'.*\s*#> legacy$',
        r'.*\s*#> long$',
        r'.*\s*#> openmpi$',
    ]

    if excluded_line_patterns:
        line_is_excluded = re.compile("|".join([
            "(?:%s)" % regex for regex in excluded_line_patterns
        ])).search
    else:
        def line_is_excluded(_):
            return False

    code_lines = defaultdict(dict)
    executable_lines = defaultdict(set)
    excluded_lines = defaultdict(set)
    current_filename = None

    with open(c_file) as lines:
        lines = iter(lines)
        for line in lines:
            match = match_source_path_line(line)
            if not match:
                if '__Pyx_TraceLine(' in line and current_filename is not None:
                    trace_line = match_trace_line(line)
                    if trace_line:
                        executable_lines[current_filename].add(int(trace_line.group(1)))
                continue
            filename, lineno = match.groups()
            current_filename = filename
            lineno = int(lineno)
            for comment_line in lines:
                match = match_current_code_line(comment_line)
                if match:
                    code_line = match.group(1).rstrip()
                    if not_executable(code_line):
                        break
                    if line_is_excluded(code_line):
                        excluded_lines[filename].add(lineno)
                        break
                    code_lines[filename][lineno] = code_line
                    break
                if match_comment_end(comment_line):
                    # unexpected comment format - false positive?
                    break

    # Remove lines that generated code but are not traceable.
    for filename, lines in code_lines.items():
        dead_lines = set(lines).difference(executable_lines.get(filename, ()))
        for lineno in dead_lines:
            del lines[lineno]

    return code_lines, excluded_lines


def coverage_init(reg, options):
    plugin = CythonCoveragePlugin()
    reg.add_configurer(plugin)
    reg.add_file_tracer(plugin)
