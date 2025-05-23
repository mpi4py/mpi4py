import mpiunittest as unittest

from mpi4py import MPI

try:
    import pickle as pyPickle
except ImportError:
    pyPickle = None

try:
    import dill
except ImportError:
    dill = None

try:
    import marshal
except ImportError:
    marshal = None

try:
    import json
except ImportError:
    json = None

try:
    import yaml

    yaml.dump(None)
except ImportError:
    yaml = None

OBJS = [
    None,
    True,
    False,
    7,
    1 << 32,
    1.62,
    1 + 2j,
    "qwerty",
    (0, 1, 2),
    [0, 1, 2],
    {"a": 0, "b": 1},
]


def tobytes(s):
    return memoryview(s).tobytes()


class TestPickle(unittest.TestCase):
    #
    def setUp(self):
        self.pickle = MPI.pickle

    def tearDown(self):
        self.pickle.__init__()

    def do_pickle(self, obj, pickle):
        comm = MPI.COMM_SELF
        o = comm.sendrecv(obj, 0, 0, None, 0, 0)
        self.assertEqual(obj, o)
        s = pickle.dumps(obj)
        o = pickle.loads(s)
        self.assertEqual(obj, o)

    def testDefault(self):
        pickle = self.pickle
        protocols = [0, 1, 2, 3, 4, 5]
        protocols.extend((-1, None))
        for proto in protocols:
            pickle.__init__(protocol=proto)
            for obj in OBJS:
                self.do_pickle(obj, pickle)
            self.do_pickle(OBJS, pickle)

    def testPyPickle(self):
        pickle = self.pickle
        dumps = pyPickle.dumps
        loads = pyPickle.loads
        protocols = [0, 1, 2, 3, 4, 5]
        protocols.extend((-1, None))
        for proto in protocols:
            pickle.__init__(dumps, loads, proto)
            for obj in OBJS:
                self.do_pickle(obj, pickle)
            self.do_pickle(OBJS, pickle)

    @unittest.skipIf(dill is None, "dill")
    def testDill(self):
        pickle = self.pickle
        dumps = dill.dumps
        loads = dill.loads
        protocols = list(range(dill.HIGHEST_PROTOCOL + 1))
        protocols.extend((-1, None))
        for proto in protocols:
            pickle.__init__(dumps, loads, proto)
            for obj in OBJS:
                self.do_pickle(obj, pickle)
            self.do_pickle(OBJS, pickle)

    @unittest.skipIf(marshal is None, "marshal")
    def testMarshal(self):
        pickle = self.pickle
        dumps = marshal.dumps
        loads = marshal.loads
        protocols = [0, 1, 2, 3, 4]
        protocols.append(None)
        for protocol in protocols:
            pickle.__init__(dumps, loads, protocol)
            for obj in OBJS:
                self.do_pickle(obj, pickle)
            self.do_pickle(OBJS, pickle)

    @unittest.skipIf(json is None, "json")
    def testJson(self):
        pickle = self.pickle

        def dumps(o):
            return json.dumps(o).encode()

        def loads(s):
            return json.loads(tobytes(s).decode())

        pickle.__init__(dumps, loads)
        OBJS2 = [o for o in OBJS if not isinstance(o, (float, complex, tuple))]
        for obj in OBJS2:
            self.do_pickle(obj, pickle)
        self.do_pickle(OBJS2, pickle)

    @unittest.skipIf(yaml is None, "yaml")
    def testYAML(self):
        pickle = self.pickle

        def dumps(o):
            return yaml.dump(o).encode()

        def loads(s):
            return yaml.load(tobytes(s).decode(), Loader=yaml.Loader)

        pickle.__init__(dumps, loads)
        OBJS2 = [o for o in OBJS if not isinstance(o, (complex, tuple))]
        for obj in OBJS2:
            self.do_pickle(obj, pickle)
        self.do_pickle(OBJS2, pickle)


if __name__ == "__main__":
    unittest.main()
