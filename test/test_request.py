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
        self.assertEqual(ret, out)
        ret = MPI.Request.Waitsome(self.REQUESTS, None)
        self.assertEqual(ret, out)
        for statuses in (self.STATUSES, []):
            ret = MPI.Request.Waitsome(self.REQUESTS, statuses)
            self.assertEqual(ret, out)
            self.assertEqual(len(statuses), len(self.REQUESTS))

    def testTestsome(self):
        out = (MPI.UNDEFINED, [])
        ret = MPI.Request.Testsome(self.REQUESTS)
        self.assertEqual(ret, out)
        ret = MPI.Request.Testsome(self.REQUESTS, None)
        self.assertEqual(ret, out)
        for statuses in (self.STATUSES, []):
            ret = MPI.Request.Testsome(self.REQUESTS, statuses)
            self.assertEqual(ret, out)
            self.assertEqual(len(statuses), len(self.REQUESTS))


if __name__ == '__main__':
    unittest.main()
