import os
import sys
import time
import warnings
import functools
import unittest

from mpi4py import MPI
from mpi4py import futures
try:
    from concurrent.futures._base import (
        PENDING, RUNNING, CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED)
except ImportError:
    from mpi4py.futures._base import (
        PENDING, RUNNING, CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED)


SHARED_POOL = futures._lib.SharedPool is not None
WORLD_SIZE  = MPI.COMM_WORLD.Get_size()


def create_future(state=PENDING, exception=None, result=None):
    f = futures.Future()
    f._state = state
    f._exception = exception
    f._result = result
    return f


PENDING_FUTURE = create_future(state=PENDING)
RUNNING_FUTURE = create_future(state=RUNNING)
CANCELLED_FUTURE = create_future(state=CANCELLED)
CANCELLED_AND_NOTIFIED_FUTURE = create_future(state=CANCELLED_AND_NOTIFIED)
EXCEPTION_FUTURE = create_future(state=FINISHED, exception=OSError())
SUCCESSFUL_FUTURE = create_future(state=FINISHED, result=42)


def mul(x, y):
    return x * y


def sleep_and_raise(t):
    time.sleep(t)
    raise Exception('this is an exception')


def check_global_var(x):
    return global_var == x


def check_run_name(name):
    return __name__ == name


class ExecutorMixin:
    worker_count = 2

    def setUp(self):
        self.t1 = time.time()
        try:
            self.executor = self.executor_type(max_workers=self.worker_count)
        except NotImplementedError:
            e = sys.exc_info()[1]
            self.skipTest(str(e))
        self._prime_executor()

    def tearDown(self):
        self.executor.shutdown(wait=True)
        dt = time.time() - self.t1
        self.assertLess(dt, 60, 'synchronization issue: test lasted too long')

    def _prime_executor(self):
        # Make sure that the executor is ready to do work before running the
        # tests. This should reduce the probability of timeouts in the tests.
        futures = [self.executor.submit(time.sleep, 0)
                   for _ in range(self.worker_count)]
        for f in futures:
            f.result()


class ProcessPoolMixin(ExecutorMixin):
    executor_type = futures.MPIPoolExecutor

    if 'coverage' in sys.modules:
        executor_type = functools.partial(
            executor_type,
            python_args='-m coverage run'.split(),
            )


@unittest.skipIf(not SHARED_POOL, 'not-shared-pool')
class ASharedPoolInitTest(unittest.TestCase):
    executor_type = futures.MPIPoolExecutor

    @unittest.skipIf(WORLD_SIZE == 1, 'world-size-1')
    def test_initializer_1(self):
        executor = self.executor_type(
            initializer=sleep_and_raise,
            initargs=(0.2,),
        )
        executor.submit(time.sleep, 0).cancel()
        future = executor.submit(time.sleep, 0)
        with self.assertRaises(futures.BrokenExecutor):
            executor.submit(time.sleep, 0).result()
        with self.assertRaises(futures.BrokenExecutor):
            future.result()
        with self.assertRaises(futures.BrokenExecutor):
            executor.submit(time.sleep, 0)

    @unittest.skipIf(WORLD_SIZE == 1, 'world-size-1')
    def test_initializer_2(self):
        executor = self.executor_type(
            initializer=time.sleep,
            initargs=(0,),
        )
        executor.bootup()
        with self.assertRaises(futures.BrokenExecutor):
            executor.submit(time.sleep, 0).result()
        with self.assertRaises(futures.BrokenExecutor):
            executor.submit(time.sleep, 0)

    @unittest.skipIf(WORLD_SIZE == 1, 'world-size-1')
    def test_initializer_3(self):
        executor = self.executor_type()
        executor.submit(time.sleep, 0).result()
        executor.shutdown()


class ProcessPoolInitTest(ProcessPoolMixin,
                          unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _prime_executor(self):
        pass

    def test_init(self):
        self.executor_type()

    def test_init_args(self):
        self.executor_type(1)

    def test_init_kwargs(self):
        executor = self.executor_type(
            python_exe=sys.executable,
            max_workers=None,
            mpi_info=dict(soft="0:1"),
            globals=None,
            main=False,
            path=[],
            wdir=os.getcwd(),
            env={},
            use_pkl5=None,
            )
        futures = [executor.submit(time.sleep, 0)
                   for _ in range(self.worker_count)]
        for f in futures:
            f.result()
        executor.shutdown()

    def test_init_pyargs(self):
        executor_type = futures.MPIPoolExecutor
        executor = executor_type(python_args=['-B', '-Wi'])
        executor.submit(time.sleep, 0).result()
        executor.shutdown()

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_init_globals(self):
        executor = self.executor_type(globals=dict(global_var=42))
        future1 = executor.submit(check_global_var, 42)
        future2 = executor.submit(check_global_var, 24)
        self.assertTrue(future1.result())
        self.assertFalse(future2.result())
        executor.shutdown()

    @unittest.skipIf(SHARED_POOL and WORLD_SIZE == 1, 'shared-pool')
    def test_run_name(self):
        executor = self.executor_type()
        run_name = futures._lib.MAIN_RUN_NAME
        future = executor.submit(check_run_name, run_name)
        self.assertTrue(future.result(), run_name)

    def test_max_workers_environ(self):
        save = os.environ.get('MPI4PY_FUTURES_MAX_WORKERS')
        os.environ['MPI4PY_FUTURES_MAX_WORKERS'] = '1'
        try:
            executor = self.executor_type()
            executor.submit(time.sleep, 0).result()
            executor.shutdown()
        finally:
            del os.environ['MPI4PY_FUTURES_MAX_WORKERS']
            if save is not None:
                os.environ['MPI4PY_FUTURES_MAX_WORKERS'] = save

    def test_max_workers_negative(self):
        for number in (0, -1):
            self.assertRaises(ValueError,
                              self.executor_type,
                              max_workers=number)

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_use_pkl5_kwarg(self):
        executor = self.executor_type(use_pkl5=True)
        executor.submit(time.sleep, 0).result()
        executor.shutdown()

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_use_pkl5_environ(self):
        save = os.environ.get('MPI4PY_FUTURES_USE_PKL5')
        try:
            for value in ('false', 'true'):
                os.environ['MPI4PY_FUTURES_USE_PKL5'] = value
                executor = self.executor_type()
                executor.submit(time.sleep, 0).result()
                executor.shutdown()
            with warnings.catch_warnings(record=True) as wlist:
                warnings.simplefilter('always')
                os.environ['MPI4PY_FUTURES_USE_PKL5'] = 'foobar'
                executor = self.executor_type()
                executor.submit(time.sleep, 0).result()
                executor.shutdown()
            self.assertTrue(wlist)
            msg = wlist[0].message
            self.assertTrue(isinstance(msg, RuntimeWarning))
            self.assertTrue('foobar' in msg.args[0])
        finally:
            del os.environ['MPI4PY_FUTURES_USE_PKL5']
            if save is not None:
                os.environ['MPI4PY_FUTURES_USE_PKL5'] = save

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_initializer(self):
        executor = self.executor_type(
            initializer=time.sleep,
            initargs=(0,),
        )
        executor.submit(time.sleep, 0).result()

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_initializer_bad(self):
        with self.assertRaises(TypeError):
            self.executor_type(initializer=123)

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_initializer_error(self):
        executor = self.executor_type(
            initializer=sleep_and_raise,
            initargs=(0.2,),
        )
        executor.submit(time.sleep, 0).cancel()
        future = executor.submit(time.sleep, 0)
        with self.assertRaises(futures.BrokenExecutor):
            executor.submit(time.sleep, 0).result()
        with self.assertRaises(futures.BrokenExecutor):
            future.result()
        with self.assertRaises(futures.BrokenExecutor):
            executor.submit(time.sleep, 0)

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_initializer_error_del(self):
        executor = self.executor_type(
            initializer=sleep_and_raise,
            initargs=(0.2,),
        )
        executor.bootup()
        del executor

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_initializer_error_del_nowait(self):
        executor = self.executor_type(
            initializer=sleep_and_raise,
            initargs=(1.2,),
        )
        executor.bootup(wait=False)
        executor.shutdown(wait=False)
        del executor


class ProcessPoolBootupTest(ProcessPoolMixin,
                            unittest.TestCase):

    def _prime_executor(self):
        pass

    def test_bootup(self):
        executor = self.executor_type(1)
        executor.bootup()
        executor.bootup()
        executor.shutdown()
        self.assertRaises(RuntimeError, executor.bootup)

    def test_bootup_wait(self):
        executor = self.executor_type(1)
        executor.bootup(wait=True)
        executor.bootup(wait=True)
        executor.shutdown(wait=True)
        self.assertRaises(RuntimeError, executor.bootup, True)

    def test_bootup_nowait(self):
        executor = self.executor_type(1)
        executor.bootup(wait=False)
        executor.bootup(wait=False)
        executor.shutdown(wait=False)
        self.assertRaises(RuntimeError, executor.bootup, False)
        executor.shutdown(wait=True)

    def test_bootup_nowait_wait(self):
        executor = self.executor_type(1)
        executor.bootup(wait=False)
        executor.bootup(wait=True)
        executor.shutdown()
        self.assertRaises(RuntimeError, executor.bootup)

    def test_bootup_shutdown_nowait(self):
        executor = self.executor_type(1)
        executor.bootup(wait=False)
        executor.shutdown(wait=False)
        worker = executor._pool
        del executor
        worker.join()


class ExecutorShutdownTestMixin:

    def test_run_after_shutdown(self):
        self.executor.shutdown()
        self.assertRaises(RuntimeError,
                          self.executor.submit,
                          pow, 2, 5)

    def test_hang_issue12364(self):
        fs = [self.executor.submit(time.sleep, 0.01) for _ in range(50)]
        self.executor.shutdown()
        for f in fs:
            f.result()


class ProcessPoolShutdownTest(ProcessPoolMixin,
                              ExecutorShutdownTestMixin,
                              unittest.TestCase):

    def _prime_executor(self):
        pass

    def test_shutdown(self):
        executor = self.executor_type(max_workers=1)
        self.assertEqual(executor._pool, None)
        self.assertEqual(executor._shutdown, False)
        executor.submit(mul, 21, 2)
        executor.submit(mul, 6, 7)
        executor.submit(mul, 3, 14)
        self.assertNotEqual(executor._pool.thread, None)
        self.assertEqual(executor._shutdown, False)
        executor.shutdown(wait=False)
        self.assertNotEqual(executor._pool.thread, None)
        self.assertEqual(executor._shutdown, True)
        executor.shutdown(wait=True)
        self.assertEqual(executor._pool, None)
        self.assertEqual(executor._shutdown, True)

    def test_submit_shutdown_cancel(self):
        executor = self.executor_type(max_workers=1)
        executor.bootup()
        num_workers = executor._pool.size
        for _ in range(num_workers*10):
            executor.submit(time.sleep, 0.1)
        fut = executor.submit(time.sleep, 0)
        executor.shutdown(wait=False, cancel_futures=False)
        self.assertFalse(fut.cancelled())
        executor.shutdown(wait=True, cancel_futures=True)
        self.assertTrue(fut.cancelled())

    def test_shutdown_cancel(self):
        executor = self.executor_type(max_workers=1)
        executor.bootup()
        executor._pool.cancel()
        executor.shutdown(wait=False, cancel_futures=False)
        executor.shutdown(wait=False, cancel_futures=False)
        executor.shutdown(wait=False, cancel_futures=True)
        executor.shutdown(wait=False, cancel_futures=True)
        executor.shutdown(wait=True,  cancel_futures=True)
        executor.shutdown(wait=True,  cancel_futures=True)

    def test_init_bootup_shutdown(self):
        executor = self.executor_type(max_workers=1)
        self.assertEqual(executor._pool, None)
        self.assertEqual(executor._shutdown, False)
        executor.bootup()
        self.assertTrue(executor._pool.event.is_set())
        self.assertEqual(executor._shutdown, False)
        executor.shutdown()
        self.assertEqual(executor._pool, None)
        self.assertEqual(executor._shutdown, True)

    def test_context_manager_shutdown(self):
        with self.executor_type(max_workers=1) as e:
            self.assertEqual(list(e.map(abs, range(-5, 5))),
                             [5, 4, 3, 2, 1, 0, 1, 2, 3, 4])
            threads = [e._pool.thread]
            queues = [e._pool.queue]
            events = [e._pool.event]

        for t in threads:
            t.join()
        for q in queues:
            self.assertRaises(LookupError, q.pop)
        for e in events:
            self.assertTrue(e.is_set())

    def test_del_shutdown(self):
        executor = self.executor_type(max_workers=1)
        list(executor.map(abs, range(-5, 5)))
        threads = [executor._pool.thread]
        queues = [executor._pool.queue]
        events = [executor._pool.event]
        if hasattr(sys, 'pypy_version_info'):
            executor.shutdown(False)
        else:
            del executor

        for t in threads:
            t.join()
        for q in queues:
            self.assertRaises(LookupError, q.pop)
        for e in events:
            self.assertTrue(e.is_set())


class WaitTestMixin:

    def test_first_completed(self):
        future1 = self.executor.submit(mul, 21, 2)
        future2 = self.executor.submit(time.sleep, 0.2)

        done, not_done = futures.wait(
                [CANCELLED_FUTURE, future1, future2],
                return_when=futures.FIRST_COMPLETED)

        self.assertEqual(set([future1]), done)
        self.assertEqual(set([CANCELLED_FUTURE, future2]), not_done)

    def test_first_completed_some_already_completed(self):
        future1 = self.executor.submit(time.sleep, 0.2)

        finished, pending = futures.wait(
                 [CANCELLED_AND_NOTIFIED_FUTURE, SUCCESSFUL_FUTURE, future1],
                 return_when=futures.FIRST_COMPLETED)

        self.assertEqual(
                set([CANCELLED_AND_NOTIFIED_FUTURE, SUCCESSFUL_FUTURE]),
                finished)
        self.assertEqual(set([future1]), pending)

    def test_first_exception(self):
        future1 = self.executor.submit(mul, 2, 21)
        future2 = self.executor.submit(sleep_and_raise, 0.2)
        future3 = self.executor.submit(time.sleep, 0.4)

        finished, pending = futures.wait(
                [future1, future2, future3],
                return_when=futures.FIRST_EXCEPTION)

        self.assertEqual(set([future1, future2]), finished)
        self.assertEqual(set([future3]), pending)

    def test_first_exception_some_already_complete(self):
        future1 = self.executor.submit(divmod, 21, 0)
        future2 = self.executor.submit(time.sleep, 0.2)

        finished, pending = futures.wait(
                [SUCCESSFUL_FUTURE,
                 CANCELLED_FUTURE,
                 CANCELLED_AND_NOTIFIED_FUTURE,
                 future1, future2],
                return_when=futures.FIRST_EXCEPTION)

        self.assertEqual(set([SUCCESSFUL_FUTURE,
                              CANCELLED_AND_NOTIFIED_FUTURE,
                              future1]), finished)
        self.assertEqual(set([CANCELLED_FUTURE, future2]), pending)

    def test_first_exception_one_already_failed(self):
        future1 = self.executor.submit(time.sleep, 0.2)

        finished, pending = futures.wait(
                 [EXCEPTION_FUTURE, future1],
                 return_when=futures.FIRST_EXCEPTION)

        self.assertEqual(set([EXCEPTION_FUTURE]), finished)
        self.assertEqual(set([future1]), pending)

    def test_all_completed(self):
        future1 = self.executor.submit(divmod, 2, 0)
        future2 = self.executor.submit(mul, 2, 21)

        finished, pending = futures.wait(
                [SUCCESSFUL_FUTURE,
                 CANCELLED_AND_NOTIFIED_FUTURE,
                 EXCEPTION_FUTURE,
                 future1,
                 future2],
                return_when=futures.ALL_COMPLETED)

        self.assertEqual(set([SUCCESSFUL_FUTURE,
                              CANCELLED_AND_NOTIFIED_FUTURE,
                              EXCEPTION_FUTURE,
                              future1,
                              future2]), finished)
        self.assertEqual(set(), pending)

    def test_timeout(self):
        future1 = self.executor.submit(mul, 6, 7)
        future2 = self.executor.submit(time.sleep, 0.5)

        finished, pending = futures.wait(
                [CANCELLED_AND_NOTIFIED_FUTURE,
                 EXCEPTION_FUTURE,
                 SUCCESSFUL_FUTURE,
                 future1, future2],
                timeout=0.2,
                return_when=futures.ALL_COMPLETED)

        self.assertEqual(set([CANCELLED_AND_NOTIFIED_FUTURE,
                              EXCEPTION_FUTURE,
                              SUCCESSFUL_FUTURE,
                              future1]), finished)
        self.assertEqual(set([future2]), pending)


class ProcessPoolWaitTest(ProcessPoolMixin,
                          WaitTestMixin,
                          unittest.TestCase):
    pass


class AsCompletedTestMixin:

    def test_no_timeout(self):
        future1 = self.executor.submit(mul, 2, 21)
        future2 = self.executor.submit(mul, 7, 6)

        completed = set(futures.as_completed(
                [CANCELLED_AND_NOTIFIED_FUTURE,
                 EXCEPTION_FUTURE,
                 SUCCESSFUL_FUTURE,
                 future1, future2]))
        self.assertEqual(set(
                [CANCELLED_AND_NOTIFIED_FUTURE,
                 EXCEPTION_FUTURE,
                 SUCCESSFUL_FUTURE,
                 future1, future2]),
                completed)

    def test_zero_timeout(self):
        future1 = self.executor.submit(time.sleep, 0.5)
        completed_futures = set()
        try:
            for future in futures.as_completed(
                    [CANCELLED_AND_NOTIFIED_FUTURE,
                     EXCEPTION_FUTURE,
                     SUCCESSFUL_FUTURE,
                     future1],
                    timeout=0):
                completed_futures.add(future)
        except futures.TimeoutError:
            pass

        self.assertEqual(set([CANCELLED_AND_NOTIFIED_FUTURE,
                              EXCEPTION_FUTURE,
                              SUCCESSFUL_FUTURE]),
                         completed_futures)

    def test_nonzero_timeout(self):
        future1 = self.executor.submit(time.sleep, 0.0)
        future2 = self.executor.submit(time.sleep, 0.5)
        completed_futures = set()
        try:
            for future in futures.as_completed(
                    [CANCELLED_AND_NOTIFIED_FUTURE,
                     EXCEPTION_FUTURE,
                     SUCCESSFUL_FUTURE,
                     future1],
                    timeout=0.2):
                completed_futures.add(future)
        except futures.TimeoutError:
            pass

        self.assertEqual(set([CANCELLED_AND_NOTIFIED_FUTURE,
                              EXCEPTION_FUTURE,
                              SUCCESSFUL_FUTURE,
                              future1]),
                         completed_futures)

    def test_duplicate_futures(self):
        # Issue 20367. Duplicate futures should not raise exceptions or give
        # duplicate responses.
        future1 = self.executor.submit(time.sleep, 0.1)
        completed = [f for f in futures.as_completed([future1, future1])]
        self.assertEqual(len(completed), 1)


class ProcessPoolAsCompletedTest(ProcessPoolMixin,
                                 AsCompletedTestMixin,
                                 unittest.TestCase):
    pass


class ExecutorTestMixin:

    def test_submit(self):
        future = self.executor.submit(pow, 2, 8)
        self.assertEqual(256, future.result())

    def test_submit_keyword(self):
        future = self.executor.submit(mul, 2, y=8)
        self.assertEqual(16, future.result())
        future = self.executor.submit(mul, x=2, y=8)
        self.assertEqual(16, future.result())

    def test_submit_cancel(self):
        future1 = self.executor.submit(time.sleep, 0.25)
        future2 = self.executor.submit(time.sleep, 0)
        future2.cancel()
        self.assertEqual(None,  future1.result())
        self.assertEqual(False, future1.cancelled())
        self.assertEqual(True,  future2.cancelled())

    def test_map(self):
        self.assertEqual(
                list(self.executor.map(pow, range(10), range(10))),
                list(map(pow, range(10), range(10))))

    def test_starmap(self):
        sequence = [(a,a) for a in range(10)]
        self.assertEqual(
                list(self.executor.starmap(pow, sequence)),
                list(map(pow, range(10), range(10))))
        self.assertEqual(
                list(self.executor.starmap(pow, iter(sequence))),
                list(map(pow, range(10), range(10))))

    def test_map_exception(self):
        i = self.executor.map(divmod, [1, 1, 1, 1], [2, 3, 0, 5])
        self.assertEqual(next(i), (0, 1))
        self.assertEqual(next(i), (0, 1))
        self.assertRaises(ZeroDivisionError, next, i)

    def test_map_timeout(self):
        results = []
        try:
            for i in self.executor.map(time.sleep, [0, 0, 1], timeout=0.25):
                results.append(i)
        except futures.TimeoutError:
            pass
        else:
            self.fail('expected TimeoutError')

        self.assertEqual([None, None], results)

    def test_map_timeout_one(self):
        results = []
        for i in self.executor.map(time.sleep, [0, 0, 0], timeout=1):
            results.append(i)
        self.assertEqual([None, None, None], results)


class ProcessPoolExecutorTest(ProcessPoolMixin,
                              ExecutorTestMixin,
                              unittest.TestCase):

    def test_map_chunksize(self):
        ref = list(map(pow, range(40), range(40)))
        self.assertEqual(
            list(self.executor.map(pow, range(40), range(40), chunksize=6)),
            ref)
        self.assertEqual(
            list(self.executor.map(pow, range(40), range(40), chunksize=50)),
            ref)
        self.assertEqual(
            list(self.executor.map(pow, range(40), range(40), chunksize=40)),
            ref)

        def bad():
            list(self.executor.map(pow, range(40), range(40), chunksize=-1))
        self.assertRaises(ValueError, bad)

    def test_starmap_chunksize(self):
        ref = list(map(pow, range(40), range(40)))
        sequence = [(a, a) for a in range(40)]
        self.assertEqual(
            list(self.executor.starmap(pow, sequence, chunksize=6)),
            ref)
        self.assertEqual(
            list(self.executor.starmap(pow, sequence, chunksize=50)),
            ref)
        self.assertEqual(
            list(self.executor.starmap(pow, sequence, chunksize=40)),
            ref)
        self.assertEqual(
            list(self.executor.starmap(pow, iter(sequence), chunksize=6)),
            ref)
        self.assertEqual(
            list(self.executor.starmap(pow, iter(sequence), chunksize=50)),
            ref)
        self.assertEqual(
            list(self.executor.starmap(pow, iter(sequence), chunksize=40)),
            ref)

        def bad():
            list(self.executor.starmap(pow, sequence, chunksize=-1))
        self.assertRaises(ValueError, bad)

    def test_map_unordered(self):
        map_unordered = functools.partial(self.executor.map, unordered=True)
        self.assertEqual(
                set(map_unordered(pow, range(10), range(10))),
                set(map(pow, range(10), range(10))))

    def test_map_unordered_timeout(self):
        map_unordered = functools.partial(self.executor.map, unordered=True)
        num_workers = self.executor._pool.size
        results = []
        try:
            args = [1] + [0]*(num_workers-1)
            for i in map_unordered(time.sleep, args, timeout=0.25):
                results.append(i)
        except futures.TimeoutError:
            pass
        else:
            self.fail('expected TimeoutError')

        self.assertEqual([None]*(num_workers-1), results)

    def test_map_unordered_timeout_one(self):
        map_unordered = functools.partial(self.executor.map, unordered=True)
        results = []
        for i in map_unordered(time.sleep, [0, 0, 0], timeout=1):
            results.append(i)
        self.assertEqual([None, None, None], results)

    def test_map_unordered_exception(self):
        map_unordered = functools.partial(self.executor.map, unordered=True)
        i = map_unordered(divmod, [1, 1, 1, 1], [2, 3, 0, 5])
        try:
            self.assertEqual(next(i), (0, 1))
        except ZeroDivisionError:
            return

    def test_map_unordered_chunksize(self):
        map_unordered = functools.partial(self.executor.map, unordered=True)
        ref = set(map(pow, range(40), range(40)))
        self.assertEqual(
            set(map_unordered(pow, range(40), range(40), chunksize=6)),
            ref)
        self.assertEqual(
            set(map_unordered(pow, range(40), range(40), chunksize=50)),
            ref)
        self.assertEqual(
            set(map_unordered(pow, range(40), range(40), chunksize=40)),
            ref)

        def bad():
            set(map_unordered(pow, range(40), range(40), chunksize=-1))
        self.assertRaises(ValueError, bad)


class ProcessPoolSubmitTest(unittest.TestCase):

    @unittest.skipIf(MPI.get_vendor()[0] == 'Microsoft MPI', 'msmpi')
    def test_multiple_executors(self):
        executor1 = futures.MPIPoolExecutor(1).bootup(wait=True)
        executor2 = futures.MPIPoolExecutor(1).bootup(wait=True)
        executor3 = futures.MPIPoolExecutor(1).bootup(wait=True)
        fs1 = [executor1.submit(abs, i) for i in range(100, 200)]
        fs2 = [executor2.submit(abs, i) for i in range(200, 300)]
        fs3 = [executor3.submit(abs, i) for i in range(300, 400)]
        futures.wait(fs3+fs2+fs1)
        for i, f in enumerate(fs1):
            self.assertEqual(f.result(), i + 100)
        for i, f in enumerate(fs2):
            self.assertEqual(f.result(), i + 200)
        for i, f in enumerate(fs3):
            self.assertEqual(f.result(), i + 300)
        executor1 = executor2 = executor3 = None

    def test_mpi_serialized_support(self):
        futures._lib.setup_mpi_threads()
        threading = futures._lib.threading
        serialized = futures._lib.serialized
        lock_save = serialized.lock
        try:
            if lock_save is None:
                serialized.lock = threading.Lock()
                executor = futures.MPIPoolExecutor(1).bootup()
                executor.submit(abs, 0).result()
                executor.shutdown()
                serialized.lock = lock_save
            else:
                serialized.lock = None
                with lock_save:
                    executor = futures.MPIPoolExecutor(1).bootup()
                    executor.submit(abs, 0).result()
                    executor.shutdown()
                serialized.lock = lock_save
        finally:
            serialized.lock = lock_save

    def test_shared_executors(self):
        if not SHARED_POOL: return
        executors = [futures.MPIPoolExecutor() for _ in range(16)]
        fs = []
        for i in range(128):
            fs.extend(e.submit(abs, i*16+j)
                      for j, e in enumerate(executors))
        assert sorted(f.result() for f in fs) == list(range(16*128))
        world_size = MPI.COMM_WORLD.Get_size()
        num_workers = max(1, world_size - 1)
        for e in executors:
            self.assertEqual(e._pool.size, num_workers)
        del e, executors


def inout(arg):
    return arg


class GoodPickle(object):

    def __init__(self, value=0):
        self.value = value
        self.pickled = False
        self.unpickled = False

    def __getstate__(self):
        self.pickled = True
        return (self.value,)

    def __setstate__(self, state):
        self.unpickled = True
        self.value = state[0]


class BadPickle(object):

    def __init__(self):
        self.pickled = False

    def __getstate__(self):
        self.pickled = True
        1/0

    def __setstate__(self, state):
        pass


class BadUnpickle(object):

    def __init__(self):
        self.pickled = False

    def __getstate__(self):
        self.pickled = True
        return (None,)

    def __setstate__(self, state):
        if state[0] is not None:
            raise ValueError
        1/0


@unittest.skipIf(SHARED_POOL and WORLD_SIZE == 1, 'shared-pool')
class ProcessPoolPickleTest(unittest.TestCase):

    def setUp(self):
        self.executor = futures.MPIPoolExecutor(1)

    def tearDown(self):
        self.executor.shutdown()

    def test_good_pickle(self):
        o = GoodPickle(42)
        r = self.executor.submit(inout, o).result()
        self.assertEqual(o.value, r.value)
        self.assertTrue(o.pickled)
        self.assertTrue(r.unpickled)

        r = self.executor.submit(GoodPickle, 77).result()
        self.assertEqual(r.value, 77)
        self.assertTrue(r.unpickled)

    def test_bad_pickle(self):
        o = BadPickle()
        self.assertFalse(o.pickled)
        f = self.executor.submit(inout, o)
        self.assertRaises(ZeroDivisionError, f.result)
        self.assertTrue(o.pickled)

        f = self.executor.submit(BadPickle)
        self.assertRaises(ZeroDivisionError, f.result)

        f = self.executor.submit(abs, 42)
        self.assertEqual(f.result(), 42)

    def test_bad_unpickle(self):
        o = BadUnpickle()
        self.assertFalse(o.pickled)
        f = self.executor.submit(inout, o)
        self.assertRaises(ZeroDivisionError, f.result)
        self.assertTrue(o.pickled)

        f = self.executor.submit(BadUnpickle)
        self.assertRaises(ZeroDivisionError, f.result)

        f = self.executor.submit(abs, 42)
        self.assertEqual(f.result(), 42)


class MPICommExecutorTest(unittest.TestCase):

    MPICommExecutor = futures.MPICommExecutor

    def test_default(self):
        with self.MPICommExecutor() as executor:
            if executor is not None:
                executor.bootup()
                future1 = executor.submit(time.sleep, 0)
                future2 = executor.submit(time.sleep, 0)
                executor.shutdown()
                self.assertEqual(None, future1.result())
                self.assertEqual(None, future2.result())

    def test_self(self):
        with self.MPICommExecutor(MPI.COMM_SELF) as executor:
            future = executor.submit(time.sleep, 0)
            self.assertEqual(None, future.result())
            self.assertEqual(None, future.exception())

            future = executor.submit(sleep_and_raise, 0)
            self.assertRaises(Exception, future.result)
            self.assertEqual(Exception, type(future.exception()))

            list(executor.map(time.sleep, [0, 0]))
            list(executor.map(time.sleep, [0, 0], timeout=1))
            iterator = executor.map(time.sleep, [0.2, 0], timeout=0)
            self.assertRaises(futures.TimeoutError, list, iterator)

    def test_args(self):
        with self.MPICommExecutor(MPI.COMM_SELF) as executor:
            self.assertTrue(executor is not None)
        with self.MPICommExecutor(MPI.COMM_SELF, 0) as executor:
            self.assertTrue(executor is not None)

    def test_kwargs(self):
        with self.MPICommExecutor(comm=MPI.COMM_SELF) as executor:
            self.assertTrue(executor is not None)
        with self.MPICommExecutor(comm=MPI.COMM_SELF, root=0) as executor:
            self.assertTrue(executor is not None)

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_arg_root(self):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        for root in range(comm.Get_size()):
            with self.MPICommExecutor(comm, root) as executor:
                if rank != root:
                    self.assertTrue(executor is None)
            with self.MPICommExecutor(root=root) as executor:
                if rank != root:
                    self.assertTrue(executor is None)

    def test_arg_root_bad(self):
        size = MPI.COMM_WORLD.Get_size()
        self.assertRaises(ValueError, self.MPICommExecutor, root=-size)
        self.assertRaises(ValueError, self.MPICommExecutor, root=-1)
        self.assertRaises(ValueError, self.MPICommExecutor, root=+size)

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_arg_comm_bad(self):
        if MPI.COMM_WORLD.Get_size() == 1: return
        intercomm = futures._lib.comm_split(MPI.COMM_WORLD)
        try:
            self.assertRaises(ValueError, self.MPICommExecutor, intercomm)
        finally:
            intercomm.Free()

    def test_with_bad(self):
        mpicommexecutor = self.MPICommExecutor(MPI.COMM_SELF)
        with mpicommexecutor as executor:
            try:
                with mpicommexecutor:
                    pass
            except RuntimeError:
                pass
            else:
                self.fail('expected RuntimeError')

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_initializer(self):
        mpicommexecutor = self.MPICommExecutor(
            initializer=time.sleep,
            initargs=(0,),
        )
        with mpicommexecutor as executor:
            if executor is not None:
                executor.bootup()
                del executor
        with mpicommexecutor as executor:
            if executor is not None:
                executor.submit(time.sleep, 0).result()

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_initializer_error(self):
        mpicommexecutor = self.MPICommExecutor(
            initializer=sleep_and_raise,
            initargs=(0.2,),
        )
        with mpicommexecutor as executor:
            if executor is not None:
                executor.submit(time.sleep, 0).cancel()
                future = executor.submit(time.sleep, 0)
                with self.assertRaises(futures.BrokenExecutor):
                    executor.submit(time.sleep, 0).result()
                with self.assertRaises(futures.BrokenExecutor):
                    future.result()

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_initializer_error_del(self):
        mpicommexecutor = self.MPICommExecutor(
            initializer=sleep_and_raise,
            initargs=(0.2,),
        )
        with mpicommexecutor as executor:
            if executor is not None:
                executor.bootup()
                del executor

    @unittest.skipIf(SHARED_POOL, 'shared-pool')
    def test_initializer_error_del_nowait(self):
        mpicommexecutor = self.MPICommExecutor(
            initializer=sleep_and_raise,
            initargs=(0.2,),
        )
        with mpicommexecutor as executor:
            if executor is not None:
                executor.bootup(wait=False)
                executor.shutdown(wait=False)
                del executor


from mpi4py.futures.aplus import ThenableFuture

class ThenTest(unittest.TestCase):

    assert_ = unittest.TestCase.assertTrue

    def test_not_done(self):

        base_f = ThenableFuture()
        new_f = base_f.then()

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f._invoke_callbacks()
        self.assert_(new_f.cancelled())

    def test_cancel(self):

        base_f = ThenableFuture()
        new_f = base_f.then()

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.cancel()
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(base_f.cancelled())
        self.assert_(new_f.cancelled())

    def test_then_multiple(self):

        base_f = ThenableFuture()
        new_f1 = base_f.then()
        new_f2 = base_f.then()
        new_f3 = base_f.then()

        self.assert_(base_f is not new_f1)
        self.assert_(base_f is not new_f2)
        self.assert_(base_f is not new_f3)
        self.assert_(not base_f.done())
        self.assert_(not new_f1.done())
        self.assert_(not new_f2.done())
        self.assert_(not new_f3.done())

        base_f.set_result('done')
        self.assert_(base_f.done())
        self.assert_(new_f1.done())
        self.assert_(new_f2.done())
        self.assert_(new_f3.done())

        self.assert_(not new_f1.exception())
        self.assert_(not new_f2.exception())
        self.assert_(not new_f3.exception())
        self.assert_(new_f1.result() == 'done')
        self.assert_(new_f2.result() == 'done')
        self.assert_(new_f3.result() == 'done')

    def test_no_callbacks_and_success(self):

        base_f = ThenableFuture()
        new_f = base_f.then()

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_result('done')
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(not new_f.exception())
        self.assert_(new_f.result() == 'done')

    def test_no_callbacks_and_failure(self):

        class MyException(Exception):
            pass

        base_f = ThenableFuture()
        new_f = base_f.then()

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_exception(MyException('sad'))
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(new_f.exception())
        with self.assertRaises(MyException) as catcher:
            new_f.result()
        self.assert_(catcher.exception.args[0] == 'sad')

    def test_success_callback_and_success(self):

        base_f = ThenableFuture()
        new_f = base_f.then(lambda result: result + ' manipulated')

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_result('done')
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(not new_f.exception())
        self.assert_(new_f.result() == 'done manipulated')

    def test_err_callback_and_failure_repackage(self):

        class MyException(Exception):
            pass

        class MyRepackagedException(Exception):
            pass

        class NotMatched(Exception):
            pass

        def on_failure(ex):
            if isinstance(ex, MyException):
                return MyRepackagedException(ex.args[0] + ' repackaged')
            else:
                return NotMatched('?')

        base_f = ThenableFuture()
        new_f = base_f.then(None, on_failure)

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_exception(MyException('sad'))
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(new_f.exception())
        with self.assertRaises(MyRepackagedException) as catcher:
            new_f.result()
        self.assert_(catcher.exception.args[0] == 'sad repackaged')

    def test_err_callback_and_failure_raised(self):

        class MyException(Exception):
            pass

        class MyRepackagedException(Exception):
            pass

        def raise_something_else(ex):
            raise MyRepackagedException(ex.args[0] + ' repackaged')

        base_f = ThenableFuture()
        new_f = base_f.then(None, raise_something_else)

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_exception(MyException('sad'))
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(new_f.exception())
        with self.assertRaises(MyRepackagedException) as catcher:
            new_f.result()
        self.assert_(catcher.exception.args[0] == 'sad repackaged')

    def test_err_callback_convert_to_success(self):

        class MyException(Exception):
            pass

        class NotMatched(Exception):
            pass

        def on_failure(ex):
            if isinstance(ex, MyException):
                return ex.args[0] + ' repackaged'
            else:
                return NotMatched('?')

        base_f = ThenableFuture()
        new_f = base_f.catch(on_failure)

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_exception(MyException('sad'))
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(not new_f.exception())
        self.assert_(new_f.result() == 'sad repackaged')

    def test_err_catch_ignore(self):

        base_f = ThenableFuture()
        new_f = base_f.catch()

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_exception(Exception('sad'))
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(new_f.exception() is None)
        self.assert_(new_f.result() is None)

    def test_success_callback_and_failure_raised(self):

        class MyException(Exception):
            pass

        def raise_something_else(value):
            raise MyException(value + ' repackaged')

        base_f = ThenableFuture()
        new_f = base_f.then(raise_something_else)

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_result('sad')
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(new_f.exception())
        with self.assertRaises(MyException) as catcher:
            new_f.result()
        assert catcher.exception.args[0] == 'sad repackaged'

    def test_chained_success_callback_and_success(self):

        def transform(value):
            f = ThenableFuture()
            if value < 5:
                f.set_result(transform(value+1))
            else:
                f.set_result(value)
            return f

        base_f = ThenableFuture()
        new_f = base_f.then(transform)

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_result(1)
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(not new_f.exception())
        self.assert_(new_f.result() == 5)

    def test_detect_circular_chains(self):

        f1 = ThenableFuture()
        f2 = ThenableFuture()
        chain = [f1, f2, f1]

        def transform(a):
            try:
                f = chain.pop(0)
                r = transform(a)
                f.__init__()
                f.set_result(r)
                return f
            except IndexError:
                return 42

        base_f = ThenableFuture()
        new_f = base_f.then(transform)

        self.assert_(base_f is not new_f)
        self.assert_(not base_f.done())
        self.assert_(not new_f.done())

        base_f.set_result(1)
        self.assert_(base_f.done())
        self.assert_(new_f.done())

        self.assert_(new_f.exception())
        with self.assertRaises(RuntimeError) as catcher:
            new_f.result()
        self.assert_('Circular future chain detected'
                     in catcher.exception.args[0])


SKIP_POOL_TEST = False
name, version = MPI.get_vendor()
if name == 'Open MPI':
    if version < (3,0,0):
        SKIP_POOL_TEST = True
    if version == (4,0,0):
        SKIP_POOL_TEST = True
    if version == (4,0,1) and sys.platform=='darwin':
        SKIP_POOL_TEST = True
    if version == (4,0,2) and sys.platform=='darwin':
        SKIP_POOL_TEST = True
if name == 'MPICH':
    if sys.platform == 'darwin':
        if version >= (3, 4) and version < (4, 0):
            SKIP_POOL_TEST = True
    if MPI.COMM_WORLD.Get_attr(MPI.APPNUM) is None:
        SKIP_POOL_TEST = True
    try:
        port = MPI.Open_port()
        MPI.Close_port(port)
    except:
        port = ""
    if port == "":
        SKIP_POOL_TEST = True
    del port
if name == 'MVAPICH2':
    SKIP_POOL_TEST = True
if name == 'MPICH2':
    if MPI.COMM_WORLD.Get_attr(MPI.APPNUM) is None:
        SKIP_POOL_TEST = True
if name == 'Microsoft MPI':
    if version < (8,1,0):
        SKIP_POOL_TEST = True
    if MPI.COMM_WORLD.Get_attr(MPI.APPNUM) is None:
        SKIP_POOL_TEST = True
if name == 'Platform MPI':
    SKIP_POOL_TEST = True
if MPI.Get_version() < (2,0):
    SKIP_POOL_TEST = True


if SHARED_POOL:
    del MPICommExecutorTest.test_arg_root
    del MPICommExecutorTest.test_arg_comm_bad
    del MPICommExecutorTest.test_initializer
    del MPICommExecutorTest.test_initializer_error
    del ProcessPoolInitTest.test_init_globals
    del ProcessPoolInitTest.test_use_pkl5_kwarg
    del ProcessPoolInitTest.test_use_pkl5_environ
    del ProcessPoolInitTest.test_initializer
    del ProcessPoolInitTest.test_initializer_bad
    del ProcessPoolInitTest.test_initializer_error
    del ProcessPoolInitTest.test_initializer_error_del
    if WORLD_SIZE == 1:
        del ASharedPoolInitTest
        del ProcessPoolInitTest.test_run_name
        del ProcessPoolPickleTest
elif WORLD_SIZE > 1 or SKIP_POOL_TEST:
    del ProcessPoolInitTest
    del ProcessPoolBootupTest
    del ProcessPoolShutdownTest
    del ProcessPoolWaitTest
    del ProcessPoolAsCompletedTest
    del ProcessPoolExecutorTest
    del ProcessPoolSubmitTest
    del ProcessPoolPickleTest
if not SHARED_POOL:
    del ASharedPoolInitTest


if __name__ == '__main__':
    unittest.main()
