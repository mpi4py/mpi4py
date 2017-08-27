from mpi4py import MPI
import mpiunittest as unittest

class GReqCtx(object):

    source = 3
    tag    = 7
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
        

@unittest.skipMPI('MPI(<2.0)')
class TestGrequest(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
