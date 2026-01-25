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
    from wheel.cli import pack as wheel_pack
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

    variant_registry = []
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

            mpipth = root_dir / "mpi.pth"
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
        variant_registry.append(variant)
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
                zip_extract(wf, zinfo, root_dir)
                extension = root_dir.joinpath(member)
                extname, suffix = extension.name.split(".", 1)
                filename = f"{extname}.{variant}.{suffix}"
                extension.rename(extension.parent / filename)
                print("OK", flush=True)

    source = package_dir / "__init__.py"
    with source.open("a", encoding="utf-8") as fh:
        fh.write(
            textwrap.dedent("""\n
        # Install MPI ABI finder
        from . import _mpiabi  # noqa: E402
        _mpiabi._install_finder()
        """)
        )
        if variant_registry:
            fh.write("# Register MPI ABI variants\n")
        for variant in variant_registry:
            for module in extensions:
                fh.write(f"_mpiabi._register({module!r}, {variant!r})\n")
        if tags[2].startswith("win"):
            fh.write(
                textwrap.dedent("""\
            # Set Windows DLL search path
            __import__('_mpi_dll_path').install()
            """)
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    wheel_pack.pack(root_dir, output_dir, None)
    shutil.rmtree(working_dir, ignore_errors=True)
    print(flush=True)
