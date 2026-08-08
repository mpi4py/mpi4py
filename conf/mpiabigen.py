import sys
import pathlib

confdir = pathlib.Path(__file__).resolve().parent
sys.path.append(confdir)

if __name__ == '__main__':
    import argparse
    from mpiapigen import Generator

    parser = argparse.ArgumentParser(description="MPI ABI generator")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("output_dir", action="store", help="Output directory")
    args = parser.parse_args()

    def log(message):
        if not args.quiet:
            print(message)

    generator = Generator()
    topdir = confdir.parent
    libmpi = topdir / "src" / "mpi4py" / "libmpi.pxd"
    mpiapi = topdir / "src" / "lib-mpi" / "config" / "mpiapi.h"
    generator.parse_file(libmpi)
    generator.parse_stdapi(mpiapi)

    outdir = pathlib.Path(args.output_dir)
    log(f"creating dir {outdir}")
    outdir.mkdir(parents=True, exist_ok=True)
    mpi_h = outdir / "mpi.h"
    log(f"writing file {mpi_h}")
    generator.dump_abiheader(mpi_h)
    mpi_c = outdir / "mpi.c"
    log(f"writing file {mpi_c}")
    generator.dump_abisource(mpi_c)
