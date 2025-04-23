import mpiunittest as unittest

from mpi4py import MPI


class TestSession(unittest.TestCase):
    #
    def testSessionInit(self):
        session = MPI.Session()
        self.assertFalse(session)
        self.assertEqual(session, MPI.SESSION_NULL)
        session = MPI.Session.Init()
        self.assertTrue(session)
        self.assertNotEqual(session, MPI.SESSION_NULL)
        self.assertEqual(session, MPI.Session(session))
        session.Finalize()

    def testSessionGetInfo(self):
        session = MPI.Session.Init()
        info = session.Get_info()
        info.Free()
        session.Finalize()

    def testSessionPsets(self):
        session = MPI.Session.Init()
        num_psets = session.Get_num_psets()
        for n in range(num_psets):
            name = session.Get_nth_pset(n)
            self.assertGreater(len(name), 0)
        session.Finalize()

    def testSessionPsetInfo(self):
        session = MPI.Session.Init()
        num_psets = session.Get_num_psets()
        for n in range(num_psets):
            name = session.Get_nth_pset(n)
            info = session.Get_pset_info(name)
            info.Free()
        session.Finalize()

    def testSessionPsetGroup(self):
        session = MPI.Session.Init()
        num_psets = session.Get_num_psets()
        for n in range(num_psets):
            name = session.Get_nth_pset(n)
            try:
                group = session.Create_group(name)
                group.Free()
                group = MPI.Group.Create_from_session_pset(session, name)
                group.Free()
            except MPI.Exception as exc:  # openmpi
                UNSUPPORTED = MPI.ERR_OTHER
                if exc.Get_error_class() != UNSUPPORTED:
                    raise
        session.Finalize()

    def testSessionSELF(self):
        session = MPI.Session.Init()
        name = "mpi://SELF"
        info = session.Get_pset_info(name)
        self.assertEqual(info.Get("mpi_size"), "1")
        info.Free()
        group = session.Create_group(name)
        self.assertEqual(group.Get_rank(), 0)
        self.assertEqual(group.Get_size(), 1)
        group.Free()
        session.Finalize()

    def testSessionWORLD(self):
        comm = MPI.COMM_WORLD
        session = MPI.Session.Init()
        name = "mpi://WORLD"
        info = session.Get_pset_info(name)
        size = comm.Get_size()
        self.assertEqual(info.Get("mpi_size"), str(size))
        info.Free()
        group = session.Create_group(name)
        self.assertEqual(group.Get_size(), comm.Get_size())
        self.assertEqual(group.Get_rank(), comm.Get_rank())
        group.Free()
        session.Finalize()

    def testBuffering(self):
        session = MPI.Session.Init()
        buf = MPI.Alloc_mem((1 << 16) + MPI.BSEND_OVERHEAD)
        try:
            with self.catchNotImplementedError(4, 1):
                session.Attach_buffer(buf)
            with self.catchNotImplementedError(4, 1):
                session.Flush_buffer()
            with self.catchNotImplementedError(4, 1):
                session.Iflush_buffer().Wait()
        finally:
            with self.catchNotImplementedError(4, 1):
                oldbuf = session.Detach_buffer()
                self.assertEqual(oldbuf.address, buf.address)
                self.assertEqual(oldbuf.nbytes, buf.nbytes)
            MPI.Free_mem(buf)
            with self.catchNotImplementedError(4, 1):
                session.Attach_buffer(MPI.BUFFER_AUTOMATIC)
                bufauto = session.Detach_buffer()
                self.assertEqual(bufauto, MPI.BUFFER_AUTOMATIC)
            session.Finalize()

    def testPickle(self):
        from pickle import dumps, loads

        session = MPI.Session.Init()
        with self.assertRaises(ValueError):
            loads(dumps(session))
        session.Finalize()


try:
    MPI.Session.Init().Finalize()
except NotImplementedError:
    unittest.disable(TestSession, "mpi-session")


if __name__ == "__main__":
    unittest.main()
