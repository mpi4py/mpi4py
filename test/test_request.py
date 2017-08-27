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
        self.assertTrue(self.REQUEST.Wait() is True)
        self.REQUEST.wait()
        self.REQUEST.wait(None)
        self.REQUEST.wait(self.STATUS)
        self.assertTrue(self.REQUEST.wait() is None)

    def testTest(self):
        self.REQUEST.Test()
        self.REQUEST.Test(None)
        self.REQUEST.Test(self.STATUS)
        self.assertTrue(self.REQUEST.Test() is True)
        self.REQUEST.test()
        self.REQUEST.test(None)
        self.REQUEST.test(self.STATUS)
        self.assertTrue(self.REQUEST.test() == (True, None))

    @unittest.skipMPI('MPICH1')
    @unittest.skipMPI('LAM/MPI')
    def testGetStatus(self):
        try:
            flag = self.REQUEST.Get_status()
        except NotImplementedError:
            self.skipTest('mpi-request-get_status')
        self.assertTrue(flag)
        flag = self.REQUEST.Get_status(self.STATUS)
        self.assertTrue(flag)
        self.assertEqual(self.STATUS.Get_source(), MPI.ANY_SOURCE)
        self.assertEqual(self.STATUS.Get_tag(),    MPI.ANY_TAG)
        self.assertEqual(self.STATUS.Get_error(),  MPI.SUCCESS)
        self.assertEqual(self.STATUS.Get_count(MPI.BYTE),    0)
        self.assertEqual(self.STATUS.Get_elements(MPI.BYTE), 0)
        try:
            self.assertFalse(self.STATUS.Is_cancelled())
        except NotImplementedError:
            self.skipTest('mpi-status-is_cancelled')


class TestRequestArray(unittest.TestCase):

    def setUp(self):
        self.REQUESTS  = [MPI.Request() for i in range(5)]
        self.STATUSES  = [MPI.Status()  for i in range(5)]

    def testWaitany(self):
        MPI.Request.Waitany(self.REQUESTS)
        MPI.Request.Waitany(self.REQUESTS, None)
        MPI.Request.Waitany(self.REQUESTS, self.STATUSES[0])
        MPI.Request.waitany(self.REQUESTS)
        MPI.Request.waitany(self.REQUESTS, None)
        MPI.Request.waitany(self.REQUESTS, self.STATUSES[0])

    def testTestany(self):
        MPI.Request.Testany(self.REQUESTS)
        MPI.Request.Testany(self.REQUESTS, None)
        MPI.Request.Testany(self.REQUESTS, self.STATUSES[0])
        MPI.Request.testany(self.REQUESTS)
        MPI.Request.testany(self.REQUESTS, None)
        MPI.Request.testany(self.REQUESTS, self.STATUSES[0])

    def testWaitall(self):
        MPI.Request.Waitall(self.REQUESTS)
        MPI.Request.Waitall(self.REQUESTS, None)
        self.assertTrue(MPI.Request.Waitall(self.REQUESTS) is True)
        for statuses in (tuple(self.STATUSES), (self.STATUSES[0],), ()):
            MPI.Request.Waitall(self.REQUESTS, statuses)
        for statuses in (self.STATUSES, []):
            MPI.Request.Waitall(self.REQUESTS, statuses)
            self.assertEqual(len(statuses), len(self.REQUESTS))
        MPI.Request.waitall(self.REQUESTS)
        MPI.Request.waitall(self.REQUESTS, None)
        for statuses in (self.STATUSES, []):
            MPI.Request.waitall(self.REQUESTS, statuses)
            self.assertEqual(len(statuses), len(self.REQUESTS))

    def testTestall(self):
        MPI.Request.Testall(self.REQUESTS)
        MPI.Request.Testall(self.REQUESTS, None)
        self.assertTrue(MPI.Request.Testall(self.REQUESTS) is True)
        for statuses in (self.STATUSES, []):
            MPI.Request.Testall(self.REQUESTS, statuses)
            self.assertEqual(len(statuses), len(self.REQUESTS))
        MPI.Request.testall(self.REQUESTS)
        MPI.Request.testall(self.REQUESTS, None)
        for statuses in (self.STATUSES, []):
            MPI.Request.testall(self.REQUESTS, statuses)
            self.assertEqual(len(statuses), len(self.REQUESTS))

    def testWaitsome(self):
        ret = MPI.Request.Waitsome(self.REQUESTS)
        self.assertEqual(ret, None)
        ret = MPI.Request.Waitsome(self.REQUESTS, None)
        self.assertEqual(ret, None)
        for statuses in (self.STATUSES, []):
            ret = MPI.Request.Waitsome(self.REQUESTS, statuses)
            self.assertEqual(ret, None)
            self.assertEqual(len(statuses), len(self.REQUESTS))

    def testTestsome(self):
        ret = MPI.Request.Testsome(self.REQUESTS)
        self.assertEqual(ret, None)
        ret = MPI.Request.Testsome(self.REQUESTS, None)
        self.assertEqual(ret, None)
        for statuses in (self.STATUSES, []):
            ret = MPI.Request.Testsome(self.REQUESTS, statuses)
            self.assertEqual(ret, None)
            self.assertEqual(len(statuses), len(self.REQUESTS))


if __name__ == '__main__':
    unittest.main()
