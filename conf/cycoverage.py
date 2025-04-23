import os
import pathlib
import re
from collections import defaultdict

from coverage.files import (
    canonical_filename as _canonical_filename,
)
from coverage.plugin import (
    CoveragePlugin,
    FileReporter,
    FileTracer,
)

CYTHON_EXTENSIONS = {".pxd", ".pyx", ".pxi"}


def canonical_filename(filename):
    filename = pathlib.Path(filename).resolve()
    filename = _canonical_filename(str(filename))
    filename = pathlib.Path(filename)
    return filename


class CythonCoveragePlugin(CoveragePlugin):
    def configure(self, config):
        self.exclude = config.get_option("report:exclude_lines")

    def file_tracer(self, filename):
        filename = canonical_filename(filename)
        ext = filename.suffix
        if ext in CYTHON_EXTENSIONS:
            return CythonFileTracer(str(filename))
        return None

    def file_reporter(self, filename):
        filename = canonical_filename(filename)
        ext = filename.suffix
        if ext in CYTHON_EXTENSIONS:
            return CythonFileReporter(str(filename), self.exclude)
        return None


class CythonFileTracer(FileTracer):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def source_filename(self):
        return self.filename


class CythonFileReporter(FileReporter):
    def __init__(self, filename, exclude=None):
        super().__init__(filename)
        self.exclude = exclude

    def lines(self):
        _setup_lines(self.exclude)
        return self._get_lines(CODE_LINES)

    def excluded_lines(self):
        _setup_lines(self.exclude)
        return self._get_lines(EXCL_LINES)

    def translate_lines(self, lines):
        _setup_lines(self.exclude)
        exec_lines = self._get_lines(EXEC_LINES)
        return set(lines).union(exec_lines)

    def _get_lines(self, lines_map):
        key = os.path.relpath(self.filename, TOPDIR)
        lines = lines_map.get(key, {})
        return set(lines)


TOPDIR = pathlib.Path(__file__).parent.parent
SRCDIR = TOPDIR / "src"
CODE_LINES = None
EXEC_LINES = None
EXCL_LINES = None


def _setup_lines(exclude):
    global CODE_LINES, EXEC_LINES, EXCL_LINES
    if CODE_LINES is None or EXEC_LINES is None or EXCL_LINES is None:
        source = SRCDIR / "mpi4py" / "MPI.c"
        CODE_LINES, EXEC_LINES, EXCL_LINES = _parse_c_file(source, exclude)


def _parse_c_file(c_file, exclude_list):
    match_filetab_begin = "static const char *__pyx_f[] = {"
    match_filetab_begin = re.compile(re.escape(match_filetab_begin)).match
    match_filetab_entry = re.compile(r' *"(.*)",').match
    match_source_path_line = re.compile(r' */[*] +"(.*)":([0-9]+)$').match
    match_current_code_line = re.compile(r" *[*] (.*) # <<<<<<+$").match
    match_comment_end = re.compile(r" *[*]/$").match
    match_trace_line = re.compile(
        r" *__Pyx_TraceLine\((\d+),\d+,__PYX_ERR\((\d+),"
    ).match
    not_executable = re.compile(
        "|".join([
            r"\s*c(?:type)?def\s+"
            r"(?:(?:public|external)\s+)?"
            r"(?:struct|union|enum|class)"
            r"(\s+[^:]+|)\s*:",
        ])
    ).match
    if exclude_list:
        line_is_excluded = re.compile(
            "|".join([rf"(?:{regex})" for regex in exclude_list])
        ).search
    else:

        def line_is_excluded(_):
            return False

    filetab = []
    modinit = False
    code_lines = defaultdict(dict)
    exec_lines = defaultdict(dict)
    executable_lines = defaultdict(set)
    excluded_lines = defaultdict(set)

    with pathlib.Path(c_file).open(encoding="utf-8") as lines:
        lines = iter(lines)
        for line in lines:
            if match_filetab_begin(line):
                for line in lines:
                    match = match_filetab_entry(line)
                    if not match:
                        break
                    filename = match.group(1)
                    filetab.append(filename)
            match = match_source_path_line(line)
            if not match:
                if '__Pyx_TraceCall("__Pyx_PyMODINIT_FUNC ' in line:
                    modinit = True
                if "__Pyx_TraceLine(" in line:
                    trace_line = match_trace_line(line)
                    if trace_line:
                        lineno, fid = map(int, trace_line.groups())
                        executable_lines[filetab[fid]].add(lineno)
                continue
            filename, lineno = match.groups()
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
                    if modinit:
                        exec_lines[filename][lineno] = code_line
                    break
                if match_comment_end(comment_line):
                    # unexpected comment format - false positive?
                    break

    # Remove lines that generated code but are not traceable.

    for filename, lines in code_lines.items():
        dead_lines = set(lines).difference(executable_lines.get(filename, ()))
        for lineno in dead_lines:
            del lines[lineno]

    for filename, lines in exec_lines.items():
        dead_lines = set(lines).difference(executable_lines.get(filename, ()))
        for lineno in dead_lines:
            del lines[lineno]

    return code_lines, exec_lines, excluded_lines


def coverage_init(reg, options):  # noqa: ARG001
    plugin = CythonCoveragePlugin()
    reg.add_configurer(plugin)
    reg.add_file_tracer(plugin)
