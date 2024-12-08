from mpi4py import MPI
import mpi4py.util.pool as pool
import concurrent.futures as cf
import itertools
import functools
import warnings
import unittest
import time
import sys
import os


def sqr(x, wait=0.0):
    time.sleep(wait)
    return x*x


def mul(x, y):
    return x*y


def identity(x):
    return x


def raising():
    raise KeyError("key")


TIMEOUT1 = 0.1
TIMEOUT2 = 0.2


class TimingWrapper:

    def __init__(self, func):
        self.func = func
        self.elapsed = None

    def __call__(self, *args, **kwds):
        t = time.monotonic()
        try:
            return self.func(*args, **kwds)
        finally:
            self.elapsed = time.monotonic() - t


class BaseTestPool:

    PoolType = None

    @classmethod
    def Pool(cls, *args, **kwargs):
        if 'coverage' in sys.modules:
            kwargs['python_args'] = '-m coverage run'.split()
        Pool = cls.PoolType
        return Pool(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pool = cls.Pool(1)

    @classmethod
    def tearDownClass(cls):
        cls.pool.terminate()
        cls.pool.join()
        cls.pool = None
        super().tearDownClass()

    def test_apply(self):
        papply = self.pool.apply
        self.assertEqual(papply(sqr, (5,)), sqr(5))
        self.assertEqual(papply(sqr, (), {'x':3}), sqr(x=3))

    def test_map(self):
        self.assertEqual(
            self.pool.map(sqr, range(10)),
            list(map(sqr, list(range(10))))
        )
        self.assertEqual(
            self.pool.map(sqr, (i for i in range(10))),
            list(map(sqr, list(range(10))))
        )
        self.assertEqual(
            self.pool.map(sqr, list(range(10))),
            list(map(sqr, list(range(10))))
        )

        self.assertEqual(
            self.pool.map(sqr, range(100), chunksize=20),
            list(map(sqr, list(range(100))))
        )
        self.assertEqual(
            self.pool.map(sqr, (i for i in range(100)), chunksize=20),
            list(map(sqr, list(range(100))))
        )
        self.assertEqual(
            self.pool.map(sqr, list(range(100)), chunksize=20),
            list(map(sqr, list(range(100))))
        )

    def test_imap(self):
        self.assertEqual(
            list(self.pool.imap(sqr, range(10))),
            list(map(sqr, list(range(10))))
        )
        self.assertEqual(
            list(self.pool.imap(sqr, (i for i in range(10)))),
            list(map(sqr, list(range(10))))
        )
        self.assertEqual(
            list(self.pool.imap(sqr, list(range(10)))),
            list(map(sqr, list(range(10))))
        )

        it = self.pool.imap(sqr, range(10))
        for i in range(10):
            self.assertEqual(next(it), i*i)
        self.assertRaises(StopIteration, next, it)
        it = self.pool.imap(sqr, list(range(10)))
        for i in range(10):
            self.assertEqual(next(it), i*i)
        self.assertRaises(StopIteration, next, it)

        it = self.pool.imap(sqr, range(100), chunksize=20)
        for i in range(100):
            self.assertEqual(next(it), i*i)
        self.assertRaises(StopIteration, next, it)
        it = self.pool.imap(sqr, list(range(100)), chunksize=20)
        for i in range(100):
            self.assertEqual(next(it), i*i)
        self.assertRaises(StopIteration, next, it)

    def test_imap_unordered(self):
        args = list(range(10))
        result = list(map(sqr, args))
        it = self.pool.imap_unordered(sqr, args)
        self.assertEqual(sorted(it), result)
        it = self.pool.imap_unordered(sqr, iter(args))
        self.assertEqual(sorted(it), result)
        it = self.pool.imap_unordered(sqr, (a for a in args))
        self.assertEqual(sorted(it), result)

        args = list(range(100))
        result = list(map(sqr, args))
        it = self.pool.imap_unordered(sqr, args, chunksize=20)
        self.assertEqual(sorted(it), result)
        it = self.pool.imap_unordered(sqr, iter(args), chunksize=20)
        self.assertEqual(sorted(it), result)
        it = self.pool.imap_unordered(sqr, (a for a in args), chunksize=20)
        self.assertEqual(sorted(it), result)

    def test_starmap(self):
        tuples = list(zip(range(10), range(9, -1, -1)))
        self.assertEqual(
            self.pool.starmap(mul, tuples),
            list(itertools.starmap(mul, tuples))
        )
        tuples = list(zip(range(100), range(99, -1, -1)))
        self.assertEqual(
            self.pool.starmap(mul, tuples, chunksize=20),
            list(itertools.starmap(mul, tuples))
        )

    def test_istarmap(self):
        tuples = list(zip(range(10), range(9, -1, -1)))
        result = list(itertools.starmap(mul, tuples))
        it = self.pool.istarmap(mul, tuples)
        self.assertEqual(list(it), result)
        iterator = zip(range(10), range(9, -1, -1))
        it = self.pool.istarmap(mul, iterator)
        self.assertEqual(list(it), result)

        tuples = list(zip(range(10), range(9, -1, -1)))
        it = self.pool.istarmap(mul, tuples)
        for i, j in tuples:
            self.assertEqual(next(it), i*j)
        self.assertRaises(StopIteration, next, it)

        tuples = list(zip(range(100), range(99, -1, -1)))
        it = self.pool.istarmap(mul, tuples, chunksize=20)
        for i, j in tuples:
            self.assertEqual(next(it), i*j)
        self.assertRaises(StopIteration, next, it)

    def test_istarmap_unordered(self):
        tuples = list(zip(range(10), range(9, -1, -1)))
        result = list(itertools.starmap(mul, tuples))
        it = self.pool.istarmap_unordered(mul, tuples)
        self.assertEqual(sorted(it), sorted(result))
        iterator = zip(range(10), range(9, -1, -1))
        it = self.pool.istarmap_unordered(mul, iterator)
        self.assertEqual(sorted(it), sorted(result))

        tuples = list(zip(range(100), range(99, -1, -1)))
        result = list(itertools.starmap(mul, tuples))
        it = self.pool.istarmap_unordered(mul, tuples, chunksize=20)
        self.assertEqual(sorted(it), sorted(result))

    def test_apply_async(self):
        res = self.pool.apply_async(sqr, (7,))
        self.assertEqual(res.get(), 49)

        res = self.pool.apply_async(sqr, (7, TIMEOUT2,))
        get = TimingWrapper(res.get)
        self.assertEqual(get(), 49)
        self.assertLess(get.elapsed, TIMEOUT2*10)
        self.assertGreater(get.elapsed, TIMEOUT2/10)

    def test_apply_async_timeout(self):
        res = self.pool.apply_async(sqr, (7, TIMEOUT2,))
        self.assertFalse(res.ready())
        self.assertRaises(ValueError, res.successful)
        res.wait(TIMEOUT2/100)
        self.assertFalse(res.ready())
        self.assertRaises(ValueError, res.successful)
        self.assertRaises(TimeoutError, res.get, TIMEOUT2/100)
        res.wait()
        self.assertTrue(res.ready())
        self.assertTrue(res.successful())
        self.assertEqual(res.get(), 49)

    def test_map_async(self):
        args = list(range(10))
        self.assertEqual(
            self.pool.map_async(sqr, args).get(),
            list(map(sqr, args))
        )
        args = list(range(100))
        self.assertEqual(
            self.pool.map_async(sqr, args, chunksize=20).get(),
            list(map(sqr, args))
        )

    def test_map_async_callbacks(self):
        call_args = []
        result = self.pool.map_async(
            int, ['1', '2'],
            callback=call_args.append,
            error_callback=call_args.append
        )
        result.wait()
        self.assertTrue(result.successful())
        self.assertEqual(len(call_args), 1)
        self.assertEqual(call_args[0], [1, 2])
        result = self.pool.map_async(
            int, ['a'],
            callback=call_args.append,
            error_callback=call_args.append
        )
        result.wait()
        self.assertFalse(result.successful())
        self.assertEqual(len(call_args), 2)
        self.assertIsInstance(call_args[1], ValueError)

    def test_starmap_async(self):
        tuples = list(zip(range(10), range(9, -1, -1)))
        self.assertEqual(
            self.pool.starmap_async(mul, tuples).get(),
            list(itertools.starmap(mul, tuples))
        )
        tuples = list(zip(range(1000), range(999, -1, -1)))
        self.assertEqual(
            self.pool.starmap_async(mul, tuples, chunksize=100).get(),
            list(itertools.starmap(mul, tuples))
        )

    # ---

    def test_terminate(self):
        p = self.Pool(1)
        for _ in range(100):
            p.apply_async(time.sleep, (TIMEOUT1,))
        result = p.apply_async(time.sleep, (TIMEOUT1,))
        p.terminate()
        p.join()
        result.wait(TIMEOUT1)
        result.wait()
        self.assertFalse(result.successful())
        self.assertRaises(Exception, result.get, TIMEOUT1)
        self.assertRaises(Exception, result.get)

        p = self.Pool(1)
        args = [TIMEOUT1] * 100
        result = p.map_async(time.sleep, args, chunksize=1)
        p.terminate()
        p.join()
        result.wait(TIMEOUT1)
        result.wait()
        self.assertFalse(result.successful())
        self.assertRaises(Exception, result.get, TIMEOUT1)
        self.assertRaises(Exception, result.get)

    def test_empty_iterable(self):
        p = self.Pool(1)

        self.assertEqual(p.map(sqr, []), [])
        self.assertEqual(list(p.imap(sqr, [])), [])
        self.assertEqual(list(p.imap_unordered(sqr, [])), [])

        self.assertEqual(p.starmap(sqr, []), [])
        self.assertEqual(list(p.istarmap(sqr, [])), [])
        self.assertEqual(list(p.istarmap_unordered(sqr, [])), [])

        self.assertEqual(p.map_async(sqr, []).get(), [])
        self.assertEqual(p.starmap_async(mul, []).get(), [])

        p.close()
        p.join()

    def test_enter_exit(self):
        pool = self.Pool(1)

        with pool:
            pass
        # with self.assertRaises(ValueError):
        #     with pool:
        #         pass

        pool.join()

    # ---

    def test_async_error_callback(self):
        p = self.Pool(1)
        scratchpad = [None]
        def errback(exc):
            scratchpad[0] = exc
        res = p.apply_async(raising, error_callback=errback)
        p.close()
        p.join()
        self.assertRaises(KeyError, res.get)
        self.assertTrue(scratchpad[0])
        self.assertIsInstance(scratchpad[0], KeyError)

    def test_pool_worker_lifetime_early_close(self):
        p = self.Pool(1)
        results = []
        for i in range(5):
            results.append(p.apply_async(sqr, (i, TIMEOUT1)))
        p.close()
        p.join()
        for (j, res) in enumerate(results):
            self.assertEqual(res.get(), sqr(j))

    # ---

    def test_arg_processes(self):
        with self.assertRaises(ValueError):
            self.Pool(-1)
        with self.assertRaises(ValueError):
            self.Pool(0)

    def test_arg_initializer(self):
        p = self.Pool(1, initializer=identity, initargs=(123,))
        with self.assertRaises(TypeError):
            self.Pool(initializer=123)

    def test_unsupported_args(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with self.assertRaises(UserWarning):
                with self.Pool(1, maxtasksperchild=1):
                    pass
            with self.assertRaises(UserWarning):
                with self.Pool(1, context=object):
                    pass


# ---

def broken_mpi_spawn():
    darwin = (sys.platform == 'darwin')
    windows = (sys.platform == 'win32')
    azure = (os.environ.get('TF_BUILD') == 'True')
    github = (os.environ.get('GITHUB_ACTIONS') == 'true')
    skip_spawn = (
        os.environ.get('MPI4PY_TEST_SPAWN')
        in (None, '0', 'no', 'off', 'false')
    )
    name, version = MPI.get_vendor()
    if name == 'Open MPI':
        if version < (3,0,0):
            return True
        if version == (4,0,0):
            return True
        if version == (4,0,1) and darwin:
            return True
        if version == (4,0,2) and darwin:
            return True
        if version >= (4,1,0) and version < (4,2,0):
            if azure or github:
                return True
        if version >= (5,0,0) and version < (5,1,0):
            if skip_spawn:
                return True
    if name == 'MPICH':
        if version >= (3, 4) and version < (4, 0) and darwin:
            return True
        if version < (4, 1):
            if MPI.COMM_WORLD.Get_attr(MPI.APPNUM) is None:
                return True
        if version < (4, 3):
            try:
                port = MPI.Open_port()
                MPI.Close_port(port)
            except:
                return True
    if name == 'Intel MPI':
        import mpi4py
        if mpi4py.rc.recv_mprobe:
            return True
        if MPI.COMM_WORLD.Get_size() > 1 and windows:
            return True
    if name == 'Microsoft MPI':
        if version < (8,1,0):
            return True
        if skip_spawn:
            return True
        if MPI.COMM_WORLD.Get_attr(MPI.APPNUM) is None:
            return True
        if os.environ.get("PMI_APPNUM") is None:
            return True
    if name == 'MVAPICH':
        if MPI.COMM_WORLD.Get_attr(MPI.APPNUM) is None:
            return True
        if version < (3,0,0):
            return True
    if name == 'MPICH2':
        if MPI.COMM_WORLD.Get_attr(MPI.APPNUM) is None:
            return True
    if MPI.Get_version() < (2,0):
        return True
    if any(map(sys.modules.get, ('cupy', 'numba'))):
        return True
    #
    return False


@unittest.skipIf(broken_mpi_spawn(), 'mpi-spawn')
@unittest.skipIf(MPI.COMM_WORLD.Get_size() > 1, 'mpi-world-size>1')
class TestProcessPool(BaseTestPool, unittest.TestCase):
    PoolType = pool.Pool


class TestThreadPool(BaseTestPool, unittest.TestCase):
    PoolType = pool.ThreadPool


# ---


class ExtraExecutorMixing:

    def map(
        self, fn, iterable,
        timeout=None, chunksize=1,
        unordered=False,
    ):
        del unordered  # ignored, unused
        return super().map(
            fn, iterable,
            timeout=timeout,
            chunksize=chunksize,
        )

    def starmap(
        self, fn, iterable,
        timeout=None, chunksize=1,
        unordered=False,
    ):
        del unordered  # ignored, unused
        fn = functools.partial(self._apply_args, fn)
        return super().map(
            fn, iterable,
            timeout=timeout,
            chunksize=chunksize,
        )

    @staticmethod
    def _apply_args(fn, args):
        return fn(*args)


class ExtraExecutor(ExtraExecutorMixing, cf.ThreadPoolExecutor):
    pass


class ExtraPool(pool.Pool):
    Executor = ExtraExecutor


class TestExtraPool(BaseTestPool, unittest.TestCase):
    PoolType = ExtraPool
    @classmethod
    def Pool(cls, *args, **kwargs):
        return cls.PoolType(*args, **kwargs)


del TestExtraPool


# ---

if __name__ == '__main__':
    unittest.main()
