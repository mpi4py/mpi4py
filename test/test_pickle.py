from mpi4py import MPI
import mpiunittest as unittest

import sys

try:
    import marshal
except ImportError:
    marshal = None

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json = None

OBJS = [
    None,
    True,
    False,
    7,
    1<<32,
    3.14,
    1+2j,
    'qwerty',
    (0, 1, 2),
    [0, 1, 2],
    {'a':0, 'b': 1},
    ]

class TestPickle(unittest.TestCase):

    def setUp(self):
        pickle = MPI._p_pickle
        self._backup = (pickle.dumps,
                        pickle.loads,
                        pickle.PROTOCOL)

    def tearDown(self):
        pickle = MPI._p_pickle
        (pickle.dumps,
         pickle.loads,
         pickle.PROTOCOL) = self._backup

    def do_pickle(self, obj, pickle):
        comm = MPI.COMM_SELF
        o = comm.sendrecv(obj)
        self.assertEqual(obj, o)
        s = pickle.dumps(obj, pickle.PROTOCOL)
        o = pickle.loads(s)
        self.assertEqual(obj, o)

    def testPickle(self):
        pickle = MPI._p_pickle
        protocols = [0, 1, 2]
        if sys.version_info[0] > 2:
            protocols.append(3)
        protocols.append(-1)
        for protocol in protocols:
            pickle.PROTOCOL = protocol
            for obj in OBJS:
                self.do_pickle(obj, pickle)
            self.do_pickle(OBJS, pickle)

    if marshal is not None:
        def testMarshal(self):
            pickle = MPI._p_pickle
            pickle.dumps = marshal.dumps
            pickle.loads = marshal.loads
            protocols = [0]
            if sys.version_info[:2] <  (2, 4):
                pickle.dumps = lambda o,p: marshal.dumps(o)
            if sys.version_info[:2] >= (2, 4):
                protocols.append(1)
            if sys.version_info[:2] >= (2, 5):
                protocols.append(2)
            for protocol in protocols:
                pickle.PROTOCOL = protocol
                for obj in OBJS:
                    self.do_pickle(obj, pickle)
                self.do_pickle(OBJS, pickle)

    if json is not None:
        def testJson(self):
            pickle = MPI._p_pickle
            pickle.dumps = lambda o,p: json.dumps(o).encode()
            pickle.loads = lambda s: json.loads(s.decode())
            OBJS2 = [o for o in OBJS if not
                     isinstance(o, (complex, tuple))]
            for obj in OBJS2:
                self.do_pickle(obj, pickle)
            self.do_pickle(OBJS2, pickle)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
