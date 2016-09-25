import sys, os, shlex
import subprocess as sp
import unittest
import mpi4py

def find_executable(exe):
    from distutils.spawn import find_executable as find_exe
    command = shlex.split(exe)
    executable = find_exe(command[0])
    if executable:
        command[0] = executable
        return ' '.join(command)

def find_mpiexec(mpiexec='mpiexec'):
    mpiexec = os.environ.get('MPIEXEC') or mpiexec
    mpiexec = find_executable(mpiexec)
    if not mpiexec and sys.platform.startswith('win'):
        MSMPI_BIN = os.environ.get('MSMPI_BIN', '')
        mpiexec = os.path.join(MSMPI_BIN, mpiexec)
        mpiexec = find_executable(mpiexec)
    if not mpiexec:
        mpiexec = find_executable('mpirun')
    return mpiexec

def launcher(np):
    mpiexec = find_mpiexec()
    python = sys.executable
    if 'coverage' in sys.modules:
        python += ' -m coverage run -p -m'
    module = 'mpi4py.run -rc threads=False'
    command = '{mpiexec} -n {np} {python} -m {module}'
    return shlex.split(command.format(**vars()))

def execute(np, command, args=''):
    env = os.environ.copy()
    pypath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
    pypath.insert(0, os.path.abspath(os.path.dirname(mpi4py.__path__[0])))
    env['PYTHONPATH'] = os.pathsep.join(pypath)
    if isinstance(command, str):
        command = shlex.split(command)
    if isinstance(args, str):
        args = shlex.split(args)
    cmdline = launcher(np) + command + args
    p = sp.Popen(cmdline, stdout=sp.PIPE, stderr=sp.PIPE, env=env, bufsize=0)
    stdout, stderr = p.communicate()
    return p.returncode, stdout.decode(), stderr.decode()


class BaseTestRun(object):

    def assertMPIAbort(self, stdout, stderr):
        if not ('MPI_Abort' in stdout or 'MPI_ABORT' in stdout or
                'MPI_Abort' in stderr or 'MPI_ABORT' in stderr):
            msg = ("expecting MPI_Abort() message in stdout/stderr:\n"
                   "[stdout]:\n{0}\n[stderr]:\n{1}\n").format(stdout, stderr)
            raise self.failureException(msg)


class TestRunScript(BaseTestRun, unittest.TestCase):
    pyfile = 'run-script.py'

    def execute(self, args='', np=1):
        dirname = os.path.abspath(os.path.dirname(__file__))
        script = os.path.join(dirname, self.pyfile)
        return execute(np, script, args)

    def testSuccess(self):
        success = 'Hello, World!'
        for np in (1, 2, 3):
            status, stdout, stderr = self.execute(np=np)
            self.assertEqual(status, 0)
            self.assertEqual(stderr, '')
            self.assertEqual(stdout.count(success), np)

    def testException(self):
        message = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        excmess = 'RuntimeError: {0}'.format(message)
        for np in (1, 2, 3):
            for rank in range(0, np):
                args = ['--rank', str(rank), '--exception', message]
                status, stdout, stderr = self.execute(args, np)
                self.assertEqual(status, 1)
                self.assertMPIAbort(stdout, stderr)
                self.assertTrue(excmess in stderr)

    def testSysExitCode(self):
        errcode = 7
        for np in (1, 2, 3):
            for r in sorted(set([0, np-1])):
                args = ['--rank', str(r), '--sys-exit', str(errcode)]
                status, stdout, stderr = self.execute(args, np)
                self.assertTrue(status in (errcode, 1))
                self.assertMPIAbort(stdout, stderr)
                self.assertTrue('Traceback' not in stderr)

    def testSysExitMess(self):
        exitmsg = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for np in (1, 2, 3):
            for r in sorted(set([0, np-1])):
                args = ['--rank', str(r), '--sys-exit-msg', exitmsg]
                status, stdout, stderr = self.execute(args, np)
                self.assertEqual(status, 1)
                self.assertMPIAbort(stdout, stderr)
                self.assertTrue('Traceback' not in stderr)
                self.assertTrue(exitmsg in stderr)

if os.path.exists(os.path.join(os.path.dirname(__file__), 'run-directory')):
    class TestRunDirectory(TestRunScript):
        pyfile = 'run-directory'

if os.path.exists(os.path.join(os.path.dirname(__file__), 'run-zipfile.zip')):
    class TestRunZipFile(TestRunScript):
        pyfile = 'run-zipfile.zip'


class TestRunModule(BaseTestRun, unittest.TestCase):

    def execute(self, module, np=1):
        return execute(np, '-m', module)

    def testSuccess(self):
        module = 'mpi4py.bench --no-threads helloworld'
        message = 'Hello, World!'
        for np in (1, 2, 3):
            status, stdout, stderr = self.execute(module, np)
            self.assertEqual(status, 0)
            self.assertEqual(stdout.count(message), np)
            self.assertEqual(stderr, '')


class TestRunCommand(BaseTestRun, unittest.TestCase):

    def execute(self, command, np=1):
        return execute(np, '-c', command)

    def testArgv0(self):
        command = '"import sys; print(sys.argv[0])"'
        status, stdout, stderr = self.execute(command, 1)
        self.assertEqual(status, 0)
        self.assertEqual(stdout, '-c\n')
        self.assertEqual(stderr, '')

    def testSuccess(self):
        command = '"from mpi4py import MPI"'
        for np in (1, 2, 3):
            status, stdout, stderr = self.execute(command, np)
            self.assertEqual(status, 0)
            self.assertEqual(stdout, '')
            self.assertEqual(stderr, '')

    def testException(self):
        command = '"from mpi4py import MPI; 1/0 if MPI.COMM_WORLD.Get_rank()==0 else 0;"'
        excmess = 'ZeroDivisionError:'
        for np in (1, 2, 3):
            for rank in range(0, np):
                status, stdout, stderr = self.execute(command, np)
                self.assertEqual(status, 1)
                self.assertMPIAbort(stdout, stderr)
                self.assertTrue(excmess in stderr)


if not find_mpiexec():
    del TestRunScript
    try: del TestRunDirectory
    except: pass
    try: del TestRunZipFile
    except: pass
    del TestRunModule
    del TestRunCommand


if __name__ == '__main__':
    unittest.main()
