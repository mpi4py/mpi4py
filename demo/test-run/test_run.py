import sys
import os
import shlex
import shutil
import warnings
import subprocess
import unittest
import mpi4py

on_win = sys.platform == 'win32'
on_gha = os.environ.get('GITHUB_ACTIONS') == 'true'
on_pypy = hasattr(sys, 'pypy_version_info')


def find_executable(exe):
    command = shlex.split(exe)
    executable = shutil.which(command[0])
    if executable:
        command[0] = executable
        try:  # Python 3.8
            return shlex.join(command)
        except AttributeError:
            return ' '.join(shlex.quote(arg) for arg in command)


def find_mpiexec(mpiexec='mpiexec'):
    mpiexec = os.environ.get('MPIEXEC') or mpiexec
    mpiexec = find_executable(mpiexec)
    if not mpiexec and sys.platform.startswith('win'):
        MSMPI_BIN = os.environ.get('MSMPI_BIN', '')
        mpiexec = os.path.join(MSMPI_BIN, 'mpiexec.exe')
        mpiexec = shutil.which(mpiexec)
        mpiexec = shlex.quote(mpiexec)
    return mpiexec


def launcher(np):
    mpiexec = find_mpiexec()
    python = shlex.quote(sys.executable)
    if 'coverage' in sys.modules:
        python += ' -m coverage run -p'
    module = 'mpi4py.run -rc threads=False'
    command = f'{mpiexec} -n {np} {python} -m {module}'
    return shlex.split(command)


def execute(np, cmd, args=''):
    mpi4pyroot = os.path.abspath(os.path.dirname(mpi4py.__path__[0]))
    pythonpath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
    pythonpath.insert(0, mpi4pyroot)

    mpiexec = launcher(np)
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    if isinstance(args, str):
        args = shlex.split(args)
    command = mpiexec + cmd + args

    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join(pythonpath)
    env['PYTHONUNBUFFERED'] = '1'

    p = subprocess.Popen(
        command, env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = p.communicate()
    return p.returncode, stdout.decode(), stderr.decode()


@unittest.skipIf(not find_mpiexec(), 'mpiexec')
@unittest.skipIf(on_gha and on_win, 'github-actions windows')
class BaseTestRun(unittest.TestCase):

    def assertMPIAbort(self, stdout, stderr, message=None):
        patterns = (
            'MPI_Abort',                # MPICH
            'MPI_ABORT',                # Open MPI
            'aborting MPI_COMM_WORLD',  # Microsoft MPI
        )
        if on_pypy and message == 'KeyboardInterrupt':
            patterns += (
                'EXIT STRING: Interrupt (signal 2)',  # MPICH
                'exited on signal 2 (Interrupt)',     # Open MPI
            )
        aborted = any(
            mpiabort in output
            for output in (stdout, stderr)
            for mpiabort in patterns
        )
        ci = any((
            os.environ.get('GITHUB_ACTIONS') == 'true',
            os.environ.get('TF_BUILD') == 'True',
            os.environ.get('CIRCLECI') == 'true',
        ))
        if aborted:
            if message is not None and not ci:
                self.assertIn(message, stderr)
            return
        if not (stdout or stderr) or ci:
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                warnings.warn(
                    "expecting MPI_Abort() message in stdout/stderr",
                    RuntimeWarning, 2,
                )
            return
        raise self.failureException(
            "expecting MPI_Abort() message in stdout/stderr:\n"
            f"[stdout]:\n{stdout}\n[stderr]:\n{stderr}\n"
        )


class TestRunScript(BaseTestRun):
    pyfile = 'run-script.py'

    def execute(self, args='', np=1):
        dirname = os.path.abspath(os.path.dirname(__file__))
        script = os.path.join(dirname, self.pyfile)
        return execute(np, shlex.quote(script), args)

    def testSuccess(self):
        success = 'Hello, World!'
        for np in (1, 2):
            status, stdout, stderr = self.execute(np=np)
            self.assertEqual(status, 0)
            self.assertEqual(stdout.count(success), np)
            self.assertEqual(stderr, '')

    def testException(self):
        message = r'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        excmess = f'RuntimeError: {message}'
        for np in (1, 2):
            for rank in range(0, np):
                args = ['--rank', str(rank), '--exception', message]
                status, stdout, stderr = self.execute(args, np)
                self.assertEqual(status, 1)
                self.assertMPIAbort(stdout, stderr, excmess)

    def testSysExitCode(self):
        errcode = 7
        for np in (1, 2):
            for r in sorted({0, np - 1}):
                args = ['--rank', str(r), '--sys-exit', str(errcode)]
                status, stdout, stderr = self.execute(args, np)
                self.assertIn(status, (errcode, 1))
                self.assertMPIAbort(stdout, stderr)
                self.assertNotIn('Traceback', stderr)

    def testSysExitMess(self):
        exitmsg = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for np in (1, 2):
            for r in sorted({0, np - 1}):
                args = ['--rank', str(r), '--sys-exit-msg', exitmsg]
                status, stdout, stderr = self.execute(args, np)
                self.assertEqual(status, 1)
                self.assertMPIAbort(stdout, stderr, exitmsg)
                self.assertNotIn('Traceback', stderr)

    def testInterrupt(self):
        from signal import SIGINT
        excmess = 'KeyboardInterrupt'
        for np in (1, 2):
            for rank in range(0, np):
                args = ['--rank', str(rank), '--interrupt']
                status, stdout, stderr = self.execute(args, np)
                if not on_pypy:
                    self.assertEqual(status, SIGINT + 128)
                self.assertMPIAbort(stdout, stderr, excmess)


class TestRunDirectory(TestRunScript):
    directory = 'run-directory'

    @classmethod
    def setUpClass(cls):
        from tempfile import mkdtemp
        cls.tempdir = mkdtemp()
        cls.directory = os.path.join(cls.tempdir, cls.directory)
        os.makedirs(cls.directory)
        topdir = os.path.dirname(__file__)
        script = os.path.join(topdir, super().pyfile)
        pymain = os.path.join(cls.directory, '__main__.py')
        shutil.copy(script, pymain)
        cls.pyfile = cls.directory

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir)


class TestRunZipFile(TestRunScript):
    zipfile = 'run-zipfile.zip'

    @classmethod
    def setUpClass(cls):
        from tempfile import mkdtemp
        from zipfile import ZipFile
        cls.tempdir = mkdtemp()
        cls.zipfile = os.path.join(cls.tempdir, cls.zipfile)
        topdir = os.path.dirname(__file__)
        script = os.path.join(topdir, super().pyfile)
        with ZipFile(cls.zipfile, 'w') as f:
            f.write(script, '__main__.py')
        cls.pyfile = cls.zipfile

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir)


class TestRunModule(BaseTestRun):

    def execute(self, module, np=1):
        return execute(np, '-m', module)

    def testSuccess(self):
        module = 'mpi4py.bench --no-threads helloworld'
        message = 'Hello, World!'
        for np in (1, 2):
            status, stdout, stderr = self.execute(module, np)
            self.assertEqual(status, 0)
            self.assertEqual(stdout.count(message), np)
            self.assertEqual(stderr, '')


class TestRunCommand(BaseTestRun):

    def execute(self, command, np=1):
        return execute(np, '-c', shlex.quote(command))

    def testArgv0(self):
        command = 'import sys; print(sys.argv[0], flush=True)'
        status, stdout, stderr = self.execute(command, 1)
        self.assertEqual(status, 0)
        self.assertEqual(stdout.strip(), '-c')
        self.assertEqual(stderr.strip(), '')

    def testSuccess(self):
        command = 'from mpi4py import MPI'
        for np in (1, 2):
            status, stdout, stderr = self.execute(command, np)
            self.assertEqual(status, 0)
            self.assertEqual(stdout, '')
            self.assertEqual(stderr, '')

    def testException(self):
        command = '; '.join((
            'from mpi4py import MPI',
            'comm = MPI.COMM_WORLD',
            'comm.Barrier()',
            'comm.Barrier()',
            'comm.Get_rank() == {} and (1/0)',
            'comm.Barrier()',
        ))
        excmess = 'ZeroDivisionError:'
        for np in (1, 2):
            for rank in range(0, np):
                status, stdout, stderr = self.execute(command.format(rank), np)
                self.assertEqual(status, 1)
                self.assertMPIAbort(stdout, stderr, excmess)


if __name__ == '__main__':
    unittest.main()
