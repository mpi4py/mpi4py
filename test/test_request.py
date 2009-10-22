from mpi4py import MPI
import mpiunittest as unittest


class TestRequest(unittest.TestCase):

    def setUp(self):
        self.REQUEST = MPI.Request()
        self.STATUS  = MPI.Status()

    def testWait(self):
        self.REQUEST.Wait()
        self.REQUEST.Wait(None)
        self.REQUEST.Wait(self.STATUS)

    def testTest(self):
        self.REQUEST.Wait()
        self.REQUEST.Wait(None)
        self.REQUEST.Test(self.STATUS)

    def testGetStatus(self):
        try: flag = self.REQUEST.Get_status()
        except NotImplementedError: return
        self.assertTrue(flag)
        flag = self.REQUEST.Get_status(self.STATUS)
        self.assertTrue(flag)
        self.assertEqual(self.STATUS.Get_source(), MPI.ANY_SOURCE)
        self.assertEqual(self.STATUS.Get_tag(),    MPI.ANY_TAG)
        self.assertEqual(self.STATUS.Get_error(),  MPI.SUCCESS)
        self.assertEqual(self.STATUS.Get_count(MPI.BYTE),    0)
        self.assertEqual(self.STATUS.Get_elements(MPI.BYTE), 0)
        try: self.assertFalse(self.STATUS.Is_cancelled())
        except NotImplementedError: pass

class TestRequestArray(unittest.TestCase):

    def setUp(self):
        self.REQUESTS  = [MPI.Request() for i in range(5)]
        self.STATUSES  = [MPI.Status()  for i in range(5)]

    def testWaitany(self):
        MPI.Request.Waitany(self.REQUESTS)
        MPI.Request.Waitany(self.REQUESTS, None)
        MPI.Request.Waitany(self.REQUESTS, self.STATUSES[0])

    def testTestany(self):
        MPI.Request.Testany(self.REQUESTS)
        MPI.Request.Testany(self.REQUESTS, None)
        MPI.Request.Testany(self.REQUESTS, self.STATUSES[0])

    def testWaitall(self):
        MPI.Request.Waitall(self.REQUESTS)
        MPI.Request.Waitall(self.REQUESTS, None)
        for statuses in (self.STATUSES, []):
            MPI.Request.Waitall(self.REQUESTS, statuses)
            self.assertEqual(len(statuses), len(self.REQUESTS))

    def testTestall(self):
        MPI.Request.Testall(self.REQUESTS)
        MPI.Request.Testall(self.REQUESTS, None)
        for statuses in (self.STATUSES, []):
            MPI.Request.Testall(self.REQUESTS, statuses)
            self.assertEqual(len(statuses), len(self.REQUESTS))

    def testWaitsome(self):
        out = (MPI.UNDEFINED, [])
        ret = MPI.Request.Waitsome(self.REQUESTS)
        self.assertEqual((ret[0],list(ret[1])), out)
        ret = MPI.Request.Waitsome(self.REQUESTS, None)
        self.assertEqual((ret[0],list(ret[1])), out)
        for statuses in (self.STATUSES, []):
            ret = MPI.Request.Waitsome(self.REQUESTS, statuses)
            self.assertEqual((ret[0],list(ret[1])), out)
            self.assertEqual(len(statuses), len(self.REQUESTS))

    def testTestsome(self):
        out = (MPI.UNDEFINED, [])
        ret = MPI.Request.Testsome(self.REQUESTS)
        self.assertEqual((ret[0],list(ret[1])), out)
        ret = MPI.Request.Testsome(self.REQUESTS, None)
        self.assertEqual((ret[0],list(ret[1])), out)
        for statuses in (self.STATUSES, []):
            ret = MPI.Request.Testsome(self.REQUESTS, statuses)
            self.assertEqual((ret[0],list(ret[1])), out)
            self.assertEqual(len(statuses), len(self.REQUESTS))

_name, _version = MPI.get_vendor()
if (_name == 'MPICH1' or
    _name == 'LAM/MPI'):
    del TestRequest.testGetStatus

if __name__ == '__main__':
    unittest.main()
