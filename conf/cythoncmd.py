#!/usr/bin/env python
import sys, os

topdir = os.path.dirname(os.path.dirname(__file__))
srcdir = os.path.join(topdir, 'src')
if '--working' not in sys.argv:
    sys.argv[1:1] = ['--working', srcdir]
if '--cleanup' not in sys.argv:
    sys.argv[1:1] = ['--cleanup', str(3)]

sys.path.insert(0, os.path.dirname(__file__))
import cyautodoc
from Cython.Compiler.Main import main
main(command_line=1)
