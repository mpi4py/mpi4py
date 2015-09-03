import mpi4py
mpi4py.get_include()
mpi4py.get_config()

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
try: mpi4py.rc(querty=False)
except TypeError: pass

import mpi4py
mpi4py.profile()
mpi4py.profile('mpe')
mpi4py.profile('mpe', path="/usr/lib")
mpi4py.profile('mpe', path=["/usr/lib"])
mpi4py.profile('mpe', logfile="mpi4py")
mpi4py.profile('mpe', logfile="mpi4py")
mpi4py.profile('vt')
mpi4py.profile('vt', path="/usr/lib")
mpi4py.profile('vt', path=["/usr/lib"])
mpi4py.profile('vt', logfile="mpi4py")
mpi4py.profile('vt', logfile="mpi4py")
try: mpi4py.profile('@querty')
except ValueError: pass

import mpi4py.__main__
