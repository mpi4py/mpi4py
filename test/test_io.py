from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl
import os, tempfile

class BaseTestIO(object):

    COMM = MPI.COMM_NULL
    FILE = MPI.FILE_NULL

    prefix = 'mpi4py-'

    def setUp(self):
        comm = self.COMM
        fname = None
        if comm.Get_rank() == 0:
            fd, fname = tempfile.mkstemp(prefix=self.prefix)
            os.close(fd)
        fname = comm.bcast(fname, 0)
        amode  = MPI.MODE_RDWR | MPI.MODE_CREATE
        amode |= MPI.MODE_DELETE_ON_CLOSE
        amode |= MPI.MODE_UNIQUE_OPEN
        info = MPI.INFO_NULL
        try:
            self.FILE = MPI.File.Open(comm, fname, amode, info)
        except Exception:
            if comm.Get_rank() == 0:
                os.remove(fname)
            raise

    def tearDown(self):
        if self.FILE:
            self.FILE.Close()
        self.COMM.Barrier()

    # non-collective

    def testReadWriteAt(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(42, typecode, count)
                fh.Write_at(count*rank, wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Read_at(count*rank, rbuf.as_mpi_c(count))
                for value in rbuf[:-1]:
                    self.assertEqual(value, 42)
                self.assertEqual(rbuf[-1], -1)

    def testIReadIWriteAt(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(42, typecode, count)
                fh.Iwrite_at(count*rank, wbuf.as_raw()).Wait()
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Iread_at(count*rank, rbuf.as_mpi_c(count)).Wait()
                for value in rbuf[:-1]:
                    self.assertEqual(value, 42)
                self.assertEqual(rbuf[-1], -1)

    def testReadWrite(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(42, typecode, count)
                for r in range(size):
                    if r == rank:
                        fh.Seek(0, MPI.SEEK_SET)
                        fh.Write(wbuf.as_raw())
                    fh.Sync()
                    comm.Barrier()
                    fh.Sync()
                    for n in range(0, len(wbuf)):
                        rbuf = array(-1, typecode, n+1)
                        fh.Seek(0, MPI.SEEK_SET)
                        fh.Read(rbuf.as_mpi_c(n))
                        for value in rbuf[:-1]:
                            self.assertEqual(value, 42)
                        self.assertEqual(rbuf[-1], -1)

    def testIReadIWrite(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(42, typecode, count)
                for r in range(size):
                    if r == rank:
                        fh.Seek(0, MPI.SEEK_SET)
                        fh.Iwrite(wbuf.as_raw()).Wait()
                    fh.Sync()
                    comm.Barrier()
                    fh.Sync()
                    for n in range(0, len(wbuf)):
                        rbuf = array(-1, typecode, n+1)
                        fh.Seek(0, MPI.SEEK_SET)
                        fh.Iread(rbuf.as_mpi_c(n)).Wait()
                        for value in rbuf[:-1]:
                            self.assertEqual(value, 42)
                        self.assertEqual(rbuf[-1], -1)

    def testReadWriteShared(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(rank%42, typecode, count)
                fh.Seek_shared(0, MPI.SEEK_SET)
                fh.Write_shared(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Seek_shared(0, MPI.SEEK_SET)
                fh.Read_shared(rbuf.as_mpi_c(count))
                for value in rbuf[:-1]:
                    self.assertTrue(0<=value<42)
                    self.assertEqual(value, rbuf[0])
                self.assertEqual(rbuf[-1], -1)

    def testIReadIWriteShared(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(rank%42, typecode, count)
                fh.Seek_shared(0, MPI.SEEK_SET)
                fh.Iwrite_shared(wbuf.as_raw()).Wait()
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Seek_shared(0, MPI.SEEK_SET)
                fh.Iread_shared(rbuf.as_mpi_c(count)).Wait()
                for value in rbuf[:-1]:
                    self.assertTrue(0<=value<42)
                    self.assertEqual(value, rbuf[0])
                self.assertEqual(rbuf[-1], -1)

    # collective

    def testReadWriteAtAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(42, typecode, count)
                fh.Write_at_all(count*rank, wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Read_at_all(count*rank, rbuf.as_mpi_c(count))
                for value in rbuf[:-1]:
                    self.assertEqual(value, 42)
                self.assertEqual(rbuf[-1], -1)

    def testIReadIWriteAtAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        try: # MPI 3.1
            for array in arrayimpl.ArrayTypes:
                for typecode in arrayimpl.TypeMap:
                    etype = arrayimpl.TypeMap[typecode]
                    fh.Set_size(0)
                    fh.Set_view(0, etype)
                    count = 13
                    wbuf = array(42, typecode, count)
                    fh.Iwrite_at_all(count*rank, wbuf.as_raw()).Wait()
                    fh.Sync()
                    comm.Barrier()
                    fh.Sync()
                    rbuf = array(-1, typecode, count+1)
                    fh.Iread_at_all(count*rank, rbuf.as_mpi_c(count)).Wait()
                    for value in rbuf[:-1]:
                        self.assertEqual(value, 42)
                    self.assertEqual(rbuf[-1], -1)
        except NotImplementedError:
            if MPI.Get_version() >= (3, 1): raise

    def testReadWriteAtAllBeginEnd(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(42, typecode, count)
                fh.Write_at_all_begin(count*rank, wbuf.as_raw())
                fh.Write_at_all_end(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Read_at_all_begin(count*rank, rbuf.as_mpi_c(count))
                fh.Read_at_all_end(rbuf.as_raw())
                for value in rbuf[:-1]:
                    self.assertEqual(value, 42)
                self.assertEqual(rbuf[-1], -1)

    def testReadWriteAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(42, typecode, count)
                fh.Seek(count*rank, MPI.SEEK_SET)
                fh.Write_all(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Seek(count*rank, MPI.SEEK_SET)
                fh.Read_all(rbuf.as_mpi_c(count))
                for value in rbuf[:-1]:
                    self.assertEqual(value, 42)
                self.assertEqual(rbuf[-1], -1)

    def testIReadIWriteAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        try: # MPI 3.1
            for array in arrayimpl.ArrayTypes:
                for typecode in arrayimpl.TypeMap:
                    etype = arrayimpl.TypeMap[typecode]
                    fh.Set_size(0)
                    fh.Set_view(0, etype)
                    count = 13
                    wbuf = array(42, typecode, count)
                    fh.Seek(count*rank, MPI.SEEK_SET)
                    fh.Iwrite_all(wbuf.as_raw()).Wait()
                    fh.Sync()
                    comm.Barrier()
                    fh.Sync()
                    rbuf = array(-1, typecode, count+1)
                    fh.Seek(count*rank, MPI.SEEK_SET)
                    fh.Iread_all(rbuf.as_mpi_c(count)).Wait()
                    for value in rbuf[:-1]:
                        self.assertEqual(value, 42)
                    self.assertEqual(rbuf[-1], -1)
        except NotImplementedError:
            if MPI.Get_version() >= (3, 1): raise

    def testReadWriteAllBeginEnd(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(42, typecode, count)
                fh.Seek(count*rank, MPI.SEEK_SET)
                fh.Write_all_begin(wbuf.as_raw())
                fh.Write_all_end(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Seek(count*rank, MPI.SEEK_SET)
                fh.Read_all_begin(rbuf.as_mpi_c(count))
                fh.Read_all_end(rbuf.as_raw())
                for value in rbuf[:-1]:
                    self.assertEqual(value, 42)
                self.assertEqual(rbuf[-1], -1)

    def testReadWriteOrdered(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(rank%42, typecode, count)
                fh.Seek_shared(0, MPI.SEEK_SET)
                fh.Write_ordered(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Seek_shared(0, MPI.SEEK_SET)
                fh.Read_ordered(rbuf.as_mpi_c(count))
                for value in rbuf[:-1]:
                    self.assertEqual(value, rank%42)
                self.assertEqual(rbuf[-1], -1)

    def testReadWriteOrderedBeginEnd(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                etype = arrayimpl.TypeMap[typecode]
                fh.Set_size(0)
                fh.Set_view(0, etype)
                count = 13
                wbuf = array(rank%42, typecode, count)
                fh.Seek_shared(0, MPI.SEEK_SET)
                fh.Write_ordered_begin(wbuf.as_raw())
                fh.Write_ordered_end(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Sync()
                rbuf = array(-1, typecode, count+1)
                fh.Seek_shared(0, MPI.SEEK_SET)
                fh.Read_ordered_begin(rbuf.as_mpi_c(count))
                fh.Read_ordered_end(rbuf.as_raw())
                for value in rbuf[:-1]:
                    self.assertEqual(value, rank%42)
                self.assertEqual(rbuf[-1], -1)

class TestIOSelf(BaseTestIO, unittest.TestCase):
    COMM = MPI.COMM_SELF
    prefix = BaseTestIO.prefix + ('%d-' % MPI.COMM_WORLD.Get_rank())

class TestIOWorld(BaseTestIO, unittest.TestCase):
    COMM = MPI.COMM_WORLD


import sys
name, version = MPI.get_vendor()
if name == 'Open MPI':
    if version < (2,2,0):
        TestIOWorld = None
    if version < (1,8,0):
        TestIOWorld = None
    if sys.platform.startswith('win'):
        TestIOSelf = None
        TestIOWorld = None
if name == 'MPICH2':
    TestIOWorld = None
if name == 'Microsoft MPI':
    TestIOWorld = None
if name == 'MPICH1':
    TestIOSelf = None
    TestIOWorld = None
if name == 'LAM/MPI':
    TestIOSelf = None
    TestIOWorld = None

try:
    dummy = BaseTestIO()
    dummy.COMM = MPI.COMM_SELF
    dummy.setUp()
    dummy.tearDown()
    del dummy
except NotImplementedError:
    TestIOSelf = None
    TestIOWorld = None

if __name__ == '__main__':
    unittest.main()
