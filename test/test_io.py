from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl
import os, tempfile
import platform


def arrayimpl_loop_io():
    openmpi = unittest.mpi_predicate('openmpi(<5.0.0)')
    is_i386 = platform.machine() in ('i386', 'i686')
    for array, typecode in arrayimpl.loop():
        if unittest.is_mpi_gpu('mvapich', array): continue
        if openmpi and is_i386 and typecode in ('g', 'G'): continue
        yield array, typecode

scalar = arrayimpl.scalar

class BaseTestIO:

    COMM = MPI.COMM_NULL
    FILE = MPI.FILE_NULL

    prefix = 'mpi4py-'

    def setUp(self):
        comm = self.COMM
        world_size = MPI.COMM_WORLD.Get_size()
        world_rank = MPI.COMM_WORLD.Get_rank()
        prefix = self.prefix
        if comm.Get_size() < world_size:
            prefix += f'{world_rank}-'
        fname = None
        if comm.Get_rank() == 0:
            fd, fname = tempfile.mkstemp(prefix=prefix)
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


class BaseTestIOBasic(BaseTestIO):

    # non-collective

    def testReadWriteAt(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                    self.assertEqual(value, scalar(42))
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()

    def testIReadIWriteAt(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                    self.assertEqual(value, scalar(42))
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()

    def testReadWrite(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                            self.assertEqual(value, scalar(42))
                        self.assertEqual(rbuf[-1], scalar(-1))
                    comm.Barrier()

    def testIReadIWrite(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                            self.assertEqual(value, scalar(42))
                        self.assertEqual(rbuf[-1], scalar(-1))
                    comm.Barrier()

    def testReadWriteShared(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()

    def testIReadIWriteShared(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()

    # collective

    def testReadWriteAtAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                    self.assertEqual(value, scalar(42))
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()

    def testIReadIWriteAtAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                try: # MPI 3.1
                    etype = array.TypeMap[typecode]
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
                        self.assertEqual(value, scalar(42))
                    self.assertEqual(rbuf[-1], scalar(-1))
                    comm.Barrier()
                except NotImplementedError:
                    if MPI.Get_version() >= (3, 1): raise
                    self.skipTest('mpi-iwrite_at_all')

    def testReadWriteAtAllBeginEnd(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                    self.assertEqual(value, scalar(42))
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()

    def testReadWriteAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                    self.assertEqual(value, scalar(42))
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()

    def testIReadIWriteAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                try: # MPI 3.1
                    etype = array.TypeMap[typecode]
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
                        self.assertEqual(value, scalar(42))
                    self.assertEqual(rbuf[-1], scalar(-1))
                    comm.Barrier()
                except NotImplementedError:
                    if MPI.Get_version() >= (3, 1): raise
                    self.skipTest('mpi-iwrite_all')

    def testReadWriteAllBeginEnd(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                    self.assertEqual(value, scalar(42))
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()

    def testReadWriteOrdered(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                    self.assertEqual(value, scalar(rank%42))
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()

    def testReadWriteOrderedBeginEnd(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                etype = array.TypeMap[typecode]
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
                    self.assertEqual(value, scalar(rank%42))
                self.assertEqual(rbuf[-1], scalar(-1))
                comm.Barrier()


class BaseTestIOView(BaseTestIO):

    def _test_contiguous(self, combiner):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                comm.Barrier()
                fh.Set_size(0)
                btype = array.TypeMap[typecode]
                if combiner == MPI.COMBINER_NAMED:
                    etype = btype
                    ftype = btype
                if combiner == MPI.COMBINER_DUP:
                    etype = btype.Dup().Commit()
                    ftype = etype.Dup().Commit()
                if combiner == MPI.COMBINER_CONTIGUOUS:
                    etype = btype
                    ftype = etype.Create_contiguous(7).Commit()
                fh.Set_view(0, etype, ftype)
                for i in range(3):
                    wval = 10*(rank+1)+i
                    wbuf = array(wval, typecode, 7)
                    fh.Write_ordered(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Set_view(0, etype, ftype)
                for i in range(3):
                    rval = 10*(rank+1)+i
                    rbuf = array(0, typecode, 7)
                    fh.Read_ordered(rbuf.as_raw())
                    for value in rbuf:
                        self.assertEqual(value, scalar(rval))
                if ftype != btype:
                    ftype.Free()
                fh.Set_view(0, etype, etype)
                for i in range(3):
                    for r in range(size):
                        rval = 10*(r+1)+i
                        rbuf = array(0, typecode, 7)
                        fh.Read_all(rbuf.as_raw())
                        for value in rbuf:
                            self.assertEqual(value, scalar(rval))
                if etype != btype:
                    etype.Free()

    def _test_strided(self, combiner):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                comm.Barrier()
                fh.Set_size(0)
                etype = array.TypeMap[typecode]
                esize = etype.size
                index1 = [0, 2, 4, 6]
                index2 = [1, 3, 5]
                if combiner in (
                    MPI.COMBINER_VECTOR,
                    MPI.COMBINER_HVECTOR,
                ):
                    if combiner == MPI.COMBINER_VECTOR:
                        ftype1 = etype.Create_vector(4, 1, 2).Commit()
                    if combiner == MPI.COMBINER_HVECTOR:
                        ftype1 = etype.Create_hvector(4, 1, esize*2).Commit()
                    fbase2 = etype.Create_indexed([1]*3, index2)
                    ftype2 = fbase2.Create_resized(0, ftype1.extent).Commit()
                    fbase2.Free()
                if combiner in (
                    MPI.COMBINER_INDEXED,
                    MPI.COMBINER_INDEXED_BLOCK,
                    MPI.COMBINER_HINDEXED,
                    MPI.COMBINER_HINDEXED_BLOCK,
                ):
                    INDEXED        = MPI.COMBINER_INDEXED
                    INDEXED_BLOCK  = MPI.COMBINER_INDEXED_BLOCK
                    HINDEXED       = MPI.COMBINER_HINDEXED
                    HINDEXED_BLOCK = MPI.COMBINER_HINDEXED_BLOCK
                    if combiner == INDEXED:
                        Create = MPI.Datatype.Create_indexed
                    if combiner == HINDEXED:
                        Create = MPI.Datatype.Create_hindexed
                    if combiner == INDEXED_BLOCK:
                        Create = MPI.Datatype.Create_indexed_block
                    if combiner == HINDEXED_BLOCK:
                        Create = MPI.Datatype.Create_hindexed_block
                    if combiner in (INDEXED, HINDEXED):
                        blens1 = [1] * 4
                        blens2 = [1] * 3
                    if combiner in (INDEXED_BLOCK, HINDEXED_BLOCK):
                        blens1 = 1
                        blens2 = 1
                    if combiner in (INDEXED, INDEXED_BLOCK):
                        disps1 = index1
                        disps2 = index2
                    if combiner in ( HINDEXED, HINDEXED_BLOCK):
                        disps1 = [esize*i for i in index1]
                        disps2 = [esize*i for i in index2]
                    ftype1 = Create(etype, blens1, disps1).Commit()
                    fbase2 = Create(etype, blens2, disps2)
                    ftype2 = fbase2.Create_resized(0, ftype1.extent).Commit()
                    fbase2.Free()
                if combiner == MPI.COMBINER_STRUCT:
                    ftype1 = MPI.Datatype.Create_struct(
                        [1] * 4,
                        [esize*i for i in index1],
                        [etype] * 4,
                    ).Commit()
                    fbase2 = MPI.Datatype.Create_struct(
                        [1] * 3,
                        [esize*i for i in index2],
                        [etype] * 3,
                    )
                    ftype2 = fbase2.Create_resized(
                        0, ftype1.extent,
                    ).Commit()
                    fbase2.Free()
                #
                fh.Set_view(0, etype, ftype1)
                for i in range(3):
                    wval = 10*(rank+1)+i
                    warg = [wval+j for j in range(0,7,2)]
                    wbuf = array(warg, typecode)
                    fh.Write_ordered(wbuf.as_raw())
                fh.Set_view(0, etype, ftype2)
                for i in range(3):
                    wval = 10*(rank+1)+i
                    warg = [wval+j for j in range(1,7,2)]
                    wbuf = array(warg, typecode)
                    fh.Write_ordered(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Set_view(0, etype, ftype1)
                for i in range(3):
                    rval = 10*(rank+1)+i
                    rbuf = array(0, typecode, 4)
                    fh.Read_ordered(rbuf.as_raw())
                    for value, j in zip(rbuf, range(0,7,2)):
                        self.assertEqual(value, scalar(rval+j))
                fh.Set_view(0, etype, ftype2)
                for i in range(3):
                    rval = 10*(rank+1)+i
                    rbuf = array(0, typecode, 3)
                    fh.Read_ordered(rbuf.as_raw())
                    for value, j in zip(rbuf, range(1,7,2)):
                        self.assertEqual(value, scalar(rval+j))
                ftype1.Free()
                ftype2.Free()
                fh.Set_view(0, etype, etype)
                for i in range(3):
                    for r in range(size):
                        rval = 10*(r+1)+i
                        rbuf = array(0, typecode, 7)
                        fh.Read_all(rbuf.as_raw())
                        for j, value in enumerate(rbuf):
                            self.assertEqual(value, scalar(rval+j))

    def testNamed(self):
        self._test_contiguous(MPI.COMBINER_NAMED)

    def testDup(self):
        self._test_contiguous(MPI.COMBINER_DUP)

    def testContiguous(self):
        self._test_contiguous(MPI.COMBINER_CONTIGUOUS)

    def testVector(self):
        self._test_strided(MPI.COMBINER_VECTOR)

    def testHVector(self):
        self._test_strided(MPI.COMBINER_HVECTOR)

    def testIndexed(self):
        self._test_strided(MPI.COMBINER_INDEXED)

    def testHIndexed(self):
        self._test_strided(MPI.COMBINER_HINDEXED)

    def testIndexedBlock(self):
        self._test_strided(MPI.COMBINER_INDEXED_BLOCK)

    def testHIndexedBlock(self):
        self._test_strided(MPI.COMBINER_HINDEXED_BLOCK)

    def testStruct(self):
        self._test_strided(MPI.COMBINER_STRUCT)

    def testSubarray(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                comm.Barrier()
                fh.Set_size(0)
                etype = array.TypeMap[typecode]
                ftype = etype.Create_subarray(
                    [size*7, 5],
                    [7, 5],
                    [rank*7, 0],
                ).Commit()
                fh.Set_view(0, etype, ftype)
                for i in range(3):
                    wval = 10*(rank+1)+i
                    wbuf = array(wval, typecode, 7*5)
                    fh.Write_all(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Set_view(0, etype, ftype)
                for i in range(3):
                    rval = 10*(rank+1)+i
                    rbuf = array(0, typecode, 7*5)
                    fh.Read_all(rbuf.as_raw())
                    for value in rbuf:
                        self.assertEqual(value, scalar(rval))
                ftype.Free()
                fh.Set_view(0, etype, etype)
                for i in range(3):
                    for r in range(size):
                        rval = 10*(r+1)+i
                        rbuf = array(0, typecode, 7*5)
                        fh.Read_all(rbuf.as_raw())
                        for value in rbuf:
                            self.assertEqual(value, scalar(rval))

    def testDarrayBlock(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        block = MPI.DISTRIBUTE_BLOCK
        none = MPI.DISTRIBUTE_NONE
        dflt = MPI.DISTRIBUTE_DFLT_DARG
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                comm.Barrier()
                fh.Set_size(0)
                etype = array.TypeMap[typecode]
                ftype = etype.Create_darray(
                    size, rank,
                    [size*7, 5],
                    [block, none],
                    [dflt, dflt],
                    [size, 1],
                ).Commit()
                fh.Set_view(0, etype, ftype)
                for i in range(3):
                    wval = 10*(rank+1)+i
                    wbuf = array(wval, typecode, 7*5)
                    fh.Write_all(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Set_view(0, etype, ftype)
                for i in range(3):
                    rval = 10*(rank+1)+i
                    rbuf = array(0, typecode, 7*5)
                    fh.Read_all(rbuf.as_raw())
                    for value in rbuf:
                        self.assertEqual(value, scalar(rval))
                ftype.Free()
                fh.Set_view(0, etype, etype)
                for i in range(3):
                    for r in range(size):
                        for j in range(7):
                            rval = 10*(r+1)+i
                            rbuf = array(0, typecode, 5)
                            fh.Read_all(rbuf.as_raw())
                            for value in rbuf:
                                self.assertEqual(value, scalar(rval))

    def testDarrayCyclic(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        fh = self.FILE
        cyclic = MPI.DISTRIBUTE_CYCLIC
        none = MPI.DISTRIBUTE_NONE
        dflt = MPI.DISTRIBUTE_DFLT_DARG
        for array, typecode in arrayimpl_loop_io():
            with arrayimpl.test(self):
                comm.Barrier()
                fh.Set_size(0)
                etype = array.TypeMap[typecode]
                ftype = etype.Create_darray(
                    size, rank,
                    [size*7, 5],
                    [cyclic, none],
                    [1, dflt],
                    [size, 1],
                ).Commit()
                fh.Set_view(0, etype, ftype)
                for i in range(3):
                    wval = 10*(rank+1)+i
                    wbuf = array(wval, typecode, 7*5)
                    fh.Write_all(wbuf.as_raw())
                fh.Sync()
                comm.Barrier()
                fh.Set_view(0, etype, ftype)
                for i in range(3):
                    rval = 10*(rank+1)+i
                    rbuf = array(0, typecode, 7*5)
                    fh.Read_all(rbuf.as_raw())
                    for value in rbuf:
                        self.assertEqual(value, scalar(rval))
                ftype.Free()
                fh.Set_view(0, etype, etype)
                for i in range(3):
                    for j in range(7):
                        for r in range(size):
                            rval = 10*(r+1)+i
                            rbuf = array(0, typecode, 5)
                            fh.Read_all(rbuf.as_raw())
                            for value in rbuf:
                                self.assertEqual(value, scalar(rval))


@unittest.skipMPI('MPICH1')
@unittest.skipMPI('LAM/MPI')
class TestIOBasicSelf(BaseTestIOBasic, unittest.TestCase):
    COMM = MPI.COMM_SELF

@unittest.skipMPI('openmpi(<2.2.0)')
@unittest.skipMPI('msmpi')
@unittest.skipMPI('MPICH2')
@unittest.skipMPI('MPICH1')
@unittest.skipMPI('LAM/MPI')
class TestIOBasicWorld(BaseTestIOBasic, unittest.TestCase):
    COMM = MPI.COMM_WORLD

@unittest.skipMPI('mpich(>=4.0.0,<4.1.0)')
@unittest.skipMPI('openmpi(<2.2.0)')
@unittest.skipMPI('MPICH1')
@unittest.skipMPI('LAM/MPI')
class TestIOViewSelf(BaseTestIOView, unittest.TestCase):
    COMM = MPI.COMM_SELF

@unittest.skipMPI('mpich(>=4.0.0,<4.1.0)')
@unittest.skipMPI('openmpi(<2.2.0)')
@unittest.skipMPI('msmpi')
@unittest.skipMPI('MPICH2')
@unittest.skipMPI('MPICH1')
@unittest.skipMPI('LAM/MPI')
class TestIOViewWorld(BaseTestIOView, unittest.TestCase):
    COMM = MPI.COMM_WORLD


@unittest.skipMPI('msmpi')
@unittest.skipMPI('openmpi')
@unittest.skipMPI('intelmpi', os.name == 'nt')
class TestDatarep(unittest.TestCase):

    def testRegister(self):
        def extent_fn(dtype):
            return dtype.extent
        try:
            MPI.Register_datarep(
                "mpi4py-datarep-dummy",
                read_fn=None,
                write_fn=None,
                extent_fn=extent_fn,
            )
        except NotImplementedError:
            self.skipTest('mpi-register-datrep')
        with self.assertRaises(MPI.Exception) as cm:
            MPI.Register_datarep(
                "mpi4py-datarep-dummy",
                read_fn=None,
                write_fn=None,
                extent_fn=extent_fn,
            )
        ierr = cm.exception.Get_error_class()
        self.assertEqual(ierr, MPI.ERR_DUP_DATAREP)


def have_feature():
    case = BaseTestIO()
    case.COMM = TestIOBasicSelf.COMM
    case.prefix = TestIOBasicSelf.prefix
    case.setUp()
    case.tearDown()
try:
    have_feature()
except NotImplementedError:
    unittest.disable(BaseTestIO, 'mpi-io')


if __name__ == '__main__':
    unittest.main()
