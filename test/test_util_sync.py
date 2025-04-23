import pathlib
import random
import sys
import time

import mpi4py.util.sync as sync
from mpi4py import MPI

try:
    import mpiunittest as unittest
except ImportError:
    sys.path.append(pathlib.Path(__file__).parent)
    import mpiunittest as unittest

# ---


def random_sleep(max_sleep=0.01):
    time.sleep(max_sleep * random.random())


# ---


class BaseTestSequential:
    #
    COMM = MPI.COMM_NULL

    def testWith(self):
        comm = self.COMM
        for _ in range(3):
            counter = sync.Counter(comm=comm)
            with sync.Sequential(comm):
                value = next(counter)
            counter.free()
            self.assertEqual(
                comm.allgather(value),
                list(range(comm.size)),
            )

    def testBeginEnd(self):
        comm = self.COMM
        seq = sync.Sequential(comm)
        for _ in range(3):
            counter = sync.Counter(comm=comm)
            seq.begin()
            value = next(counter)
            seq.end()
            counter.free()
            self.assertEqual(
                comm.allgather(value),
                list(range(comm.size)),
            )


class TestSequentialSelf(BaseTestSequential, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


class TestSequentialWorld(BaseTestSequential, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


# ---


class BaseTestCounter:
    #
    COMM = MPI.COMM_NULL

    def testIter(self):
        comm = self.COMM
        size = comm.Get_size()
        counter = sync.Counter(comm=comm)
        for value in counter:
            random_sleep()
            if value >= size - 1:
                break
        counter.free()

    def testNext(self):
        comm = self.COMM
        size = comm.Get_size()
        counter = sync.Counter(comm=comm)
        while True:
            value = next(counter)
            random_sleep()
            if value >= size - 1:
                break
        counter.free()

    def execute(self, counter, its, condition=True):
        values = []
        if condition:
            for _ in range(its):
                value = counter.next()
                values.append(value)
        return sorted(self.COMM.allreduce(values))

    def testDefault(self):
        comm = self.COMM
        size = comm.Get_size()
        counter = sync.Counter(comm=comm)
        values = self.execute(counter, 5)
        counter.free()
        self.assertEqual(values, list(range(5 * size)))

    def testStart(self):
        comm = self.COMM
        size = comm.Get_size()
        counter = sync.Counter(start=7, comm=comm)
        values = self.execute(counter, 5)
        counter.free()
        self.assertEqual(values, list(range(7, 7 + 5 * size)))

    def testStep(self):
        comm = self.COMM
        size = comm.Get_size()
        counter = sync.Counter(step=2, comm=comm)
        values = self.execute(counter, 5)
        counter.free()
        self.assertEqual(values, list(range(0, 2 * 5 * size, 2)))

    def testTypechar(self):
        comm = self.COMM
        size = comm.Get_size()
        for typechar in "hHiIlLqQ" + "fd":
            counter = sync.Counter(typecode=typechar, comm=comm)
            values = self.execute(counter, 3)
            counter.free()
            self.assertEqual(values, list(range(3 * size)))

    def testRoot(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        for root in range(size):
            counter = sync.Counter(comm=comm, root=root)
            values = self.execute(counter, 5, rank != root)
            counter.free()
            self.assertEqual(values, list(range(5 * (size - 1))))

    def testFree(self):
        comm = self.COMM
        counter = sync.Counter(comm=comm)
        for _ in range(5):
            counter.free()
        self.assertRaises(RuntimeError, counter.next)


class TestCounterSelf(BaseTestCounter, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


class TestCounterWorld(BaseTestCounter, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


# ---


class BaseTestMutexBasic:
    #
    COMM = MPI.COMM_NULL

    def setUp(self):
        self.mutex = sync.Mutex(comm=self.COMM)

    def tearDown(self):
        self.mutex.free()

    def testExclusion(self):
        comm = self.COMM
        mutex = self.mutex
        counter = sync.Counter(comm=comm)
        values = []
        comm.Barrier()
        mutex.acquire()
        for _ in range(10):
            values.append(next(counter))
        mutex.release()
        counter.free()
        first, last = values[0], values[-1]
        self.assertEqual(first % 10, 0)
        self.assertEqual(last - first + 1, 10)
        self.assertEqual(values, list(range(first, last + 1)))

    def testFairness(self):
        comm = self.COMM
        mutex = self.mutex
        number = 0
        counter = sync.Counter(comm=comm)
        while next(counter) < comm.Get_size() * 5:
            mutex.acquire()
            number += 1
            mutex.release()
            comm.Barrier()
        counter.free()
        self.assertEqual(number, 5)

    def testWith(self):
        def test_with():
            mutex = self.mutex
            self.assertFalse(mutex.locked())
            self.assertRaises(RuntimeError, mutex.release)
            with mutex:
                self.assertTrue(mutex.locked())
                self.assertRaises(RuntimeError, mutex.acquire)
            self.assertFalse(mutex.locked())
            self.assertRaises(RuntimeError, mutex.release)

        for _ in range(5):
            self.COMM.Barrier()
            test_with()
        for _ in range(5):
            random_sleep()
            test_with()

    def testAcquireRelease(self):
        def test_acquire_release():
            mutex = self.mutex
            self.assertFalse(mutex.locked())
            self.assertRaises(RuntimeError, mutex.release)
            locked = mutex.acquire()
            self.assertTrue(locked)
            self.assertTrue(mutex.locked())
            self.assertRaises(RuntimeError, mutex.acquire)
            mutex.release()
            self.assertFalse(mutex.locked())
            self.assertRaises(RuntimeError, mutex.release)

        for _ in range(5):
            self.COMM.Barrier()
            test_acquire_release()
        for _ in range(5):
            random_sleep()
            test_acquire_release()

    def testAcquireNonblocking(self):
        def test_acquire_nonblocking():
            comm = self.COMM
            mutex = self.mutex
            self.assertFalse(mutex.locked())
            comm.Barrier()
            locked = mutex.acquire(blocking=False)
            comm.Barrier()
            self.assertEqual(mutex.locked(), locked)
            if locked:
                mutex.release()
            self.assertFalse(mutex.locked())
            states = comm.allgather(locked)
            self.assertEqual(states.count(True), 1)
            comm.Barrier()
            while not mutex.acquire(blocking=False):
                pass
            mutex.release()
            comm.Barrier()

        for _ in range(5):
            self.COMM.Barrier()
            test_acquire_nonblocking()
        for _ in range(5):
            random_sleep()
            test_acquire_nonblocking()

    def testAcquireFree(self):
        mutex = self.mutex
        mutex.acquire()
        for _ in range(5):
            mutex.free()
        self.assertRaises(RuntimeError, mutex.acquire)
        self.assertRaises(RuntimeError, mutex.release)
        self.assertRaises(RuntimeError, mutex.locked)

    def testFree(self):
        mutex = self.mutex
        for _ in range(5):
            mutex.free()
        self.assertRaises(RuntimeError, mutex.acquire)
        self.assertRaises(RuntimeError, mutex.release)
        self.assertRaises(RuntimeError, mutex.locked)


class TestMutexBasicSelf(BaseTestMutexBasic, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


@unittest.skipMPI("msmpi")
class TestMutexBasicWorld(BaseTestMutexBasic, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD

    @unittest.skipMPI("msmpi")
    def testExclusion(self):
        super().testExclusion()


# ---


class BaseTestMutexRecursive:
    #
    COMM = MPI.COMM_NULL

    def setUp(self):
        self.mutex = sync.Mutex(recursive=True, comm=self.COMM)

    def tearDown(self):
        self.mutex.free()

    def testWith(self):
        def test_with():
            mutex = self.mutex
            self.assertEqual(mutex.count(), 0)
            self.assertRaises(RuntimeError, mutex.release)
            with mutex:
                self.assertEqual(mutex.count(), 1)
                with mutex:
                    self.assertEqual(mutex.count(), 2)
                    with mutex:
                        self.assertEqual(mutex.count(), 3)
                    self.assertEqual(mutex.count(), 2)
                self.assertEqual(mutex.count(), 1)
            self.assertEqual(mutex.count(), 0)
            self.assertRaises(RuntimeError, mutex.release)

        for _ in range(5):
            self.COMM.Barrier()
            test_with()
        for _ in range(5):
            random_sleep()
            test_with()

    def testAcquireRelease(self):
        def test_acquire_release():
            mutex = self.mutex
            self.assertFalse(mutex.locked())
            self.assertEqual(mutex.count(), 0)
            self.assertRaises(RuntimeError, mutex.release)
            mutex.acquire()
            self.assertTrue(mutex.locked())
            self.assertEqual(mutex.count(), 1)
            mutex.acquire()
            self.assertTrue(mutex.locked())
            self.assertEqual(mutex.count(), 2)
            mutex.acquire()
            self.assertTrue(mutex.locked())
            self.assertEqual(mutex.count(), 3)
            mutex.release()
            self.assertTrue(mutex.locked())
            self.assertEqual(mutex.count(), 2)
            mutex.release()
            self.assertTrue(mutex.locked())
            self.assertEqual(mutex.count(), 1)
            mutex.release()
            self.assertFalse(mutex.locked())
            self.assertEqual(mutex.count(), 0)
            self.assertRaises(RuntimeError, mutex.release)

        for _ in range(5):
            self.COMM.Barrier()
            test_acquire_release()
        for _ in range(5):
            random_sleep()
            test_acquire_release()

    def testAcquireNonblocking(self):
        def test_acquire_nonblocking():
            comm = self.COMM
            mutex = self.mutex
            self.assertEqual(mutex.count(), 0)
            comm.Barrier()
            locked = mutex.acquire(blocking=False)
            self.assertEqual(mutex.locked(), locked)
            comm.Barrier()
            self.assertEqual(mutex.count(), int(locked))
            if locked:
                self.assertEqual(mutex.count(), 1)
                flag = mutex.acquire(blocking=False)
                self.assertTrue(flag)
                self.assertEqual(mutex.count(), 2)
                flag = mutex.acquire(blocking=True)
                self.assertTrue(flag)
                self.assertEqual(mutex.count(), 3)
                mutex.release()
                self.assertEqual(mutex.count(), 2)
                mutex.release()
                self.assertEqual(mutex.count(), 1)
                mutex.release()
            comm.Barrier()
            self.assertFalse(mutex.locked())
            self.assertEqual(mutex.count(), 0)
            states = comm.allgather(locked)
            self.assertEqual(states.count(True), 1)
            comm.Barrier()
            while not mutex.acquire(blocking=False):
                pass
            mutex.release()
            comm.Barrier()

        for _ in range(5):
            self.COMM.Barrier()
            test_acquire_nonblocking()
        for _ in range(5):
            random_sleep()
            test_acquire_nonblocking()

    def testAcquireFree(self):
        mutex = self.mutex
        mutex.acquire()
        mutex.acquire()
        mutex.acquire()
        for _ in range(5):
            mutex.free()
        self.assertRaises(RuntimeError, mutex.acquire)
        self.assertRaises(RuntimeError, mutex.release)
        self.assertRaises(RuntimeError, mutex.count)

    def testFree(self):
        mutex = self.mutex
        for _ in range(5):
            mutex.free()
        self.assertRaises(RuntimeError, mutex.acquire)
        self.assertRaises(RuntimeError, mutex.release)
        self.assertRaises(RuntimeError, mutex.count)


class TestMutexRecursiveSelf(BaseTestMutexRecursive, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


@unittest.skipMPI("msmpi")
class TestMutexRecursiveWorld(BaseTestMutexRecursive, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


# ---


class BaseTestCondition:
    #
    COMM = MPI.COMM_NULL

    def setUp(self):
        self.mutex = None
        self.condition = sync.Condition(comm=self.COMM)

    def tearDown(self):
        self.condition.free()

    def testWaitNotify(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        cv = self.condition
        if rank == 0:
            with cv:
                num = cv.notify()
            self.assertEqual(num, 0)
            comm.Barrier()
            while num < size - 1:
                with cv:
                    num += cv.notify()
                    random_sleep()
            with cv:
                num = cv.notify()
            self.assertEqual(num, 0)
        else:
            comm.Barrier()
            with cv:
                random_sleep()
                cv.wait()
        self.assertRaises(RuntimeError, cv.wait)
        self.assertRaises(RuntimeError, cv.notify)

    def testWaitForNotify(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        cv = self.condition
        if rank == 0:
            with cv:
                num = cv.notify()
            self.assertEqual(num, 0)
            comm.Barrier()
            reqs1 = [comm.isend(00, dest) for dest in range(1, size)]
            reqs2 = [comm.isend(42, dest) for dest in range(1, size)]
            while num < size - 1:
                MPI.Request.Testall(reqs1)
                with cv:
                    num += cv.notify()
                    random_sleep()
            self.assertEqual(num, size - 1)
            MPI.Request.Waitall(reqs2)
            with cv:
                num = cv.notify()
            self.assertEqual(num, 0)
        else:
            comm.Barrier()
            with cv:
                random_sleep()
                result = cv.wait_for(lambda: comm.recv())
            self.assertEqual(result, 42)
        self.assertRaises(RuntimeError, cv.wait_for, lambda: False)
        self.assertRaises(RuntimeError, cv.notify)

    def testWaitNotifyAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        cv = self.condition
        if rank == 0:
            with cv:
                num = cv.notify_all()
            self.assertEqual(num, 0)
            comm.Barrier()
            while num < size - 2:
                with cv:
                    num += cv.notify_all()
                    random_sleep()
            self.assertEqual(num, max(0, size - 2))
            with cv:
                num = cv.notify()
            self.assertEqual(num, 0)
        elif rank == 1:
            comm.Barrier()
        else:
            comm.Barrier()
            with cv:
                random_sleep()
                cv.wait()
        self.assertRaises(RuntimeError, cv.wait)
        self.assertRaises(RuntimeError, cv.notify_all)

    def testAcquireFree(self):
        cv = self.condition
        cv.acquire()
        for _ in range(5):
            cv.free()

    def testFree(self):
        cv = self.condition
        for _ in range(5):
            cv.free()
        self.assertRaises(RuntimeError, cv.acquire)
        self.assertRaises(RuntimeError, cv.release)
        self.assertRaises(RuntimeError, cv.wait)
        self.assertRaises(RuntimeError, cv.wait_for, lambda: False)
        self.assertRaises(RuntimeError, cv.notify)
        self.assertRaises(RuntimeError, cv.notify_all)


class TestConditionSelf(BaseTestCondition, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


@unittest.skipMPI("msmpi")
class TestConditionWorld(BaseTestCondition, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


# ---


class BaseTestConditionMutex(BaseTestCondition):
    #
    COMM = MPI.COMM_NULL

    def setUp(self):
        comm = self.COMM
        self.mutex = sync.Mutex(comm=comm)
        self.condition = sync.Condition(self.mutex)

    def tearDown(self):
        self.mutex.free()
        self.condition.free()


class TestConditionMutexSelf(BaseTestConditionMutex, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


@unittest.skipMPI("msmpi")
class TestConditionMutexWorld(BaseTestConditionMutex, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


# ---


class BaseTestSemaphore:
    #
    COMM = MPI.COMM_NULL

    def setUp(self):
        comm = self.COMM
        value = max(1, comm.Get_size() - 1)
        self.semaphore = sync.Semaphore(value, bounded=False, comm=comm)

    def tearDown(self):
        self.semaphore.free()

    def testValue(self):
        sem = self.semaphore
        self.assertRaises(ValueError, sem.release, 0)
        self.assertRaises(ValueError, sem.release, -1)
        self.assertRaises(ValueError, sync.Semaphore, -1)

    def testBounded(self):
        sem = self.semaphore
        comm = self.COMM
        count = max(1, comm.size - 1)
        sem._bounded = False
        if comm.size > 1:
            if comm.rank == 0:
                sem.release()
        comm.Barrier()
        self.assertEqual(sem._counter.next(0), comm.size)
        comm.Barrier()
        if comm.size > 1:
            if comm.rank == 0:
                sem.acquire()
        comm.Barrier()
        self.assertEqual(sem._counter.next(0), count)
        sem._bounded = True
        self.assertRaises(ValueError, sem.release)
        comm.Barrier()
        sem.acquire()
        sem.release()
        comm.Barrier()
        self.assertEqual(sem._counter.next(0), count)

    def testWith(self):
        def test_with():
            sem = self.semaphore
            with sem:
                pass

        for _ in range(5):
            self.COMM.Barrier()
            test_with()
        for _ in range(5):
            random_sleep()
            test_with()

    def testAcquireRelease(self):
        def test_acquire_release():
            sem = self.semaphore
            locked = sem.acquire()
            sem.release()
            self.assertTrue(locked)

        for _ in range(5):
            self.COMM.Barrier()
            test_acquire_release()
        for _ in range(5):
            random_sleep()
            test_acquire_release()

    def testAcquireNonblocking(self):
        def test_acquire_nonblocking():
            sem = self.semaphore
            comm = self.COMM
            count = max(1, comm.size - 1)
            comm.Barrier()
            locked = sem.acquire(blocking=False)
            comm.Barrier()
            self.assertEqual(sem._counter.next(0), 0)
            comm.Barrier()
            if locked:
                sem.release()
            comm.Barrier()
            states = comm.allgather(locked)
            self.assertEqual(states.count(True), count)
            self.assertEqual(sem._counter.next(0), count)
            comm.Barrier()
            while not sem.acquire(blocking=False):
                random_sleep()
            sem.release()
            comm.Barrier()
            self.assertEqual(sem._counter.next(0), count)

        for _ in range(5):
            self.COMM.Barrier()
            test_acquire_nonblocking()
        for _ in range(5):
            random_sleep()
            test_acquire_nonblocking()

    def testAcquireFree(self):
        comm = self.COMM
        sem = self.semaphore
        if comm.rank > 0:
            sem.acquire()
        for _ in range(5):
            sem.free()

    def testFree(self):
        sem = self.semaphore
        for _ in range(5):
            sem.free()
        self.assertRaises(RuntimeError, sem.acquire)
        self.assertRaises(RuntimeError, sem.release)


class TestSemaphoreSelf(BaseTestSemaphore, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


@unittest.skipMPI("msmpi")
class TestSemaphoreWorld(BaseTestSemaphore, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


# ---

try:
    MPI.Win.Allocate(1, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except (NotImplementedError, MPI.Exception):
    unittest.skip("mpi-win-allocate")(BaseTestCounter)
    unittest.skip("mpi-win-allocate")(BaseTestMutexBasic)
    unittest.skip("mpi-win-allocate")(BaseTestMutexRecursive)
    unittest.skip("mpi-win-allocate")(BaseTestCondition)
    unittest.skip("mpi-win-allocate")(BaseTestSemaphore)

# ---

if __name__ == "__main__":
    unittest.main()
