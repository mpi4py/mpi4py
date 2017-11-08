# ---

import mpi4py
try: mpi4py.get_include()
except: pass
try: mpi4py.get_config()
except: pass

# ---

def test_mpi4py_rc():
    import mpi4py.rc
    mpi4py.rc(
    initialize = True,
    threads = True,
    thread_level = 'multiple',
    finalize = None,
    fast_reduce = True,
    recv_mprobe = True,
    errors = 'exception',
    )
    try: mpi4py.rc(qwerty=False)
    except TypeError: pass
    else: raise RuntimeError

test_mpi4py_rc()

# ---

def test_mpi4py_profile():
    import mpi4py
    def mpi4py_profile(*args, **kargs):
        try: mpi4py.profile(*args, **kargs)
        except ValueError: pass
    import warnings
    warnings.simplefilter('ignore')
    mpi4py_profile('mpe')
    mpi4py_profile('mpe', path="/usr/lib")
    mpi4py_profile('mpe', path=["/usr/lib"])
    mpi4py_profile('mpe', logfile="mpi4py")
    mpi4py_profile('mpe', logfile="mpi4py")
    mpi4py_profile('vt')
    mpi4py_profile('vt', path="/usr/lib")
    mpi4py_profile('vt', path=["/usr/lib"])
    mpi4py_profile('vt', logfile="mpi4py")
    mpi4py_profile('vt', logfile="mpi4py")
    mpi4py_profile('@querty')
    mpi4py_profile('c', path=["/usr/lib", "/usr/lib64"])
    mpi4py_profile('m', path=["/usr/lib", "/usr/lib64"])
    mpi4py_profile('dl', path=["/usr/lib", "/usr/lib64"])
    mpi4py_profile('hosts', path=["/etc"])

test_mpi4py_profile()

# ---

import mpi4py.__main__
import mpi4py.bench
import mpi4py.futures
import mpi4py.futures.__main__
import mpi4py.futures.server
import mpi4py.run
