import os
import pathlib
import shlex
import shutil
import signal
import string
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

import mpi4py

on_ci = any((
    os.environ.get("GITHUB_ACTIONS") == "true",
    os.environ.get("TF_BUILD") == "True",
    os.environ.get("CIRCLECI") == "true",
))


def find_executable(exe):
    command = shlex.split(exe)
    executable = shutil.which(command[0])
    if executable:
        command[0] = executable
        return shlex.join(command)
    return None


def find_mpiexec(mpiexec="mpiexec"):
    mpiexec = os.environ.get("MPIEXEC") or mpiexec
    mpiexec = find_executable(mpiexec)
    if not mpiexec and sys.platform.startswith("win"):
        I_MPI_DIR = pathlib.Path(os.environ.get("I_MPI_DIR", ""))
        mpiexec = str(I_MPI_DIR / "bin" / "mpiexec.exe")
        mpiexec = shutil.which(mpiexec)
        if mpiexec:
            mpiexec = shlex.quote(mpiexec)
    if not mpiexec and sys.platform.startswith("win"):
        MSMPI_BIN = pathlib.Path(os.environ.get("MSMPI_BIN", ""))
        mpiexec = str(MSMPI_BIN / "mpiexec.exe")
        mpiexec = shutil.which(mpiexec)
        if mpiexec:
            mpiexec = shlex.quote(mpiexec)
    return mpiexec


def launcher(np):
    mpiexec = find_mpiexec()
    python = shlex.quote(sys.executable)
    if "coverage" in sys.modules:
        python += " -m coverage run -p"
    module = "mpi4py.run -rc threads=False"
    command = f"{mpiexec} -n {np} {python} -m {module}"
    return shlex.split(command)


def execute(np, cmd, args=""):
    mpi4pyroot = pathlib.Path(mpi4py.__path__[0]).resolve().parent
    pythonpath = os.environ.get("PYTHONPATH", "").split(os.pathsep)
    pythonpath.insert(0, str(mpi4pyroot))

    mpiexec = launcher(np)
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    if isinstance(args, str):
        args = shlex.split(args)
    command = mpiexec + cmd + args

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    env["PYTHONUNBUFFERED"] = "1"

    p = subprocess.Popen(
        command,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = p.communicate()
    return p.returncode, stdout.decode(), stderr.decode()


@unittest.skipIf(not find_mpiexec(), "mpiexec")
class BaseTestRun(unittest.TestCase):
    #

    def assertFailure(self, status, expected):
        if on_ci and status in {221, 222}:
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                warnings.warn(
                    f"expecting status {expected}, got {status}",
                    RuntimeWarning,
                    2,
                )
            return
        if isinstance(expected, int):
            self.assertEqual(status, expected)
        else:
            self.assertIn(status, expected)

    def assertMPIAbort(self, stdout, stderr, message=None):
        patterns = (
            "MPI_Abort",  # MPICH
            "MPI_ABORT",  # Open MPI
            "aborting MPI_COMM_WORLD",  # Microsoft MPI
        )
        aborted = any(
            mpiabort in output
            for output in (stdout, stderr)
            for mpiabort in patterns
        )
        if aborted:
            if message is not None and not on_ci:
                self.assertIn(message, stderr)
            return
        if not (stdout or stderr) or on_ci:
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                warnings.warn(
                    "expecting MPI_Abort() message in stdout/stderr",
                    RuntimeWarning,
                    2,
                )
            return
        raise self.failureException(
            "expecting MPI_Abort() message in stdout/stderr:\n"
            f"[stdout]:\n{stdout}\n[stderr]:\n{stderr}\n"
        )


class TestRunScript(BaseTestRun):
    pyfile = "run-script.py"

    def execute(self, args="", np=1):
        dirname = pathlib.Path(__file__).resolve().parent
        script = dirname / self.pyfile
        return execute(np, shlex.quote(str(script)), args)

    def testSuccess(self):
        success = "Hello, World!"
        for np in (1, 2):
            status, stdout, stderr = self.execute(np=np)
            self.assertEqual(status, 0)
            self.assertEqual(stdout.count(success), np)
            self.assertEqual(stderr, "")

    def testException(self):
        message = string.ascii_uppercase
        excmess = f"RuntimeError: {message}"
        for np in (1, 2):
            for rank in range(np):
                args = ["--rank", str(rank), "--exception", message]
                status, stdout, stderr = self.execute(args, np)
                self.assertFailure(status, 1)
                self.assertMPIAbort(stdout, stderr, excmess)

    def testSysExitCode(self):
        errcode = 7
        for np in (1, 2):
            for r in sorted({0, np - 1}):
                args = ["--rank", str(r), "--sys-exit", str(errcode)]
                status, stdout, stderr = self.execute(args, np)
                self.assertFailure(status, (errcode, 1))
                self.assertMPIAbort(stdout, stderr)
                self.assertNotIn("Traceback", stderr)

    def testSysExitMess(self):
        exitmsg = string.ascii_uppercase
        for np in (1, 2):
            for r in sorted({0, np - 1}):
                args = ["--rank", str(r), "--sys-exit-msg", exitmsg]
                status, stdout, stderr = self.execute(args, np)
                self.assertFailure(status, 1)
                self.assertMPIAbort(stdout, stderr, exitmsg)
                self.assertNotIn("Traceback", stderr)

    def testInterrupt(self):
        excmess = "KeyboardInterrupt"
        for np in (1, 2):
            for rank in range(np):
                args = ["--rank", str(rank), "--interrupt"]
                status, stdout, stderr = self.execute(args, np)
                self.assertFailure(status, signal.SIGINT + 128)
                self.assertMPIAbort(stdout, stderr, excmess)


class TestRunDirectory(TestRunScript):
    directory = "run-directory"

    @classmethod
    def setUpClass(cls):
        cls.tempdir = pathlib.Path(tempfile.mkdtemp())
        cls.directory = cls.tempdir / cls.directory
        cls.directory.mkdir(parents=True)
        topdir = pathlib.Path(__file__).parent
        script = topdir / super().pyfile
        pymain = cls.directory / "__main__.py"
        shutil.copy(script, pymain)
        cls.pyfile = cls.directory

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir)


class TestRunZipFile(TestRunScript):
    zipfile = "run-zipfile.zip"

    @classmethod
    def setUpClass(cls):
        cls.tempdir = pathlib.Path(tempfile.mkdtemp())
        cls.zipfile = cls.tempdir / cls.zipfile
        topdir = pathlib.Path(__file__).parent
        script = topdir / super().pyfile
        with zipfile.ZipFile(cls.zipfile, "w") as f:
            f.write(script, "__main__.py")
        cls.pyfile = cls.zipfile

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir)


class TestRunModule(BaseTestRun):
    def execute(self, module, np=1):
        return execute(np, "-m", module)

    def testSuccess(self):
        module = "mpi4py.bench --no-threads helloworld"
        message = "Hello, World!"
        for np in (1, 2):
            status, stdout, stderr = self.execute(module, np)
            self.assertEqual(status, 0)
            self.assertEqual(stdout.count(message), np)
            self.assertEqual(stderr, "")


class TestRunCommand(BaseTestRun):
    def execute(self, command, np=1):
        return execute(np, "-c", shlex.quote(command))

    def testArgv0(self):
        command = "import sys; print(sys.argv[0], flush=True)"
        status, stdout, stderr = self.execute(command, 1)
        self.assertEqual(status, 0)
        self.assertEqual(stdout.strip(), "-c")
        self.assertEqual(stderr.strip(), "")

    def testSuccess(self):
        command = "from mpi4py import MPI"
        for np in (1, 2):
            status, stdout, stderr = self.execute(command, np)
            self.assertEqual(status, 0)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, "")

    def testException(self):
        command = "; ".join((
            "from mpi4py import MPI",
            "comm = MPI.COMM_WORLD",
            "comm.Barrier()",
            "comm.Barrier()",
            "comm.Get_rank() == {} and (1/0)",
            "comm.Barrier()",
        ))
        excmess = "ZeroDivisionError:"
        for np in (1, 2):
            for rank in range(np):
                status, stdout, stderr = self.execute(command.format(rank), np)
                self.assertFailure(status, 1)
                self.assertMPIAbort(stdout, stderr, excmess)


if __name__ == "__main__":
    unittest.main()
