import argparse
import collections
import os
import shutil
import tempfile
import textwrap
from pathlib import Path

try:
    from wheel._commands import pack as wheel_pack
except ModuleNotFoundError:
    from wheel.cli import pack as wheel_pack  # ty: ignore[import-not-found]
from wheel.wheelfile import WheelFile


def zip_extract(zfile, zinfo, destination):
    zfile.extract(zinfo, destination)
    # https://github.com/python/cpython/issues/59999
    permissions = zinfo.external_attr >> 16 & 0o777
    destination.joinpath(zinfo.filename).chmod(permissions)


parser = argparse.ArgumentParser()
parser.add_argument("wheelhouse", nargs="?", default="wheelhouse")
parser.add_argument("output_dir", nargs="?", default="dist")
opts = parser.parse_args()

wheelhouse = Path(opts.wheelhouse)
output_dir = Path(opts.output_dir)
working_dir = Path(tempfile.mkdtemp())
ext_suffix = ".so" if os.name == "posix" else ".pyd"
extensions = ["mpi4py.MPI"]

shutil.rmtree(output_dir, ignore_errors=True)
output_dir.mkdir(parents=True, exist_ok=True)

wheels = collections.defaultdict(list)
for whl in sorted(wheelhouse.glob("*.whl")):
    dist, version, py, abi, plat = whl.stem.split("-")
    if "+" in version:  # local version
        package = dist
        version, sep, variant = version.partition("+")
        variant = sep + variant
    else:  # dist suffix
        package, sep, variant = dist.partition("_")
        variant = sep + variant
    wheels[package, version, (py, abi, plat)].append(variant)

for (package, version, tags), variantlist in wheels.items():
    namever = f"{package}-{version}"
    wheeltags = "-".join(tags)
    root_dir = working_dir / namever
    package_dir = root_dir / package.partition("_")[0]
    distinfo_dir = root_dir / f"{namever}.dist-info"
    ext_suffix_glob = f".*{ext_suffix}"
    if tags[1] == "abi3" and tags[2].startswith("win"):
        ext_suffix_glob = f"{ext_suffix}"

    for i, variant in enumerate(sorted(variantlist)):
        if variant[0] == "+":  # local version
            dist = f"{package}"
            distver = f"{dist}-{version}{variant}"
        if variant[0] == "_":  # dist suffix
            dist = f"{package}{variant}"
            distver = f"{dist}-{version}"

        wheelname = f"{distver}-{wheeltags}.whl"
        wheelpath = wheelhouse / wheelname

        if i == 0:
            with WheelFile(wheelpath) as wf:
                message = f"Unpacking wheel {wheelpath}..."
                print(message, end="", flush=True)
                for zinfo in wf.filelist:
                    zip_extract(wf, zinfo, root_dir)
                print("OK", flush=True)

            distinfo_dir.with_stem(distver).rename(distinfo_dir)

            for extension in extensions:
                extpath = Path().joinpath(*extension.split("."))
                for extfile in root_dir.glob(f"{extpath}{ext_suffix_glob}"):
                    extfile.unlink()

            for libdir in (
                Path(dist).with_suffix(".libs"),
                Path(package).with_suffix(".libs"),
                Path(package) / ".libs",
            ):
                libdir = root_dir / libdir
                if libdir.exists():
                    libdir.rmdir()

            for pthfile in ("_mpi_dll_path.py", "mpi.pth", "mpi.start"):
                mpipth = root_dir / pthfile
                if mpipth.exists():
                    mpipth.unlink()

            record = distinfo_dir / "RECORD"
            record.unlink()

            metadata = distinfo_dir / "METADATA"
            data = metadata.read_text(encoding="utf-8")
            data = data.replace(variant.replace("_", "-"), "")
            data = data.replace(variant, "")
            metadata.write_text(data, encoding="utf-8")

        transtb = str.maketrans("_.", "--")
        variant = variant[1:].translate(transtb)
        with WheelFile(wheelpath) as wf:
            extract = []
            for zinfo in wf.filelist:
                member = Path(zinfo.filename)
                for extension in extensions:
                    extpath = Path().joinpath(*extension.split("."))
                    if member.match(f"{extpath}{ext_suffix_glob}"):
                        extract.append(zinfo)
            for zinfo in extract:
                member = Path(zinfo.filename)
                message = f"Extracting: {member} [{variant}]..."
                print(message, end="", flush=True)
                zip_extract(wf, zinfo, root_dir.parent)
                extension = root_dir.parent.joinpath(member)
                suffix = "" if variant == "mpiabi" else f".{variant}"
                location = root_dir / f"{member.parent}{suffix}"
                location.mkdir(exist_ok=True)
                extension.rename(location / member.name)
                print("OK", flush=True)

    source = package_dir / "__init__.py"
    content = textwrap.dedent("""\n
    # Support for MPI ABI variants
    from . import _mpiabi
    _mpiabi._install_getattr_hook(__name__, "MPI")
    """)
    with source.open("a", encoding="utf-8") as fh:
        fh.write(content)

    output_dir.mkdir(parents=True, exist_ok=True)
    wheel_pack.pack(os.fspath(root_dir), os.fspath(output_dir), None)
    shutil.rmtree(os.fspath(working_dir), ignore_errors=True)
    print(flush=True)
