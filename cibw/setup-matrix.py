import argparse
import collections
import copy
import fnmatch
import json

parser = argparse.ArgumentParser()
parser.add_argument("--os", nargs="*")
parser.add_argument("--py", nargs="*")
opts = parser.parse_args()


def py(py, x, y_min, y_max, abi=""):
    return [f"{py}{x}{y}{abi}" for y in range(y_min, y_max + 1)]


def cp3(y_min=8, y_max=14):
    return py("cp", 3, y_min, y_max)


def cp3t(y_min=13, y_max=14):
    return py("cp", 3, y_min, y_max, abi="t")


def abi3(y_min=10, y_max=10):
    return py("cp", 3, y_min, y_max, abi="-abi3")


def pp3(y_min=10, y_max=11):
    return py("pp", 3, y_min, y_max)


OS_ARCH_PY = {
    "Linux": {
        "aarch64": cp3() + cp3t() + abi3() + pp3(),
        "x86_64": cp3() + cp3t() + abi3() + pp3(),
    },
    "macOS": {
        "arm64": cp3() + cp3t() + abi3() + pp3(),
        "x86_64": cp3() + cp3t() + abi3() + pp3(),
    },
    "Windows": {
        "AMD64": cp3() + cp3t() + abi3() + pp3(),
    },
}

MPI_ABI_POSIX = [
    "mpich",
    "openmpi",
]
MPI_ABI_WINNT = [
    "impi",
    "msmpi",
]
MPI_ABI = {
    "Linux": MPI_ABI_POSIX.copy(),
    "macOS": MPI_ABI_POSIX.copy(),
    "Windows": MPI_ABI_WINNT.copy(),
}

GHA_RUNNER = {
    "Linux": {
        "aarch64": "ubuntu-24.04-arm",
        "x86_64": "ubuntu-24.04",
        None: "ubuntu-latest",
    },
    "macOS": {
        "arm64": "macos-15",
        "x86_64": "macos-13",
        None: "macos-latest",
    },
    "Windows": {
        "AMD64": "windows-2022",
        None: "windows-latest",
    },
}

os_arch_py = copy.deepcopy(OS_ARCH_PY)
if opts.os and not set(opts.os) & {"*", "all"}:
    select = collections.defaultdict(list)
    for entry in opts.os:
        for sep in "=+/@":
            entry = entry.replace(sep, "-")
        os, _, arch = entry.partition("-")
        assert os in OS_ARCH_PY  # noqa: S101
        if arch and arch not in ("*", "all"):
            assert arch in OS_ARCH_PY[os]  # noqa: S101
            if arch not in select[os]:
                select[os].append(arch)
        else:
            for arch in OS_ARCH_PY[os]:
                if arch not in select[os]:
                    select[os].append(arch)
    os_arch_py = collections.defaultdict(dict)
    for os in select:
        for arch in select[os]:
            os_arch_py[os][arch] = OS_ARCH_PY[os][arch].copy()
if opts.py and not set(opts.py) & {"*", "all"}:
    for os in os_arch_py:
        for arch in os_arch_py[os]:
            xplist = os_arch_py[os][arch] + pp3()
            select = []
            for pat in opts.py:
                for xp in fnmatch.filter(xplist, pat):
                    if xp not in select:
                        select.append(xp)
            if "abi3" in opts.py:
                for xp in abi3():
                    if xp not in select:
                        select.append(xp)
            os_arch_py[os][arch][:] = select

matrix_build = [
    {
        "os": os,
        "arch": arch,
        "py": py.partition("-")[0],
        "py-sabi": py.partition("-")[2],
        "mpi-abi": mpi_abi,
        "runner": GHA_RUNNER[os][arch],
    }
    for os in os_arch_py
    for arch in os_arch_py[os]
    for py in os_arch_py[os][arch]
    for mpi_abi in MPI_ABI[os]
]

matrix_merge = [
    {
        "os": os,
        "arch": arch,
        "runner": GHA_RUNNER[os][None],
    }
    for os in os_arch_py
    for arch in os_arch_py[os]
]

matrix_test = []
for build in matrix_build:
    os = build["os"]
    arch = build["arch"]
    pytag = build["py"]
    mpi_abi = build["mpi-abi"]
    py_sabi = build["py-sabi"]
    runner = GHA_RUNNER[os][arch]
    mpilist = [mpi_abi]
    if (os, arch, mpi_abi) == ("Linux", "x86_64", "mpich"):
        mpilist.insert(0, "impi")
    if py_sabi:
        pyvers = [py for py in cp3() if int(py[3:]) >= int(pytag[3:])]
        pylist = [py[2:3] + "." + py[3:] for py in pyvers]
    else:
        pyimpl = "pypy" if pytag.startswith("pp") else ""
        pylist = [pyimpl + pytag[2:3] + "." + pytag[3:]]
    matrix_test += [
        {
            "mpi": mpi,
            "py": py,
            "py-sabi": py_sabi,
            "os": os,
            "arch": arch,
            "runner": runner,
        }
        for py in pylist
        if py not in {"3.14", "3.14t"}
        for mpi in mpilist
    ]

print(f"matrix-build={json.dumps(matrix_build)}")
print(f"matrix-merge={json.dumps(matrix_merge)}")
print(f"matrix-test={json.dumps(matrix_test)}")
