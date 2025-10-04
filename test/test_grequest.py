import mpitestutil as testutil
import mpiunittest as unittest

from mpi4py import MPI


class GReqCtx:
    #
    source = 3
    tag = 7
    completed = False

    cancel_called = False
    free_called = False

    def query(self, status):
        status.Set_source(self.source)
        status.Set_tag(self.tag)

    def free(self):
        self.free_called = True

    def cancel(self, completed):
        self.cancel_called = True
        if completed is not self.completed:
            raise MPI.Exception(MPI.ERR_PENDING)


@unittest.skipMPI("MPI(<2.0)")
@unittest.skipMPI("openmpi(==4.1.0)")
class TestGrequest(unittest.TestCase):
    #
    def testConstructor(self):
        ctx = GReqCtx()
        greq = MPI.Grequest.Start(ctx.query, ctx.free, ctx.cancel)
        dupe = MPI.Grequest(greq)
        self.assertIs(type(dupe), MPI.Grequest)
        self.assertEqual(dupe, greq)
        dupe = MPI.Grequest.fromhandle(greq.tohandle())
        self.assertIs(type(dupe), MPI.Grequest)
        self.assertEqual(dupe, greq)
        if greq.toint() != -1:
            dupe = MPI.Grequest.fromint(greq.toint())
            self.assertIs(type(dupe), MPI.Grequest)
            self.assertEqual(dupe, greq)
        if greq.py2f() != -1:
            dupe = MPI.Grequest.f2py(greq.py2f())
            self.assertIs(type(dupe), MPI.Grequest)
            self.assertEqual(dupe, greq)
        dupe = MPI.Request(greq)
        self.assertIs(type(dupe), MPI.Request)
        self.assertEqual(dupe, greq)
        with self.assertRaises(TypeError):
            dupe = MPI.Prequest(greq)
        greq.Cancel()
        greq.Complete()
        greq.Wait()

    @unittest.skipMPI("openmpi")  # TODO(dalcinl): open-mpi/ompi#11681
    def testExceptionHandling(self):
        ctx = GReqCtx()

        def raise_mpi(*_args):
            raise MPI.Exception(MPI.ERR_BUFFER)

        def raise_rte(*_args):
            raise ValueError(42)

        def check_exc(exception, is_mpi, stderr):
            output = stderr.getvalue()
            header = "Traceback (most recent call last):\n"
            if is_mpi:
                chkcode = MPI.ERR_BUFFER
                excname = MPI.Exception.__name__
            else:
                chkcode = MPI.ERR_OTHER
                excname = ValueError.__name__
            ierr = exception.Get_error_class()
            self.assertEqual(ierr, chkcode)
            self.assertTrue(output.startswith(header))
            self.assertIn(excname, output)

        for raise_fn, is_mpi in (
            (raise_mpi, True),
            (raise_rte, False),
        ):
            greq = MPI.Grequest.Start(raise_fn, ctx.free, ctx.cancel)
            greq.Complete()
            with self.assertRaises(MPI.Exception) as exc_cm:
                with testutil.capture_stderr() as stderr:
                    greq.Wait()
            if greq:
                greq.Free()
            check_exc(exc_cm.exception, is_mpi, stderr)
            #
            greq = MPI.Grequest.Start(ctx.query, raise_fn, ctx.cancel)
            greq.Complete()
            with self.assertRaises(MPI.Exception) as exc_cm:
                with testutil.capture_stderr() as stderr:
                    greq.Wait()
            if greq:
                greq.Free()
            check_exc(exc_cm.exception, is_mpi, stderr)
            #
            greq = MPI.Grequest.Start(ctx.query, ctx.free, raise_fn)
            with self.assertRaises(MPI.Exception) as exc_cm:
                with testutil.capture_stderr() as stderr:
                    greq.Cancel()
            greq.Complete()
            greq.Wait()
            if greq:
                greq.Free()
            check_exc(exc_cm.exception, is_mpi, stderr)

    def testAll(self):
        ctx = GReqCtx()
        greq = MPI.Grequest.Start(ctx.query, ctx.free, ctx.cancel)
        self.assertFalse(greq.Test())
        self.assertFalse(ctx.free_called)
        greq.Cancel()
        self.assertTrue(ctx.cancel_called)
        ctx.cancel_called = False
        greq.Complete()
        ctx.completed = True
        greq.Cancel()
        self.assertTrue(ctx.cancel_called)
        status = MPI.Status()
        self.assertTrue(greq.Test(status))
        self.assertEqual(status.Get_source(), ctx.source)
        self.assertEqual(status.Get_tag(), ctx.tag)
        self.assertEqual(status.Get_error(), MPI.SUCCESS)
        greq.Wait()
        self.assertTrue(ctx.free_called)

    def testAll1(self):
        ctx = GReqCtx()
        greq = MPI.Grequest.Start(ctx.query, None, None)
        self.assertFalse(greq.Test())
        greq.Cancel()
        greq.Complete()
        status = MPI.Status()
        self.assertTrue(greq.Test(status))
        self.assertEqual(status.Get_source(), ctx.source)
        self.assertEqual(status.Get_tag(), ctx.tag)
        self.assertEqual(status.Get_error(), MPI.SUCCESS)
        self.assertFalse(status.Is_cancelled())
        greq.Wait()

    def testAll2(self):
        greq = MPI.Grequest.Start(None, None, None)
        self.assertFalse(greq.Test())
        greq.Cancel()
        greq.Complete()
        status = MPI.Status()
        self.assertTrue(greq.Test(status))
        self.assertEqual(status.Get_source(), MPI.ANY_SOURCE)
        self.assertEqual(status.Get_tag(), MPI.ANY_TAG)
        self.assertEqual(status.Get_error(), MPI.SUCCESS)
        self.assertFalse(status.Is_cancelled())
        greq.Wait()

    def testPyCompleteTest(self):
        greq = MPI.Grequest.Start()
        self.assertFalse(greq.Test())
        greq.cancel()
        greq.complete(42)
        status = MPI.Status()
        flag, result = greq.test(status)
        self.assertTrue(flag)
        self.assertEqual(result, 42)
        self.assertEqual(status.Get_source(), MPI.ANY_SOURCE)
        self.assertEqual(status.Get_tag(), MPI.ANY_TAG)
        self.assertEqual(status.Get_error(), MPI.SUCCESS)
        self.assertFalse(status.Is_cancelled())
        obj = greq.wait()
        self.assertIsNone(obj)

    def testPyCompleteWait(self):
        greq = MPI.Grequest.Start()
        self.assertFalse(greq.Test())
        greq.cancel()
        greq.complete(42)
        status = MPI.Status()
        result = greq.wait(status)
        self.assertEqual(result, 42)
        self.assertEqual(status.Get_source(), MPI.ANY_SOURCE)
        self.assertEqual(status.Get_tag(), MPI.ANY_TAG)
        self.assertEqual(status.Get_error(), MPI.SUCCESS)
        self.assertFalse(status.Is_cancelled())
        flag, obj = greq.test()
        self.assertTrue(flag)
        self.assertIsNone(obj)


if __name__ == "__main__":
    unittest.main()
