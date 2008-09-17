from mpi4py import MPI
import mpiunittest as unittest

class GReqCtx:
    source = 1
    tag    = 7
    completed = False
    free_called = False

    def query(self, status):
        status.Set_source(self.source)
        status.Set_tag(self.tag)
    def free(self):
        self.free_called = True
    def cancel(self, completed):
        if completed is not self.completed:
            raise AssertionError()

class TestGrequest(unittest.TestCase):

    def testAll(self):

        ctx = GReqCtx()
        greq = MPI.Grequest.Start(ctx.query, ctx.free, ctx.cancel)
        self.assertFalse(greq.Test())
        self.assertFalse(ctx.free_called)

        ctx.completed = False
        greq.Cancel()
        greq.Complete()
        ctx.completed = True
        greq.Cancel()

        status = MPI.Status()
        self.assertTrue(greq.Test(status))
        self.assertEqual(status.Get_source(), ctx.source)
        self.assertEqual(status.Get_tag(), ctx.tag)

        greq.Wait()
        self.assertTrue(ctx.free_called)

_name, _version = MPI.get_vendor()
if _name == 'MPICH1' or _name == 'LAM/MPI' \
       or _version < (2, 0):
    del GReqCtx
    del TestGrequest

if __name__ == '__main__':
    unittest.main()
